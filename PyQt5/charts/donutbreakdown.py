#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2012 Digia Plc
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


from PyQt5.QtChart import QChart, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class DonutBreakdownChart(QChart):

    def __init__(self, parent=None):
        super(DonutBreakdownChart, self).__init__(parent)

        self.mainSeries = QPieSeries()
        self.mainSeries.setPieSize(0.7)
        self.addSeries(self.mainSeries)

    def addBreakdownSeries(self, series, color):
        # Add breakdown series as a slice to center pie.
        slice = self.mainSeries.append(series.name(), series.sum())

        # Customize the slice.
        slice.setBrush(color)
        slice.setLabelVisible()
        slice.setLabelColor(Qt.white)
        slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)

        # Position and customize the breakdown series.
        series.setPieSize(0.8)
        series.setHoleSize(0.7)
        series.setLabelsVisible()

        color = QColor(color)

        for slice in series.slices():
            color = color.lighter(115)
            slice.setBrush(color)
            slice.setLabelFont(QFont("Arial", 8))

        # Add the series to the chart.
        self.addSeries(series)

        # Recalculate breakdown donut segments.
        self.recalculateAngles()

    def recalculateAngles(self):
        angle = 0.0

        for slice in self.mainSeries.slices():
            series = self.find(slice.label())
            if series is not None:
                series.setPieStartAngle(angle)
                angle += slice.percentage() * 360.0
                series.setPieEndAngle(angle)

    def find(self, seriesName):
        for series in self.series():
            if isinstance(series, QPieSeries) and series.name() == seriesName:
                return series

        return None


if __name__ == '__main__':
    import sys

    from PyQt5.QtChart import QChartView
    from PyQt5.QtGui import QPainter
    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    series1 = QPieSeries()
    series1.setName("Fossil fuels")
    series1.append("Oil", 353295)
    series1.append("Coal", 188500)
    series1.append("Natural gas", 148680)
    series1.append("Peat", 94545)

    series2 = QPieSeries()
    series2.setName("Renewables")
    series2.append("Wood fuels", 319663)
    series2.append("Hydro power", 45875)
    series2.append("Wind power", 1060)

    series3 = QPieSeries()
    series3.setName("Others")
    series3.append("Nuclear energy", 238789)
    series3.append("Import energy", 37802)
    series3.append("Other", 32441)

    donutBreakdown = DonutBreakdownChart()
    donutBreakdown.setAnimationOptions(QChart.AllAnimations)
    donutBreakdown.setTitle("Total consumption of energy in Finland 2010")
    donutBreakdown.legend().setVisible(False)
    donutBreakdown.addBreakdownSeries(series1, Qt.red)
    donutBreakdown.addBreakdownSeries(series2, Qt.darkGreen)
    donutBreakdown.addBreakdownSeries(series3, Qt.darkBlue)

    chartView = QChartView(donutBreakdown)
    chartView.setRenderHint(QPainter.Antialiasing)

    window = QMainWindow()
    window.setCentralWidget(chartView)
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec_())
