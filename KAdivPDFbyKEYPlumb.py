
import os
#import tarfile
#import glob
import subprocess
import shutil
import multiprocessing
from multiprocessing import Pool
#import time
import sys
from pdfminer.pdfpage import PDFPage
import minePDF #Import the selfmade module which mines the pdf file
import re
from subprocess import call

"""
GLOBAL VARIABLE DEFINITIONS
"""
#gspath = '/home/user/ghostscript/gs-922'
gspath= '/usr/bin/gs'
messagenumber = 1
"""
DEFs that are called from elsewhere
"""
import datetime
import pdfplumber

def check_list(teksti,mlist):
    pfound = -1
    for i in range(0,len(mlist)):
        pfound = max(pfound,teksti.find(mlist[i]))
    return pfound

#Prints and saves messages into log file
def printmessage(message):
    global messagenumber
    try:
        print(str(messagenumber)+" : "+str(message))
        logfile.write(str(messagenumber)+" : "+str(message)+"\n")
        messagenumber+=1
    except OSError:
        pass
    return

def docmd(cmd):    
    #printmessage("manipulating "+str(cmd))
    cmdprocess = subprocess.Popen(cmd)
    cmdprocess.communicate()
    #convertedFilesCount +=1
    return


def stringtoint(s): #simply just tries to convert string to int, failure returns 000
    try:
        return int(s)
    except ValueError:
        return "000"


"""Called at the beginning to ensure that
the there aren't directory that we are going to form
"""
def removeDir(dirname): #actual method that removes the folder
    try:
        printmessage ("Trying to delete folder "+dirname)
        shutil.rmtree(dirname)
    except OSError:
        pass
    return


