from queue import PriorityQueue

from nearest_neighbor import dist

def get_voronoi(genPts, sz):
  matrix = [[-1 for x in range(sz[0])] for y in range(sz[1])]

  q = PriorityQueue()
  for k in range(len(genPts)):
    if (isValid(genPts[k], sz)):
      q.put((0, genPts[k], k))
  while (not q.empty()):
    val = q.get() 
    pt = val[1]
    k = val[2]
    if (matrix[pt[1]][pt[0]] != -1):
      continue

    matrix[pt[1]][pt[0]] = k 

    for n in neighbors(pt, sz):
      if isValid(n, sz) and matrix[n[1]][n[0]] == -1:
        newD = dist(genPts[k], n)
        q.put((newD, n, k))

  return matrix

def neighbors(pt, sz):
  dx = [0, 1,  0, -1]
  dy = [1, 0, -1,  0]

  retVal = []
  for i in range(len(dx)):
    retVal.append((pt[0] + dx[i], pt[1] + dy[i]))

  return retVal

def isValid(pt, sz):
  return (pt[0] >= 0) and (pt[0] < sz[0]) and (pt[1] >= 0) and (pt[1] < sz[1])

def findCentroids(A, sz, numGen, rho):
  mX = [0]*numGen
  mY = [0]*numGen
  m  = [0]*numGen
  
  for y in range(sz[1]):
    for x in range(sz[0]):
      k = A[y][x]
      m[k]  +=   rho(x, y)
      mY[k] += y*rho(x, y)
      mX[k] += x*rho(x, y)

  centroids = [(mX[k]/m[k], mY[k]/m[k]) for k in range(numGen) if m[k] > 0]
  return centroids

def drawCirc(draw, pt, r):
  pt0 = (pt[0]-r, pt[1]-r)
  pt1 = (pt[0]+r, pt[1]+r)
  draw.ellipse([pt0, pt1], fill=(0))
