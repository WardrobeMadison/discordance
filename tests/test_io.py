from multiprocessing import Pool
from pathlib import Path
from dissonance import viewer, io, epochtypes
from functools import partial


def test_to_json():
    path = "tests/data/2020-07-21A.h5"
    outpath = "tests/output/2020-07-21A.json"

    filemap = io.FileMap(path, outpath)

    sr = io.SymphonyReader(filemap.symphonyfilepath)
    sr.to_json(filemap.dissonancefilepath)


def test_to_h5():
    exclude = []
    #folders = ["GA1 KO", "GG2 control", "GG2 KO"]
    folders = ["GG2 KO", "GG2 control"]

    root_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
    out_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
    for folder in folders:
        wdir = root_dir / folder

        wodir = (out_dir / folder)
        wodir.mkdir(parents=True, exist_ok=True)

        files = [file for file in wdir.glob("*.h5") if file.name not in exclude]
        func = partial(write_file, wodir = wodir)

        with Pool(4) as p:
            for x in p.imap(func, files):
                print(x)


def write_file(file, wodir):
    try:
        print(file)
        sr = io.SymphonyReader(file)
        sr.to_h5(wodir / file.name)
    except Exception as e:
        print(f"FAILED {file}")
        raise e

    return f"Done reading {file}"


def test_reader():
    path = Path(r"tests/output/2020-07-21A.h5")
    dr = io.DissonanceReader([path])
    epochs = dr.to_epochs()

    print(epochs)

    assert True
