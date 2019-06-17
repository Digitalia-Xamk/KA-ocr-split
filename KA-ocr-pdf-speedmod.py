#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 11:44:09 2017

@author: digitalia-aj
"""
import multiprocessing
from multiprocessing import Pool
from PIL import Image
import sys
import os
import time
import subprocess
import atexit
import csv
#import uuid
import re
from PyPDF2 import PdfFileReader, PdfFileWriter

"""
*************************************************************
Select variables according to environment
*************************************************************
"""
#BOOLEANS
deltempfiles = True #All runtime files will be deleted, switch to false for testing
convertToGrey = False #Just test to get better ocr quality, looses all color information
producePDFA = False #If true the final file will be prepress quality PDF/A-3b file otherwise ebook quality PDF file
composeSingleFile = True #Combines all files in one direrctory into one final ocr file
deleteNonTextPages = True #If True deletes all pages without text/ocr info


#firstEncounter = True #This is used to get the path of the manipulated file during the first run

#OTHERS
#Used to count pages and ocred amount
ocrFilesCount = 0
ocrPagesCount = 0
allPagesCount = 0


ocrTimesTable = []
useLangs = 'fin' #'eng+fin+swe+deu'

#DIRS
#tessdatadir = '/usr/local/share/tessdata'
gspath = '/home/user/ghostscript/gs-926'
#gspath = '/home/user/ghostscript/gs-922' #923 seems to have a bug when combining lots of pdf files (memory thingie)

def setOcrFilesCount(x):
    global ocrFilesCount
    ocrFilesCount+=x    
    return

def setOcrPagesCount(x):
    global ocrPagesCount
    ocrPagesCount+=x    
    return

def setAllPagesCount(x):
    global allPagesCount
    allPagesCount+=x
    return


def renameFile(origfile, renamedFile):
    #printmessage("Renaming:"+str(origfile)+" into "+str(renamedFile))
    os.replace(origfile, renamedFile)
    if os.path.isfile(renamedFile):
        return
   

def writecsv(message):
    global csvwriter
    try:
        #message = time.strftime("%H:%M:%S", time.localtime())+">"+str(message)
        #print(message+ "CSV")
        #csvwriter.write("möö")
        csvwriter.write(message+"\n")
    except OSError:
        pass
    return

def printmessage(message):
    #printmessage(time.strftime("%H:%M:%S", time.localtime()))    
    try:
        message = time.strftime("%H:%M:%S", time.localtime())+">"+str(message)
        print(message)
        logfile.write(message+"\n")
    except OSError:
        pass
    return

def docmd(cmd):   
    returnValue = False #This is only used on tesseract error case
    #printmessage("manipulating "+str(cmd))
    cmdProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #convertprocess = subprocess.getoutput(cmd)
    cmdResults, cmdError = cmdProcess.communicate() 
    #printmessage("RESULT:{}".format(cmdResults))
    #printmessage("ERROR:{}".format(cmdError))
    
    if len(cmdError)>0: #ONly process the error message if it's longer than 0
        if deleteNonTextPages: #If set to true, drop pages without text
            cmdError = str(cmdError).lower()
            if "skipping" in cmdError or "empty" in cmdError: #Tesseract returns these if no text in page
                returnValue = True
                #printmessage("Lenght {} and content {}".format(len(cmdError), cmdError))        
       
    return returnValue

def multiPDFtoPNG(cmd):
    print("Multi call with {}".format(cmd))
    docmd(cmd)
    return


"""Called if the deltempfiles flag is set to True
Removes given file inside a directory
"""
def removeFile(file): #actual method that removes the folder
    try:
        #delfile = os.path.join(root, filename)
        #printmessage ("Trying to delete file -->%s "%file)
        os.remove(file)

    except OSError:
        pass
    return

def ocrmyfile(item):    
    #printmessage(item)
    begin, ending = os.path.splitext(item)    
    PNGfile = begin+".png"    
    i = 0    
    PNGfile_ = begin+"-"+str(i)+".png"
    if deltempfiles:
        dellist = [] #list containing all temp files to be deleted
        
    if str(item).endswith('pdf'): #Creates X amount of pdf files and lists those        
        cpus = multiprocessing.cpu_count()
        pdfPool = Pool(cpus)
        
        #Tries to split multipage pdf into separate pages with pyPDF2
        inputpdf = PdfFileReader(open(item, "rb"))
        pdfPagesList = []
        if inputpdf.numPages > 1:
            for z in range(inputpdf.numPages):
                #printmessage(i)
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(z))
                outputFile = begin+"_"+str(z)+".pdf"
                tempPNG = begin+"_"+str(z)+".png" #png file is used in convert phase below
                outputstream = open(outputFile, "wb")
                output.write(outputstream)
                outputstream.close()
                if os.path.isfile(outputFile):
                    tempDict = []
                    tempDict.append(outputFile)
                    tempDict.append(tempPNG)
                    pdfPagesList.append(tempDict)
                    
        else:
            tempDict = []
            tempDict.append(item)
            tempDict.append(PNGfile)
            pdfPagesList.append(tempDict)
        
        #printmessage(pdfPagesList)
        #printmessage(len(pdfPagesList))
        topngStartTime = time.time()
        for x in pdfPagesList:
            #printmessage(x)                        
            #printmessage("Muuhkis")           
            #printmessage(pdfPagesList[x][0])
            topngcmd = ['convert', '-flatten', '-density', '288', '-quality', '100', '-deskew', '40%', '-enhance', '-enhance',
                        '-resize', '50%', '-unsharp', '2', x[0], x[1]]
            #printmessage(topngcmd)
            pdfPool.apply_async(multiPDFtoPNG, args=(topngcmd,))    
        pdfPool.close()
        pdfPool.join()
            #docmd(topngcmd)
            #x+=1        
        ocrPool = Pool(cpus)
        for x in pdfPagesList:
            pngFile = x[1]
            #printmessage("Test again")                        
            ocrPool.apply_async(ocrmyfile, args=(pngFile,), callback=getocrResult) #this should lead eventually to below section
        ocrPool.close()
        ocrPool.join()
        
        
    else: #This happens if item is not pdf file but an image     
        img = Image.open(item)
        croppedimg = begin+'_cropped'+ending
        #printmessage("Cropped image = {}".format(croppedimg))
        if convertToGrey: #Loses all other information than text
            #printmessage("Converting to grey scale")            
            gray = img.convert('L') #L = rgb mode
            bw = gray.point(lambda x: 0 if x<165 else 250, '1')            
            bw.save(croppedimg)                                    
            img = Image.open(PNGfile)
            item = PNGfile
        
        cropcmd =  ['convert', '-density', '144', '-fuzz', '25%', '-trim', item, croppedimg] #removes border color to make the picture a bit smaller
        docmd(cropcmd)
        
        if os.path.isfile(croppedimg): #If cropping done, use the gropped file to create png
            item = croppedimg        
        
        if deltempfiles:
            dellist.append(croppedimg)
        
        img_width, img_height = img.size
        mega_pixels = (img_width * img_height)/1000000
        #printmessage(item)
        
        if mega_pixels<0.5:
            scale = 400  
        elif mega_pixels<1:
            scale=300
        elif mega_pixels<2:                
            scale=200   
        else:
            scale=100
            #change=False
        """     
        if img_height>1080 or img_width>1500 and change==True:
            #printmessage("luuruu"+str(scale))    
            scale = scale*0.75
        """ 
        #printmessage(item+" "+str(img.size)+" total pixels = %s"%mega_pixels)
        #printmessage(scale)
        scale = str(int(scale))+"%"
        topngcmd = ['convert', '-quality', '100', '-deskew', '50%', '-enhance', '-enhance', '-unsharp', '2', item, '-resize', scale, PNGfile_]     
    
        #pool.apply_async(docmd, args=(topngcmd, item))
        topngStartTime = time.time()    
        #pool.apply_async(docmd, args=(topngcmd,))     
        docmd(topngcmd)         
    #pdf to png conversion does different filenames depending on amounf of pages. just one page is a problem --> fix here. No more PNGfile
    if os.path.isfile(PNGfile):        
        #printmessage("MÖÖ")
        #renameFile(os.path.join(os.path.dirname(PNGfile), PNGfile), os.path.join(os.path.dirname(PNGfile_), PNGfile_))
        renameFile(PNGfile, PNGfile_)
        
    topngEndTime = time.time()
    topngRunTime = topngEndTime - topngStartTime
    
    if deltempfiles:
        dellist.append(PNGfile_)
   
    #At this point the conversion should be ended and we can start the OCR part
    #names will be begin-0.png - begin-12345.png
   
    #printmessage("möö"+str(PNGfile))
    #printmessage(os.path.isfile(PNGfile))
    if os.path.isfile(PNGfile_):       
        ocroutputfile = begin+"-"+str(i)
                
        finalorcfile = "-o"+str(begin)+"-gs_shrink.pdf"
        #screen 72dpi, ebook 150dpi, printer 300dpi, prepress 300dpi+

        if producePDFA: #Boolean value at the beginning
            gscmd =[gspath, '-dPDFA=3',
            '-dBATCH', '-dNOPAUSE', '-dNOOUTERSAVE', '-dNOSAFER', '-dPDFSETTINGS=/printer',
            '-dPDFACompatibilityPolicy=1', '-dAutoFilterColorImages=false', '-dColorImageFilter=/FlateEncode',
            '-dAutoFilterGrayImages=false', '-dGrayImageFilter=/FlateEncode', '-dMonoImageFilter=/FlateEncode',
            '-dEmbedAllFonts=true', '-dCompressFonts=true', '-sPAPERSIZE=a4', '-dDetectDuplicateImages', '-dPDFFitPage', 
            '-dNOTRANSPARENCY', '-sDEVICE=pdfwrite', finalorcfile]           
        else:       
             gscmd =[gspath, '-dBATCH', '-dNOPAUSE', '-dNOOUTERSAVE', '-dNOSAFER', '-dPDFSETTINGS=/ebook',
             '-dCompatibilityLevel=1.4','-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dDetectDuplicateImages', '-dPDFFitPage', finalorcfile]
        
        droppedFilesList = []
        ocrStartTime = time.time()        
        while os.path.isfile(PNGfile_):                       
            ocroutputfile = begin+"-"+str(i)
            #tesseract testi-0.png -l fin 1944-poytakirja-s1 pdf
            #--psm 6 --oem 2 DLM-0.png text
            #print("Tesseract output file = {}".format(ocroutputfile))
            #tesseract 0088.jpg output.pdf -l fin --psm 12 
            ocrcmd = ['tesseract', PNGfile_, ocroutputfile, '-l', useLangs, 'pdf']
            #ocrcmd = ['tesseract', '--psm', '12', PNGfile_, '--tessdata-dir', tessdatadir, '-l', useLangs, ocroutputfile, 'pdf']
            dropValue = docmd(ocrcmd) #return True if file should be dropped due to being empty         
                
            i+=1
            PNGfile_ = begin+"-"+str(i)+".png"
            setAllPagesCount(1)
            #printmessage(dropValue)
            if dropValue == False: #If dropvalue is True, no need to process it
                #printmessage("muuhkista")
                gscmd.append(ocroutputfile+".pdf")
            else: #Add the dropped file to a list
                droppedFilesList.append(PNGfile_)
        #print("test")                                  
        ocrRunTime = time.time() - ocrStartTime
        print("OCR took:"+str(round(ocrRunTime, 4))+" vs. png conversion:"+str(round(topngRunTime, 4)))
        
        ocrTimesTable.append(ocrRunTime)            
        
        if deltempfiles:
            dellist.append(PNGfile_)
            dellist.append(ocroutputfile+".pdf")
       
        setAllPagesCount(1)
       
           
    
        gsStartTime = time.time() 
        if dropValue == False:
            docmd(gscmd)
        gsEndTime = time.time()
        gsRunTime = gsEndTime - gsStartTime    
        #ocrTimesTable.append(gsRunTime)
        #writecsv("GS:"+str(round(gsRunTime,4))+", OCR:"+str(round(ocrRunTime, 4))+", PNG:"+str(round(topngRunTime, 4)))
        if deltempfiles:
           for x in range(len(dellist)):
               removeFile(dellist[x])
        print(finalorcfile)
        finalSingleFile = finalorcfile.lstrip('-o')
        #returnstr = "tempreturn"
        returnList=[]
        if dropValue == False:
            returnstr = "GS:"+str(round(gsRunTime,4))+", OCR:"+str(round(ocrRunTime, 4))+", PNG:"+str(round(topngRunTime, 4)) 
            returnList = [returnstr]        
            returnList.append(finalSingleFile)
            printmessage (returnList)
        else:
            printmessage ("The following files were dropped thus not text found inside {}".format(droppedFilesList))
        return returnList      

def getocrResult(results):
    #global finalFiles
    setAllPagesCount(1)
    #setOcrFilesCount(1)
    #printmessage("getOCR-Results XXX")
    #printmessage("results : {}".format(results))
    if len(results)>0: #0 lenght is returned if a file is dropped do to being empty
        setOcrPagesCount(1)       
    return

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

#Related to below method display_time
intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )
def display_time(seconds, granularity=2): #Converts seconds to weeks, days, hours, minutes
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def endofscript():
    global csvwriter
    global pool
    global starttime
    global allPagesCount, ocrFilesCount, ocrPagesCount
    #global convertedFilesCount
    pool.close()
    pool.join()
    
    endtime = time.time()
    runtime = int(round(endtime-starttime,0))
    runtimeText = display_time(runtime, 3)
        
    
    printmessage("Checked {} files, ocred {} pages from which {} contained text in {}".format(allPagesCount, ocrFilesCount, ocrPagesCount, runtimeText))
    #printmessage("OCRed {} pages in {} seconds".format(pagecount, round(runtime, 3)))
    printmessage(str(ocrTimesTable))
    logfile.close
    csvwriter.close    
    return


"""THIS IS THE MAIN APP"""
starttime = time.time() 

logfile = open('fileconversion.log', 'w')
csvwriter = open('runtimes.csv', 'w')
cpucount = multiprocessing.cpu_count()

printmessage ("CPUs: "+str(cpucount))
printmessage ("PYTHON VERSION: "+str(sys.version_info))
printmessage ("Script is run in dir: "+str(os.path.dirname(os.path.abspath(__file__))))
#original_walk_dir = os.path.dirname(os.path.abspath(__file__))
walk_dir = os.getcwd()



"""
Appends supported fileformats to list
"""
#reader = csv.reader(open('formats.csv'), encoding='utf-8', delimiter=";")
reader = csv.reader(open('formats.csv'), delimiter=";")
fileformatresult = []

i = 0        
for row in reader:   
    fileformatresult.append(row[0]) #recognized formats in a list
    #printmessage(str(row))        
    i += 1
#printmessage(fileformatresult)
#templist=[]
"""
First browse the directory structure and extract a list of paths which
contain either acceptable image file or a pdf file and save those into a list
"""
pathList = []
for root, dirs, items in os.walk(walk_dir):    
    for item in items:
        #templist = []
        fullitempath = os.path.join(root, item)
        #printmessage(item+" "+fullitempath)      
        begin, end = os.path.splitext(item)
        end = str(end).lstrip('.')
        #printmessage(end)
        if end in fileformatresult and 'jpeg' in fullitempath:  
            tempFilePath = os.path.dirname(os.path.abspath(fullitempath))
            parentDirPath = os.path.dirname(os.path.abspath(tempFilePath))
            parentContent = os.listdir(parentDirPath)
            tempString = str(parentContent)                           
            pathList.append(tempFilePath)
            break
            
printmessage("Path list before reduce: {}".format(pathList))
pathList = list(set(pathList)) #Removes the duplicates from the big list
printmessage("After path reduce {}".format(pathList))

pool = Pool(cpucount*2)

for singlePath in pathList:    
    
    #printmessage(singlePath)
    #finalFiles = [] #Clears possible existing items from the list    
    #finalFilePath = os.path.dirname(singlePath)
    #printmessage("Just: {}".format(finalFilePath))
    #break
    dirContent = os.listdir(singlePath)
    for item in dirContent:        
        begin, end = os.path.splitext(str(item))
        end = str(end).lstrip('.')
        #printmessage(end)
        if end in fileformatresult:        
        #if str(item).endswith("pdf"):
            fullitempath = os.path.join(singlePath, item)    
            #printmessage(fullitempath)
            #templist=[]    
            #templist.append(fullitempath)
            #printmessage("PDF foudn")pool.apply_async(walkthroughmultiprocess, args=(root, str(templist[0]), beginfilenamestriped), callback=multiprocess_results)
            if end != 'pdf': #If called with image file               
                #printmessage(item)
                #ocrmyfile(templist[0])
                pool.apply_async(ocrmyfile, args=(fullitempath,), callback=getocrResult)                
            #else: #In case it is a .pdf file                
                #testresult = ocrmyfile(templist[0]) #Newer return back
                
            setOcrFilesCount(1)
        

pool.close()
pool.join()



if composeSingleFile:
    #pool = Pool(cpucount)
    for singlePath in pathList:
        finalFilePath = os.path.dirname(singlePath)
        printmessage("Handling file path {}".format(singlePath))
        tempDisposeList = []
        singleFile = os.path.split(finalFilePath)[1]+"_kaikki.pdf"
        #printmessage(singleFile)
        dircontent = os.listdir(singlePath)
        #printmessage(dircontent)
        finalFiles = []
        for onefile in dircontent:
            if str(onefile).endswith('pdf'):
                finalFiles.append(os.path.join(singlePath, onefile))
            
        #printmessage(finalFiles)
        #singleFile = str(uuid.uuid4())+".pdf"
        singleFile = os.path.join(finalFilePath, singleFile)
        singleFile = "-o"+singleFile
        finalFiles.sort(key=alphanum_key)
    
        #sortedFinalFiles = sorted(finalFiles) #Change to https://stackoverflow.com/questions/4623446/how-do-you-sort-files-numerically
        #printmessage(finalFiles) #prints OK
        
        if producePDFA:
            combineGCcmd =[gspath, '-dPDFA=3',
            '-dBATCH', '-dNOPAUSE', '-dNOOUTERSAVE', '-dNOSAFER', '-dPDFSETTINGS=/printer',
            '-dPDFACompatibilityPolicy=1', '-dAutoFilterColorImages=false', '-dColorImageFilter=/FlateEncode',
            '-dAutoFilterGrayImages=false', '-dGrayImageFilter=/FlateEncode', '-dMonoImageFilter=/FlateEncode',
            '-dEmbedAllFonts=true', '-dCompressFonts=true', '-sPAPERSIZE=a4', '-dDetectDuplicateImages', '-dPDFFitPage', 
            '-dNOTRANSPARENCY', '-sDEVICE=pdfwrite', singleFile]
        else:                
            combineGCcmd =[gspath, '-dBATCH', '-dNOPAUSE', '-dNOOUTERSAVE', '-dNOSAFER', '-dPDFSETTINGS=/ebook',
            '-dCompatibilityLevel=1.4','-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dDetectDuplicateImages', '-dPDFFitPage', singleFile]
        
        for file in finalFiles:
            combineGCcmd.append(file)
            if deltempfiles:
                tempDisposeList.append(file)
        docmd(combineGCcmd)
        #pool.apply_async(docmd, args=(combineGCcmd,))
        if deltempfiles:
           for x in range(len(tempDisposeList)):
               removeFile(tempDisposeList[x])
    #pool.close()
    #pool.join()

atexit.register(endofscript)     