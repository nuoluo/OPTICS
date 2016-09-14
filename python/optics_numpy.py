import numpy
import sys
from math import *

UNDEFINED = sys.float_info.max
NOISE = sys.maxsize

class Bunch(dict):
    """Container object for datasets

    Dictionary-like object that exposes its keys as attributes.

    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6

    """

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass

class OpticsPoint:
    def __init__(self, pid):
        self.pid = pid
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
        length = len(points)
        self.pid = numpy.array(range(length))
        self.neighbors = []
        self.coreDist = numpy.full(length, UNDEFINED)
        self.processed = numpy.zeros(length, dtype=bool)
        self.reachDist = numpy.full(length, UNDEFINED)
        self.clusterId = numpy.full(length, NOISE, dtype=numpy.int64)

    def getPoint(self, pid):
        return self.points[pid]

    def getNeighbors(self, pid):
        return self.neighbors[pid]

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

    def enqueue(self, Seeds, pid, newD):
        i = 0
        while (i < len(Seeds)) and (Seeds[i][1] < newD):
            i += 1
        Seeds.insert(i, (pid, newD))

    def moveUp(self, Seeds, pid, newD):
        i = 0
        while i < len(Seeds):
            if Seeds[i][0] == pid:
                Seeds.pop(i)
                break
            i += 1
        self.enqueue(Seeds, pid, newD)

    def dequeue(self, Seeds):
        return Seeds.pop(0)

    def update(self, Seeds, N, pid):
        for oid in N:
            if not self.processed[oid]:
                newReachDist = max(self.coreDist[pid], self.getDistance(pid, oid))
                if self.reachDist[oid] == UNDEFINED:
                    self.reachDist[oid] = newReachDist
                    self.enqueue(Seeds, oid, newReachDist)
                elif newReachDist < self.reachDist[oid]:
                    self.reachDist[oid] = newReachDist
                    self.moveUp(Seeds, oid, newReachDist)

    def extractCluster(self, orderedPoints):
        C = 0
        for pid in orderedPoints:
            if self.reachDist[pid] > self.epsilon:
                if self.coreDist[pid] <= self.epsilon:
                    C += 1
                    self.clusterId[pid] = C
                else:
                    self.clusterId[pid] = NOISE
            else:
                self.clusterId[pid] = C

    def initPoint(self, pid):
        distances = []
        neighbors = []
        for oid in self.pid:
            if oid != pid:
                distance = self.getDistance(pid, oid)
                if distance < self.epsilon:
                    neighbors.append(oid)
                    distances.append(distance)
        self.neighbors.append(neighbors)
        if len(self.neighbors[pid]) >= self.minPts:
            self.coreDist[pid] = sorted(distances)[self.minPts-1]

    def run(self):
        for pid in self.pid:
            self.initPoint(pid)
        orderedPoints = []
        Seeds = []
        for pid in self.pid:
            if not self.processed[pid]:
                N = self.getNeighbors(pid)
                self.processed[pid] = True
                orderedPoints.append(pid)
                # print(pid)
                if self.coreDist[pid] != UNDEFINED:
                    self.update(Seeds, N, pid)
                    while len(Seeds) > 0:
                        seed = self.dequeue(Seeds)
                        qid = seed[0]
                        NN = self.getNeighbors(qid)
                        self.processed[qid] = True
                        orderedPoints.append(qid)
                        # print(qid)
                        if self.coreDist[qid] != UNDEFINED:
                            self.update(Seeds, NN, qid)
        orderedPoints = numpy.array(orderedPoints)
        self.extractCluster(orderedPoints)
        return Bunch(pid=self.pid,
                     clusterId=self.clusterId,
                     reachDist=self.reachDist,
                     coreDist=self.coreDist,
                     neighbors=self.neighbors,
                     orderedPoints=orderedPoints)



