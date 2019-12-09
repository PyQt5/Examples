#!/usr/bin/env python3


#############################################################################
##
## Copyright (C) 2014 Riverbank Computing Limited.
## Copyright (C) 2014 Digia Plc
## All rights reserved.
## For any questions to Digia, please use contact form at http://qt.digia.com
##
## This file is part of the QtDataVisualization module.
##
## Licensees holding valid Qt Enterprise licenses may use this file in
## accordance with the Qt Enterprise License Agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and Digia.
##
## If you have questions regarding the use of this file, please use
## contact form at http://qt.digia.com
##
#############################################################################


from PyQt5.QtCore import QObject, QPoint, QSize, QSizeF, Qt, QTimer
from PyQt5.QtDataVisualization import (Q3DBars, Q3DCamera, Q3DTheme,
        QAbstract3DGraph, QAbstract3DSeries, QBar3DSeries,
        QItemModelBarDataProxy)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QSizePolicy, QTableWidget,
        QVBoxLayout, QWidget)


class GraphDataGenerator(QObject):

    def __init__(self, bargraph, tableWidget):
        super(GraphDataGenerator, self).__init__()

        self.m_graph = bargraph
        self.m_tableWidget = tableWidget

        self.m_graph.setBarThickness(1.0)
        self.m_graph.setBarSpacing(QSizeF(0.2, 0.2))

        self.m_graph.setSelectionMode(
                QAbstract3DGraph.SelectionItemAndRow |
                QAbstract3DGraph.SelectionSlice)

        self.m_graph.activeTheme().setType(Q3DTheme.ThemeDigia)
        self.m_graph.activeTheme().setFont(QFont('Impact', 20))

        self.m_graph.scene().activeCamera().setCameraPreset(
                Q3DCamera.CameraPresetFront)

    def start(self):
        self.setupModel()

        # The table needs to be shown before the size of its headers can be
        # accurately obtained so we postpone it a bit.
        QTimer.singleShot(100, self.fixTableSize)

    def setupModel(self):
        days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")

        weeks = ("week 1", "week 2", "week 3", "week 4", "week 5")

        #         Mon  Tue  Wed  Thu  Fri  Sat  Sun
        hours = ((2.0, 1.0, 3.0, 0.2, 1.0, 5.0, 10.0),  # week 1
                 (0.5, 1.0, 3.0, 1.0, 2.0, 2.0, 3.0),   # week 2
                 (1.0, 1.0, 2.0, 1.0, 4.0, 4.0, 4.0),   # week 3
                 (0.0, 1.0, 0.0, 0.0, 2.0, 2.0, 0.3),   # week 4
                 (3.0, 3.0, 6.0, 2.0, 2.0, 1.0, 1.0))   # week 5

        self.m_graph.rowAxis().setTitle("Week of year")
        self.m_graph.columnAxis().setTitle("Day of week")
        self.m_graph.valueAxis().setTitle("Hours spent on the Internet")
        self.m_graph.valueAxis().setLabelFormat("%.1f h")

        self.m_tableWidget.setRowCount(len(weeks))
        self.m_tableWidget.setColumnCount(len(days))
        self.m_tableWidget.setHorizontalHeaderLabels(days)
        self.m_tableWidget.setVerticalHeaderLabels(weeks)
        self.m_tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.m_tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.m_tableWidget.setCurrentCell(-1, -1)

        model = self.m_tableWidget.model()

        for week in range(len(weeks)):
            for day in range(len(days)):
                index = model.index(week, day)
                model.setData(index, hours[week][day])

    def selectFromTable(self, selection):
        self.m_tableWidget.setFocus()
        self.m_tableWidget.setCurrentCell(selection.x(), selection.y())

    def selectedFromTable(self, currentRow, currentColumn, previousRow, previousColumn):
        self.m_graph.seriesList()[0].setSelectedBar(
                QPoint(currentRow, currentColumn))

    def fixTableSize(self):
        width = self.m_tableWidget.horizontalHeader().length()
        width += self.m_tableWidget.verticalHeader().width()
        self.m_tableWidget.setFixedWidth(width + 2)

        height = self.m_tableWidget.verticalHeader().length()
        height += self.m_tableWidget.horizontalHeader().height()
        self.m_tableWidget.setFixedHeight(height + 2)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    graph = Q3DBars()
    container = QWidget.createWindowContainer(graph)

    screenSize = graph.screen().size()
    container.setMinimumSize(
            QSize(screenSize.width() / 2, screenSize.height() / 2))
    container.setMaximumSize(screenSize)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    container.setFocusPolicy(Qt.StrongFocus)

    widget = QWidget()
    layout = QVBoxLayout(widget)
    tableWidget = QTableWidget()
    layout.addWidget(container, 1)
    layout.addWidget(tableWidget, 1, Qt.AlignHCenter)

    tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    tableWidget.setAlternatingRowColors(True)

    widget.setWindowTitle("Hours spent on the Internet")

    # Since we are dealing with QTableWidget, the model will already have data
    # sorted properly into rows and columns, so we simply set the
    # useModelCategories property to True to utilise this.
    proxy = QItemModelBarDataProxy(tableWidget.model())
    proxy.setUseModelCategories(True)

    series = QBar3DSeries(proxy)
    series.setMesh(QAbstract3DSeries.MeshPyramid)
    graph.addSeries(series)

    generator = GraphDataGenerator(graph, tableWidget)
    series.selectedBarChanged.connect(generator.selectFromTable)
    tableWidget.currentCellChanged.connect(generator.selectedFromTable)

    widget.show()
    generator.start()
    sys.exit(app.exec_())
