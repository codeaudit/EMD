import numpy as np
from numpy.random import randint
import subprocess
import sys
from os.path import isfile
import os
from PIL import Image
from fractions import Fraction

path = os.environ["HASKPATH"]

def sinksrand(num):
    return randint(0,num,num,np.uint32)

def sourcesrand(num):
    return randint(0,num,num,np.uint32)

## Makes sure that randomly generated sinks and sources both have the same sum
def equalize(sinks, sources):
    if sum(sinks) > sum(sources):
        sources = np.append(sources, sum(sinks)-sum(sources))
        sinks = np.append(sinks, 0)
    else:
        sinks = np.append(sinks, sum(sources)-sum(sinks))
        sources = np.append(sources, 0)
    return (sinks, sources)

## Writes a 1-dimensional array as a bitmap for use by Haskell Accelerate
def tobmp (lists, filename):
    arr = np.uint32(np.int32(lists))
    arr = np.expand_dims(arr, axis=1)
    arr = np.expand_dims(arr, axis=1)
    arr = np.expand_dims(arr, axis=1)
    img = Image.fromarray(arr, 'RGBA')
    img.save(path+filename+'.png')
    subprocess.Popen(["mogrify","-format","bmp",filename+'.png'], cwd=path).wait()

## Converts an array of probabilites into an array of unsigned integers for efficient use by the GPU
def multiplier (list1, list2):
    maximum = 1
    l = np.concatenate((list1, list2), axis=0)
    for i in np.nditer(l):
        maximum = np.maximum(maximum, Fraction(float(i)).limit_denominator().denominator)
    return maximum

def testemd(list1, list2):
    mult = multiplier(list1, list2)
    list1 = mult*list1
    list2 = mult*list2
    var = np.std(list1-list2)
    #nodes = int(np.log2(len(list1)))
    #logmean = np.log2((np.average(list1)+np.average(list2))/2)
    mean = (np.average(list1)+np.average(list2))/2
    l1 = tobmp (list1, "list1")
    l2 = tobmp (list2, "list2")
    if not isfile(path+"data/matrix-"+(str(list1.size))+".png"):
        makemat(list1)
    output = haskemd("list1.bmp","list2.bmp","data/matrix-"+(str(list1.size))+".png")
    output = str(output)
    factor = 1
    back = float(''.join(filter(lambda x: x.isdigit() or x=='.', output)))/float(mult)
    return (round(float(factor)*back), mean, var)

##Computes the Earth Mover's distance between two distributions
def emd(list1, list2):
    mult = multiplier(list1, list2)
    list1 = mult*list1
    list2 = mult*list2
    var = np.std(list1-list2)
    nodes = int(np.log2(len(list1)))
    logmean = np.log2((np.average(list1)+np.average(list2))/2)
    l1 = tobmp (list1, "list1")
    l2 = tobmp (list2, "list2")
    if not isfile(path+"data/matrix-"+(str(list1.size))+".png"):
        makemat(list1)
    output = haskemd("list1.bmp","list2.bmp","data/matrix-"+(str(list1.size))+".png")
    output = str(output)
    factor = min(1, np.float64((((2*np.sqrt(2))**(8-logmean))*.000206201*var)+.253198))
    back = float(''.join(filter(lambda x: x.isdigit(), output)))/float(mult)
    return round(float(factor)*back)

##Calls the Haskell program which actually does the computation
def haskemd(list1, list2, matrix):
    command = "sudo -E env \"PATH=$PATH\" EMD "+str(list1)+" "+str(list2)+" "+matrix+" -N8"
    p=subprocess.Popen(command, shell=True, cwd=path, stdout=subprocess.PIPE)
    out, trash = p.communicate()
    cleanup()
    return out

##Calls the Haskell program that generates matrices from the metric
def makemat(l):
    dim = l.size
    subprocess.Popen (["Mat",str(dim),"data/matrix-"+str(dim),"-N8"], cwd=path).wait()

##Deletes bitmaps that were fed into the Haskell program
def cleanup():
    subprocess.Popen (["rm","list1.bmp","list2.bmp","list1.png","list2.png"], cwd=path).wait()