#def multipath(walk_dir, metaname, dname, beginfilename, pool):
def multipath(walk_dir, metaname, beginfilename):
    #global pool
    printmessage("MultiPath operation started")
    #beginfilename_begin = beginfilename.split('.', 1)[0] 
    bookmarklist = []
    printmessage("metaname in multipath"+str(metaname))
    f = open(os.path.join(walk_dir, metaname),'r')
    lines = f.readlines()
    printmessage ("Total lines="+str(len(lines)))
    bookmarkloopcount = 0    
    lastpage = 0
    endofheader = 0
    bookmarkentry = [] #name, startpage, endpage
    
    for i in range(0, len(lines)):    
        """Gets the total number of pages of the pdf file
        used later on when the final bookmark last page is added"""
        if str(lines[i]).startswith("NumberOfPages:"):
            line3key, line3value = str(lines[i]).split(":", 1)
            lastpage = stringtoint(line3value)+1 #just to make sure ending and possible final detection are not on a same page
            #printmessage("test2")
            #Adds the ending bookmark at first, sorted out later on
            bookmarkentry.append('End')
            bookmarkentry.append(lastpage)
            bookmarklist.append(bookmarkentry)
            bookmarkentry = []
        
        """
        BookmarkBegin
        BookmarkTitle: Change
        BookmarkLevel: 1
        BookmarkPageNumber: 50
        """
        if str(lines[i]).startswith("BookmarkTitle"): #BookmarkTitle 1-4 lines, BookmarkLevel BookmarkPageNumber
            
            line1key, temp1value = str(lines[i]).split(":", 1)
            line1value = str(temp1value).rstrip()
            #printmessage("test3")            

            if str(lines[i+1]).startswith("BookmarkLevel"):
                endofheader = i
            elif str(lines[i+2]).startswith("BookmarkLevel"):
                endofheader = i+1
                line1value+=str(lines[i+1]).rstrip()
            elif str(lines[i+3]).startswith("BookmarkLevel"):
                endofheader = i+2
                line1value+=str(lines[i+1]).rstrip()
                line1value+=str(lines[i+2]).rstrip()
            elif str(lines[i+4]).startswith("BookmarkLevel"):
                line1value+=str(lines[i+1]).rstrip()
                line1value+=str(lines[i+2]).rstrip()
                line1value+=str(lines[i+3]).rstrip()
                endofheader = i+3
            
            line1value = line1value.strip() #Trims possible whitespaces and newlines            
            bookmarkentry.append(str(line1value).lstrip(' ')) #Entry begins with whitespace --> trim
                       
            #printmessage(str(lines[endofheader+2])) #+1 = BookmarkLevel
            if lines[endofheader+2].startswith("BookmarkPageNumber:"):
                #printmessage("I="+str(i))
                line2key, line2value = str(lines[endofheader+2]).split(":", 1)
                #printmessage ("Bookmarkbeginvalue"+str(line2value))
                ibookmarkbegin = stringtoint(line2value)
                bookmarkentry.append(ibookmarkbegin)
                #printmessage("Bookmarkentry = "+str(bookmarkentry))                
                bookmarklist.append(bookmarkentry)
                bookmarkentry = []
                #printmessage(str(line1value)+str(line2value)+str(bookmarkloopcount))
                bookmarkloopcount+=1               
        
   
    #printmessage("Bookmarks = "+str(bookmarklist))     
    #print ("I =",i+1)
    #print ("len=",len(lines))
    
    if i+1 == len(lines):
        if bookmarkloopcount==0:                             
            printmessage("No bookmarks found inside metadata, lets try with keywords..")
            printmessage("Browse the whole document first and then create bookmark lists")
            pageProbabilities = [] #List that holds probabilities for every scanned page
            
            #Lets first add the beginning reference infos
            bookmarkentry.append('Tunnisteet') #Safe to assume that every NA document starts with these
            bookmarkentry.append(1)
            bookmarklist.append(bookmarkentry)
            bookmarkentry = []

            memoSignatures = ['muistio', 'mui<tio']

            endSignatures = ['valtionarkistonhoitaja', 'pääjohtaja', 'arkistoneuvos', 'yksikönjohtaja',
                             'yksikön johtaja', 'toimistopäällikkö', 'vs. toimistopäällikkö',
                             'ylitarkastaja', 'vs. ylitarkastaja', 'tutkija', 'vs. tutkija', 'vs. valtionarkistonhoitaja',
                             'toimistopäällikkö','valtionarkistonhoitaja','ylijohtaja','vs. valtionarkiston-',
                             'valtionarkistonhoitaja','erikoistutkija', 'vt. toimistopäällikkö','vt. valtionsrkistonhoitaja',
                             'vs. toimistoväällikkö', 'valtionarkistonhoita ja', 'vt. valtionarkiston-', 'vakuudeksi', 'tarkistettu',
                             'tarkistanut']
            
            endSignatureNames = ['päivi', 'happonen', 'jussi', 'nuorteva', 'kari', 'tarkiainen', 
                                 'markku', 'leppänen', 'pirkko', 'rastas', 'leena', 'vanhanen',
                                 'juhani', 'saarenheimo', 'eljas','orrman','mirja','härkönen']
            
            vlist = ['valtionarkiston', 'vaitionarkiston','ionarkiston', 'valtionarkisto','valtionäarkiston',
                     'valktionarkiukon', 'veltionarkiston','valktionarkiukon' ]
            plist = ['pöytäkirja','päätöspöytäkirja','pöytökirja','pöytäökirja']

            pdf_file = os.path.join(walk_dir, beginfilename)
            esityscount = 0
            with pdfplumber.open(pdf_file) as pdf:
                #first_page = pdf.pages[0]
                #allpages = pdf.pages
