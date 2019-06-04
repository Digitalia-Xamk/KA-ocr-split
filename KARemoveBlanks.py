"""Multiface processing
1 pdftk inputfile.pdf dump_data_utf8 output doc-data.txt
This face extract all metadata information from the original pdf file
including possible bookmarknames, leves and pages.

2 The extracted doc-data.txt must be read and parsed
could be a list that contains a list
[[nimi, alku, loppu] [nimi, alku, loppu] jne]

3. If bookmarks are not found we will try to use predefined valuelists for detecting splitpoints
"""


import os
#import tarfile
#import glob
import subprocess
#import shutil
import multiprocessing
from multiprocessing import Pool
#import time
import sys
from pdfminer.pdfpage import PDFPage
import minePDF #Import the selfmade module which mines the pdf file
#import re


"""
GLOBAL VARIABLE DEFINITIONS
"""
messagenumber = 1
"""
DEFs that are called from elsewhere
"""
#Prints and saves messages into log file
def printmessage(message):
    global messagenumber
    try:
        print(str(messagenumber)+" : "+str(message))        
        messagenumber+=1
    except OSError:
        pass
    return

def docmd(cmd):    
    printmessage("manipulating "+str(cmd))
    cmdprocess = subprocess.Popen(cmd)
    cmdprocess.communicate()
    #convertedFilesCount +=1
    return

def multiprocess(root, tempFile, pdf_file):
    print ("Multiprocessing")
    pdfMinerData = minePDF.startParsingPDF(tempFile)            
    printmessage("pdf document parsed, length of return string is {}".format(len(pdfMinerData)))
    #printmessage(pdfMinerData)
    finalPages = []
    if len(pdfMinerData)==3: #See above [document, interpreter, device]
        pagecount = 1 #1 since pdf read starts from page 1 in ghostscript                 
        #print("Inside loop")
        for page in PDFPage.create_pages(pdfMinerData[0]):                                                                                  
            textContent = minePDF.getPDFPagePlainText(page, pdfMinerData[1], pdfMinerData[2])                        
            #print (len(textContent))
            if len(textContent)<3: #Should be safe to assume the page is empty                             
                print("No text, just {} found inside page {}".format(textContent,pagecount))
            else:
                finalPages.append(pagecount)
            pagecount+=1
            #printmessage(textContent)
              
    #printmessage(finalPages)
    cmd = ["pdftk", tempFile, "cat"] 
    
    for num in finalPages:
        cmd.append(str(num))
        #print("Adding {}".format(num))
    #print(cmd)    
    cmd.extend(["output", pdf_file])          
    
    #print(cmd)
    docmd(cmd)
    if os.path.isfile(pdf_file):
        os.remove(tempFile)
        pagecountFile = open(os.path.join(root,'pages_after_ocr.txt'),'w')
        #pagecountFile
        printmessage(len(finalPages)-1)
        pagecountFile.write(len(finalPages)-1)
        pagecountFile.close
        
    return    

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
        #printmessage(str(item))
        if (str(item)).endswith(".pdf"):
            #for beginfile in glob.glob("*.pst"):
            pdf_file = os.path.join(root, item)
            tempFile = os.path.join(root, "tempFile.pdf")
            os.rename(pdf_file, tempFile)            
            pool.apply_async(multiprocess, args=(root, tempFile, pdf_file))  
            
           

pool.close()
pool.join()        
printmessage("Time to wrap up..")
