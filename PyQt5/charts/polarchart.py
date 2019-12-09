#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
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

from PyQt5.QtChart import (QAreaSeries, QChart, QChartView, QLineSeries,
        QPolarChart, QScatterSeries, QSplineSeries, QValueAxis)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow


class ChartView(QChartView):

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Plus:
            self.chart().zoomIn()
        elif key == Qt.Key_Minus:
            self.chart().zoomOut()
        elif key == Qt.Key_Left:
            self.chart().scroll(-1.0, 0)
        elif key == Qt.Key_Right:
            self.chart().scroll(1.0, 0)
        elif key == Qt.Key_Up:
            self.chart().scroll(0, 1.0)
        elif key == Qt.Key_Down:
            self.chart().scroll(0, -1.0)
        elif key == Qt.Key_Space:
            self.switchChartType()
        else:
            super(ChartView, self).keyPressEvent(event)

    def switchChartType(self):
        oldChart = self.chart()

        if oldChart.chartType() == QChart.ChartTypeCartesian:
            newChart = QPolarChart()
        else:
            newChart = QChart()

        seriesList = oldChart.series()
        axisList = oldChart.axes()
        axisRanges = [(axis.min(), axis.max()) for axis in axisList]

        for series in seriesList:
            oldChart.removeSeries(series)

        for axis in axisList:
            oldChart.removeAxis(axis)
            if isinstance(newChart, QPolarChart):
                newChart.addAxis(axis, QPolarChart.axisPolarOrientation(axis))
            else:
                newChart.addAxis(axis, axis.alignment())

        for series in seriesList:
            newChart.addSeries(series)
            for axis in axisList:
                series.attachAxis(axis)

        for (min, max), axis in zip(axisRanges, axisList):
            axis.setRange(min, max)

        newChart.setTitle(oldChart.title())
        self.setChart(newChart)


app = QApplication(sys.argv)

ANGULAR_MIN = -100
ANGULAR_MAX = 100

RADIAL_MIN = -100
RADIAL_MAX = 100

series1 = QScatterSeries()
series1.setName("scatter")
for i in range(ANGULAR_MIN, ANGULAR_MAX + 1, 10):
    series1.append(i, (float(i) / RADIAL_MAX) * RADIAL_MAX + 8.0)

series2 = QSplineSeries()
series2.setName("spline")
for i in range(ANGULAR_MIN, ANGULAR_MAX + 1, 10):
    series2.append(i, (float(i) / RADIAL_MAX) * RADIAL_MAX)

series3 = QLineSeries()
series3.setName("star outer")
ad = (ANGULAR_MAX - ANGULAR_MIN) / 8.0
rd = (RADIAL_MAX - RADIAL_MIN) / 3.0 * 1.3
series3.append(ANGULAR_MIN, RADIAL_MAX)
series3.append(ANGULAR_MIN + ad*1, RADIAL_MIN + rd)
series3.append(ANGULAR_MIN + ad*2, RADIAL_MAX)
series3.append(ANGULAR_MIN + ad*3, RADIAL_MIN + rd)
series3.append(ANGULAR_MIN + ad*4, RADIAL_MAX)
series3.append(ANGULAR_MIN + ad*5, RADIAL_MIN + rd)
series3.append(ANGULAR_MIN + ad*6, RADIAL_MAX)
series3.append(ANGULAR_MIN + ad*7, RADIAL_MIN + rd)
series3.append(ANGULAR_MIN + ad*8, RADIAL_MAX)

series4 = QLineSeries()
series4.setName("star inner")
ad = (ANGULAR_MAX - ANGULAR_MIN) / 8.0
rd = (RADIAL_MAX - RADIAL_MIN) / 3.0
series4.append(ANGULAR_MIN, RADIAL_MAX)
series4.append(ANGULAR_MIN + ad*1, RADIAL_MIN + rd)
series4.append(ANGULAR_MIN + ad*2, RADIAL_MAX)
series4.append(ANGULAR_MIN + ad*3, RADIAL_MIN + rd)
series4.append(ANGULAR_MIN + ad*4, RADIAL_MAX)
series4.append(ANGULAR_MIN + ad*5, RADIAL_MIN + rd)
series4.append(ANGULAR_MIN + ad*6, RADIAL_MAX)
series4.append(ANGULAR_MIN + ad*7, RADIAL_MIN + rd)
series4.append(ANGULAR_MIN + ad*8, RADIAL_MAX)

series5 = QAreaSeries()
series5.setName("star area")
series5.setUpperSeries(series3)
series5.setLowerSeries(series4)
series5.setOpacity(0.5)

chart = QPolarChart()
chart.addSeries(series1)
chart.addSeries(series2)
chart.addSeries(series3)
chart.addSeries(series4)
chart.addSeries(series5)
chart.setTitle("Use arrow keys to scroll, +/- to zoom, and space to switch chart type.")

angularAxis = QValueAxis()
angularAxis.setTickCount(9)
angularAxis.setLabelFormat('%.1f')
angularAxis.setShadesVisible(True)
angularAxis.setShadesBrush(QBrush(QColor(249, 249, 255)))
chart.addAxis(angularAxis, QPolarChart.PolarOrientationAngular)

radialAxis = QValueAxis()
radialAxis.setTickCount(9)
radialAxis.setLabelFormat('%d')
chart.addAxis(radialAxis, QPolarChart.PolarOrientationRadial)

series1.attachAxis(radialAxis)
series1.attachAxis(angularAxis)
series2.attachAxis(radialAxis)
series2.attachAxis(angularAxis)
series3.attachAxis(radialAxis)
series3.attachAxis(angularAxis)
series4.attachAxis(radialAxis)
series4.attachAxis(angularAxis)
series5.attachAxis(radialAxis)
series5.attachAxis(angularAxis)

radialAxis.setRange(RADIAL_MIN, RADIAL_MAX)
angularAxis.setRange(ANGULAR_MIN, ANGULAR_MAX)

chartView = ChartView()
chartView.setChart(chart)
chartView.setRenderHint(QPainter.Antialiasing)

window = QMainWindow()
window.setCentralWidget(chartView)
window.resize(800, 600)
window.show()

sys.exit(app.exec_())
