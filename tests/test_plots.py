import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from dissonance import io, epochtypes, viewer, analysis
from pathlib import Path
import pytest
import sys
sys.path.append("..")

ROOTDIR = Path("/home/joe/Projects/DataStore/MappedData")


class TestLedWholeAnalysis():

    @pytest.fixture
    def setUp(self):
        self.root_dir = ROOTDIR
        self.tree = self.load_epochs(["Test"], "wholetrace")
        self.tofind = dict(
            Name="LedWholeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC\OFF-transient",
            genotype="DR",
            cellname="20211208A_Cell3",
            lightamplitude=0.0,
            lightmean=0.007,
            startdate="2021-12-08 15:55:28.228351")

        with open("delete.txt", "w+") as fin:
            fin.writelines(self.tree.visual)

    @pytest.fixture
    def tearDown(self):
        ...

    @pytest.fixture
    def load_epochs(self, folders, tracetype, uncheckedpath=None, nfiles=5):
        paramnames = (
            "protocolname",
            "led",
            "celltype",
            "genotype",
            "cellname",
            "lightamplitude",
            "lightmean",
            "startdate")
        if uncheckedpath is None:
            unchecked = None
        else:
            unchecked = io.read_unchecked_file(uncheckedpath)

        paths = []
        for fldr in folders:
            paths.extend(
                [file
                    for ii, file in enumerate((self.root_dir/fldr).glob("*.h5"))
                    if ii < nfiles
                 ]
            )

        dr = io.DissonanceReader(paths)
        epochs = dr.to_params(paramnames, filters={"tracetype": tracetype})

        tree = analysis.LedWholeAnalysis(epochs, paths)
        return tree

    def test_epoch_summary(self):
        canvas = analysis.charting.MplCanvas(offline=True)

        node = self.tree.select_node(**self.tofind)

        self.tree.plot(node, canvas)

    def test_cell_summary(self):
        canvas = analysis.charting.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name=self.tofind["Name"],
            protocolname=self.tofind["protocolname"],
            led=self.tofind["led"],
            celltype=self.tofind["celltype"],
            genotype=self.tofind["genotype"],
            cellname=self.tofind["cellname"])

        self.tree.plot(node, canvas)

    def test_genotype_summary(self):
        canvas = analysis.charting.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name=self.tofind["Name"],
            protocolname=self.tofind["protocolname"],
            led=self.tofind["led"],
            celltype=self.tofind["celltype"],
            genotype=self.tofind["genotype"])

        self.tree.plot(node, canvas)

    def test_genotype_comparison(self):
        canvas = analysis.charting.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name=self.tofind["Name"],
            protocolname=self.tofind["protocolname"],
            led=self.tofind["led"],
            celltype=self.tofind["celltype"])

        self.tree.plot(node, canvas)


class TestLedSpikeAnalysis():

    def setUp(self):
        self.root_dir = ROOTDIR
        self.load_epochs(["Test"])

        self.tofind = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC",
            genotype="DR",
            cellname="20210706A_Cell5",
            lightmean=1000.0,
            lightamplitude=250.0,
            startdate="2021-07-06 13:38:29.641577")

    def load_epochs(self, folders, uncheckedpath=None, nfiles=5):
       
        if uncheckedpath is None:
            unchecked = None
        else:
            unchecked = io.read_unchecked_file(uncheckedpath)

        paths = []
        for fldr in folders:
            paths.extend(
                [file
                    for ii, file in enumerate((self.root_dir/fldr).glob("*.h5"))
                    if ii < nfiles
                 ]
            )

        dr = io.DissonanceReader(paths)
        paramnames = ["led", "protocolname", "celltype", "genotype",
                        "cellname", "lightamplitude", "lightmean", "startdate"]
        params = dr.to_params(paramnames, filters={
                                "tracetype": "spiketrace"})
        params = params.loc[params.protocolname.isin(
            ["LedPulseFamily", "LedPulse"])]

        self.epochio = io.EpochIO(params, paths)
        self.lsa = analysis.LedSpikeAnalysis()

    def test_epoch_summary(self):
        self.setUp()
        canvas = analysis.charting.MplCanvas(offline=True)

        #eframe = self.epochio.query(filters=[self.tofind])
        eframe = self.epochio.query(filters=[self.tofind])

        self.lsa.plot("startdate", eframe, canvas)
        canvas.draw()

    def test_cell_summary(self):
        self.setUp()
        canvas = analysis.charting.MplCanvas(offline=True)

        filter = {key:val for key,val in self.tofind.items() if key not in ["startdate", "lightmean", "lightamplitude"]}
        eframe = self.epochio.query(filters=[filter])

        self.lsa.plot("cellname", eframe, canvas)
        canvas.draw()

    def test_genotype_summary(self):
        self.setUp()

        canvas = analysis.charting.MplCanvas(offline=True)

        # TEST CRF
        params = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC",
            genotype="DR")

        eframe = self.epochio.query(filters = [params])
        self.lsa.plot("genotype", eframe, canvas)

        canvas.draw()

        # TEST HILL
        params = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulseFamily",
            led="Green LED",
            celltype="RGC",
            genotype="DR"
        )

        eframe = self.epochio.query(filters = [params])
        self.lsa.plot("genotype", eframe, canvas)

        canvas.draw()

    def test_genotype_comparison(self):
        self.setUp()

        canvas = analysis.charting.MplCanvas(offline=True)

        params = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC\ON-alpha")

        eframe = self.epochio.query(filters = [params])
        self.lsa.plot("celltype", eframe, canvas)

        canvas.draw()