#

                for i in range(0, len(pdf.pages)):
                # print(first_page.chars[0])
                    current_page = pdf.pages[i]
                    teksti = current_page.extract_text()
                    teksti = teksti[0:150]
                    teksti = teksti.lower()
                    #vcount = teksti.find('valtionarkiston')
                    vcount = check_list(teksti, vlist)
                    pcount = check_list(teksti, plist)
                    #pcount = teksti.find('pöytäkirja')
                    liite = teksti.find('liite')
                    if vcount > -1 and pcount > - 1 and liite ==-1:
                        #if vcount < 100 and pcount < 100:
                        testTester = teksti
                        print(testTester)
                        testTester.replace('\ņ',' ')
                        Mlist = testTester.split(' ')
                        regex1 = r'\d{1,2}(\.|\:)(\d{1,2}(\.|\:))\d{2,4}'
                        dst = ''
                        for j in range(0, len(Mlist)):
                            testTester = Mlist[j]

                            mnumber = ''
                            if re.match(r'\d{1,2}(\.|\:)(\d{1,2}(\.|\:))\d{2,4}', testTester):
                                mdate = re.search(regex1, testTester)
                                print('date found')

                                dst = mdate.group()
                                try:
                                    dst = datetime.datetime.strptime(dst, '%d.%m.%Y')
                                    dst = dst.strftime('%d%m%Y')
                                except:
                                    pass
                                print(dst)
                                #if re.match(r'\d{1,2}(/)(\d{1,2})', testTester):
                                #    print('Number found')
                                #    mnumber = re.search(r'\d{1,2}(/)(\d{1,2})', testTester)

                        bookmarkentry.append('Istuntopoytakirja_nro' + str(esityscount+1)+'_')
                        bookmarkentry.append(i+1)
                        bookmarklist.append(bookmarkentry)
                        k = len(bookmarklist)
                        bookmarklist[k - 1][0] = bookmarklist[k - 1][0] + dst
                        esityscount += 1
                        bookmarkentry = []
                print(bookmarklist)

                try:
                    os.remove(os.path.join(walk_dir, metaname))
                except FileNotFoundError:
                    pass
                print(bookmarklist)
                returnList = [bookmarklist, walk_dir, beginfilename]
                return returnList






def getPagenum(elem):
    return elem[1]

def checkitem(inlist,resultlist):
    check = False
    for item in inlist:
        if item in resultlist:
            check = True
    return check


def buildFinalBreakpoints(brList):
    for i in range(len(brList)):
        if str(brList[i][0])=="Muistio-END":#If muistio-end is before muistio, switch places            
            if str(brList[i+1][0])=="Muistio":    
                brList[i], brList[i+1] = brList[i+1], brList[i]        
    for i in range(len(brList)):            
        if str(brList[i][0])=="Muistio":
            #Seek forward if Muistio-END is found
            try:
                if brList[i+1][0] == "Muistio-END": #Next element name
                    endNum = brList[i+1][1] #The page number of this is the end of muistio                    
                    printmessage("Muistio-END at page {}".format(endNum))
                   # """Check if the next element starts one after muistio-END as it should"""
                    printmessage(brList[i+2][1])
                    if str(brList[i+2][1]-1) != str(endNum):
                        printmessage("Lets update the next starting point")
                        brList[i+2][1]=endNum+1               
                    del brList[i+1]
                    break
                    
                elif brList[i+2][0] == "Muistio-END": #the second Next element
                    brList[i+1], brList[i+2] = brList[i+2], brList[i+1]
                    endnum1 = brList[i+1][1]
                    endnum2 = brList[i+2][1]
                    if endnum1 > endnum2:
                        brList[i+2][1] = endnum1+1
                    del brList[i+1]
                    break
            except IndexError as e:
                printmessage (e)
                printmessage("Moving on..")
                pass
    printmessage(brList)
    return brList 

