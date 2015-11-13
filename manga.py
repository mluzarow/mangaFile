#region Dependencies
import argparse
from bs4 import BeautifulSoup
import logging
import os
#endregion Dependencies

################################################################################
## manga.py
##
## Reads manga details :>
################################################################################

#region Classes
# Stores the meat of the anime
class Manga(object):
    def __init__ (self, title=None, author=None, year=None, isIndepent=None, numOriginals=None,
                  originals=None, numScanlators=None, scanlators=None, isFinished=None, numVolumes=None,
                  volumes=None):
        self.title = title
        self.author = author
        self.year = year
        self.isIndependent = isIndepent
        self.numOriginals = numOriginals
        self.originals = originals
        self.numScanlators = numScanlators
        self.scanlators = scanlators
        self.isFinished = isFinished
        self.numVolumes = numVolumes
        self.volumes = volumes

class Original(object):
    def __init__ (self, n=None, title=None):
        self.n = n
        self.title = title

class Scanlator(object):
    def __init__ (self, n=None, title=None, website=None):
        self.n = n
        self.title = title
        self.website = website

class Volume(object):
    def __init__ (self, n=None, name=None, title=None, subtitle=None, chapters=None):
        self.n = n
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.chapters = chapters

class Chapter(object):
    def __init__ (self, n=None, name=None, pages=None, title=None, subtitle=None, hasOriginal=None, 
                  originalN=None, originalVolume=None, originalDay=None, originalMonth=None, 
                  originalYear=None, scanN=None, scanDay=None, scanMonth=None, scanYear=None):
        self.n = n
        self.name = name
        self.pages = pages
        self.title = title
        self.subtitle = subtitle
        self.hasOriginal = hasOriginal
        self.originalN = originalN
        self.originalVolume = originalVolume
        self.originalDay = originalDay
        self.originalMonth = originalMonth
        self.originalYear = originalYear
        self.scanN = scanN
        self.scanDay = scanDay
        self.scanMonth = scanMonth
        self.scanYear = scanYear
#endregion Classes

#region Read XML
# Returns the Manga object 
def getInfo(fileName):
    dir = "Manga/" + fileName + "/Info.xml"

    # Set up manga object
    mangaInfo = Manga()

    # Reads file into memory
    info = readXML (dir)
    # Spruce up the soup
    parsedInfo = BeautifulSoup(info, "lxml")

    # Process <top>
    pi = parsedInfo.find("top")

    # Add variables to Manga
    mangaInfo.title = pi.title.string
    mangaInfo.author = pi.author.string
    mangaInfo.year = pi.year.string
    mangaInfo.isIndependent = pi.indie.string
    if (mangaInfo.isIndependent == "N"):
        mangaInfo.isIndependent = False
    elif (mangaInfo.isIndependent == "Y"):
        mangaInfo.isIndependent = True

    # Find number or original sources in which this manga was printed
    mangaInfo.numOriginals = int(pi.originals.string)
    # Set up original sources dict
    mangaInfo.originals = dict()

    # Find all original sources under <original> tags
    origs = pi.findAll ("original")

    # Add each original source's data to Originals object and add that object to originals dict
    for orig in origs:
        mangaInfo.originals[int(orig.thisoriginal.string)] = Original (int(orig.thisoriginal.string), 
                                                                        orig.title.string)

    # Find number of scanlators that worked on this project
    mangaInfo.numScanlators = int(pi.scanlators.string)
    # Set up scanlators dict
    mangaInfo.scanlators = dict()

    # Find all scanlators that worked on this project under <scanlator> tags
    scans = pi.findAll("scanlator")

    # Add each scanlator's data to Scanlator object and add that object to scanlators dict
    for scan in scans:
        mangaInfo.scanlators[int(scan.thisscanlator.string)] = Scanlator(int(scan.thisscanlator.string), 
                                                                            scan.title.string, 
                                                                            scan.website.string)

    # Process <content>
    pi = parsedInfo.find ("content")

    # Add variables to Manga
    mangaInfo.isFinished = pi.finished.string
    if (mangaInfo.isFinished == "N"):
        mangaInfo.isFinished = False
    elif (mangaInfo.isFinished == "Y"):
        mangaInfo.isFinished = True
    mangaInfo.numVolumes = int(pi.totalvol.string)

    # Set up volumes dict
    mangaInfo.volumes = dict()
             
    # Find all volumes under <volume> tags
    vols = pi.findAll("volume")

    # Iterate through all <volume> tags
    for vol in vols:
        # Find the current volume number
        currentVolume = int(vol.thisvolume.string)

        # Enter current volume into volumes dict
        # chapters dict in None and will be added after this
        mangaInfo.volumes[currentVolume] = Volume(currentVolume, 
                                                    vol.volumename.string, 
                                                    vol.title.string, 
                                                    vol.subtitle.string, 
                                                    None)
        # Find all <chapter> tags
        chaps = vol.findAll ("chapter")
        # Set up chapters dict
        chapDict = dict()

        # Iterate through all <chapter> tags
        for chap in chaps:
            # Find the current chapter number
            currentChapter = int(chap.thischapter.string)

            # If chapter is using an original source, add it
            if chap.usingoriginal.string == "Y":
                chapDict[currentChapter] = Chapter(currentChapter, 
                                                chap.chaptername.string, 
                                                int(chap.pagecount.string), 
                                                chap.title.string,
                                                chap.subtitle.string,
                                                chap.usingoriginal.string,
                                                mangaInfo.originals[int(chap.original.n.string)].title,
                                                chap.original.originalvolume.string,
                                                chap.original.day.string,
                                                chap.original.month.string,
                                                chap.original.year.string,
                                                mangaInfo.scanlators[int(chap.scanlator.n.string)].title,
                                                chap.scanlator.day.string,
                                                chap.scanlator.month.string,
                                                chap.scanlator.year.string)
            # If chapter is NOT using an original source, do not look for it
            elif chap.usingoriginal.string == "N":
                chapDict[currentChapter] = Chapter(currentChapter, 
                                                    chap.chaptername.string, 
                                                    int(chap.pagecount.string), 
                                                    chap.title.string,
                                                    chap.subtitle.string,
                                                    chap.usingoriginal.string,
                                                    None,
                                                    None,
                                                    None,
                                                    None,
                                                    None,
                                                    mangaInfo.scanlators[int(chap.scanlator.n.string)].title,
                                                    chap.scanlator.day.string,
                                                    chap.scanlator.month.string,
                                                    chap.scanlator.year.string)

        mangaInfo.volumes[currentVolume].chapters = chapDict

    return mangaInfo

