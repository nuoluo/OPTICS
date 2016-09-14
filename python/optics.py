import numpy
import sys
from math import *

UNDEFINED = sys.float_info.max
NOISE = sys.maxsize


class OpticsPoint():
    def __init__(self, id):
        self.pid = id
        self.neighbors = numpy.empty(0, dtype=int)
        self.processed = False
        self.coreDist = UNDEFINED
        self.reachDist = UNDEFINED
        self.clusterId = NOISE


class Optics:

    def __init__(self,
                 epsilon:   float,
                 minPts:    int,
                 points:    numpy.array,
                 distType:  str):
        self.epsilon = epsilon
        self.minPts = minPts
        self.points = points
        self.distType = distType
        self.optPoints = numpy.array([OpticsPoint(i) for i in range(len(points))])

    def getPoint(self, p:OpticsPoint):
        return self.points[p.pid]

    def getNeighbors(self, p:OpticsPoint):
        return [self.optPoints[i] for i in p.neighbors]

    def getDistance(self, p:OpticsPoint, o:OpticsPoint):
        X1 = self.getPoint(p)
        X2 = self.getPoint(o)
        if self.distType == 'euclidean':
            sub = numpy.subtract(X1, X2)
            sqr = numpy.square(sub)
            return sqrt(sqr.sum())
        elif self.distType == 'angle':
            absX1 = sqrt(numpy.square(X1).sum())
            absX2 = sqrt(numpy.square(X2).sum())
            dotProd = numpy.prod([X1, X2], axis=0).sum()
            return dotProd/(absX1 * absX2)

    def initPoint(self, p:OpticsPoint):
        neighbors = []
        distances = []
        for o in self.optPoints:
            if o != p:
                distance = self.getDistance(p, o)
                if distance < self.epsilon:
                    neighbors.append(o.pid)
                    distances.append(distance)
        p.neighbors = numpy.array(neighbors)
        if len(p.neighbors) >= self.minPts:
            p.coreDist = sorted(distances)[self.minPts-1]

    def enqueue(self, Seeds, p:OpticsPoint, newD):
        i = 0
        while (i < len(Seeds)) and (Seeds[i][1] < newD):
            i += 1
        Seeds.insert(i, (p, newD))

    def moveUp(self, Seeds, p:OpticsPoint, newD):
        i = 0
        while i < len(Seeds):
            if Seeds[i][0] == p:
                Seeds.pop(i)
            i += 1
        self.enqueue(Seeds, p, newD)

    def dequeue(self, Seeds):
        return Seeds.pop(0)

    def update(self, Seeds, N, p:OpticsPoint):
        for o in N:
            if not o.processed:
                newReachDist = max(p.coreDist, self.getDistance(p, o))
                if o.reachDist == UNDEFINED:
                    o.reachDist = newReachDist
                    self.enqueue(Seeds, o, newReachDist)
                elif newReachDist < o.reachDist:
                    o.reachDist = newReachDist
                    self.moveUp(Seeds, o, newReachDist)

    def extractCluster(self, orderedPoints):
        C = 0
        for p in orderedPoints:
            if p.reachDist > self.epsilon:
                if p.coreDist <= self.epsilon:
                    C += 1
                    p.clusterId = C
            else:
                p.clusterId = C
        return orderedPoints

    def run(self):
        for p in self.optPoints:
            self.initPoint(p)
        orderedPoints = []
        Seeds = []
        for p in self.optPoints:
            if not p.processed:
                N = self.getNeighbors(p)
                p.processed = True
                orderedPoints.append(p)
                if p.coreDist != UNDEFINED:
                    self.update(Seeds, N, p)
                    while len(Seeds) > 0:
                        seed = self.dequeue(Seeds)
                        q = seed[0]
                        NN = self.getNeighbors(q)
                        q.processed = True
                        orderedPoints.append(q)
                        if q.coreDist != UNDEFINED:
                            self.update(Seeds, NN, q)
        return self.extractCluster(orderedPoints)
