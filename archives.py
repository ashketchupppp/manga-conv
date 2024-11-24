import os
import pathlib as path
import zipfile
import xml.etree.ElementTree as ET
import shutil
from typing import List

class ComicInfo:
    def __init__(self, path: path.Path):
        self.path = path
        self.title = 'Unknown'
        self.series = 'Unknown'
        self.pageCount = 0

    def read(self):
        root = ET.parse(self.path).getroot()
        self.title = root.find('Title').text
        self.series = root.find('Series').text
        self.pageCount = int(root.find('PageCount').text)

    def write(self):
        # This is lazy but I don't care, it works
        return f"""
        <?xml version="1.0" encoding="utf-8"?>
        <ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <Title>{self.title}</Title>
            <Series>{self.series}</Series>
            <PageCount>{self.pageCount}</PageCount>
        </ComicInfo>
        """

class ExtractedCBZArchive:
    def __init__(self, directory: path.Path):
        self.directory = directory
        assert(self.directory.is_dir())

        # Read ComicInfo.xml or create it
        comicInfoPath = self.directory.joinpath('ComicInfo.xml')
        if not os.path.exists(comicInfoPath):
            self.comicInfo = ComicInfo(comicInfoPath)
        else:
            self.comicInfo = ComicInfo(self.directory.joinpath('ComicInfo.xml'))
            self.comicInfo.read()

    def __iter__(self):
        pages = os.listdir(self.directory)
        pages.remove('ComicInfo.xml')

        for i in os.listdir(self.directory):
            if i != 'ComicInfo.xml':
                yield self.directory.joinpath(i)

    def append(self, other):
        # Figure out how much zero padding we need to add to the pages
        newPageTotal = self.pageCount() + other.pageCount()
        pageNamePadding = len(str(newPageTotal))

        # Move the pages across
        subtotal = self.pageCount() + 1
        for pagePath in other:
            pageFileExtension = pagePath.suffix
            newPageName = ( '%0'+str(pageNamePadding)+'d' ) % subtotal
            newPagePath = self.directory.joinpath(newPageName + pageFileExtension)
            shutil.move(pagePath, newPagePath)
            subtotal += 1

    def pageCount(self):
        return self.comicInfo.pageCount

    def archive(self, archivePath: path.Path): # -> CBZArchive
        shutil.make_archive(archivePath, 'zip', self.directory)


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
    def __init__(self, name: str):
        self.archives: List[ExtractedCBZArchive | CBZArchive] = []
        self.name: str = name

    def append(self, archive: CBZArchive | ExtractedCBZArchive):
        self.archives.append(archive)

    def insert(self, archive: CBZArchive | ExtractedCBZArchive, pos: int):
        self.archives.insert(pos, archive)

    def collate(self):
        '''
            Unzips each archive and puts them into a single CBZArchive
        '''
        volPath = path.Path('./').joinpath(self.name)
        if not os.path.exists(volPath):
            os.mkdir(volPath)
        volume = ExtractedCBZArchive(volPath)

        # Unzip all of the archives
        for archive in self.archives:
            if type(archive) == CBZArchive:
                archive = archive.extract()
        
        volume.append(archive)
            
