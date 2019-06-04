## Create Table of contents 

import os
#import tarfile
#import glob
#import subprocess
#import shutil
#import multiprocessing
#from multiprocessing import Pool
from PyPDF2 import PdfFileReader
import sys
#from pdfminer.pdfpage import PDFPage
#import minePDF #Import the selfmade module which mines the pdf file
#import re

from operator import itemgetter
"""
GLOBAL VARIABLE DEFINITIONS
"""
#gspath = '/home/user/ghostscript/gs-922'
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
Read pdf filenames inside the run directory to form Table of contents
"""

for root, dirs, items in os.walk(walk_dir):
#    contentFile = open(os.path.join(root, 'Table_of_contents.txt'), 'w')
    for dir in dirs:
#        print(dir)
        if 'KA' in dir:
#            contentFile = open(os.path.join(root,dir, 'Table_of_contents.txt'), 'w')

#            print(contentFile)
            content=[]
            for file in os.listdir(root+'/'+dir):
                if 'KA_' in file:
                    try:
                        print(file)
                        content.append(file)
                    except Exception:
                        failcount += 1
                        print(str(item) + ' ' + ' failed ')
                        print('L')
                        pass
            contentFile = open(os.path.join(root,dir, 'Table_of_contents.txt'), 'w+')
            contentFile.write(dir + '\n')
            scontent = []
            for i in range(0, len(content)):
                content[i] = content[i].split('_')
            for i in range(0, len(content)):
                if len(content[i]) == 5:
                    scontent.append(content[i])

            for i in range(0, len(scontent)):
                print(scontent[i], i)
                scontent[i][2] = scontent[i][2].replace('nro', '')
                scontent[i][2] = int(scontent[i][2])
            aa = (sorted(scontent, key=itemgetter(2)))
            pagenumbers = []
            pages = []
            for i in range(0, len(scontent)):
                print(aa[i])
                rivi = aa[i][4].split(' ')
#                pages.append(rivi[1])
                pagenumbers.append(rivi[0].replace('.pdf', ''))
            for i in range(0, len(aa)):
                temp = aa[i][4].split(' ')
                print(temp)
                    #    print('Istuntopöytäkirja nro',i+1,'yhteensä', temp[1],' sivua' )
                contentFile.write('Pöytäkirja nro ' + str(aa[i][2])  + '\n')
                temp[0].replace('.pdf', '')
                print('     sivut ', temp[0].replace('.pdf', ''))
                print('     pvm. ', aa[i][3])
                contentFile.write('     Sivut ' + temp[0].replace('.pdf', '') + '\n')
                if aa[i][3] != '':
                    contentFile.write(
                         '     Pvm. ' + aa[i][3][0:2] + '.' + aa[i][3][2:4] + '.' + aa[i][3][4:] + '\n')
            contentFile.close()

##    for item in items:
##        if 'KA_' in item:
##            tempfile = PdfFileReader(open(os.path.join(root,item), 'rb'))
##            #pages_after_ocr.txt
##            pagecountFile = open(os.path.join(root,'pages_after_ocr.txt'),'w')
#            contentFile = open(os.path.join(root,'Table_of_contents.txt'),'w')
            #pagecountFile
##            pages = tempfile.getNumPages()
#            printmessage(pages)
##            pagecountFile.write(str(pages))
#            contentFile.write(item)
##            pagecountFile.close
            #printmessage(tempfile.getNumPages())
            #printmessage(item)
            #printmessage(os.path.dirname(root))
            #pagecountFile = open(os.path.join(os.path.dirname(root),'pages_before_ocr.txt'),'w')
            #pagecountFile.write(str(len(os.listdir(root))))
            #pagecountFile.close
            #printmessage(len(os.listdir(root)))
            #break
              
           

#pool.close()
#pool.join()        
#printmessage("Time to wrap up..")
