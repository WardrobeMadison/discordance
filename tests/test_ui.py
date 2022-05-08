from pathlib import Path

from dissonance import analysis, init_log, io, viewer

from .constants import MAPPED_DIR

logger = init_log()

FOLDERS = ["DR","WT"]

class TestGui():

    def test_window_wholecell(self):
        try:
            #uncheckedpath = Path("DemoForJenna.txt")
            #unchecked = io.read_unchecked_file(uncheckedpath)
            unchecked = None
            uncheckedpath = None

            folders = FOLDERS
            #folders = ["GG2 control", "GG2 KO"]
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

            epochio = io.EpochIO(params, paths)
            wa = analysis.LedWholeAnalysis()

            viewer.run(epochio, wa, unchecked, uncheckedpath)
        except SystemExit as e:
            ...
        finally:
            assert True

    def test_window_spikecell(self):
        try:

            #uncheckedpath = Path("DemoForJenna.txt")
            #unchecked = io.read_unchecked_file(uncheckedpath)
            unchecked = None
            uncheckedpath = None

            folders = FOLDERS
            #folders = ["GG2 control", "GG2 KO"]
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

            epochio = io.EpochIO(params, paths)
            lsa = analysis.LedSpikeAnalysis()

            viewer.run(epochio, lsa, unchecked, uncheckedpath)
        except SystemExit as e:
            ...
        finally:
            assert True

    def test_window_browsing(self):
        try:
            #uncheckedpath = Path("DemoForJenna.txt")
            #unchecked = io.read_unchecked_file(uncheckedpath)
            unchecked = None
            uncheckedpath = None

            folders = FOLDERS
            #folders = ["GG2 control", "GG2 KO"]
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

            epochio = io.EpochIO(params, paths)

            viewer.run(epochio, lsa, unchecked, uncheckedpath)
        except SystemExit as e:
            ...
        finally:
            assert True
