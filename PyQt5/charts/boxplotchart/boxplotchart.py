#!/usr/bin/env python3


#############################################################################
##
## Copyright (C) 2014 Riverbank Computing Limited
## Copyright (C) 2013 Digia Plc
## All rights reserved.
##
## This file is part of the examples of PyQtChart.
##
## $QT_BEGIN_LICENSE$
## Licensees holding valid Qt Commercial licenses may use this file in
## accordance with the Qt Commercial License Agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and Digia.
## $QT_END_LICENSE$
##
#############################################################################


import sys

from PyQt5.QtChart import QBoxPlotSeries, QBoxSet, QChart, QChartView
from PyQt5.QtCore import QFile, QFileInfo, Qt, QTextStream
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow


class BoxDataReader(QTextStream):

    def readBox(self):
        line = self.readLine()
        if line.startswith("#"):
            return None

        strList = line.split()
        sortedList = [float(s) for s in strList[1:]]
        sortedList.sort()
        count = len(sortedList)

        box = QBoxSet(strList[0])
        box.setValue(QBoxSet.LowerExtreme, sortedList[0])
        box.setValue(QBoxSet.UpperExtreme, sortedList[-1])
        box.setValue(QBoxSet.Median, self.findMedian(sortedList, 0, count));
        box.setValue(QBoxSet.LowerQuartile,
                self.findMedian(sortedList, 0, count // 2))
        box.setValue(QBoxSet.UpperQuartile,
                self.findMedian(sortedList, count // 2 + (count % 2), count))

        return box

    @staticmethod
    def findMedian(sortedList, begin, end):
        count = end - begin
        if count % 2 != 0:
            return sortedList[count // 2 + begin]

        right = sortedList[count // 2 + begin]
        left = sortedList[count // 2 - 1 + begin]

        return (right + left) / 2.0


app = QApplication(sys.argv)

dataDir = QFileInfo(__file__).absolutePath()

acmeSeries = QBoxPlotSeries()
acmeSeries.setName("Acme Ltd")

boxWhiskSeries = QBoxPlotSeries()
boxWhiskSeries.setName("BoxWhisk Inc")

acmeData = QFile(dataDir + '/acme_data.txt')
if not acmeData.open(QFile.ReadOnly | QFile.Text):
    sys.exit(1)

dataReader = BoxDataReader(acmeData)
while not dataReader.atEnd():
    box = dataReader.readBox()
    if box is not None:
        acmeSeries.append(box)

boxwhiskData = QFile(dataDir + '/boxwhisk_data.txt')
if not boxwhiskData.open(QFile.ReadOnly | QFile.Text):
    sys.exit(1)

dataReader.setDevice(boxwhiskData)
while not dataReader.atEnd():
    box = dataReader.readBox()
    if box is not None:
        boxWhiskSeries.append(box)

chart = QChart()
chart.addSeries(acmeSeries)
chart.addSeries(boxWhiskSeries)
chart.setTitle("Acme Ltd and BoxWhisk Inc share deviation in 2012")
chart.setAnimationOptions(QChart.SeriesAnimations)

chart.createDefaultAxes()
chart.axisY().setMin(15.0)
chart.axisY().setMax(34.0)

chart.legend().setVisible(True)
chart.legend().setAlignment(Qt.AlignBottom)

chartView = QChartView(chart)
chartView.setRenderHint(QPainter.Antialiasing)

window = QMainWindow()
window.setCentralWidget(chartView)
window.resize(800, 600)
window.show()

sys.exit(app.exec_())
