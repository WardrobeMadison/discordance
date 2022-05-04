from pathlib import Path

import dissonance
from dissonance import analysis, io, viewer

logger = dissonance.init_log()

# PATH TO MAPPED DATA DIRECTORY - GENOTYPES TO ANALYZE
root_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/MappedData")
folders = ["DR", "WT"]

# SET UNCHECKED PATH - CONTAINS STARTDATES TO EXCLUDE
#uncheckedpath = Path("DemoForJenna.txt")
#unchecked = io.read_unchecked_file(uncheckedpath)
unchecked = None
uncheckedpath = None

# GET LIST OF ALL FILES TO ANALYZE
paths = []
for fldr in folders:
    paths.extend([
        file
        for ii, file in enumerate((root_dir/fldr).glob("*.h5"))])

# READER FOR MAPPED H5 FILES
dr = io.DissonanceReader(paths)

# ANALYSIS OBJECT
lsa = analysis.BrowsingAnalysis()
paramnames = [*lsa.labels, "startdate"]

# CREATE DATATABLE WITH PARAMETERS FOR EACH EPOCH - CORRESPONDS TO DATA WE WILL SPLIT ON
params = dr.to_params(paramnames)

# CREATE INPUT/OUTPUT OBJECT FOR QUERYING H5 FILES
epochio = io.EpochIO(params, paths)

# RUN GUI
viewer.run(epochio, lsa, unchecked, uncheckedpath)