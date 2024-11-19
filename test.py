import pathlib as path
import archives

a = archives.CBZArchive(path.Path('C:\\Users\\compu\\git\\manga-conv\\testdata\\Episode 1.cbz'))
a.extract()