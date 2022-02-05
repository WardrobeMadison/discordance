import numpy as np
from sklearn.cluster import KMeans

from .passfilters import high_pass_filter, low_pass_filter
from .get_peaks import get_peaks
from .get_rebounds import get_rebounds

def spike_detector(R):
    """
    R   signal matrix
    """
    #HighPassCut_drift = 70; %Hz, in order to remove drift and 60Hz noise
    #HighPassCut_spikes = 500; %Hz, in order to remove everything but spikes
    #SampleInterval = 1E-4;
    #ref_period = 2E-3; %s
    #searchInterval = 1E-3; %s

    if R is None:
        return None
    elif len(R.shape) == 1:
        R = R[None, :]

    highpasscut_drift = 70
    highpasscut_spikes = 500
    sample_interval = 1e-4
    ref_period  = 2e-3
    search_interval = 1e-3

    #results = [];
    results = []

    #%thres = 25; %stds
    #ref_period_points = round(ref_period./SampleInterval);
    #searchInterval_points = round(searchInterval./SampleInterval);

    # Set refactory period 
    ref_period_points = round(ref_period / sample_interval)
    search_interval_points = round(search_interval / sample_interval)

    #[Ntraces,L] = size(D);
    #D_noSpikes = BandPassFilter(D,HighPassCut_drift,HighPassCut_spikes,SampleInterval);
    #Dhighpass = HighPassFilter(D,HighPassCut_spikes,SampleInterval);
    #     function Xfilt = BandPassFilter(X,low,high,SampleInterval)
    # %this is not really correct
    # Xfilt = LowPassFilter(HighPassFilter(X,low,SampleInterval),high,SampleInterval);

    # 1 dimensional array or matrix of responses
    if len(R.shape) == 1:
        n_traces = 1
        length = len(R)
    else: 
        n_traces, length = R.shape

    R_no_spikes = low_pass_filter(high_pass_filter(R, highpasscut_drift, sample_interval), highpasscut_spikes, sample_interval)
    R_high_pass = high_pass_filter(R, highpasscut_spikes, sample_interval)

    #sp = cell(Ntraces,1);
    #spikeAmps = cell(Ntraces,1);
    #violation_ind = cell(Ntraces,1);
    #minSpikePeakInd = zeros(Ntraces,1);
    #maxNoisePeakTime = zeros(Ntraces,1);

    #for i=1:Ntraces
        #%get the trace and noise_std
        #trace = Dhighpass(i,:);
        #trace(1:20) = D(i,1:20) - mean(D(i,1:20));
    #%     plot(trace);
    #%     pause;
        #if abs(max(trace)) > abs(min(trace)) %flip it over
            #trace = -trace;
        #end
    
    sp = []
    violation_idx = []
    spike_amps = []
    max_noise_peak_time = []
    min_spike_peak_idx = []  
    max_noise_peak_idx = []
    for ii, trace in enumerate(R_high_pass):

        trace[:20] = R[ii, 0:20] - R[ii, :20].mean(axis=-1)

        if abs(max(trace)) > abs(min(trace)):
            trace = -trace

        #trace_noise = D_noSpikes(i,:);
        #noise_std = std(trace_noise);

        trace_noise = R_no_spikes[ii,:]
        noise_std = trace_noise.std()
        
        #%get peaks
        #function [peaks,Ind] = getPeaks(X,dir)
            #if dir > 0 %local max
                #Ind = find(diff(diff(X)>0)<0)+1;
            #else %local min
                #Ind = find(diff(diff(X)>0)>0)+1;
            #end
            #peaks = X(Ind);
        #[peaks,peak_times] = getPeaks(trace,-1); %-1 for negative peaks
        #peak_times = peak_times(peaks<0); %only negative deflections
        #peaks = trace(peak_times);    
        peaks, peak_times = get_peaks(trace, -1)
        try:
            neg_def_idx = np.nonzero(np.where(peaks < 0, 1, 0))
            peak_times = peak_times[neg_def_idx]
        except TypeError:
            peak_times = None
        peaks = trace[peak_times]

        #%basically another filtering step:
        #%remove single sample peaks, don't know if this helps
        #trace_res_even = trace(2:2:end);
        #trace_res_odd = trace(1:2:end);
        #[null,peak_times_res_even] = getPeaks(trace_res_even,-1);
        #[null,peak_times_res_odd] = getPeaks(trace_res_odd,-1);

        trace_res_even = trace[1::2]
        trace_res_odd = trace[::2]
        _, peak_times_res_even = get_peaks(trace_res_even, -1)
        _, peak_times_res_odd = get_peaks(trace_res_odd, -1)
        # #peak_times_res_even = peak_times_res_even*2;
        # #peak_times_res_odd = 2*peak_times_res_odd-1;
        # #peak_times = intersect(peak_times,[peak_times_res_even,peak_times_res_odd]);
        # #peaks = trace(peak_times);
        peak_times_res_even = peak_times_res_even * 2
        peak_times_res_odd = 2 * peak_times_res_odd - 1
        peak_times = np.array(sorted(set(peak_times) & set([*peak_times_res_even, *peak_times_res_odd]))) # could be trouble
        try: 
            peaks = trace[peak_times]
        except IndexError: 
            peaks = np.array([])

        if len(peaks):  
            #%add a check for rebounds on the other side
            #r = getRebounds(peak_times,trace,searchInterval_points);
            #peaks = abs(peaks);
            #peakAmps = peaks+r;
            rebounds = get_rebounds(peak_times, trace, search_interval_points)
            peaks = abs(peaks)
            peak_amps = peaks + rebounds
        
            #if ~isempty(peaks) && max(D(i,:)) > min(D(i,:)) %make sure we don't have bad/empty trace
                #options = statset('MaxIter',10000);
                #[Ind,centroid_amps] = kmeans(peakAmps,2,'start',[median(peakAmps);max(peakAmps)],'Options',options);

            if len(peaks) and max(R[ii,:]) > min(R[ii,:]):
                n_clusters = 2
                max_iter = 100000
                init = np.array([[np.percentile(peak_amps, q=0.5)],[peak_amps.max()]] )
                try: 
                    clusters = KMeans(n_clusters=n_clusters, init=init, n_init = 1, max_iter=max_iter).fit(peak_amps.reshape(-1,1))
                    idx, centroids = clusters.labels_, clusters.cluster_centers_
                except ValueError:
                    idx = np.array([0])
                    centroids = peak_amps
                
                #[m,m_ind] = max(centroid_amps);
                #spike_ind_log = (Ind==m_ind);
                #%spike_ind_log is logical, length of peaks

                m, m_idx =  max(centroids), np.where(centroids == max(centroids))[0]
                spike_ind_log = np.where(idx == m_idx)[0]
                
                #%distribution separation check
                #spike_peaks = peakAmps(spike_ind_log);
                #nonspike_peaks = peakAmps(~spike_ind_log);
                #nonspike_Ind = find(~spike_ind_log);
                #spike_Ind = find(spike_ind_log);
                #[m,sigma,m_ci,sigma_ci] = normfit(sqrt(nonspike_peaks));
                #mistakes = find(sqrt(nonspike_peaks)>m+5*sigma);
                spike_peaks = peak_amps[idx.nonzero()[0]]
                nonspike_peaks = peak_amps[np.where(idx == 0)[0]]
                nonspike_idx = np.where(idx == 0)[0]
                #spike_indx = bool(spike_ind_log)
                sigma = np.sqrt(nonspike_peaks).std()
                                    
                #%no spikes check - still not real happy with how sensitive this is
                #if mean(sqrt(spike_peaks)) < mean(sqrt(nonspike_peaks)) + 4*sigma; %no spikes
                    #disp(['Epoch ' num2str(i) ': no spikes']);
                    #sp{i} = [];
                    #spikeAmps{i} = [];
                
                    
                #else %spikes found
                    #overlaps = length(find(spike_peaks < max(nonspike_peaks)));%this check will not do anything
                    #if overlaps > 0
                        #disp(['warning: ' num2str(overlaps) ' spikes amplitudes overlapping tail of noise distribution']);
                    #end
                    #sp{i} = peak_times(spike_ind_log);
                    #spikeAmps{i} = peakAmps(spike_ind_log)./noise_std;
                    
                    #[minSpikePeak,minSpikePeakInd(i)] = min(spike_peaks);
                    #[maxNoisePeak,maxNoisePeakInd] = max(nonspike_peaks);
                    #maxNoisePeakTime(i) = peak_times(nonspike_Ind(maxNoisePeakInd));
                    
                    #%check for violations again, just for warning this time
                    #violation_ind{i} = find(diff(sp{i})<ref_period_points) + 1;
                    #ref_violations = length(violation_ind{i});
                    #if ref_violations>0
                        #%find(diff(sp{i})<ref_period_points)
                        #disp(['warning, trial '  num2str(i) ': ' num2str(ref_violations) ' refractory violations']);
                    #end
                #end %if spikes found

                if (np.sqrt(spike_peaks).mean() < np.sqrt(nonspike_peaks).mean() + 4 * sigma ) or len(spike_ind_log) == 0:
                    #print(f"Epoch {str(ii)}: no spikes.")
                    sp.append(None)
                    spike_amps.append(0)
                    min_spike_peak_idx.append(None)
                    max_noise_peak_time.append(None)
                    violation_idx.append(None)

                else: 
                    overlaps = len(np.where(spike_peaks < max(nonspike_peaks)))
                    #if overlaps < 0:
                        #print(f"Warning: {overlaps} spikes amplitudes overlapping tail of noise distribution.")
                    
                    sp.append(peak_times[spike_ind_log])
                    spike_amps.append(peak_amps[spike_ind_log] / noise_std)
                    min_spike_peak_idx.append(np.where(spike_peaks == min(spike_peaks))[0])
                    max_noise_peak_idx = np.where(nonspike_peaks == max(nonspike_peaks))[0]
                    max_noise_peak_time.append(peak_times[nonspike_idx[max_noise_peak_idx]])

                    violation_idx.append(peak_times[nonspike_idx[max_noise_peak_idx]])
                    ref_violations = len(violation_idx[-1])

                    #if ref_violations > 0:
                    #print(f"Warning: Trial {str(ii)}: {ref_violations} refactory violations.")
            else:
                #print(f"Epoch {str(ii)}: no spikes.")
                sp.append(None)
                spike_amps.append(0)
                min_spike_peak_idx.append(None)
                max_noise_peak_time.append(None)
                violation_idx.append(None)

        #end %end if not bad trace
    #end

    #if length(sp) == 1 %return vector not cell array if only 1 trial
        #sp = sp{1};
        #spikeAmps = spikeAmps{1};    
        #violation_ind = violation_ind{1};
    #end

    #results.sp = sp;
    #results.spikeAmps = spikeAmps;
    #results.minSpikePeakInd = minSpikePeakInd;
    #results.maxNoisePeakTime = maxNoisePeakTime;
    #results.violation_ind = violation_ind;

    results = dict()

    results["sp"] = sp
    results["spike_amps"] = spike_amps
    results["min_spike_peak_idx"] = min_spike_peak_idx
    results["max_noise_peak_time"] = max_noise_peak_time
    results["violation_idx"] = violation_idx

    return results