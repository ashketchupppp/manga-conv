import os
import pathlib as path
import zipfile
import xml.etree.ElementTree as ET
import shutil

class ExtractedCBZArchive:
    def __init__(self, directory: path.Path):
        self.directory = directory
        assert(self.directory.is_dir())
        # Parse ComicInfo.xml
        self.pages = []

        # Take stock of what pages there are

    def archive(self, archivePath: path.Path): # -> CBZArchive
        shutil.make_archive(archivePath, 'zip', self.directory)

    def _parseComicInfo(self):
        comicInfoPath = self.directory.joinpath('ComicInfo.xml')
        assert(comicInfoPath.is_file())
        tree = ET.parse(comicInfoPath)
        root = tree.getroot()
        pageCount = int(root[2].text)


class CBZArchive:
    def __init__(self, archivePath: path.Path):
        self.archivePath = archivePath
        assert(self.archivePath.is_file())

    def extract(self, extractPath = None) -> ExtractedCBZArchive:
        if extractPath == None:
            extractPath = self.archivePath.parent.joinpath(self.archivePath.stem)

        with zipfile.ZipFile(self.archivePath, 'r') as _zip:
            _zip.extractall(extractPath)
        return ExtractedCBZArchive(extractPath)

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