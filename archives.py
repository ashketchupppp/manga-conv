class CBZArchive:
    def __init__(self, path: str):
        self.path = path
        self.clean = True

    def extract(self, extractPath: str):
        pass

    def append(self, other):
        pass

    def insert(self, other, pos):
        pass

class Volume:
    def __init__(self):
        self.archives = []

    def append(self, archive: CBZArchive):
        self.archives.append(archive)
    
    def insert(self, archive: CBZArchive, pos: int):
        self.archives.insert(pos, archive)

    def collate(self):
        '''
            Unzips each archive and puts them into a single CBZArchive
        '''
        pass