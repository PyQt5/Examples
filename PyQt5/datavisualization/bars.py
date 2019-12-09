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


from PyQt5.QtCore import pyqtSignal, QObject, QSize, Qt
from PyQt5.QtDataVisualization import (Q3DBars, Q3DCamera, Q3DTheme,
        QAbstract3DGraph, QAbstract3DSeries, QBar3DSeries, QBarDataItem,
        QCategory3DAxis, QValue3DAxis)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QFontComboBox,
        QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QVBoxLayout,
        QWidget)


class GraphModifier(QObject):

    tempOulu = (
        (-6.7, -11.7, -9.7, 3.3, 9.2, 14.0, 16.3, 17.8, 10.2, 2.1, -2.6, -0.3),
        (-6.8, -13.3, 0.2, 1.5, 7.9, 13.4, 16.1, 15.5, 8.2, 5.4, -2.6, -0.8),
        (-4.2, -4.0, -4.6, 1.9, 7.3, 12.5, 15.0, 12.8, 7.6, 5.1, -0.9, -1.3),
        (-7.8, -8.8, -4.2, 0.7, 9.3, 13.2, 15.8, 15.5, 11.2, 0.6, 0.7, -8.4),
        (-14.4, -12.1, -7.0, 2.3, 11.0, 12.6, 18.8, 13.8, 9.4, 3.9, -5.6, -13.0),
        (-9.0, -15.2, -3.8, 2.6, 8.3, 15.9, 18.6, 14.9, 11.1, 5.3, 1.8, -0.2),
        (-8.7, -11.3, -2.3, 0.4, 7.5, 12.2, 16.4, 14.1, 9.2, 3.1, 0.3, -12.1),
        (-7.9, -5.3, -9.1, 0.8, 11.6, 16.6, 15.9, 15.5, 11.2, 4.0, 0.1, -1.9)
    )

    tempHelsinki = (
        (-3.7, -7.8, -5.4, 3.4, 10.7, 15.4, 18.6, 18.7, 14.3, 8.5, 2.9, 4.1),
        (-1.2, -7.5, 3.1, 5.5, 10.3, 15.9, 17.4, 17.9, 11.2, 7.3, 1.1, 0.5),
        (-0.6, 1.2, 0.2, 6.3, 10.2, 13.8, 18.1, 15.1, 10.1, 9.4, 2.5, 0.4),
        (-2.9, -3.5, -0.9, 4.7, 10.9, 14.0, 17.4, 16.8, 13.2, 4.1, 2.6, -2.3),
        (-10.2, -8.0, -1.9, 6.6, 11.3, 14.5, 21.0, 18.8, 12.6, 6.1, -0.5, -7.3),
        (-4.4, -9.1, -2.0, 5.5, 9.9, 15.6, 20.8, 17.8, 13.4, 8.9, 3.6, 1.5),
        (-3.5, -3.2, -0.7, 4.0, 11.1, 13.4, 17.3, 15.8, 13.1, 6.4, 4.1, -5.1),
        (-4.8, -1.8, -5.0, 2.9, 12.8, 17.2, 18.0, 17.1, 12.5, 7.5, 4.5, 2.3)
    )

    months = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    )

    years = ("2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013")

    shadowQualityChanged = pyqtSignal(int)
    backgroundEnabledChanged = pyqtSignal(bool)
    gridEnabledChanged = pyqtSignal(bool)
    fontChanged = pyqtSignal(QFont)
    fontSizeChanged = pyqtSignal(int)

    def __init__(self, bargraph):
        super(GraphModifier, self).__init__()

        self.m_graph = bargraph

        self.m_xRotation = 0.0
        self.m_yRotation = 0.0
        self.m_fontSize = 30
        self.m_segments = 4
        self.m_subSegments = 3
        self.m_minval = -20.0
        self.m_maxval = 20.0
        self.m_temperatureAxis = QValue3DAxis()
        self.m_yearAxis = QCategory3DAxis()
        self.m_monthAxis = QCategory3DAxis()
        self.m_primarySeries = QBar3DSeries()
        self.m_secondarySeries = QBar3DSeries()
        self.m_barMesh = QAbstract3DSeries.MeshBevelBar
        self.m_smooth = False

        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftMedium)
        self.m_graph.activeTheme().setBackgroundEnabled(False)
        self.m_graph.activeTheme().setFont(
                QFont('Times New Roman', self.m_fontSize))
        self.m_graph.activeTheme().setLabelBackgroundEnabled(True)
        self.m_graph.setMultiSeriesUniform(True)

        self.m_temperatureAxis.setTitle("Average temperature")
        self.m_temperatureAxis.setSegmentCount(self.m_segments)
        self.m_temperatureAxis.setSubSegmentCount(self.m_subSegments)
        self.m_temperatureAxis.setRange(self.m_minval, self.m_maxval)
        self.m_temperatureAxis.setLabelFormat(u"%.1f \N{degree sign}C")

        self.m_yearAxis.setTitle("Year")
        self.m_monthAxis.setTitle("Month")

        self.m_graph.setValueAxis(self.m_temperatureAxis)
        self.m_graph.setRowAxis(self.m_yearAxis)
        self.m_graph.setColumnAxis(self.m_monthAxis)

        self.m_primarySeries.setItemLabelFormat(
                "Oulu - @colLabel @rowLabel: @valueLabel")
        self.m_primarySeries.setMesh(QAbstract3DSeries.MeshBevelBar)
        self.m_primarySeries.setMeshSmooth(False)

        self.m_secondarySeries.setItemLabelFormat(
                "Helsinki - @colLabel @rowLabel: @valueLabel")
        self.m_secondarySeries.setMesh(QAbstract3DSeries.MeshBevelBar)
        self.m_secondarySeries.setMeshSmooth(False)
        self.m_secondarySeries.setVisible(False)

        self.m_graph.addSeries(self.m_primarySeries)
        self.m_graph.addSeries(self.m_secondarySeries)

        self.m_preset = Q3DCamera.CameraPresetFront
        self.changePresetCamera()

        self.resetTemperatureData()

    def resetTemperatureData(self):
        dataSet = []
        for row in self.tempOulu:
            dataSet.append([QBarDataItem(v) for v in row])

        self.m_primarySeries.dataProxy().resetArray(dataSet, self.years,
                self.months)

        dataSet = []
        for row in self.tempHelsinki:
            dataSet.append([QBarDataItem(v) for v in row])

        self.m_secondarySeries.dataProxy().resetArray(dataSet, self.years,
                self.months)

    def changeRange(self, range):
        if range >= len(self.years):
            self.m_yearAxis.setRange(0, len(self.years) - 1)
        else:
            self.m_yearAxis.setRange(range, range)

    def changeStyle(self, style):
        comboBox = self.sender()
        if isinstance(comboBox, QComboBox):
            self.m_barMesh = QAbstract3DSeries.Mesh(comboBox.itemData(style))
            self.m_primarySeries.setMesh(self.m_barMesh)
            self.m_secondarySeries.setMesh(self.m_barMesh)

    def changePresetCamera(self):
        self.m_graph.scene().activeCamera().setCameraPreset(self.m_preset)

        preset = int(self.m_preset) + 1
        if preset > Q3DCamera.CameraPresetDirectlyBelow:
            self.m_preset = Q3DCamera.CameraPresetFrontLow
        else:
            self.m_preset = Q3DCamera.CameraPreset(preset)

    def changeTheme(self, theme):
        currentTheme = self.m_graph.activeTheme()
        currentTheme.setType(Q3DTheme.Theme(theme))
        self.backgroundEnabledChanged.emit(currentTheme.isBackgroundEnabled())
        self.gridEnabledChanged.emit(currentTheme.isGridEnabled())
        self.fontChanged.emit(currentTheme.font())
        self.fontSizeChanged.emit(currentTheme.font().pointSize())

    def changeLabelBackground(self):
        self.m_graph.activeTheme().setLabelBackgroundEnabled(
                not self.m_graph.activeTheme().isLabelBackgroundEnabled())

    def changeSelectionMode(self, selectionMode):
        comboBox = selfsender()
        if isinstance(comboBox, QComboBox):
            flags = comboBox.itemData(selectionMode)
            self.m_graph.setSelectionMode(
                    QAbstract3DGraph.SelectionFlags(flags))

    def changeFont(self, font):
        self.m_graph.activeTheme().setFont(font)

    def changeFontSize(self, fontsize):
        self.m_fontSize = fontsize
        font = self.m_graph.activeTheme().font()
        font.setPointSize(self.m_fontSize)
        self.m_graph.activeTheme().setFont(font)

    def shadowQualityUpdatedByVisual(self, sq):
        self.shadowQualityChanged.emit(int(sq))

    def changeShadowQuality(self, quality):
        sq = QAbstract3DGraph.ShadowQuality(quality)
        self.m_graph.setShadowQuality(sq)
        self.shadowQualityChanged.emit(quality)

    def rotateX(self, rotation):
        self.m_xRotation = rotation
        self.m_graph.scene().activeCamera().setCameraPosition(
                self.m_xRotation, self.m_yRotation)

    def rotateY(self, rotation):
        self.m_yRotation = rotation
        self.m_graph.scene().activeCamera().setCameraPosition(
                self.m_xRotation, self.m_yRotation)

    def setBackgroundEnabled(self, enabled):
        self.m_graph.activeTheme().setBackgroundEnabled(enabled)

    def setGridEnabled(self, enabled):
        self.m_graph.activeTheme().setGridEnabled(enabled)

    def setSmoothBars(self, smooth):
        self.m_smooth = bool(smooth)
        self.m_primarySeries.setMeshSmooth(self.m_smooth)
        self.m_secondarySeries.setMeshSmooth(self.m_smooth)

    def setSeriesVisibility(self, enabled):
        self.m_secondarySeries.setVisible(enabled)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    widgetgraph = Q3DBars()
    container = QWidget.createWindowContainer(widgetgraph)

    screenSize = widgetgraph.screen().size()
    container.setMinimumSize(
            QSize(screenSize.width() / 2, screenSize.height() / 1.5))
    container.setMaximumSize(screenSize)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    container.setFocusPolicy(Qt.StrongFocus)

    widget = QWidget()
    hLayout = QHBoxLayout(widget)
    vLayout = QVBoxLayout()
    hLayout.addWidget(container, 1)
    hLayout.addLayout(vLayout)

    widget.setWindowTitle(
            "Average temperatures in Oulu and Helsinki, Finland (2006-2013)")

    themeList = QComboBox()
    themeList.addItem("Qt")
    themeList.addItem("Primary Colors")
    themeList.addItem("Digia")
    themeList.addItem("Stone Moss")
    themeList.addItem("Army Blue")
    themeList.addItem("Retro")
    themeList.addItem("Ebony")
    themeList.addItem("Isabelle")
    themeList.setCurrentIndex(0)

    labelButton = QPushButton("Change label style")

    smoothCheckBox = QCheckBox("Smooth bars")

    barStyleList = QComboBox()
    barStyleList.addItem("Bar", QAbstract3DSeries.MeshBar)
    barStyleList.addItem("Pyramid", QAbstract3DSeries.MeshPyramid)
    barStyleList.addItem("Cone", QAbstract3DSeries.MeshCone)
    barStyleList.addItem("Cylinder", QAbstract3DSeries.MeshCylinder)
    barStyleList.addItem("Bevel bar", QAbstract3DSeries.MeshBevelBar)
    barStyleList.addItem("Sphere", QAbstract3DSeries.MeshSphere)
    barStyleList.setCurrentIndex(4)

    cameraButton = QPushButton("Change camera preset")

    selectionModeList = QComboBox()
    selectionModeList.addItem("None", QAbstract3DGraph.SelectionNone)
    selectionModeList.addItem("Bar", QAbstract3DGraph.SelectionItem)
    selectionModeList.addItem("Row", QAbstract3DGraph.SelectionRow)
    selectionModeList.addItem("Bar and Row",
            QAbstract3DGraph.SelectionItemAndRow)
    selectionModeList.addItem("Column", QAbstract3DGraph.SelectionColumn)
    selectionModeList.addItem("Bar and Column",
            QAbstract3DGraph.SelectionItemAndColumn)
    selectionModeList.addItem("Row and Column",
            QAbstract3DGraph.SelectionRowAndColumn)
    selectionModeList.addItem("Bar, Row and Column",
            QAbstract3DGraph.SelectionItemRowAndColumn)
    selectionModeList.addItem("Slice into Row",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionRow)
    selectionModeList.addItem("Slice into Row and Item",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndRow)
    selectionModeList.addItem("Slice into Column",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionColumn)
    selectionModeList.addItem("Slice into Column and Item",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndColumn)
    selectionModeList.addItem("Multi: Bar, Row, Col",
            QAbstract3DGraph.SelectionItemRowAndColumn | QAbstract3DGraph.SelectionMultiSeries)
    selectionModeList.addItem("Multi, Slice: Row, Item",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndRow | QAbstract3DGraph.SelectionMultiSeries)
    selectionModeList.addItem("Multi, Slice: Col, Item",
            QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndColumn | QAbstract3DGraph.SelectionMultiSeries)
    selectionModeList.setCurrentIndex(1)

    backgroundCheckBox = QCheckBox("Show background")

    gridCheckBox = QCheckBox("Show grid")
    gridCheckBox.setChecked(True)

    seriesCheckBox = QCheckBox("Show second series")

    rotationSliderX = QSlider(Qt.Horizontal)
    rotationSliderX.setTickInterval(30)
    rotationSliderX.setTickPosition(QSlider.TicksBelow)
    rotationSliderX.setMinimum(-180)
    rotationSliderX.setValue(0)
    rotationSliderX.setMaximum(180)
    rotationSliderY = QSlider(Qt.Horizontal)
    rotationSliderY.setTickInterval(15)
    rotationSliderY.setTickPosition(QSlider.TicksAbove)
    rotationSliderY.setMinimum(-90)
    rotationSliderY.setValue(0)
    rotationSliderY.setMaximum(90)

    fontSizeSlider = QSlider(Qt.Horizontal)
    fontSizeSlider.setTickInterval(10)
    fontSizeSlider.setTickPosition(QSlider.TicksBelow)
    fontSizeSlider.setMinimum(1)
    fontSizeSlider.setValue(30)
    fontSizeSlider.setMaximum(100)

    fontList = QFontComboBox()
    fontList.setCurrentFont(QFont('Times New Roman'))

    shadowQuality = QComboBox()
    shadowQuality.addItem("None")
    shadowQuality.addItem("Low")
    shadowQuality.addItem("Medium")
    shadowQuality.addItem("High")
    shadowQuality.addItem("Low Soft")
    shadowQuality.addItem("Medium Soft")
    shadowQuality.addItem("High Soft")
    shadowQuality.setCurrentIndex(5)

    rangeList = QComboBox()
    rangeList.addItems(GraphModifier.years)
    rangeList.addItem("All")
    rangeList.setCurrentIndex(len(GraphModifier.years))

    vLayout.addWidget(QLabel("Rotate horizontally"))
    vLayout.addWidget(rotationSliderX, 0, Qt.AlignTop)
    vLayout.addWidget(QLabel("Rotate vertically"))
    vLayout.addWidget(rotationSliderY, 0, Qt.AlignTop)
    vLayout.addWidget(labelButton, 0, Qt.AlignTop)
    vLayout.addWidget(cameraButton, 0, Qt.AlignTop)
    vLayout.addWidget(backgroundCheckBox)
    vLayout.addWidget(gridCheckBox)
    vLayout.addWidget(smoothCheckBox)
    vLayout.addWidget(seriesCheckBox)
    vLayout.addWidget(QLabel("Show year"))
    vLayout.addWidget(rangeList)
    vLayout.addWidget(QLabel("Change bar style"))
    vLayout.addWidget(barStyleList)
    vLayout.addWidget(QLabel("Change selection mode"))
    vLayout.addWidget(selectionModeList)
    vLayout.addWidget(QLabel("Change theme"))
    vLayout.addWidget(themeList)
    vLayout.addWidget(QLabel("Adjust shadow quality"))
    vLayout.addWidget(shadowQuality)
    vLayout.addWidget(QLabel("Change font"))
    vLayout.addWidget(fontList)
    vLayout.addWidget(QLabel("Adjust font size"))
    vLayout.addWidget(fontSizeSlider, 1, Qt.AlignTop)

    modifier = GraphModifier(widgetgraph)

    rotationSliderX.valueChanged.connect(modifier.rotateX)
    rotationSliderY.valueChanged.connect(modifier.rotateY)

    labelButton.clicked.connect(modifier.changeLabelBackground)
    cameraButton.clicked.connect(modifier.changePresetCamera)

    backgroundCheckBox.stateChanged.connect(modifier.setBackgroundEnabled)
    gridCheckBox.stateChanged.connect(modifier.setGridEnabled)
    smoothCheckBox.stateChanged.connect(modifier.setSmoothBars)
    seriesCheckBox.stateChanged.connect(modifier.setSeriesVisibility)

    modifier.backgroundEnabledChanged.connect(backgroundCheckBox.setChecked)
    modifier.gridEnabledChanged.connect(gridCheckBox.setChecked)

    rangeList.currentIndexChanged.connect(modifier.changeRange)

    barStyleList.currentIndexChanged.connect(modifier.changeStyle)

    selectionModeList.currentIndexChanged.connect(modifier.changeSelectionMode)

    themeList.currentIndexChanged.connect(modifier.changeTheme)

    shadowQuality.currentIndexChanged.connect(modifier.changeShadowQuality)

    modifier.shadowQualityChanged.connect(shadowQuality.setCurrentIndex)
    widgetgraph.shadowQualityChanged.connect(
            modifier.shadowQualityUpdatedByVisual)

    fontSizeSlider.valueChanged.connect(modifier.changeFontSize)
    fontList.currentFontChanged.connect(modifier.changeFont)

    modifier.fontSizeChanged.connect(fontSizeSlider.setValue)
    modifier.fontChanged.connect(fontList.setCurrentFont)

    widget.show()
    sys.exit(app.exec_())    
