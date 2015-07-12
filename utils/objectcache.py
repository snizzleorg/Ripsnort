#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import shelve
import tempfile
import logging


def _cacheStorageDir():
    homeDir = os.getenv("HOME")
    
    if not os.path.isdir(homeDir):
        homeDir = tempfile.gettempdir()
    
    cacheDir = os.path.join(homeDir,'.cache','ripsnort')
    
    if not os.path.isdir(cacheDir):
        os.makedirs(cacheDir)

    return cacheDir

def _openShelveDbForCaller(caller):
    tempDir = _cacheStorageDir()
    tempFile = os.path.join(tempDir,caller)
    
    if os.path.exists(tempDir) == False:
        os.makedirs(tempDir)
    
    s = shelve.open(tempFile)
    
    return s

def saveObject(caller,key,obj):
    didSave = True
    
    try:
        s = _openShelveDbForCaller(caller)
        s[key] = obj
    except:
        didSave = False
    
    return didSave

def searchCache(caller,key):
    retObject = None
    
    try:
        s = _openShelveDbForCaller(caller)    
        retObject = s[key]
    except:
        pass
    
    logging.debug('Cache search ' + key + ' (' +str(caller)+ ') results: ' + str(retObject))

    return retObject

def clearCache(caller):
    filePath = os.path.join(_cacheStorageDir(),caller)
    
    if os.path.exists(filePath):
        logging.info('Clearing cache: ' + filePath)
        os.remove(filePath)

def availableCaches():
    cacheList = []
    
    for fileName in os.listdir(_cacheStorageDir()):
        cacheList.append(fileName)
        
    return cacheList

def clearAllCaches():
    for cacheName in availableCaches():
        clearCache(cacheName)

