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


from PyQt5.QtCore import (pyqtSignal, QFile, QFileInfo, QIODevice, QObject,
        QPoint, QSizeF, Qt, QTextStream)
from PyQt5.QtDataVisualization import (Q3DBars, Q3DCamera, Q3DTheme,
        QAbstract3DGraph, QAbstract3DSeries, QBar3DSeries, QBarDataItem,
        QBarDataProxy)
from PyQt5.QtGui import QFont, QGuiApplication


class VariantBarDataProxy(QBarDataProxy):

    def __init__(self, newSet=None, mapping=None):
        super(VariantBarDataProxy, self).__init__()

        self.m_dataSet = None
        self.m_mapping = None

        if newSet is not None:
            self.setDataSet(newSet)

        if mapping is not None:
            self.setMapping(mapping)

    def setDataSet(self, newSet):
        if self.m_dataSet is not None:
            self.m_dataSet.itemsAdded.disconnect(self.handleItemsAdded)
            self.m_dataSet.dataCleared.disconnect(self.handleDataCleared)

        self.m_dataSet = newSet

        if self.m_dataSet is not None:
            self.m_dataSet.itemsAdded.connect(self.handleItemsAdded)
            self.m_dataSet.dataCleared.connect(self.handleDataCleared)

        self.resolveDataSet()

    def dataSet(self):
        return self.m_dataSet

    def setMapping(self, mapping):
        if self.m_mapping is not None:
            self.m_mapping.mappingChanged.disconnect(self.handleMappingChanged)

        self.m_mapping = mapping

        if self.m_mapping is not None:
            self.m_mapping.mappingChanged.connect(self.handleMappingChanged)

        self.resolveDataSet()

    def mapping(self):
        return self.m_mapping

    def handleItemsAdded(self, index, count):
        self.resolveDataSet()

    def handleDataCleared(self):
        self.resetArray(None)

    def handleMappingChanged(self):
        self.resolveDataSet()

    def resolveDataSet(self):
        # If we have no data or mapping, or the categories are not defined,
        # simply clear the array.
        if self.m_dataSet is None or self.m_mapping is None or len(self.m_mapping.rowCategories()) == 0 or len(self.m_mapping.columnCategories()) == 0:
            self.resetArray(None)
            return

        rowIndex = self.m_mapping.rowIndex()
        columnIndex = self.m_mapping.columnIndex()
        valueIndex = self.m_mapping.valueIndex()
        rowList = self.m_mapping.rowCategories()
        columnList = self.m_mapping.columnCategories()

        # Sort values into rows and columns.
        itemValueMap = {}
        for item in self.m_dataSet.itemList():
            columnValueMap = itemValueMap.setdefault(item[rowIndex], {})
            columnValueMap[item[columnIndex]] = item[valueIndex]

        newProxyArray = []
        for rowKey in rowList:
            newProxyRow = []
            for columnKey in columnList:
                newProxyRow.append(
                        QBarDataItem(itemValueMap[rowKey][columnKey]))

            newProxyArray.append(newProxyRow)

        self.resetArray(newProxyArray)


class VariantBarDataMapping(QObject):

    mappingChanged = pyqtSignal()

    def __init__(self, rowIndex=0, columnIndex=1, valueIndex=2, rowCategories=None, columnCategories=None):
        super(VariantBarDataMapping, self).__init__()

        self.m_rowIndex = rowIndex
        self.m_columnIndex = columnIndex
        self.m_valueIndex = valueIndex

        self.m_rowCategories = [] if rowCategories is None else list(rowCategories)
        self.m_columnCategories = [] if columnCategories is None else list(columnCategories)

    def setRowIndex(self, index):
        self.m_rowIndex = index
        self.mappingChanged.emit()

    def rowIndex(self):
        return self.m_rowIndex

    def setColumnIndex(self, index):
        self.m_columnIndex = index
        self.mappingChanged.emit()

    def columnIndex(self):
        return self.m_columnIndex

    def setValueIndex(self, index):
        self.m_valueIndex = index
        self.mappingChanged.emit()

    def valueIndex(self):
        return self.m_valueIndex

    def setRowCategories(self, categories):
        self.m_rowCategories[:] = categories
        self.mappingChanged.emit()

    def rowCategories(self):
        return self.m_rowCategories

    def setColumnCategories(self, categories):
        self.m_columnCategories[:] = categories
        self.mappingChanged.emit()

    def columnCategories(self):
        return self.m_columnCategories

    def remap(sefl, rowIndex, columnIndex, valueIndex, rowCategories, columnCategories):
        self.m_rowIndex = rowIndex
        self.m_columnIndex = columnIndex
        self.m_valueIndex = valueIndex
        self.m_rowCategories[:] = rowCategories
        self.m_columnCategories[:] = columnCategories
        self.mappingChanged.emit()


