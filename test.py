from dissonance import io
from multiprocessing import Pool

from dissonance.io import add_genotype

info = [
("2021-10-21A",	"GG2 KO"),
("g2021-07-12A2",	"DR"),
("pdr2021-07-12A",	"DR"),
("pdr2021-08-25A2","DR"),
("2021-10-05A",	"WT"),
("2021-09-23A",	"WT"),
]

def read(filename):
	print(f"Start. {filename}")
	fin = f"tests/data/{filename}.h5"
	fout = f"tests/output/{filename}.h5"

	sr = io.SymphonyReader(fin)
	sr.to_h5(fout)
	print(f"Done. {filename}")	

def threadread():
	filenames = [x[0] for x in info]

	with Pool(5) as p:
		for x in p.imap(read, filenames):
			print(f"Read {info}")

def add_genotypes():
	for key, val in info:
		filepath = f"tests/output/{key}.h5"
		print(filepath)
		add_genotype(filepath, val)
