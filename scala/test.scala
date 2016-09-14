/**
 * Created by ASUS-PC on 2016/9/6.
 */
import math._
import java.io._
import scala.io._
import org.apache.spark.{SparkConf,SparkContext}

object test {

  def readFile(path:String): Array[Vector[Double]] = {
    Source.fromFile(path).getLines().map(_.split(",").map(_.toDouble).toVector).toArray
  }

  def main (args: Array[String]): Unit = {
//    val conf = new SparkConf().setAppName("SVMWithSGDExample").setMaster("local[*]")
//    val sc = new SparkContext(conf)
//    sc.setLogLevel("ERROR")
//    sc.setCheckpointDir("checkpoint")
//
//    val points = readFile("CES.txt")
//    val minPts: Int = 3
//    val radius: Double = 1000
//    val distanceType : String = "EuclideanDistance"
//
//    val _pointsRDD = new ParallelOptics(minPts = minPts, radius = radius, distanceType = distanceType).run(sc.parallelize(points))
//    val processedPoints = points.zip(_pointsRDD.collect())
//
//    processedPoints.take(30).foreach(row => println(row._2.getP.opticsId, row._2.getP.reachDis))
    val raw =  readFile("CES.txt")
    val points = raw.map(_.map(log))
    val minPts: Long = 2.toLong
    val epsilon: Double = 0.02
    val clustering = new Optics(epsilon, minPts, points)
    val t0 = System.nanoTime()
    val processedPoints = clustering.run()
    val t1 = System.nanoTime()
    println("Done in "+(t1-t0)+"ns")

    val file = new File("clusters")
    val bw = new BufferedWriter(new FileWriter(file))
    processedPoints.sortBy(_.id).foreach(p => bw.write(p.id.toString + ", " + p.clusterId.toString+ ", " + p.reachDist.toString+'\n'))
    bw.close()

  }
}
