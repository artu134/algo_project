from PIL import Image
from PIL import ImageStat
from PIL import ImageDraw
import copy
import random
import sys
import itertools
import voronoi_algo as voronoi_algo
from segment import Seg
from itertools import product
import nearest_neighbor
from nearest_neighbor import dist

def ccw(A, B, C):
  return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersections(seg1, seg2):
  A = seg1[0]
  B = seg1[1]
  C = seg2[0]
  D = seg2[1]
  return ccw(C,D,A) != ccw(C,D,B) and ccw(A,B,C) != ccw(A,B,D)

def get_crossed(set1, set2):
  retVal = set() 
  for (seg1, seg2) in product(set1, set2):
    if (seg1.is_adjacent(seg2)): continue
    if (intersections(seg1.to_list(), seg2.to_list())):
      retVal.add((seg1, seg2))

  return retVal

def correct(segSet): 
  crossingSet = get_crossed(segSet, segSet)
  while crossingSet:
    (seg1, seg2) = crossingSet.pop()
    segSet.remove(seg1)
    segSet.remove(seg2)

    zero_values(seg1, seg2)

    seg1.nextSeg.reverse()

    newSeg1, newSeg2 = set_values(segSet, seg1, seg2)

    crossingSet = {c for c in crossingSet if c[0]!=seg1 and c[0]!=seg2 and c[1]!=seg1 and c[1]!=seg2}
    crossingSet = crossingSet | get_crossed({newSeg1, newSeg2}, segSet)

  return segSet

def zero_values(seg1, seg2):
    seg1.nextSeg.prevSeg = None
    seg1.prevSeg.nextSeg = None
    seg2.nextSeg.prevSeg = None
    seg2.prevSeg.nextSeg = None

    endSeg = seg1.nextSeg
    while (endSeg.nextSeg != None):
      endSeg = endSeg.nextSeg

def set_values(segSet, seg1, seg2):
    newSeg1 = Seg(seg1.sharedPt(seg1.prevSeg), seg2.sharedPt(seg2.prevSeg))
    newSeg2 = Seg(seg2.sharedPt(seg2.nextSeg), seg1.sharedPt(seg1.nextSeg))
      
    newSeg1.prevSeg = seg1.prevSeg
    newSeg1.nextSeg = seg2.prevSeg
    newSeg2.prevSeg = seg1.nextSeg
    newSeg2.nextSeg = seg2.nextSeg
    newSeg1.prevSeg.nextSeg = newSeg1
    newSeg1.nextSeg.prevSeg = newSeg1
    newSeg2.prevSeg.nextSeg = newSeg2
    newSeg2.nextSeg.prevSeg = newSeg2

    segSet.add(newSeg1)
    segSet.add(newSeg2)
    return newSeg1,newSeg2
  

def compute_distance(lst):
  retVal = dist(lst[0], lst[len(lst)-1])
  for i in range(len(lst)-1):
    retVal += dist(lst[i], lst[i+1])

  return retVal

def readImage(filename):
  im = Image.open(filename).convert('L')
  return im


def stipple(im, bxSz, itr):
  xSz = im.size[0]
  ySz = im.size[1]
  genPts = []
  for x in itertools.product(range(0, xSz-int(bxSz/2), bxSz), range(0, ySz-int(bxSz/2), bxSz)):
    box = (x[0], x[1], x[0]+bxSz, x[1]+bxSz)
    region = im.crop(box)
    if (ImageStat.Stat(region).mean[0]/255 < random.random()):
      genPts.append((x[0]+int(bxSz/2), x[1]+int(bxSz/2)))
  for i in range(itr):
    im2 = copy.deepcopy(im)
    m = voronoi_algo.get_voronoi(genPts, (xSz, ySz))

    draw = ImageDraw.Draw(im2)

    for pt in genPts:
      drawCirc(draw, (pt[0], pt[1]), 1, (0))
    
    centroids = voronoi_algo.findCentroids(m, (xSz, ySz), len(genPts), lambda x, y : 1-im.getpixel((x, y))/255)

    genPts = [(round(pt[0]), round(pt[1])) for pt in centroids]
    
    print('Completed {} try of stippling.'.format(i))

  return genPts

def drawCirc(draw, pt, r, color):
  pt0 = (pt[0]-r, pt[1]-r)
  pt1 = (pt[0]+r, pt[1]+r)
  draw.ellipse([pt0, pt1], fill=color)

def createSegSet(lst):
  segList = [Seg(lst[i], lst[i+1]) for i in range(len(lst)-1)] + [Seg(lst[0], lst[len(lst)-1])]
  for i in range(len(segList)):
    segList[i].prevSeg = segList[i-1]
    segList[i].nextSeg = segList[(i+1)%len(segList)]

  return set(segList)
  
def drawSegSet(segSet, sz, fname, red=set(), green=set(), blue=set()):
  im = Image.new('RGB', sz, (255, 255, 255))
  draw = ImageDraw.Draw(im)
  
  for seg in segSet:
    draw.line(seg.to_list(), fill=(127, 127, 127), width=1)

  for seg in red:
    draw.line(seg.to_list(), fill=(255, 0, 0), width=2)

  for seg in green:
    draw.line(seg.to_list(), fill=(0, 255, 0), width=2)

  for seg in blue:
    draw.line(seg.to_list(), fill=(0, 0, 255), width=2)

  del draw

  im.save(fname)

if __name__ == '__main__':
  sys.setrecursionlimit(6000)
  if (len(sys.argv) < 2):
    print('Usage: python3 {} filename', sys.argv[0])
    pass 

  filename = sys.argv[1]
  im = readImage(filename)
  if (max(im.size) > 600):
    im = im.resize((int(600*(float(im.size[0])/max(im.size))), int(600*(float(im.size[1])/max(im.size)))))

  cellSize = 2
  lst = stipple(im, cellSize, 0)
  while (len(lst) > 6000):
    cellSize += 1
    lst = stipple(im, cellSize, 0)
  lst = stipple(im, cellSize, 8)
  lst = nearest_neighbor.tsp(lst)
  segSet = createSegSet(lst)
  drawSegSet(segSet, im.size, 'start.jpg')
  segSet = correct(segSet)
  drawSegSet(segSet, im.size, 'end.jpg')
  print('Done.')
