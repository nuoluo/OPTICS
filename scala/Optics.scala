/**
 * Created by ASUS-PC on 2016/9/6.
 */
import math._
import scala.collection.mutable._

/**
 *
 * @param epsilon The maximum distance (radius) to consider
 * @param minPts The number of points required to form a cluster
 * @param points data points
 */
class Optics(epsilon:Double,
             minPts:Long,
             points:Array[Vector[Double]]) {

  val UNDEFINED = Double.MaxValue
  val NOISE = Int.MaxValue
  
  class OpticsPoint(_id:Int) {
    val id = _id
    var neighbors = Array.empty[Int]
    var processed = false
    var coreDist = UNDEFINED
    var reachDist = UNDEFINED
    var clusterId = NOISE

    def getPoint: Vector[Double] = points(id)
  }
  
  val optPoints  = points.indices.map(new OpticsPoint(_))

  def getOptPoint(p:Vector[Double]): OpticsPoint = optPoints(points.indexOf(p))

  def getNeighbors(p:OpticsPoint): Array[OpticsPoint] = p.neighbors.map(optPoints(_))

  def getDistance(X1:Vector[Double], X2:Vector[Double]): Double = sqrt(X1.zip(X2).map(x => pow(x._1 - x._2, 2)).sum)
  def getDistance(X1:OpticsPoint, X2:OpticsPoint): Double = getDistance(X1.getPoint,X2.getPoint)

  def initPoint(p:OpticsPoint):Unit = {
    val distances = optPoints.map(x => getDistance(x, p))
    val neighbors = optPoints.zip(distances).filter( np => (np._2 < epsilon) && (np._1.id !=p.id) ).sortBy(_._2)
    p.neighbors = neighbors.map(_._1.id).toArray
    p.coreDist = if (neighbors.length >= minPts) neighbors(minPts.toInt - 1)._2 else UNDEFINED
  }

  def enqueue(Seeds: ArrayBuffer[(OpticsPoint, Double)], p: OpticsPoint, newD: Double): Unit ={
    var i = 0
    while ( i<Seeds.length && Seeds(i)._2<newD) { i+=1 }
    Seeds.insert(i, (p,newD))
  }

  def moveUp(Seeds: ArrayBuffer[(OpticsPoint, Double)], p: OpticsPoint, newD: Double): Unit ={
    val i = Seeds.map(_._1).indexOf(p)
    Seeds.remove(i)
    enqueue(Seeds, p, newD)
  }

  def dequeue(Seeds: ArrayBuffer[(OpticsPoint, Double)]): (OpticsPoint, Double) ={
    Seeds.remove(0)
  }

  def update(Seeds:ArrayBuffer[(OpticsPoint, Double)], N: Array[OpticsPoint], p:OpticsPoint): Unit = {
//    println("updating seeds of point:" + p.id.toString + ", neighborhood:(" + N.map(_.id.toString).mkString(",") + ")")
    for (o <- N) {
      if (!o.processed) {
        val newReachDist = max(p.coreDist, getDistance(p, o))
        if (o.reachDist == UNDEFINED) {
          o.reachDist = newReachDist
          enqueue(Seeds, o, newReachDist)
        } else if ( newReachDist < o.reachDist) {
          o.reachDist = newReachDist
          moveUp(Seeds, o, newReachDist)
        }
      }
    }
  }

  def extractCluster(orderedPoints: ArrayBuffer[OpticsPoint]): ArrayBuffer[OpticsPoint] ={
    var C = 0
    for (p <- orderedPoints){
      if (p.reachDist > epsilon) {
        if (p.coreDist <= epsilon) {
          C += 1
          p.clusterId = C
        } else p.clusterId = NOISE
      } else {
        p.clusterId = C
      }
    }
    orderedPoints
  }

  def run(): ArrayBuffer[OpticsPoint] ={
    val orderedPoints = new ArrayBuffer[OpticsPoint]
    optPoints.foreach(initPoint)
    val Seeds = ArrayBuffer.empty[(OpticsPoint,Double)]
    for (p <- optPoints) {
      if (!p.processed) {
        val N = getNeighbors(p)
        p.processed = true
        orderedPoints.append(p)
        if ( p.coreDist != UNDEFINED) {
          update(Seeds, N, p)
          while ( Seeds.nonEmpty){
            val seed = dequeue(Seeds)
            val q = seed._1
            val NN = getNeighbors(q)
            q.processed = true
            orderedPoints.append(q)
            if ( q.coreDist != UNDEFINED ) {
              update(Seeds, NN, q)
            }
          }
        }
      }
    }
    extractCluster(orderedPoints)
  }
}
