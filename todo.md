# TODO 

## Jenna's Suggestions

- [?] PRIORITY 2 axes are overalled on some plots
- [?] Spikes>GreenLED>PulseFamily not all lightamplitudes are showing up in tree
- [X] PRIORITY Hill fit and CRF should be at the CellType level so that I can compare between genotype. There should be only 1 graph with 2 lines for each genotype
- [X] PRIORITY X axis for time in graphs needs to be broken up by 0.5 s increments
- [X] PRIORITY I like how the peak on the PSTH (or excitation/inhibition trace)  is denoted by the dotted line, but I also want the value of the peak to be shown. It would also be nice to see the value of the TTP (ask me for clarification)
- [X] PRIORITY everything needs to be averaged according to RStarr instead of SymphonyUnits
- [X] PRIORITY sample size needs to come up for graphs at the genotype
- [ ] PRIORITY sample size appears inconsistent between swarm plots and PSTHs (or excitation/inhibition trace)  at the CellType node
- [X] need to be able to uncheck at higher levels of the tree than epoch
- [?] Weber needs to be implemented!
- [ ] LN model needs to be implemented


## Structure changes

- [ ] Merge Dissonance Reader and EpochIO?

## Review with Jenna

Spike Analysis
- [X] Cell summary: light amplitude and light mean
- [X] Get a different color map
- [X] Fix CRF axes - x values off and y values should be rounded, put light mean in title

Whole Cell Analysis
- [X] Whole Cell Analysis: Split on background amp1 (inhibition > 0, excitation < 0. holdingpotential)
- [ ] Epoch: print background amp value just for inhibition. Make inhibition analysis split on background amp 1 value
- [X] Genotype comparison: Don't label by cell
- [X] Genotype summary: Change colors for cell traces. Put labels on hill and weber fits. Weber fit is UVLED only


## GUI
- [ ] COMPARE SPIKE DETECTION CODE
- [X] Replace light amplitude and light mean
- [X] Start X values at 0 where stimtime is
- [X] Automatic resizing of scroll window with subplots
- [X] Associate raster epoch plots with number of epoch for easier filtering
- [X] Change cell label to include experiment name
- [X] Display name of filter file being used

- [X] Test updating of celltyes and genotypes within GUI

## ANALYSIS
- [X] Spike Analysis
    - [X] LED Pulse
        - [X] Contrast response curve (UV LED only)
    - [X] LED Pulse Family
        - [X] Hill fit (Green LED)
- [ ] Whole Cell Analysis
    - [X] Replace peak amplitude with min peak amp
    - [X] Width at half max in addition to peak amp and ttp
    - [X] Replace psth's with mean traces
    - [-] Led Pulse 
        - [x] Genotype comparison (swarm plots)
        - [X] Contrast response curve (UV LED only)
    - [ ] LED Pulse Family
        - [-] Hill fit (Green LED)
        - [-] Webere fit (UV LED)
- [ ] Linear model analysis


## DAY 2
- [-] Automatic plot update on uncheck Maybe add an uncheck button?
- [ ] Create logging for each session
- [ ] Check on 6_ file that doesn't have light mean, and other files with bad headers
- [ ] Information theory analysis