def readXML (path):
    # Open XML file and read in all data
    with open (path, 'r') as f:
        data = f.read()
    f.closed

    return (data)
#endregion Read XML

############################ MAIN IS RIGHT HERE ################################
#region Main

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--fn', dest = "name", required = True, help = "File name of Manga in Manga folder")
parser.add_argument("--op", dest = "op", required = True, help = "Operation")

args = parser.parse_args(['--fn', 'Two and Two','--op', '1'])

# Check operation type
# 0: Write new XML file using name as title
# 1: Read an existing XML sheet titled name
if int(args.op) == 0:
    print "Writing new XML file for: %s" % args.name
    # createDir(args.name)
elif int(args.op) == 1:
    print "Getting sheet for:  %s" % args.name

    # Read XML and throw info into class
    info = getInfo(args.name)
     
    # Print the info
    print "\n==================== General Information ===================="
    print "Manga title: %s" % info.title
    print "Manga author: %s" % info.author  
    print "Year of initial release: %s" % info.year
    print "Manga is independent: %s" % info.isIndependent
    print "\nOriginal Sources: %d" % info.numOriginals
    for orig in info.originals:
        print "Source [%d]: %s" % (orig, info.originals[orig].title)
    
    print "\nScanlators: %d" % info.numScanlators
    for key in info.scanlators:
        print "Group [%d]: %s" % (key, info.scanlators[key].title)
        print "Website: %s" % info.scanlators[key].website

    print "\n======================= Manga Content ======================="
    print "Total Volumes: %s\n" % info.numVolumes

    for vol in info.volumes:
        print "Volume [%s]:" % info.volumes[vol].name
        print "   Title:    %s" % info.volumes[vol].title
        print "   Subtitle: %s" % info.volumes[vol].subtitle
        print "Chapters in this volume:"

        for chap in info.volumes[vol].chapters:
            print "Chapter [%s]:" % info.volumes[vol].chapters[chap].name
            print "   Title: %s" % info.volumes[vol].chapters[chap].title
            print "   Subtitle: %s" % info.volumes[vol].chapters[chap].subtitle

#endregion Main
