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


import math

from PyQt5.QtCore import QFileInfo, QObject, QSize, Qt
from PyQt5.QtDataVisualization import (Q3DSurface, Q3DTheme, QAbstract3DGraph,
        QHeightMapSurfaceDataProxy, QSurface3DSeries, QSurfaceDataItem,
        QSurfaceDataProxy, QValue3DAxis)
from PyQt5.QtGui import (QBrush, QIcon, QImage, QLinearGradient, QPainter,
        QPixmap, QVector3D)
from PyQt5.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
        QLabel, QPushButton, QRadioButton, QSizePolicy, QSlider, QVBoxLayout,
        QWidget)


class SurfaceGraph(QObject):

    sampleCountX = 50
    sampleCountZ = 50
    heightMapGridStepX = 6
    heightMapGridStepZ = 6
    sampleMin = -8.0
    sampleMax = 8.0

    def __init__(self, surface):
        super(SurfaceGraph, self).__init__()

        self.m_graph = surface
        self.m_graph.setAxisX(QValue3DAxis())
        self.m_graph.setAxisY(QValue3DAxis())
        self.m_graph.setAxisZ(QValue3DAxis())

        self.m_sqrtSinProxy = QSurfaceDataProxy()
        self.m_sqrtSinSeries = QSurface3DSeries(self.m_sqrtSinProxy)
        self.fillSqrtSinProxy()

        heightMapImage = QImage(
                QFileInfo(__file__).absolutePath() + '/mountain.png')
        self.m_heightMapProxy = QHeightMapSurfaceDataProxy(heightMapImage)
        self.m_heightMapSeries = QSurface3DSeries(self.m_heightMapProxy)
        self.m_heightMapSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self.m_heightMapProxy.setValueRanges(34.0, 40.0, 18.0, 24.0)
        self.m_heightMapWidth = heightMapImage.width()
        self.m_heightMapHeight = heightMapImage.height()

        self.m_axisMinSliderX = None
        self.m_axisMaxSliderX = None
        self.m_axisMinSliderZ = None
        self.m_axisMaxSliderZ = None
        self.m_rangeMinX = 0.0
        self.m_rangeMinZ = 0.0
        self.m_stepX = 0.0
        self.m_stepZ = 0.0

    def fillSqrtSinProxy(self):
        stepX = (self.sampleMax - self.sampleMin) / (self.sampleCountX - 1)
        stepZ = (self.sampleMax - self.sampleMin) / (self.sampleCountZ - 1)

        dataArray = []
        for i in range(self.sampleCountZ):

            # Keep values within range bounds, since just adding step can cause
            # minor drift due to the rounding errors.
            z = min(self.sampleMax, (i * stepZ + self.sampleMin))
            newRow = []
            for j in range(self.sampleCountX):
                x = min(self.sampleMax, (j * stepX + self.sampleMin))
                R = math.sqrt(z * z + x * x) + 0.01
                y = (math.sin(R) / R + 0.24) * 1.61

                newRow.append(QSurfaceDataItem(QVector3D(x, y, z)))

            dataArray.append(newRow)

        self.m_sqrtSinProxy.resetArray(dataArray)

    def toggleModeNone(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    def toggleModeItem(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    def toggleModeSliceRow(self):
        self.m_graph.setSelectionMode(
                QAbstract3DGraph.SelectionItemAndRow |
                QAbstract3DGraph.SelectionSlice)

    def toggleModeSliceColumn(self):
        self.m_graph.setSelectionMode(
                QAbstract3DGraph.SelectionItemAndColumn |
                QAbstract3DGraph.SelectionSlice)

    def setAxisMinSliderX(self, slider):
        self.m_axisMinSliderX = slider

    def setAxisMaxSliderX(self, slider):
        self.m_axisMaxSliderX = slider

    def setAxisMinSliderZ(self, slider):
        self.m_axisMinSliderZ = slider

    def setAxisMaxSliderZ(self, slider):
        self.m_axisMaxSliderZ = slider

    def enableSqrtSinModel(self, enable):
        if not enable:
            return

        self.m_sqrtSinSeries.setDrawMode(
                QSurface3DSeries.DrawSurfaceAndWireframe)
        self.m_sqrtSinSeries.setFlatShadingEnabled(True)

        self.m_graph.axisX().setLabelFormat("%.2f")
        self.m_graph.axisZ().setLabelFormat("%.2f")
        self.m_graph.axisX().setRange(self.sampleMin, self.sampleMax)
        self.m_graph.axisY().setRange(0.0, 2.0)
        self.m_graph.axisZ().setRange(self.sampleMin, self.sampleMax)
        self.m_graph.axisX().setLabelAutoRotation(30)
        self.m_graph.axisY().setLabelAutoRotation(90)
        self.m_graph.axisZ().setLabelAutoRotation(30)

        self.m_graph.removeSeries(self.m_heightMapSeries)
        self.m_graph.addSeries(self.m_sqrtSinSeries)

        self.m_rangeMinX = self.sampleMin
        self.m_rangeMinZ = self.sampleMin
        self.m_stepX = (self.sampleMax - self.sampleMin) / (self.sampleCountX - 1)
        self.m_stepZ = (self.sampleMax - self.sampleMin) / (self.sampleCountZ - 1)
        self.m_axisMinSliderX.setMaximum(self.sampleCountX - 2)
        self.m_axisMinSliderX.setValue(0)
        self.m_axisMaxSliderX.setMaximum(self.sampleCountX - 1)
        self.m_axisMaxSliderX.setValue(self.sampleCountX - 1)
        self.m_axisMinSliderZ.setMaximum(self.sampleCountZ - 2)
        self.m_axisMinSliderZ.setValue(0)
        self.m_axisMaxSliderZ.setMaximum(self.sampleCountZ - 1)
        self.m_axisMaxSliderZ.setValue(self.sampleCountZ - 1)

    def enableHeightMapModel(self, enable):
        if not enable:
            return

        self.m_heightMapSeries.setDrawMode(QSurface3DSeries.DrawSurface)
        self.m_heightMapSeries.setFlatShadingEnabled(False)

        self.m_graph.axisX().setLabelFormat("%.1f N")
        self.m_graph.axisZ().setLabelFormat("%.1f E")
        self.m_graph.axisX().setRange(34.0, 40.0)
        self.m_graph.axisY().setAutoAdjustRange(True)
        self.m_graph.axisZ().setRange(18.0, 24.0)

        self.m_graph.axisX().setTitle("Latitude")
        self.m_graph.axisY().setTitle("Height")
        self.m_graph.axisZ().setTitle("Longitude")

        self.m_graph.removeSeries(self.m_sqrtSinSeries)
        self.m_graph.addSeries(self.m_heightMapSeries)

        mapGridCountX = self.m_heightMapWidth // self.heightMapGridStepX
        mapGridCountZ = self.m_heightMapHeight // self.heightMapGridStepZ
        self.m_rangeMinX = 34.0
        self.m_rangeMinZ = 18.0
        self.m_stepX = 6.0 / (mapGridCountX - 1)
        self.m_stepZ = 6.0 / (mapGridCountZ - 1)
        self.m_axisMinSliderX.setMaximum(mapGridCountX - 2)
        self.m_axisMinSliderX.setValue(0)
        self.m_axisMaxSliderX.setMaximum(mapGridCountX - 1)
        self.m_axisMaxSliderX.setValue(mapGridCountX - 1)
        self.m_axisMinSliderZ.setMaximum(mapGridCountZ - 2)
        self.m_axisMinSliderZ.setValue(0)
        self.m_axisMaxSliderZ.setMaximum(mapGridCountZ - 1)
        self.m_axisMaxSliderZ.setValue(mapGridCountZ - 1)

    def adjustXMin(self, min):
        minX = self.m_stepX * min + self.m_rangeMinX

        max = self.m_axisMaxSliderX.value()
        if min >= max:
            max = min + 1
            self.m_axisMaxSliderX.setValue(max)

        maxX = self.m_stepX * max + self.m_rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustXMax(self, max):
        maxX = self.m_stepX * max + self.m_rangeMinX

        min = self.m_axisMinSliderX.value()
        if max <= min:
            min = max - 1
            self.m_axisMinSliderX.setValue(min)

        minX = self.m_stepX * min + self.m_rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustZMin(self, min):
        minZ = self.m_stepZ * min + self.m_rangeMinZ

        max = self.m_axisMaxSliderZ.value()
        if min >= max:
            max = min + 1
            self.m_axisMaxSliderZ.setValue(max)

        maxZ = self.m_stepZ * max + self.m_rangeMinZ

        self.setAxisZRange(minZ, maxZ)

    def adjustZMax(self, max):
        maxZ = self.m_stepZ * max + self.m_rangeMinZ

        min = self.m_axisMinSliderZ.value()
        if max <= min:
            min = max - 1
            self.m_axisMinSliderZ.setValue(min)

        minZ = self.m_stepZ * min + self.m_rangeMinZ

        self.setAxisZRange(minZ, maxZ)

    def setAxisXRange(self, min, max):
        self.m_graph.axisX().setRange(min, max)

    def setAxisZRange(self, min, max):
        self.m_graph.axisZ().setRange(min, max)

    def changeTheme(self, theme):
        self.m_graph.activeTheme().setType(Q3DTheme.Theme(theme))

    def setBlackToYellowGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        self.m_graph.seriesList()[0].setBaseGradient(gr)
        self.m_graph.seriesList()[0].setColorStyle(
                Q3DTheme.ColorStyleRangeGradient)

    def setGreenToRedGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkGreen)
        gr.setColorAt(0.5, Qt.yellow)
        gr.setColorAt(0.8, Qt.red)
        gr.setColorAt(1.0, Qt.darkRed)

        self.m_graph.seriesList()[0].setBaseGradient(gr)
        self.m_graph.seriesList()[0].setColorStyle(
                Q3DTheme.ColorStyleRangeGradient)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    graph = Q3DSurface()
    container = QWidget.createWindowContainer(graph)

    screenSize = graph.screen().size()
    container.setMinimumSize(
            QSize(screenSize.width() / 2, screenSize.height() / 1.6))
    container.setMaximumSize(screenSize)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    container.setFocusPolicy(Qt.StrongFocus)

    widget = QWidget()
    hLayout = QHBoxLayout(widget)
    vLayout = QVBoxLayout()
    hLayout.addWidget(container, 1)
    hLayout.addLayout(vLayout)
    vLayout.setAlignment(Qt.AlignTop)

    widget.setWindowTitle("Surface example")

    modelGroupBox = QGroupBox("Model")

    sqrtSinModelRB = QRadioButton("Sqrt && Sin")
    heightMapModelRB = QRadioButton("Height Map")

    modelVBox = QVBoxLayout()
    modelVBox.addWidget(sqrtSinModelRB)
    modelVBox.addWidget(heightMapModelRB)
    modelGroupBox.setLayout(modelVBox)

    selectionGroupBox = QGroupBox("Selection Mode")

    modeNoneRB = QRadioButton("No selection")
    modeItemRB = QRadioButton("Item")
    modeSliceRowRB = QRadioButton("Row Slice")
    modeSliceColumnRB = QRadioButton("Column Slice")

    selectionVBox = QVBoxLayout()
    selectionVBox.addWidget(modeNoneRB)
    selectionVBox.addWidget(modeItemRB)
    selectionVBox.addWidget(modeSliceRowRB)
    selectionVBox.addWidget(modeSliceColumnRB)
    selectionGroupBox.setLayout(selectionVBox)

    axisMinSliderX = QSlider(Qt.Horizontal, minimum=0, tickInterval=1)
    axisMaxSliderX = QSlider(Qt.Horizontal, minimum=1, tickInterval=1)
    axisMinSliderZ = QSlider(Qt.Horizontal, minimum=0, tickInterval=1)
    axisMaxSliderZ = QSlider(Qt.Horizontal, minimum=1, tickInterval=1)

    themeList = QComboBox()
    themeList.addItem("Qt")
    themeList.addItem("Primary Colors")
    themeList.addItem("Digia")
    themeList.addItem("Stone Moss")
    themeList.addItem("Army Blue")
    themeList.addItem("Retro")
    themeList.addItem("Ebony")
    themeList.addItem("Isabelle")

    colorGroupBox = QGroupBox("Custom gradient")

    grBtoY = QLinearGradient(0, 0, 1, 100)
    grBtoY.setColorAt(1.0, Qt.black)
    grBtoY.setColorAt(0.67, Qt.blue)
    grBtoY.setColorAt(0.33, Qt.red)
    grBtoY.setColorAt(0.0, Qt.yellow)
    pm = QPixmap(24, 100)
    pmp = QPainter(pm)
    pmp.setBrush(QBrush(grBtoY))
    pmp.setPen(Qt.NoPen)
    pmp.drawRect(0, 0, 24, 100)
    gradientBtoYPB = QPushButton()
    gradientBtoYPB.setIcon(QIcon(pm))
    gradientBtoYPB.setIconSize(QSize(24, 100))

    grGtoR = QLinearGradient(0, 0, 1, 100)
    grGtoR.setColorAt(1.0, Qt.darkGreen)
    grGtoR.setColorAt(0.5, Qt.yellow)
    grGtoR.setColorAt(0.2, Qt.red)
    grGtoR.setColorAt(0.0, Qt.darkRed)
    pmp.setBrush(QBrush(grGtoR))
    pmp.drawRect(0, 0, 24, 100)
    gradientGtoRPB = QPushButton()
    gradientGtoRPB.setIcon(QIcon(pm))
    gradientGtoRPB.setIconSize(QSize(24, 100))

    colorHBox = QHBoxLayout()
    colorHBox.addWidget(gradientBtoYPB)
    colorHBox.addWidget(gradientGtoRPB)
    colorGroupBox.setLayout(colorHBox)

    vLayout.addWidget(modelGroupBox)
    vLayout.addWidget(selectionGroupBox)
    vLayout.addWidget(QLabel("Column range"))
    vLayout.addWidget(axisMinSliderX)
    vLayout.addWidget(axisMaxSliderX)
    vLayout.addWidget(QLabel("Row range"))
    vLayout.addWidget(axisMinSliderZ)
    vLayout.addWidget(axisMaxSliderZ)
    vLayout.addWidget(QLabel("Theme"))
    vLayout.addWidget(themeList)
    vLayout.addWidget(colorGroupBox)

    widget.show()

    modifier = SurfaceGraph(graph)

    heightMapModelRB.toggled.connect(modifier.enableHeightMapModel)
    sqrtSinModelRB.toggled.connect(modifier.enableSqrtSinModel)
    modeNoneRB.toggled.connect(modifier.toggleModeNone)
    modeItemRB.toggled.connect(modifier.toggleModeItem)
    modeSliceRowRB.toggled.connect(modifier.toggleModeSliceRow)
    modeSliceColumnRB.toggled.connect(modifier.toggleModeSliceColumn)
    axisMinSliderX.valueChanged.connect(modifier.adjustXMin)
    axisMaxSliderX.valueChanged.connect(modifier.adjustXMax)
    axisMinSliderZ.valueChanged.connect(modifier.adjustZMin)
    axisMaxSliderZ.valueChanged.connect(modifier.adjustZMax)
    themeList.currentIndexChanged.connect(modifier.changeTheme)
    gradientBtoYPB.pressed.connect(modifier.setBlackToYellowGradient)
    gradientGtoRPB.pressed.connect(modifier.setGreenToRedGradient)

    modifier.setAxisMinSliderX(axisMinSliderX)
    modifier.setAxisMaxSliderX(axisMaxSliderX)
    modifier.setAxisMinSliderZ(axisMinSliderZ)
    modifier.setAxisMaxSliderZ(axisMaxSliderZ)

    sqrtSinModelRB.setChecked(True)
    modeItemRB.setChecked(True)
    themeList.setCurrentIndex(2)

    sys.exit(app.exec_())
