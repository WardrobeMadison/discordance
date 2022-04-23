"""
Spike detection algorithm
1. Band pass
2. Find peaks
3. Remove single sample
4. Separate peaks with k means clustering
5. Check for 4 sigma difference from noise
"""
from typing import Tuple

import numpy as np
from sklearn.cluster import KMeans

from .. import epochtypes as et
from .passfilters import high_pass_filter, low_pass_filter

HIGHPASSCUT_DRIFT = 70
HIGHPASSCUT_SPIKES = 500
SAMPLE_INTERVAL = 1e-4
REF_PERIOD = 2e-3
SEARCH_INTERVAL = 1e-3
REF_PERIOD_POINTS = round(REF_PERIOD / SAMPLE_INTERVAL)
SEARCH_INTERVAL_POINTS = round(SEARCH_INTERVAL / SAMPLE_INTERVAL)


def detect_spikes(R: np.array) -> et.EpochSpikeInfo:
    # PASS FILTERS
    R_no_spikes = low_pass_filter(
        high_pass_filter(
            R,
            HIGHPASSCUT_DRIFT,
            SAMPLE_INTERVAL),
        HIGHPASSCUT_SPIKES,
        SAMPLE_INTERVAL)

    R_high_pass = high_pass_filter(
        R,
        HIGHPASSCUT_SPIKES,
        SAMPLE_INTERVAL)

    # GET TRACE AND NOISE_STD
    trace = R_high_pass.copy()
    trace[:20] = R[:20] - np.mean(R[:20])

    # FILP IF NEEDED
    if abs(max(trace)) > abs(min(trace)):
        trace = -trace

    noise_std = R_no_spikes.std()

    # GET PEAKS
    peaks, peak_times = get_peaks(trace, -1)
    neg_def_idx = np.flatnonzero(peaks < 0)
    peak_times = peak_times[neg_def_idx]
    peaks = trace[peak_times]

    # REMOVE SINGLE SAMPLE PEAKS
    trace_res_even = trace[0::2]
    trace_res_odd = trace[1::2]
    _, peak_times_res_even = get_peaks(trace_res_even, -1)
    _, peak_times_res_odd = get_peaks(trace_res_odd, -1)
    peak_times_res_even = peak_times_res_even * 2
    peak_times_res_odd = 2 * peak_times_res_odd - 1
    peak_times = np.array(sorted(set(peak_times) & set(
        [*peak_times_res_even, *peak_times_res_odd])))  # could be trouble
    peaks = trace[peak_times]

    # CLUSTER PEAKS
    if len(peaks):
        # CHECK FOR REBOUNDS ON THE OTHER SIDE
        rebounds = get_rebounds(peak_times, trace, SEARCH_INTERVAL_POINTS)
        peaks = abs(peaks)
        peak_amps = peaks + rebounds

        if len(peaks) and np.max(R) > np.min(R):
            max_iter = 100000
            init = np.array(
                [[np.percentile(peak_amps, q=0.5)], [peak_amps.max()]])

            clusters = KMeans(
                n_clusters=2, init=init, n_init=1,
                max_iter=max_iter).fit(peak_amps.reshape(-1, 1))

            idx, centroids = clusters.labels_, clusters.cluster_centers_

            _, m_idx = max(centroids), np.where(centroids == max(centroids))[0]
            spike_ind_log = np.where(idx == m_idx)[0]

            # DISTRIBUTION SEPARATION CHECK
            spike_peaks = peak_amps[np.flatnonzero(idx)]
            nonspike_peaks = peak_amps[np.flatnonzero(idx == 0)]
            nonspike_idx = np.where(idx == 0)[0]
            sigma = np.sqrt(nonspike_peaks).std()

            # NO SPIKES CHECK - MUST HAVE 4 SIGMA DIFFERENCE
            if (
                (np.sqrt(spike_peaks).mean() < np.sqrt(
                    nonspike_peaks).mean() + 4 * sigma)
                or
                    len(spike_ind_log) == 0):
                print(f"Epoch: no spikes.")
                sp = np.array([0.0], dtype=float)
                spike_amps = np.array([0.0], dtype=float)
                min_spike_peak_idx = np.array([0.0], dtype=float)
                max_noise_peak_time = np.array([0.0], dtype=float)
                violation_idx = np.array([0.0], dtype=float)
            # SPIKES ARE FOUND
            else:
                overlaps = len(np.where(spike_peaks < max(nonspike_peaks)))
                if overlaps < 0:
                    print(
                        f"Warning: {overlaps} spikes amplitudes overlapping tail of noise distribution.")

                sp = peak_times[spike_ind_log]
                spike_amps = peak_amps[spike_ind_log] / noise_std
                min_spike_peak_idx = np.flatnonzero(
                    spike_peaks == min(spike_peaks))
                max_noise_peak_idx = np.flatnonzero(
                    nonspike_peaks == max(nonspike_peaks))
                max_noise_peak_time = peak_times[nonspike_idx[max_noise_peak_idx]]
                violation_idx = peak_times[nonspike_idx[max_noise_peak_idx]]

                # CHECK FOR VIOLATIONS AGAIN
                # if ref_violations > 0:
                #	print(f"WARNING: {ref_violations} refactory violations.")
        # NO SPIKES
        else:
            print(f"Epoch: no spikes.")
            sp = np.array([0.0], dtype=float)
            spike_amps = np.array([0.0], dtype=float)
            min_spike_peak_idx = np.array([0.0], dtype=float)
            max_noise_peak_time = np.array([0.0], dtype=float)
            violation_idx = np.array([0.0], dtype=float)

    if len(sp) == 1:  # HACK IF ONLY ONE SPIKE SET TO NO SPIKE
        sp = peak_times[spike_ind_log]
        spike_amps = peak_amps[spike_ind_log] / noise_std
        min_spike_peak_idx = np.flatnonzero(
            spike_peaks == min(spike_peaks))
        max_noise_peak_idx = np.flatnonzero(
            nonspike_peaks == max(nonspike_peaks))
        max_noise_peak_time = peak_times[nonspike_idx[max_noise_peak_idx]]
        violation_idx = peak_times[nonspike_idx[max_noise_peak_idx]]

    return et.EpochSpikeInfo(
        sp=sp,
        spike_amps=spike_amps,
        min_spike_peak_idx=min_spike_peak_idx,
        max_noise_peak_time=max_noise_peak_time,
        violation_idx=violation_idx)


def get_rebounds(peaks_idx: np.array, trace_in: np.array, search_interval: float) -> np.array:
    trace = abs(trace_in)
    peaks = trace[peaks_idx]
    r = np.zeros(peaks.shape)

    for i, peak in enumerate(peaks):
        end_point = min(peaks_idx[i] + search_interval, len(trace)) + 1
        next_min, _ = get_peaks(trace[peaks_idx[i]:end_point], -1)

        if len(next_min) == 0:
            next_min = peak
        else:
            next_min = next_min[0]

        next_max, _ = get_peaks(trace[peaks_idx[i]:end_point], 1)
        if len(next_max) == 0:
            next_max = 0
        else:
            next_max = next_max[0]

        if next_min < peak:
            r[i] = 0
        else:
            r[i] = next_max
    return r


def get_peaks(R: np.array, direction: int) -> Tuple[np.array, np.array]:
    if direction > 0:
        mat = np.diff(np.diff(R) > 0)
        idx = np.flatnonzero(mat < 0)+1
    else:
        mat = np.diff(np.diff(R) > 0)
        idx = np.flatnonzero(mat > 0)+1

    peaks = R[idx]
    peak_times = idx

    return peaks, peak_times
