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


from PyQt5.QtCore import (pyqtSignal, QAbstractAnimation, QFile, QFileInfo,
        QIODevice, QObject, QPropertyAnimation, QSequentialAnimationGroup,
        QSize, Qt, QTextStream, QTimer)
from PyQt5.QtDataVisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
        QAbstract3DGraph, QAbstract3DInputHandler, QAbstract3DSeries,
        QScatter3DSeries, QScatterDataItem, QValue3DAxis)
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QVBoxLayout, QWidget)


class CustomInputHandler(QAbstract3DInputHandler):

    def mouseMoveEvent(self, event, mousePos):
        self.setInputPosition(mousePos)

    def wheelEvent(self, event):
        # Adjust the zoom level based on what zoom range we're in.
        zoomLevel = self.scene().activeCamera().zoomLevel()

        if zoomLevel > 100:
            zoomLevel += event.angleDelta().y() / 12
        elif zoomLevel > 50:
            zoomLevel += event.angleDelta().y() / 60
        else:
            zoomLevel += event.angleDelta().y() / 120

        if zoomLevel > 500:
            zoomLevel = 500
        elif zoomLevel < 10:
            zoomLevel = 10

        self.scene().activeCamera().setZoomLevel(zoomLevel)


class ScatterDataModifier(QObject):

    shadowQualityChanged = pyqtSignal()

    def __init__(self, scatter):
        super(ScatterDataModifier, self).__init__()

        self.m_graph = scatter
        self.m_inputHandler = CustomInputHandler()

        self.m_graph.activeTheme().setType(Q3DTheme.ThemeDigia)
        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualityMedium)
        self.m_graph.scene().activeCamera().setCameraPreset(
                Q3DCamera.CameraPresetFront)

        self.m_graph.setAxisX(QValue3DAxis())
        self.m_graph.setAxisY(QValue3DAxis())
        self.m_graph.setAxisZ(QValue3DAxis())

        self.m_graph.axisX().setRange(-10.0, 10.0)
        self.m_graph.axisY().setRange(-5.0, 5.0)
        self.m_graph.axisZ().setRange(-5.0, 5.0)

        series = QScatter3DSeries()
        series.setItemLabelFormat("@xLabel, @yLabel, @zLabel")
        series.setMesh(QAbstract3DSeries.MeshCube)
        series.setItemSize(0.15)
        self.m_graph.addSeries(series)

        self.m_animationCameraX = QPropertyAnimation(
                self.m_graph.scene().activeCamera(), 'xRotation')
        self.m_animationCameraX.setDuration(20000)
        self.m_animationCameraX.setStartValue(0.0)
        self.m_animationCameraX.setEndValue(360.0)
        self.m_animationCameraX.setLoopCount(-1)

        upAnimation = QPropertyAnimation(self.m_graph.scene().activeCamera(),
                'yRotation')
        upAnimation.setDuration(9000)
        upAnimation.setStartValue(5.0)
        upAnimation.setEndValue(45.0)

        downAnimation = QPropertyAnimation(self.m_graph.scene().activeCamera(),
                'yRotation')
        downAnimation.setDuration(9000)
        downAnimation.setStartValue(45.0)
        downAnimation.setEndValue(5.0)

        self.m_animationCameraY = QSequentialAnimationGroup()
        self.m_animationCameraY.setLoopCount(-1)
        self.m_animationCameraY.addAnimation(upAnimation)
        self.m_animationCameraY.addAnimation(downAnimation)

        self.m_animationCameraX.start()
        self.m_animationCameraY.start()

        self.m_graph.setActiveInputHandler(self.m_inputHandler)

        self.m_selectionTimer = QTimer()
        self.m_selectionTimer.setInterval(10)
        self.m_selectionTimer.timeout.connect(self.triggerSelection)
        self.m_selectionTimer.start()

    def start(self):
        self.addData()

    def addData(self):
        dataArray = []

        stream = QTextStream()
        dataFile = QFile(QFileInfo(__file__).absolutePath() + '/data.txt')
        if dataFile.open(QIODevice.ReadOnly | QIODevice.Text):
            stream.setDevice(dataFile)
            while not stream.atEnd():
                line = stream.readLine()
                if line.startswith('#'):
                    continue

                strList = line.split(',')
                # Each line has three data items: xPos, yPos and zPos values.
                if len(strList) < 3:
                    continue

                position = QVector3D(float(strList[0]), float(strList[1]),
                        float(strList[2]))
                dataArray.append(QScatterDataItem(position))

        self.m_graph.seriesList()[0].dataProxy().resetArray(dataArray)

    def toggleCameraAnimation(self):
        if self.m_animationCameraX.state() != QAbstractAnimation.Paused:
            self.m_animationCameraX.pause()
            self.m_animationCameraY.pause()
        else:
            self.m_animationCameraX.resume()
            self.m_animationCameraY.resume()

    def triggerSelection(self):
        self.m_graph.scene().setSelectionQueryPosition(
                self.m_inputHandler.inputPosition())

    def shadowQualityUpdatedByVisual(self, sq):
        self.shadowQualityChanged.emit(int(sq))

    def changeShadowQuality(self, quality):
        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQuality(quality))


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    graph = Q3DScatter()
    container = QWidget.createWindowContainer(graph)

    screenSize = graph.screen().size()
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

    widget.setWindowTitle("Custom Input Handling")

    cameraButton = QPushButton("Toggle camera animation")

    shadowQuality = QComboBox()
    shadowQuality.addItem("None")
    shadowQuality.addItem("Low")
    shadowQuality.addItem("Medium")
    shadowQuality.addItem("High")
    shadowQuality.addItem("Low Soft")
    shadowQuality.addItem("Medium Soft")
    shadowQuality.addItem("High Soft")
    shadowQuality.setCurrentIndex(2)

    vLayout.addWidget(cameraButton, 0, Qt.AlignTop)
    vLayout.addWidget(QLabel("Adjust shadow quality"), 0, Qt.AlignTop)
    vLayout.addWidget(shadowQuality, 1, Qt.AlignTop)

    modifier = ScatterDataModifier(graph)

    cameraButton.clicked.connect(modifier.toggleCameraAnimation)
    shadowQuality.currentIndexChanged.connect(modifier.changeShadowQuality)
    modifier.shadowQualityChanged.connect(shadowQuality.setCurrentIndex)

    widget.show()
    modifier.start()
    sys.exit(app.exec_())
