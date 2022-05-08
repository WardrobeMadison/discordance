import sys
sys.path.append("..")
import numpy as np
from pathlib import Path
from dissonance import io, epochtypes, viewer
from scipy.fft import fft
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# %%
ROOTDIR = Path("/home/joe/Projects/DataStore/MappedData")

# LOAD DATA
def load_epochs(folders, filters, uncheckedpath = None):
    if uncheckedpath is None:
        unchecked = None
    else:
        unchecked = io.read_unchecked_file(uncheckedpath)

    paths = []
    for fldr in folders:
        paths.extend(
            [	file
                for ii, file in enumerate((ROOTDIR/fldr).glob("*.h5"))
            ]
        )

    dr = io.DissonanceReader(paths)

    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                    "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    params = dr.to_params(paramnames, filters)

    epochio = io.EpochIO(params, paths)
    return epochio

# %%
epochio = load_epochs(["DR", "WT"], {"protocolname":"LedNoiseFamily"})

eparams = epochio.query(
    filters =[{"startdate":epochio.frame.startdate.iloc[0]}])

# %%
epoch = eparams.epoch.iloc[0]

epoch.stimparams
# CREATE STIMULUS
std = epoch.stimparams["stdev"]
mean = epoch.stimparams["mean"]
lower = epoch.stimparams["lowerlimit"]
upper = epoch.stimparams["upperlimit"]
seed = int(epoch.stimparams["seed"])

stimPts = epoch.stimtime
sampleRate = epoch.stimparams["samplerate"]
numFilters = epoch.stimparams["numfilters"]
freqCutOff = epoch.stimparams["freqcutoff"]


np.random.seed(int(seed))

# REVERSE ORDER TO MATCH MATLAB
#% Create gaussian noise.
#noiseTime = obj.stDev * stream.randn(1, stimPts);
noiseTime = std * np.random.randn(len(epoch.trace), 1).T

#% To frequency domain.
#noiseFreq = fft(noiseTime);
noiseFreq = fft(noiseTime)

#% The filter will change based on whether or not there are an even or odd number of points.
#freqStep = obj.sampleRate / stimPts;
#if mod(stimPts, 2) == 0
    #% Construct the filter.
    #frequencies = (0:stimPts / 2) * freqStep;
    #oneSidedFilter = 1 ./ (1 + (frequencies / obj.freqCutoff) .^ (2 * obj.numFilters));
    #filter = [oneSidedFilter fliplr(oneSidedFilter(2:end - 1))];
#else
    #% Construct the filter.
    #frequencies = (0:(stimPts - 1) / 2) * freqStep;
    #oneSidedFilter = 1 ./ (1 + (frequencies / obj.freqCutoff) .^ (2 * obj.numFilters));
    #filter = [oneSidedFilter fliplr(oneSidedFilter(2:end))];
#end

freqStep = sampleRate / stimPts
if stimPts % 2 == 0:
    frequences = np.arange(stimPts // 2) * freqStep
    oneSidedFilter = 1 / (1 + frequences / freqCutOff) ** (2 * numFilters)
    filter = np.column_stack([oneSidedFilter, oneSidedFilter[1:][::-1]])
else:
    frequences = np.arange((stimPts - 1)/2) * freqStep
    oneSidedFilter = 1 / (1 + frequences / freqCutOff) ** (2 * numFilters)
    filter = np.column_stack([oneSidedFilter, oneSidedFilter[1:][::-1]])

#% Figure out factor by which filter will alter st dev - in the frequency domain, values should be 
#% proportional to standard deviation of each independent sinusoidal component, but it is the variances of 
#% these sinusoidal components that add to give the final variance, therefore, one needs to consider how the 
#% filter values will affect the variances; note that the first value of the filter is omitted, because the 
#% first value of the fft is the mean, and therefore shouldn't contribute to the variance/standard deviation
#% in the time domain.
#filterFactor = sqrt(filter(2:end) * filter(2:end)' / (stimPts - 1));

#% Filter in freq domain.
#noiseFreq = noiseFreq .* filter;

#% Set first value of fft (i.e., mean in time domain) to 0.
#noiseFreq(1) = 0;

#% Go back to time domain.
#noiseTime = ifft(noiseFreq);

#% FilterFactor should represent how much the filter is expected to affect the standard deviation in the time 
#% domain, use it to rescale the noise.
#noiseTime = noiseTime / filterFactor;

#noiseTime = real(noiseTime);

#% Flip if specified.
#if obj.inverted
    #noiseTime = -noiseTime;
#end

#data = ones(1, prePts + stimPts + tailPts) * obj.mean;
#data(prePts + 1:prePts + stimPts) = noiseTime + obj.mean;

#% Clip signal to upper and lower limit.
#% NOTE: IF THERE ARE POINTS THAT ARE ACTUALLY OUT OF BOUNDS, THIS WILL MAKE IT SO THAT THE EXPECTATION OF 
#% THE STANDARD DEVIATION IS NO LONGER WHAT WAS SPECIFIED...
#data(data > obj.upperLimit) = obj.upperLimit;
#data(data < obj.lowerLimit) = obj.lowerLimit;

#quantities = data;



# stimulus, response, spikes
I = np.array()
R = np.array()
S = np.array()



# calculate spike triggered average

# calculate generator signal

# normalize filter

# convolution with normalized filtered

# make continuous spike rate

# sort and bin spikes

# plot linear

# fit sigmoid

# plot nonlinear


