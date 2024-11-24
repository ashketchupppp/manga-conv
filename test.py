import os
import pathlib as path
import archives

v = archives.Volume('Volume 1')
a = archives.CBZArchive(path.Path('C:/Users/compu/GitHub/manga-conv/testdata/Vol.02 Ch.0005 - Enfermería (es-la) [Kings Slayers Fansub].cbz'))
b = archives.CBZArchive(path.Path('C:/Users/compu/GitHub/manga-conv/testdata/Vol.02 Ch.0006 - Fiesta en el jardín -Parte 1 (es-la) [Kings Slayers Fansub].cbz'))

v.append(a)
v.append(b)

v.collate()