def multipathResults(brList):    
    printmessage("Multipath results gained {}".format(brList))
    breakpointsList = brList[0]    
    root = brList[1]    
    beginfilename = brList[2]
    #printmessage(breakpointsList)
    """Sorts the bookmarklist according to page numbers"""
    #breakpointsList=bookmarkList[0]
    breakpointsList.sort(key=getPagenum)
    printmessage("How about here {}".format(breakpointsList))
    breakpointsList = buildFinalBreakpoints(breakpointsList)
    printmessage(breakpointsList)
    #break
    
    #One list which contains X lists [[name, 1][name, 6], etc.
    #finalBreakPoints = []
    if len(breakpointsList)>0:
        i = 0
        for i in range(len(breakpointsList)):
            try:
                oneBreakPoint = breakpointsList[i]
                printmessage(oneBreakPoint)                                                                                   
                name = oneBreakPoint[0]
                startpoint = oneBreakPoint[1]
                if name == "end":
                    break
                else:
                    try:
                        secondBreakPoint = breakpointsList[i+1]
                        #printmessage(secondBreakPoint[0])
                        if str(secondBreakPoint[0])=="End":
                            #printmessage("Just test")
                            endpoint = secondBreakPoint[1] -1
                        else:
                            endpoint = secondBreakPoint[1]-1 #The start page of the next breakpoint, so -1 is the last page of previous
                        
                        firstpage = "-dFirstPage="+str(startpoint)
                        lastpage = "-dLastPage="+str(endpoint)            
                        #printmessage ("firstpage:"+str(firstpage))
                        #printmessage ("lastpage:"+str(lastpage))
                        name = str(root).rsplit('/', 1)[1]+"_"+str(name)
                        #name = str(item).split('.')[0]+"_"+str(name).replace('/','-').rstrip().replace(' ','-')
                        #name = 
                        output = str(os.path.join(root, name))+'_'+str(startpoint)+'-'+str(endpoint)+".pdf"
                        pagestring = str(startpoint)+'-'+ str(endpoint)
                        #gscmd = [gspath, '-dNOPAUSE', '-dNOOUTERSAVE',
                        #'-dNOSAFER', '-dPDFSETTINGS=/printer', '-dGrayImageFilter=/FlateEncode', '-dMonoImageFilter=/FlateEncode',
                        #'-sColorConversionStrategy=/RGB', '-sDEVICE=pdfwrite',
                        #'-dAutoFilterGrayImages=false',
                        #firstpage, lastpage, output, beginfilename]
                        #, firstpage, lastpage, output, beginfilename
                        #printmessage(gscmd)
                        print(output)
                        gscmd = ['/usr/bin/qpdf', beginfilename, '--pages', beginfilename, pagestring, '--', output]
                        print(gscmd)
                        docmd(gscmd)
                        #call(gscmd)
                        i+=1
                    except IndexError:
                    #If not more breakpoints is found, use the last page as endpoint
                        break    
                        #endpoint = 'NA'
                        pass
                                                                   
            except IndexError:
                pass

"""
VARIABLE defitinions
"""

logfile = open('dividePDF.log', 'w')

walk_dir = os.getcwd() # should be the directory where program was run


if __name__ == "__main__":
    cpucount = multiprocessing.cpu_count()
    printmessage ("CPUs: "+str(cpucount))
    printmessage ("PYTHON VERSION: "+str(sys.version_info))
    pool = Pool(cpucount)
    #gspool = Pool(cpucount)
    fixedOutPath = os.path.join(walk_dir,"runtime")
    #printmessage(fixedOutPath)

"""
Read pdf file inside the run directory
"""

for root, dirs, items in os.walk(walk_dir):
    for item in items:
        if os.path.isfile(os.path.join(root, item)):
            #printmessage(str(item))
            if (str(item)).endswith(".pdf"):
                #for beginfile in glob.glob("*.pst"):
                beginfilename = os.path.join(root, item)
                printmessage ("Begin filename:"+beginfilename)
                                 
                metaname = beginfilename[:-4]+".txt"
                
                cmd = ["pdftk", beginfilename, "dump_data_utf8", "output", metaname]
                #subprocess.call(cmd, shell=True)
                printmessage ("Go pool.apply:"+beginfilename)
                pool.apply(docmd, args=(cmd,))
                #docmd(cmd)
                printmessage ("After pool.apply:"+beginfilename)
                """Read and save to list dumped metadata phase"""
                if os.path.isfile(metaname):
                    printmessage("Metafile found")
                    #breakpointsList = multipath(walk_dir, metaname, dname, beginfilename, pool)
                    pool.apply_async(multipath, args=(root, metaname, beginfilename), callback=multipathResults)
                    
                                                              
                else:
                    printmessage("No doc-data-txt found yet!")
                
    else:
        #break
        printmessage("No more files found inside the directory")

printmessage("Time to wrap up..")
pool.close()
pool.join()
#pool.close()
quit()




