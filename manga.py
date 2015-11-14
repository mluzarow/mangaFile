#region Dependencies
import argparse
from bs4 import BeautifulSoup
import logging
import os
import zipfile
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
    #info = readXML (dir)
    info = readZIP (fileName)
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

def readZIP (filename):
    zf = zipfile.ZipFile ("Manga/" + filename + ".zip")

    for name in [filename + "/Info.xml"]:
        try:
            data = zf.read(name)

            zf.close()
        except KeyError:
            print "Info.xml could not be found"
        else:
            return (data)

def readXML (path):
    # Open XML file and read in all data
    with open (path, 'r') as f:
        data = f.read()
    f.closed

    return (data)

# Check that the directory in which manga exists, exists
def checkDir (name):
    # Check for the directory
    if not os.path.exists ("Manga"):
        # Directory is not there, so this is the first manga to be added; make the directory
        os.makedirs ("Manga")

#endregion Read XML

# Write the new XML file
def writeXML (data):
    with open ("Manga/Info.xml", 'w') as f:
        f.write (data)
    f.closed

# Add the XML file to a new zip file
def makeZIP (name, data):
    if not os.path.isfile ("Manga/" + name):
        zf = zipfile.ZipFile ("Manga/%s.zip" % name, 'w')

        writeXML (data)

        try:
            zf.write ("Manga/Info.xml", "%s/Info.xml" % name)
            zf.close()

            os.remove("Manga/Info.xml")
        except:
            print "Something bad happened :<"
    else:
        print "File already exists"

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
    checkDir (args.name)

    data = ""

    data += "<info>\n\t<top>\n\t\t<title>%s</title>\n" % args.name
    data += "\t\t<author>%s</author>\n" % raw_input ("Name of author: ")
    data += "\t\t<year>%s</year>\n" % raw_input ("Year of release: ")
    data += "\t\t<type>%s</type>\n" % raw_input ("Type: ")

    x = raw_input ("Indie? ")
    data += "\t\t<indie>%s</indie>\n\n" % x
    
    if (x == "N"):
        x = raw_input ("Number of original sources: ")
        data += "\t\t<originals>%s<\originals>\n" % x

        for num in range (1, int(x) + 1):
            data += "\t\t<original>\n\t\t\t<thisOriginal>%d</thisOriginal>\n\t\t\t<title>%s</title>" % (num, raw_input ("Title of source [%d]: " % num))
            data += "\n\t\t</original>\n"

    x = raw_input ("Number of scanlators: ")
    data += "\t\t<scanlators>%s</scanlators>" % x

    for num in range (1, int(x) + 1):
        data += "\n\t\t<scanlator>\n\t\t\t<thisScanlator>%d</thisScanlator>\n\t\t\t" % num
        data += "<title>%s</title>" % raw_input ("Title of scanlator [%d]: " % num)
        data += "\n\t\t\t<website>%s</website>" % raw_input ("Website of scanlator [%d]: " % num)
        data += "\n\t\t</scanlator>"

    data += "\n\t</top>\n\n\t<content>"
    data += "\n\t\t<finished>%s</finished>" % raw_input ("Finished? ")
    
    x = raw_input ("Total volumes: ")
    data += "\n\t\t<totalVol>%s</totalVol>" % x
    data += "\n\n"

    for num in range (1, int(x) + 1):
        data += "\t\t<volume>\n\t\t\t<thisVolume>%d</thisVolume>" % num
        data += "\n\t\t\t<volumeName>%s</volumeName>" % raw_input ("Volume Name: ")
        data += "\n\t\t\t<title>%s</title>" % raw_input ("Volume Title: ")
        data += "\n\t\t\t<subtitle>%s<subtitle>" % raw_input ("Volume Subtitle: ")

        y = raw_input ("Chapters in this volume: ")

        data += "\n\t\t\t<volumeChapters>%s</volumeChapters>" % y
        data += "\n\n"

        for num2 in range (1, int(y) + 1):
            data += "\t\t\t<chapter>\n\t\t\t\t<thisChapter>%d</thisChapter>" % num2
            data += "\n\t\t\t\t<chapterName>%s</chapterName>" % raw_input ("Name of chapter [%d] Vol [%d]: " % (num2, num))
            data += "\n\t\t\t\t<pageCount>%s</pageCount>" % raw_input ("Page Count of chapter [%d] Vol [%d]: " % (num2, num))
            data += "\n\t\t\t\t<title>%s</title>" % raw_input ("Title of chapter [%d] Vol [%d]: " % (num2, num))
            data += "\n\t\t\t\t<subtitle>%s</subtitle>" % raw_input ("Subtitle of chapter [%d] Vol [%d]: " % (num2, num))
            
            z = raw_input ("Using original? ")
            data += "\n\t\t\t\t<usingOriginal>%s</usingOriginal>" % z
            data += "\n\n"

            if x == "Y":
                data += "\t\t\t\t<original>\n\t\t\t\t\t<n>%s</n>" % raw_input ("Source index: ")
                data += "\n\t\t\t\t\t<originalVolume>%s</originalVolume>" % raw_input ("Original Volume: ")
                data += "\n\t\t\t\t\t<day>%s</day>" % raw_input ("Original Day: ")
                data += "\n\t\t\t\t\t<month>%s</month>" % raw_input ("Original Month: ")
                data += "\n\t\t\t\t\t<year>%s</year>" % raw_input ("Original Year: ")
                data += "\n\t\t\t\t</original>\n\n"

            data += "\t\t\t\t<scanlator>\n\t\t\t\t\t<n>%s</n>" % raw_input ("Scanlator Index: ")
            data += "\n\t\t\t\t\t<day>%s</day>" % raw_input ("Scanned Day: ")
            data += "\n\t\t\t\t\t<month>%s</month>" % raw_input ("Scanned Month: ")
            data += "\n\t\t\t\t\t<year>%s</year>" % raw_input ("Scanned Year: ")
            data += "\n\t\t\t\t</scanlator>\n\t\t\t</chapter>"

            if not num2 == int(y):
                data += "\n\n"

        data += "\n\t\t</volume>"

        if not num == int(x):
            data += "\n\n"

    data += "\n\t</content>\n</info>"

    makeZIP (args.name, data)
    print readZIP ("Manga/%s" % args.name)

elif int(args.op) == 1:
    print "Opening \"%s.manga\"..." % args.name

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
        print "Chapters in this volume:\n"

        for chap in info.volumes[vol].chapters:
            print "Chapter [%s]:" % info.volumes[vol].chapters[chap].name
            print "   Title: %s" % info.volumes[vol].chapters[chap].title
            print "   Subtitle: %s" % info.volumes[vol].chapters[chap].subtitle
            print "   Page Count: %s" % info.volumes[vol].chapters[chap].pages

            if info.volumes[vol].chapters[chap].hasOriginal == "Y":
                print "   This chapter was featured originally in:"

                if info.volumes[vol].chapters[chap].originalDay == None:
                     print "      %s Vol. %s [%s %s]" % (info.volumes[vol].chapters[chap].originalN,
                                                 info.volumes[vol].chapters[chap].originalVolume,
                                                 info.volumes[vol].chapters[chap].originalMonth,
                                                 info.volumes[vol].chapters[chap].originalYear)
                else: 
                    print "      %s Vol. %s [%s %s %s]" % (info.volumes[vol].chapters[chap].originalN,
                                                 info.volumes[vol].chapters[chap].originalVolume,
                                                 info.volumes[vol].chapters[chap].originalDay,
                                                 info.volumes[vol].chapters[chap].originalMonth,
                                                 info.volumes[vol].chapters[chap].originalYear)
               

#endregion Main
