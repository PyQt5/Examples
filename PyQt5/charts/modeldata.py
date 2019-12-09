#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2012 Digia Plc
## All rights reserved.
##
## This file is part of the PyQtChart examples.
##
## $QT_BEGIN_LICENSE$
## Licensees holding valid Qt Commercial licenses may use this file in
## accordance with the Qt Commercial License Agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and Digia.
## $QT_END_LICENSE$
##
#############################################################################


import random

from PyQt5.QtChart import QChart, QChartView, QLineSeries, QVXYModelMapper
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QRect, Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QGridLayout, QHeaderView, QTableView, QWidget


class CustomTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super(CustomTableModel, self).__init__(parent)

        random.seed()

        self.m_columnCount = 4
        self.m_rowCount = 15

        self.m_data = []
        self.m_mapping = {}

        for i in range(self.m_rowCount):
            dataVec = [0] * self.m_columnCount
            for k in range(len(dataVec)):
                if k % 2 == 0:
                    dataVec[k] = i * 50 + random.randint(0, 20)
                else:
                    dataVec[k] = random.randint(0, 100)

            self.m_data.append(dataVec)

    def rowCount(self, parent=QModelIndex()):
        return self.m_rowCount

    def columnCount(self, parent=QModelIndex()):
        return self.m_columnCount

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return "x" if section % 2 == 0 else "y"

        return str(section + 1)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            return self.m_data[row][column]

        if role == Qt.EditRole:
            return float(self.m_data[row][column])

        if role == Qt.BackgroundRole:
            for color, areas in self.m_mapping.items():
                for rect in areas:
                    if rect.contains(column, row):
                        return QColor(color)

            # The cell is not mapped so return white.
            return QColor(Qt.white)

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            column = index.column()

            self.m_data[row][column] = value
            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        return super(CustomTableModel, self).flags(index) | Qt.ItemIsEditable

    def addMapping(self, color, area):
        self.m_mapping.setdefault(color, []).append(area)

    def clearMapping(self):
        self.m_mapping.clear()


class TableWidget(QWidget):

    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)

        # Create a simple model for storing data.
        model = CustomTableModel()

        # Create the table view and add the model to it.
        tableView = QTableView()
        tableView.setModel(model)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        chart = QChart()
        chart.setAnimationOptions(QChart.AllAnimations)

        # Series 1.
        series = QLineSeries()
        series.setName("Line 1")

        mapper = QVXYModelMapper(self)
        mapper.setXColumn(0)
        mapper.setYColumn(1)
        mapper.setSeries(series)
        mapper.setModel(model)
        chart.addSeries(series)

        # Get the color of the series and use it for showing the mapped area.
        seriesColorHex = self._series_color(series)
        model.addMapping(seriesColorHex, QRect(0, 0, 2, model.rowCount()))

        # Series 2.
        series = QLineSeries()
        series.setName("Line 2")

        mapper = QVXYModelMapper(self)
        mapper.setXColumn(2)
        mapper.setYColumn(3)
        mapper.setSeries(series)
        mapper.setModel(model)
        chart.addSeries(series)

        # Get the color of the series and use it for showing the mapped area.
        seriesColorHex = self._series_color(series)
        model.addMapping(seriesColorHex, QRect(2, 0, 2, model.rowCount()))

        chart.createDefaultAxes()
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        chartView.setMinimumSize(640, 480)

        # Create the main layout.
        mainLayout = QGridLayout()
        mainLayout.addWidget(tableView, 1, 0)
        mainLayout.addWidget(chartView, 1, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(0, 0)
        self.setLayout(mainLayout)

    @staticmethod
    def _series_color(series):
        """ Return the colour of a series as a hexadecimal string. """

        color = hex(series.pen().color().rgb()).upper()

        if color.endswith('L'):
            color = color[:-1]

        return '#' + color[-6:]


if __name__ == '__main__':

    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = TableWidget()
    w.show()
    
    sys.exit(app.exec_())
