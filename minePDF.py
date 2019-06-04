#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 13:35:53 2018
This script mines the pdf content and returns it as a manageable object

@author: digitalia-aj
"""

"""
input: full path to pdf file
output: 
"""

import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
#from pdfminer.pdfpage import PDFPage
#from pdfminer.pdfinterp import resolve1 #Needed in pdfPageCount

from PyPDF2 import PdfFileReader

def startParsingPDF(fullitempath):
    # Open a PDF file.
    fp = open(fullitempath, "rb")
    print("parsing")
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    print("creating pdf object")
    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)
    
    #pdfPageCount = resolve1(document.catalog['Pages'])['Count'] #Total count of pages
    
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
    laparams = LAParams(all_texts=True)

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # loop over all pages in the document
    #pagecount = 0
    #print("test")
    #for page in PDFPage.get_pages(document):
    returnList = [document, interpreter, device]
    return returnList    
    

def get_toc(pdf_path):
    reader = PdfFileReader(pdf_path)
    print (reader.outlines)    
    #return toc


def getPDFPagePlainText(page, interpreter, device):
    interpreter.process_page(page)
    layout = device.get_result()
    textContent = []
    textContent = parse_obj_just_text(layout, textContent)
    return textContent    

def parse_obj_just_text(lt_objs, textContent):
    #print("parse_obj")
    #print(lt_objs)
    """
    parse_obj
    [<LTTextLineHorizontal 334.100,769.332,385.603,783.129 '17.10.2005\n'>]
    """
   
    #tempword = ""           
    #forbiddenChars =[',','.',':','>','<','!','?','[',']','(',')','{','}','&']       
   
    for obj in lt_objs:
        #print("Main obj = {}".format(obj))
        # if it's a textbox, print text and location        
        """
        if isinstance(obj, pdfminer.layout.LTChar):           
            print("LTChar type item found")
            tempChar = str(obj.get_text())
            #print(tempChar)                                                      
            tempword+=tempChar                
                
        elif isinstance(obj, pdfminer.layout.LTAnno): #Annotation character found  
            print("LTAnno type item found")
            if len(tempword)>1: #If previous tempword is not empty --> add to list                
                textContent.append(tempword) #and add the word itself
                               
                tempword = ""
        """
        if isinstance(obj, pdfminer.layout.LTTextLine): #Further parse textline object            
            linetext = pdfminer.layout.LTTextLine.get_text(obj)
            """            
            Complete text line - 17.10.2005            
            """            
            textContent.append(linetext)
            #print("Complete text line - {}".format(linetext))
            #tempword=""
            #parse_obj_just_text(obj._objs, textlocations)
        
        elif isinstance(obj, pdfminer.layout.LTTextBoxHorizontal): #Furthher parse textbox objects
            #tempword=""
            parse_obj_just_text(obj._objs, textContent)
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure): #What to do with image type objects
            print("Image type item found")
            parse_obj_just_text(obj._objs, textContent)            
            
        elif isinstance(obj, pdfminer.layout.LTPage):
            print("page")
            #parse_obj_just_text(obj._objs, textlocations)
    #print("Kukkuu")
    #print(textContent)    
    return textContent


def handlePDFPages(page, interpreter, device):
    #print("MUUH")
    #print(page)
    # read the page into a layout object
    interpreter.process_page(page)
    layout = device.get_result()
    print("LAYOUT {}".format(layout))
    
    #print("test")
    # extract text from this object
    textlocations = []
    textlocations = parse_obj_with_coordinates(layout, textlocations)
    return textlocations

def parse_obj_with_coordinates(lt_objs, textlocations):
    #print("parse_obj")
    #print(lt_objs)
    #textlocations = []
    # loop over the object list
    tempword = ""           
    forbiddenChars =[',','.',':','>','<','!','?','[',']','(',')','{','}','&']   
    tempWordData = []
    endY = endX = 0
    #print(lt_objs.__dir__)
    #print(lt_objs.__len__)
    
    """
    if isinstance(lt_objs, pdfminer.layout.LTPage):
        print("pageobject")
        #elements = []
        for lt_obj in lt_objs:
            print(lt_obj)
        
        #parse_obj(lt_objs, textlocations)
    """ 
    for obj in lt_objs:
        #print("Main obj = {}".format(obj))
        # if it's a textbox, print text and location        
        if isinstance(obj, pdfminer.layout.LTChar):
            #print("lt object found")
            """
            13:07:28><LTChar 56.988,796.411,61.080,808.269 matrix=[1.00,0.00,0.00,1.00, (56.99,799.09)] font='RTUZQR+TeXGyreHeros-Regular' adv=4.091904 text='r'>
            13:07:28>lt object found
            13:07:28><LTChar 61.068,796.411,64.484,808.269 matrix=[1.00,0.00,0.00,1.00, (61.07,799.09)] font='RTUZQR+TeXGyreHeros-Regular' adv=3.4160640000000004 text=' '>
            """
            tempChar = str(obj.get_text())
            #print(tempChar)
            if tempChar not in forbiddenChars:
                beginX =round(obj.x0, 2) #Gets the co-ordinates of every character
                endX = round(obj.x1, 2)
                beginY =round(obj.y0, 2)
                endY = round(obj.y1, 2)
                if tempword=="": #Word is currently blank, --> coordinates of the first character
                    tempWordData.append(beginX)
                    tempWordData.append(beginY)
                    #print(str(beginX)+" "+str(beginY))
                #print("Blank")
                tempword+=tempChar                
            else:
                #print("blank or ending character found")
                if tempWordData:
                    tempWordData.append(endX)
                    tempWordData.append(endY)
                    tempWordData.append(tempword)
                    #print(tempWordData)
                    textlocations.append(tempWordData)
                    tempWordData=[]
                tempword=""
        elif isinstance(obj, pdfminer.layout.LTAnno): #Annotation character found  
            if len(tempWordData)>1: #If previous tempworddata is not empty --> add ending coordinates
                tempWordData.append(endX)
                tempWordData.append(endY)
                tempWordData.append(tempword) #and add the word itself
                #print(tempWordData)
                textlocations.append(tempWordData) #Add all to textlocations list
                tempWordData=[]
                tempword = ""
        
        elif isinstance(obj, pdfminer.layout.LTTextLineHorizontal): #Further parse textline object            
            tempword=""
            parse_obj_with_coordinates(obj._objs, textlocations)
        
        elif isinstance(obj, pdfminer.layout.LTTextBoxHorizontal): #Furthher parse textbox objects
            tempword=""
            parse_obj_with_coordinates(obj._objs, textlocations)
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure): #What to do with image type objects
            print("Image type item found")            
            beginX =abs(round(obj.x0, 2)) #Gets the co-ordinates of a figure
            endX = abs(round(obj.x1, 2))
            beginY =abs(round(obj.y0, 2))
            endY = abs(round(obj.y1, 2))
            tempWordData.append(beginX)
            tempWordData.append(beginY)
            tempWordData.append(endX)
            tempWordData.append(endY)
            tempWordData.append("Figure")
            textlocations.append(tempWordData)
            tempWordData=[]
            parse_obj_with_coordinates(obj._objs, textlocations)
        elif isinstance(obj, pdfminer.layout.LTPage):
            print("page")
            parse_obj_with_coordinates(obj._objs, textlocations)
    #print("Kukkuu")
    #print(textlocations)    
    return textlocations
   