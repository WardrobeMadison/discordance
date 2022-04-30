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
        self.tree = self.load_epochs(["DR", "WT"], "wholetrace")
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

    @pytest.fixture
    def setUp(self):
        self.root_dir = ROOTDIR
        self.tree = self.load_epochs(["Test"], "spiketrace")

        self.tofind = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC",
            genotype="DR",
            cellname="Cell5_20210706A",
            lightmean=0.005,
            lightamplitude=0.005,
            startdate="2021-07-06 13:36:28.791547")

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
        params = dr.to_params(paramnames, filters={"tracetype": tracetype})
        tree = analysis.LedSpikeAnalysis(params, paths)
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

        # TEST CRF
        params = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC",
            genotype="DR")

        node = self.tree.select_node(**params)
        self.tree.plot(node, canvas)

        # TEST HILL
        params = dict(
            Name="LedSpikeAnalysis",
            protocolname="LedPulseFamily",
            led="Green LED",
            celltype="RGC",
            genotype="DR"
        )

        node = self.tree.select_node(**params)
        self.tree.plot(node, canvas)

    def test_genotype_comparison(self):
        canvas = analysis.charting.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name=self.tofind["Name"],
            protocolname=self.tofind["protocolname"],
            led=self.tofind["led"],
            celltype=self.tofind["celltype"])

        self.tree.plot(node, canvas)
