from pathlib import Path
import pandas as pd

from dissonance import analysis, init_log, io, viewer

from .constants import MAPPED_DIR

logger = init_log()

#FOLDERS = ["WT","DR"]
FOLDERS = ["GG2 KO", "GG2 control"]
UNCHECKEDPATH = Path("WHOLECELLFILTERS.txt")
UNCHECKED = set(pd.read_csv(UNCHECKEDPATH, parse_dates=["startdate"]).iloc[:, 0].values)

class TestGui():

    def test_window_wholecell(self):
        try:
            #uncheckedpath = Path("DemoForJenna.txt")

            folders = FOLDERS
            paths = []
            for fldr in folders:
                paths.extend(
                    [file
                     for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
                     ]
                )

            dr = io.DissonanceReader(paths)
            paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                          "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
            params = dr.to_params(paramnames, filters={
                                  "tracetype": "wholetrace"})
            params = params.loc[params.protocolname.isin(
                ["LedPulseFamily", "LedPulse"])]

            epochio = io.EpochIO(params, paths, unchecked=UNCHECKED)
            wa = analysis.LedWholeAnalysis()

            viewer.run(epochio, wa, UNCHECKED, UNCHECKEDPATH)
        except SystemExit as e:
            ...
        finally:
            assert True

    def test_window_spikecell(self):
        try:

            folders = FOLDERS
            paths = []
            for fldr in folders:
                paths.extend(
                    [file
                     for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
                     ]
                )

            dr = io.DissonanceReader(paths)
            paramnames = ["led", "protocolname", "celltype", "genotype",
                          "cellname", "lightamplitude", "lightmean", "startdate"]
            params = dr.to_params(paramnames, filters={
                                  "tracetype": "spiketrace"})
            params = params.loc[params.protocolname.isin(
                ["LedPulseFamily", "LedPulse"])]

            epochio = io.EpochIO(params, paths, UNCHECKED)
            lsa = analysis.LedSpikeAnalysis()

            viewer.run(epochio, lsa, UNCHECKED, UNCHECKEDPATH)
        except SystemExit as e:
            ...
        finally:
            assert True
    
    def test_window_saccadecell(self):
        try:

            folders = FOLDERS
            paths = []
            for fldr in folders:
                paths.extend(
                    [file
                     for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
                     ]
                )

            dr = io.DissonanceReader(paths)
            paramnames = ["holdingpotential", "led", "protocolname", "celltype", "genotype",
                          "cellname", "lightamplitude", "lightmean", "startdate"]
            params = dr.to_params(paramnames)
            params = params.loc[params.protocolname.isin(
                ["SaccadeTrajectory2"])]

            epochio = io.EpochIO(params, paths, UNCHECKED)
            lsa = analysis.SaccadeAnalysis()

            viewer.run(epochio, lsa, UNCHECKED, UNCHECKEDPATH)
        except SystemExit as e:
            ...
        finally:
            assert True

    def test_window_chirpcell(self):
        try:

            folders = FOLDERS
            paths = []
            for fldr in folders:
                paths.extend(
                    [file
                     for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
                     ]
                )

            dr = io.DissonanceReader(paths)
            paramnames = ["holdingpotential", "led", "protocolname", "celltype", "genotype",
                          "cellname", "lightamplitude", "lightmean", "startdate"]
            params = dr.to_params(paramnames)
            params = params.loc[params.protocolname.isin(
                ["ChirpStimulusLED"])]

            epochio = io.EpochIO(params, paths, UNCHECKED)
            lsa = analysis.ChirpAnalysis()

            viewer.run(epochio, lsa, UNCHECKED, UNCHECKEDPATH)
        except SystemExit as e:
            ...
        finally:
            assert True

    def test_window_browsing(self):
        try:
            folders = FOLDERS
            paths = []
            for fldr in folders:
                paths.extend(
                    [
						file
                    	for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
                     ]
                )

            dr = io.DissonanceReader(paths)
            lsa = analysis.BrowsingAnalysis()
            paramnames = ["led", "protocolname", "celltype", "genotype", "cellname",
                          "tracetype", "backgroundval", "lightamplitude", "lightmean", "startdate"]
            params = dr.to_params(paramnames)
            params = params.loc[params.protocolname.isin(
                ["LedPulse", "LedPulseFamily"])]

            epochio = io.EpochIO(params, paths, UNCHECKED)

            viewer.run(epochio, lsa, UNCHECKED, UNCHECKEDPATH)
        except SystemExit as e:
            ...
        finally:
            assert True
