import os
import re
import pathlib
import zipfile
import shutil
import xml.etree.ElementTree as ET

def buildComicInfo (volumeTitle, seriesTitle, pagecount):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Title>{volumeTitle}</Title>
    <Series>{seriesTitle}</Series>
    <PageCount>{pagecount}</PageCount>
</ComicInfo>
"""

chapterRegex = r"Vol\.\d\d Ch\.(\d\d\d\d).*"
chapterNumCaptureGroup = 1

mangaDir = "C:\\Users\\compu\\Documents\\Mangas\\Otoyomegatari"
seriesTitle = "Otoyomegatari"
volumePrefix = "Volume"
chapterExtension = ".cbz"
chapterNums = [
    # add 1 because list is not inclusive on the stop number
    list(range(1, 68 + 1))
]

def unzippedPath(p: str):
    return '.'.join(p.split('.')[0:-1])

def chapFName(chapNum, unzipped = False, fullPath = False):
    chapPath = ''
    filesDirs = os.listdir(mangaDir)
    chapterMatched = False
    for fileDir in filesDirs:
        path = pathlib.Path(os.path.join(mangaDir, fileDir))
        if not path.is_file():
            continue

        m = re.match(chapterRegex, fileDir)
        if m == None:
            continue

        if int(m.groups()[0]) == chapNum:
            chapterMatched = True
            chapPath = fileDir
            break
    
    if not chapterMatched:
        print(f"Unable to find a match for chapter {chapNum}")
        raise FileNotFoundError(f'Chapter {chapNum}')
    
    if unzipped:
        chapPath = unzippedPath(chapPath)

    if fullPath:
        chapPath = os.path.join(mangaDir, chapPath)

    return chapPath

# unzip all chapters
volumePaths = []
volNum = 1
for volume in chapterNums:
    print(f'Reading {volumePrefix} {volNum}')

    # extract each chapter into it's own directory
    for chapNum in volume:
        # Try to find the file name for the current chapter
        chapNameZipped = chapFName(chapNum)
        chapNameUnzipped = unzippedPath(chapNameZipped)
        chapPathZipped = os.path.join(mangaDir, chapNameZipped)
        chapPathUnzipped = os.path.join(mangaDir, chapNameUnzipped)
        print(f'Unzipping {chapNameZipped} {chapNum}{chapterExtension} to {chapNameUnzipped} {chapNum}')
        with zipfile.ZipFile(chapPathZipped, 'r') as _zip:
            _zip.extractall(chapPathUnzipped)

    # each chapter has image files (pages) numbered 1 to X (X = number of pages in the chapter)
    # e.g we need to copy from page 1 chapter 2 to page X + 1 volume 1
    volumeName = f"{seriesTitle} - {volumePrefix} {volNum}"
    volumePath = os.path.join(mangaDir, volumeName)
    try:
        os.makedirs(volumePath)
    except FileExistsError:
        print("WARN: Volume Path already exists")

    volPageTotal = 1
    for chapNum in volume:
        chapPath = chapFName(chapNum, unzipped=True, fullPath=True)
        tree = ET.parse(os.path.join(chapPath, 'ComicInfo.xml'))
        root = tree.getroot()
        pageCount = int(root[2].text)
        volPageTotal += pageCount
    
    pageSubtotal = 1
    pageFileZeroPadding = len(str(volPageTotal))
    for chapNum in volume:
        chapPath = chapFName(chapNum, unzipped=True, fullPath=True)
    
        # parse comicinfo to find out how many pages we have
        tree = ET.parse(os.path.join(chapPath, 'ComicInfo.xml'))
        root = tree.getroot()
        pageCount = int(root[2].text)
        print(f"Found {pageCount} pages in Chapter {chapNum}")

        # copy pages from chapters to volumes, updating the page number
        pages = os.listdir(chapPath)
        for page in pages:
            pageExt = page.split('.')[1]
            if page != "ComicInfo.xml":
                pageStr = ( '%0'+str(pageFileZeroPadding)+'d' ) % pageSubtotal
                print(f"Page: {page} -> {pageStr}.{pageExt}")
                shutil.copy(os.path.join(chapPath, page), os.path.join(volumePath, f"{pageStr}.{pageExt}"))
                pageSubtotal += 1
        
        # cleanup the individual chapter files
        shutil.rmtree(chapPath)

    # remove that final addition to pageSubtotal so we have an accurate number
    pageSubtotal -= 1

    # create ComicInfo.xml
    comicInfo = buildComicInfo(
        f"{seriesTitle}: {volumePrefix} {volNum}",
        seriesTitle,
        pageSubtotal
    )
    with open(os.path.join(volumePath, 'ComicInfo.xml'), 'w') as fh:
        fh.write(comicInfo)

    # zip it all up
    print(f"Zipping up {volumePath}...")
    shutil.make_archive(volumePath, 'zip', volumePath)
    print("Zip complete.")

    # rename file as .cbz
    shutil.move(volumePath + '.zip', volumePath + '.cbz')

    # cleanup intermediate volume directory
    shutil.rmtree(volumePath)

    volNum += 1
