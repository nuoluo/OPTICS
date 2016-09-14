import optics
import optics_numpy
import numpy
import utils

raw = numpy.loadtxt('CES.txt', ndmin=2)
logs = numpy.log10(raw)
epsilon = 0.02
minPts = 2
distType = 'euclidean'
clustering1 = optics.Optics(epsilon, minPts, logs, distType)
processedPoints1, execTime = utils.timedExecution(clustering1.run)
processedPoints1 = sorted(processedPoints1, key=lambda p: p.pid)
print("Done in", execTime, 's')
clustering2 = optics_numpy.Optics(epsilon, minPts, logs, distType)
processedPoints2, execTime = utils.timedExecution(clustering2.run)
print("Done in", execTime, 's')

with open("cluster1.txt", 'w') as f:
    for p in processedPoints1:
        f.write(str(p.pid) + ',' + str(p.clusterId) + '\n')
with open("cluster2.txt", 'w') as f:
    for i in range(len(logs)):
        f.write(str(processedPoints2.pid[i]) + ',' + str(processedPoints2.clusterId[i]) + '\n')

