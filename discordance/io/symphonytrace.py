from dataclasses import dataclass
from h5py._hl.files import File

@dataclass
class SymphonyTrace:

	filepath: File
	tracepath: str
