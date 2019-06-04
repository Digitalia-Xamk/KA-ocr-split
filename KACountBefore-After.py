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
#import subprocess
#import shutil
#import multiprocessing
#from multiprocessing import Pool
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
#from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1
import sys
#from pdfminer.pdfpage import PDFPage
#import minePDF #Import the selfmade module which mines the pdf file
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

walk_dir = os.getcwd() # should be the directory where program was run

if __name__ == "__main__":
    #cpucount = multiprocessing.cpu_count()
    #printmessage ("CPUs: "+str(cpucount))
    printmessage ("PYTHON VERSION: "+str(sys.version_info))
    #pool = Pool(cpucount)
    #gspool = Pool(cpucount)
    fixedOutPath = os.path.join(walk_dir,"runtime")
    #printmessage(fixedOutPath)

"""
Read pdf file inside the run directory
"""

for root, dirs, items in os.walk(walk_dir):
    for item in items:
        #print (item)
        if str(root).endswith('jpeg'):
            #printmessage(root)
            #printmessage(os.path.dirname(root))
            pagecountFile = open(os.path.join(os.path.dirname(root),'pages_before_ocr.txt'),'w')
            pagecountFile.write(str(len(os.listdir(root))))
            pagecountFile.close
            #printmessage(len(os.listdir(root)))
            #break
        
                   
        if 'KA_kaikki.pdf' in str(item):
            printmessage("found "+str(item))
            pdffile = open(os.path.join(root,item), 'rb')
            parser = PDFParser(pdffile)
            document = PDFDocument(parser)
            #print(document.catalog)
            pagecount = resolve1(document.catalog['Pages'])['Count']
            print(pagecount)
            pagecountFile = open(os.path.join(root ,'pages_after_ocr.txt'),'w')
            pagecountFile.write(str(pagecount))
            printmessage("written pagecount")
            pagecountFile.close
        #break
              
           

#pool.close()
#pool.join()        
printmessage("Time to wrap up..")
