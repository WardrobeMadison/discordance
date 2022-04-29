import unittest
import sys; sys.path.append("..")
from pathlib import Path
from dissonance import io, epochtypes, viewer
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

ROOTDIR = Path("/home/joe/Projects/DataStore/MappedData")

class LedWholeAnalysis(unittest.TestCase):

    def setUp(self):
        self.root_dir = ROOTDIR
        self.tree = self.load_epochs(["DR", "WT"], "wholetrace")
        self.tofind = dict(
            Name="LedWholeAnalysis",
            protocolname="LedPulseFamily",
            led="Green LED",
            celltype="RGC\OFF-sustained",
            genotype="WT",
            cellname="Cell2_20220215A",
            lightamplitude=3.2,
            lightmean= 0,   
            startdate="2022-02-15 13:15:48.094611")


        with open("delete.txt", "w+") as fin:
            fin.writelines(self.tree.visual)

    def tearDown(self):
        ...

    # LOAD DATA
    def load_epochs(self,folders, tracetype, uncheckedpath = None, nfiles = 5):
        if uncheckedpath is None:
            unchecked = None
        else:
            unchecked = io.read_unchecked_file(uncheckedpath)

        paths = []
        for fldr in folders:
            paths.extend(
                [	file
                    for ii, file in enumerate((self.root_dir/fldr).glob("*.h5"))
                    if ii < nfiles
                ]
            )

        dr = io.DissonanceReader(paths)
        epochs = dr.to_epochs(tracetype = tracetype)
        epochs = epochtypes.WholeEpochs(epochs)

        tree = viewer.analysistrees.LedWholeAnalysis(epochs)
        return tree

    def test_epoch_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(**self.tofind)

        self.tree.plot(node, canvas)

    def test_cell_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name = self.tofind["Name"],
            protocolname = self.tofind["protocolname"],
            led = self.tofind["led"],
            celltype = self.tofind["celltype"],
            genotype = self.tofind["genotype"],
            cellname = self.tofind["cellname"])

        self.tree.plot(node, canvas)

    def test_genotype_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name = self.tofind["Name"],
            protocolname = self.tofind["protocolname"],
            led = self.tofind["led"],
            celltype = self.tofind["celltype"],
            genotype = self.tofind["genotype"])

        self.tree.plot(node, canvas)

    def test_genotype_comparison(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name = self.tofind["Name"],
            protocolname = self.tofind["protocolname"],
            led = self.tofind["led"],
            celltype = self.tofind["celltype"])

        self.tree.plot(node, canvas)

class LedSpikeAnalysis(unittest.TestCase):

    def setUp(self):
        self.root_dir = ROOTDIR
        self.tree = self.load_epochs(["DR", "WT"], "spiketrace")

        self.tofind = dict(
            Name = "LedSpikeAnalysis",
            protocolname = "LedPulse",
            led = "Green LED",
            celltype = "RGC\ON-alpha",
            genotype="DR",
            cellname="Cell8_20220104A",
            lightmean=0, 
            lightamplitude=10.0,
            startdate="2022-01-04 12:20:52.230819")

        with open("delete.txt", "w+") as fin:
            fin.writelines(self.tree.visual)

    def tearDown(self):
        ...

    # LOAD DATA
    def load_epochs(self,folders, tracetype, uncheckedpath = None, nfiles = 5):
        if uncheckedpath is None:
            unchecked = None
        else:
            unchecked = io.read_unchecked_file(uncheckedpath)

        paths = []
        for fldr in folders:
            paths.extend(
                [	file
                    for ii, file in enumerate((self.root_dir/fldr).glob("*.h5"))
                    if ii < nfiles
                ]
            )

        dr = io.DissonanceReader(paths)
        epochs = dr.to_epochs(tracetype = tracetype)
        epochs = epochtypes.SpikeEpochs(epochs)

        tree = viewer.analysistrees.LedSpikeAnalysis(epochs)
        return tree

    def test_epoch_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(**self.tofind)

        self.tree.plot(node, canvas)

    def test_cell_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name = self.tofind["Name"],
            protocolname = self.tofind["protocolname"],
            led = self.tofind["led"],
            celltype = self.tofind["celltype"],
            genotype = self.tofind["genotype"],
            cellname = self.tofind["cellname"])

        self.tree.plot(node, canvas)

    def test_genotype_summary(self):
        canvas = viewer.components.MplCanvas(offline=True)

        # TEST CRF
        params = dict(
            Name = "LedSpikeAnalysis",
            protocolname="LedPulse",
            led="UV LED",
            celltype="RGC\ON-alpha",
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
        canvas = viewer.components.MplCanvas(offline=True)

        node = self.tree.select_node(
            Name = self.tofind["Name"],
            protocolname = self.tofind["protocolname"],
            led = self.tofind["led"],
            celltype = self.tofind["celltype"])

        self.tree.plot(node, canvas)