class VariantDataSet(QObject):

    itemsAdded = pyqtSignal(int, int)
    dataCleared = pyqtSignal()

    def __init__(self):
        super(VariantDataSet, self).__init__()

        self.m_variantData = []

    def clear(self):
        del self.m_variantData[:]
        self.dataCleared.emit()

    def addItem(self, item):
        addIndex = len(self.m_variantData)
        self.m_variantData.append(item)

        self.itemsAdded.emit(addIndex, 1)

        return addIndex

    def addItems(self, itemList):
        addIndex = len(self.m_variantData)
        newCount = len(itemList)

        self.m_variantData += itemList

        self.itemsAdded.emit(addIndex, newCount)

        return addIndex

    def itemList(self):
        return self.m_variantData


class RainfallGraph(QObject):

    months = ("January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December")

    def __init__(self, rainfall):
        super(RainfallGraph, self).__init__()

        self.m_graph = rainfall

        self.m_mapping = None
        self.m_dataSet = None

        # In the data file the months are in numeric format, so create a custom
        # list.
        self.m_numericMonths = [str(m) for m in range(1, 12 + 1)]
        self.m_columnCount = len(self.m_numericMonths)

        self.m_years = [str(y) for y in range(2000, 2012 + 1)]
        self.m_rowCount = len(self.m_years)

        self.m_proxy = VariantBarDataProxy()
        series = QBar3DSeries(self.m_proxy)
        series.setMesh(QAbstract3DSeries.MeshCylinder)
        self.m_graph.addSeries(series)

        self.m_graph.setBarThickness(1.0)
        self.m_graph.setBarSpacing(QSizeF(0.2, 0.2))

        self.m_graph.rowAxis().setTitle("Year")
        self.m_graph.columnAxis().setTitle("Month")
        self.m_graph.valueAxis().setTitle("rainfall")
        self.m_graph.valueAxis().setLabelFormat("%d mm")
        self.m_graph.valueAxis().setSegmentCount(5)
        self.m_graph.rowAxis().setLabels(self.m_years)
        self.m_graph.columnAxis().setLabels(self.months)

        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualityMedium)

        self.m_graph.setSelectionMode(
                QAbstract3DGraph.SelectionItemAndColumn |
                QAbstract3DGraph.SelectionSlice)

        self.m_graph.activeTheme().setType(Q3DTheme.ThemeArmyBlue)
        self.m_graph.activeTheme().setFont(QFont('Century Gothic', 30))
        self.m_graph.activeTheme().setLabelBackgroundEnabled(False)

        self.m_graph.scene().activeCamera().setCameraPreset(
                Q3DCamera.CameraPresetIsometricRightHigh)

        self.m_graph.setTitle("Monthly rainfall in Northern Finland")

    def start(self):
        self.addDataSet()

    def addDataSet(self):
        self.m_dataSet = VariantDataSet()
        itemList = []

        stream = QTextStream()
        dataFile = QFile(QFileInfo(__file__).absolutePath() + '/raindata.txt')
        if dataFile.open(QIODevice.ReadOnly | QIODevice.Text):
            stream.setDevice(dataFile)
            while not stream.atEnd():
                line = stream.readLine()
                if line.startswith('#'):
                    continue

                # Each line has three data items: year, month, and rainfall
                # values.
                strList = line.split(',')
                if len(strList) < 3:
                    continue

                # Store year and month as strings, and rainfall value as a
                # float into a tuple and add the tupe to the item list.
                newItem = (strList[0].strip(), strList[1].strip(),
                        float(strList[2]))
                itemList.append(newItem)

        self.m_dataSet.addItems(itemList)
        self.m_proxy.setDataSet(self.m_dataSet)

        self.m_mapping = VariantBarDataMapping(rowCategories=self.m_years,
                columnCategories=self.m_numericMonths)
        self.m_proxy.setMapping(self.m_mapping)


if __name__ == '__main__':

    import sys

    app = QGuiApplication(sys.argv)

    rainfall = Q3DBars()
    rainfall.setFlags(rainfall.flags() ^ Qt.FramelessWindowHint)
    rainfall.resize(1000, 800)
    rainfall.setPosition(QPoint(10, 30))
    rainfall.show()

    rainfallgraph = RainfallGraph(rainfall)
    rainfallgraph.start()

    sys.exit(app.exec_())
