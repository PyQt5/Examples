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


from PyQt5.QtCore import QFileInfo, QObject, QSize, Qt, QTimer
from PyQt5.QtDataVisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
        QAbstract3DGraph, QCustom3DLabel, QCustom3DVolume)
from PyQt5.QtGui import (qBlue, qGreen, qRed, qRgba, QFont, QImage,
        QOpenGLContext, QPixmap, QQuaternion, QVector3D)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
        QHBoxLayout, QLabel, QRadioButton, QSizePolicy, QSlider, QVBoxLayout,
        QWidget)


class VolumetricModifier(QObject):

    lowDetailSize = 128
    mediumDetailSize = 256
    highDetailSize = 512
    colorTableSize = 256
    layerDataSize = 512
    mineShaftDiameter = 1

    airColorIndex = 254
    mineShaftColorIndex = 255
    layerColorThickness = 60
    heightToColorDiv = 140
    magmaColorsMin = 0
    magmaColorsMax = layerColorThickness
    aboveWaterGroundColorsMin = magmaColorsMax + 1
    aboveWaterGroundColorsMax = aboveWaterGroundColorsMin + layerColorThickness
    underWaterGroundColorsMin = aboveWaterGroundColorsMax + 1
    underWaterGroundColorsMax = underWaterGroundColorsMin + layerColorThickness
    waterColorsMin = underWaterGroundColorsMax + 1
    waterColorsMax = waterColorsMin + layerColorThickness
    terrainTransparency = 12

    def __init__(self, scatter):
        super(VolumetricModifier, self).__init__()

        self.m_graph = scatter
        self.m_volumeItem = None
        self.m_sliceIndexX = self.lowDetailSize // 2
        self.m_sliceIndexY = self.lowDetailSize // 4
        self.m_sliceIndexZ = self.lowDetailSize // 2
        self.m_slicingX = False
        self.m_slicingY = False
        self.m_slicingZ = False
        self.m_mediumDetailRB = None
        self.m_highDetailRB = None
        self.m_lowDetailData = None
        self.m_mediumDetailData = None
        self.m_highDetailData = None
        self.m_mediumDetailIndex = 0
        self.m_timer = QTimer()
        self.m_highDetailIndex = 0
        self.m_mediumDetailShaftIndex = 0
        self.m_highDetailShaftIndex = 0
        self.m_sliceSliderX = None
        self.m_sliceSliderY = None
        self.m_sliceSliderZ = None
        self.m_colorTable1 = []
        self.m_colorTable2 = []
        self.m_usingPrimaryTable = True
        self.m_sliceLabelX = None
        self.m_sliceLabelY = None
        self.m_sliceLabelZ = None
        self.m_magmaLayer = None
        self.m_waterLayer = None
        self.m_groundLayer = None
        self.m_mineShaftArray = ()

        self.m_graph.activeTheme().setType(Q3DTheme.ThemeQt)
        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualityNone)
        self.m_graph.scene().activeCamera().setCameraPreset(
                Q3DCamera.CameraPresetFront)
        self.m_graph.setOrthoProjection(True)
        self.m_graph.activeTheme().setBackgroundEnabled(False)

        # Only allow zooming at the center and limit the zoom to 200% to avoid
        # clipping issues.
        self.m_graph.activeInputHandler().setZoomAtTargetEnabled(False)
        self.m_graph.scene().activeCamera().setMaxZoomLevel(200.0)

        self.toggleAreaAll(True)

        if self.isOpenGLES():
            # OpenGL ES2 doesn't support 3D textures, so show a warning label
            # instead.
            warningLabel = QCustom3DLabel(
                    "QCustom3DVolume is not supported with OpenGL ES2",
                    QFont(), QVector3D(0.0, 0.5, 0.0),
                    QVector3D(1.5, 1.5, 0.0), QQuaternion())
            warningLabel.setPositionAbsolute(True)
            warningLabel.setFacingCamera(True)
            self.m_graph.addCustomItem(warningLabel)

        else:
            self.m_lowDetailData = bytearray((self.lowDetailSize ** 3) // 2)
            self.m_mediumDetailData = bytearray(
                    (self.mediumDetailSize ** 3) // 2)
            self.m_highDetailData = bytearray((self.highDetailSize ** 3) // 2)

            heightmaps_dir = QFileInfo(__file__).absolutePath() + '/heightmaps'
            self.m_groundLayer = self.initHeightMap(
                    heightmaps_dir + '/layer_ground.png')
            self.m_waterLayer = self.initHeightMap(
                    heightmaps_dir + '/layer_water.png')
            self.m_magmaLayer = self.initHeightMap(
                    heightmaps_dir + '/layer_magma.png')

            self.initMineShaftArray()

            self.createVolume(self.lowDetailSize, 0, self.lowDetailSize,
                    self.m_lowDetailData)
            self.excavateMineShaft(self.lowDetailSize, 0,
                    len(self.m_mineShaftArray), self.m_lowDetailData)

            self.m_volumeItem = QCustom3DVolume()

            # Adjust the water level to zero with a minor tweak to the
            # y-coordinate position and scaling.
            axisX_min = self.m_graph.axisX().min()
            axisX_max = self.m_graph.axisX().max()
            axisY_min = self.m_graph.axisY().min()
            axisY_max = self.m_graph.axisY().max()
            axisZ_min = self.m_graph.axisZ().min()
            axisZ_max = self.m_graph.axisZ().max()

            self.m_volumeItem.setScaling(
                    QVector3D(axisX_max - axisX_min,
                            (axisY_max - axisY_min) * 0.91,
                            axisZ_max - axisZ_min))
            self.m_volumeItem.setPosition(
                    QVector3D((axisX_max + axisX_min) / 2.0,
                            -0.045 * (axisY_max - axisY_min) + (axisY_max + axisY_min) / 2.0,
                            (axisZ_max + axisZ_min) / 2.0))

            self.m_volumeItem.setScalingAbsolute(False)
            self.m_volumeItem.setTextureWidth(self.lowDetailSize)
            self.m_volumeItem.setTextureHeight(self.lowDetailSize // 2)
            self.m_volumeItem.setTextureDepth(self.lowDetailSize)
            self.m_volumeItem.setTextureFormat(QImage.Format_Indexed8)
            self.m_volumeItem.setTextureData(self.m_lowDetailData)

            # Generate colour tables.  The alternate colour table just has grey
            # gradients for all terrain except water.
            self.m_colorTable1 = [None] * self.colorTableSize
            self.m_colorTable2 = [None] * self.colorTableSize

            for i in range(self.colorTableSize - 2):
                if i < self.magmaColorsMax:
                    color1 = qRgba(130 - (i * 2), 0, 0, 255)
                    color2 = qRgba(((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2), 255)
                elif i < self.aboveWaterGroundColorsMax:
                    color1 = qRgba((i - self.magmaColorsMax) * 4,
                            ((i - self.magmaColorsMax) * 2) + 120,
                            (i - self.magmaColorsMax) * 5,
                            self.terrainTransparency)
                    color2 = qRgba(((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2), 255)
                elif i < self.underWaterGroundColorsMax:
                    color1 = qRgba(
                            ((self.layerColorThickness - i - self.aboveWaterGroundColorsMax)) + 70,
                            ((self.layerColorThickness - i - self.aboveWaterGroundColorsMax) * 2) + 20,
                            ((self.layerColorThickness - i - self.aboveWaterGroundColorsMax)) + 50,
                            self.terrainTransparency)
                    color2 = qRgba(((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2),
                            ((i - self.aboveWaterGroundColorsMax) * 2),
                            self.terrainTransparency)
                elif i < self.waterColorsMax:
                    color1 = color2 = qRgba(0, 0,
                            ((i - self.underWaterGroundColorsMax) * 2) + 120,
                            self.terrainTransparency)
                else:
                    # Not used.
                    color1 = color2 = qRgba(0, 0, 0, 0)

                self.m_colorTable1[i] = color1
                self.m_colorTable2[i] = color2

            self.m_colorTable1[self.airColorIndex] = qRgba(0, 0, 0, 0)
            self.m_colorTable1[self.mineShaftColorIndex] = qRgba(50, 50, 50,
                    255)

            self.m_colorTable2[self.airColorIndex] = qRgba(0, 0, 0, 0)
            self.m_colorTable2[self.mineShaftColorIndex] = qRgba(255, 255, 0,
                    255)

            self.m_volumeItem.setColorTable(self.m_colorTable1)

            self.m_volumeItem.setSliceFrameGaps(QVector3D(0.01, 0.02, 0.01))
            self.m_volumeItem.setSliceFrameThicknesses(
                    QVector3D(0.0025, 0.005, 0.0025))
            self.m_volumeItem.setSliceFrameWidths(
                    QVector3D(0.0025, 0.005, 0.0025))
            self.m_volumeItem.setDrawSliceFrames(False);
            self.handleSlicingChanges();

            self.m_graph.addCustomItem(self.m_volumeItem);

            self.m_timer.start(0)

        self.m_graph.currentFpsChanged.connect(self.handleFpsChange)
        self.m_timer.timeout.connect(self.handleTimeout)

    def setFpsLabel(self, fpsLabel):
        self.m_fpsLabel = fpsLabel

    def setMediumDetailRB(self, button):
        self.m_mediumDetailRB = button

    def setHighDetailRB(self, button):
        self.m_highDetailRB = button

    def setSliceLabels(self, xLabel, yLabel, zLabel):
        self.m_sliceLabelX = xLabel
        self.m_sliceLabelY = yLabel
        self.m_sliceLabelZ = zLabel

        self.adjustSliceX(self.m_sliceSliderX.value())
        self.adjustSliceY(self.m_sliceSliderY.value())
        self.adjustSliceZ(self.m_sliceSliderZ.value())

    def setAlphaMultiplierLabel(self, label):
        self.m_alphaMultiplierLabel = label

    def sliceX(self, enabled):
        self.m_slicingX = enabled
        self.handleSlicingChanges()

    def sliceY(self, enabled):
        self.m_slicingY = enabled
        self.handleSlicingChanges()

    def sliceZ(self, enabled):
        self.m_slicingZ = enabled
        self.handleSlicingChanges()

    def adjustSliceX(self, value):
        if self.m_volumeItem is not None:
            self.m_sliceIndexX = value // (1024 // self.m_volumeItem.textureWidth())
            if self.m_sliceIndexX == self.m_volumeItem.textureWidth():
                self.m_sliceIndexX -= 1
            if self.m_volumeItem.sliceIndexX() != -1:
                self.m_volumeItem.setSliceIndexX(self.m_sliceIndexX)
            self.m_sliceLabelX.setPixmap(
                    QPixmap.fromImage(
                            self.m_volumeItem.renderSlice(Qt.XAxis,
                                    self.m_sliceIndexX)))

    def adjustSliceY(self, value):
        if self.m_volumeItem is not None:
            self.m_sliceIndexY = value // (1024 // self.m_volumeItem.textureHeight())
            if self.m_sliceIndexY == self.m_volumeItem.textureHeight():
                self.m_sliceIndexY -= 1
            if self.m_volumeItem.sliceIndexY() != -1:
                self.m_volumeItem.setSliceIndexY(self.m_sliceIndexY)
            self.m_sliceLabelY.setPixmap(
                    QPixmap.fromImage(
                            self.m_volumeItem.renderSlice(Qt.YAxis,
                                    self.m_sliceIndexY)))

    def adjustSliceZ(self, value):
        if self.m_volumeItem is not None:
            self.m_sliceIndexZ = value // (1024 // self.m_volumeItem.textureDepth())
            if self.m_sliceIndexZ == self.m_volumeItem.textureDepth():
                self.m_sliceIndexZ -= 1
            if self.m_volumeItem.sliceIndexZ() != -1:
                self.m_volumeItem.setSliceIndexZ(self.m_sliceIndexZ)
            self.m_sliceLabelZ.setPixmap(
                    QPixmap.fromImage(
                            self.m_volumeItem.renderSlice(Qt.ZAxis,
                                    self.m_sliceIndexZ)))

    def handleFpsChange(self, fps):
        self.m_fpsLabel.setText("FPS: %.1f" % fps)

    def handleTimeout(self):
        if not self.m_mediumDetailRB.isEnabled():
            if self.m_mediumDetailIndex != self.mediumDetailSize:
                self.m_mediumDetailIndex = self.createVolume(
                        self.mediumDetailSize, self.m_mediumDetailIndex, 4,
                        self.m_mediumDetailData)
            elif self.m_mediumDetailShaftIndex != len(self.m_mineShaftArray):
                self.m_mediumDetailShaftIndex = self.excavateMineShaft(
                        self.mediumDetailSize, self.m_mediumDetailShaftIndex,
                        1, self.m_mediumDetailData)
            else:
                self.m_mediumDetailRB.setEnabled(True)
                self.m_mediumDetailRB.setText(
                        "Medium (%dx%dx%d)" % (self.mediumDetailSize,
                                self.mediumDetailSize // 2,
                                self.mediumDetailSize))

        elif not self.m_highDetailRB.isEnabled():
            if self.m_highDetailIndex != self.highDetailSize:
                self.m_highDetailIndex = self.createVolume(
                        self.highDetailSize, self.m_highDetailIndex, 1,
                        self.m_highDetailData)
            elif self.m_highDetailShaftIndex != len(self.m_mineShaftArray):
                self.m_highDetailShaftIndex = self.excavateMineShaft(
                        self.highDetailSize, self.m_highDetailShaftIndex, 1,
                        self.m_highDetailData)
            else:
                self.m_highDetailRB.setEnabled(True)
                self.m_highDetailRB.setText(
                        "High (%dx%dx%d)" % (self.highDetailSize,
                                self.highDetailSize // 2, self.highDetailSize))
                self.m_timer.stop()

    def toggleLowDetail(self, enabled):
        if enabled and self.m_volumeItem is not None:
            self.m_volumeItem.setTextureData(self.m_lowDetailData)
            self.m_volumeItem.setTextureDimensions(self.lowDetailSize,
                    self.lowDetailSize // 2, self.lowDetailSize)
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def toggleMediumDetail(self, enabled):
        if enabled and self.m_volumeItem is not None:
            self.m_volumeItem.setTextureData(self.m_mediumDetailData)
            self.m_volumeItem.setTextureDimensions(self.mediumDetailSize,
                    self.mediumDetailSize // 2, self.mediumDetailSize)
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def toggleHighDetail(self, enabled):
        if enabled and self.m_volumeItem is not None:
            self.m_volumeItem.setTextureData(self.m_highDetailData)
            self.m_volumeItem.setTextureDimensions(self.highDetailSize,
                    self.highDetailSize // 2, self.highDetailSize)
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def setFpsMeasurement(self, enabled):
        self.m_graph.setMeasureFps(enabled)

        if enabled:
            self.m_fpsLabel.setText("Measuring...")
        else:
            self.m_fpsLabel.setText('')

    def setSliceSliders(self, sliderX, sliderY, sliderZ):
        self.m_sliceSliderX = sliderX
        self.m_sliceSliderY = sliderY
        self.m_sliceSliderZ = sliderZ

        # Set sliders to interesting values.
        self.m_sliceSliderX.setValue(715)
        self.m_sliceSliderY.setValue(612)
        self.m_sliceSliderZ.setValue(715)

    def changeColorTable(self, enabled):
        if self.m_volumeItem is not None:
            if enabled:
                self.m_volumeItem.setColorTable(self.m_colorTable2)
            else:
                self.m_volumeItem.setColorTable(self.m_colorTable1)

            self.m_usingPrimaryTable = not enabled

            # Re-render image labels.
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def setPreserveOpacity(self, enabled):
        if self.m_volumeItem is not None:
            self.m_volumeItem.setPreserveOpacity(enabled)

            # Re-render image labels.
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def setTransparentGround(self, enabled):
        if self.m_volumeItem is not None:
            newAlpha = self.terrainTransparency if enabled else 255

            for i in range(self.aboveWaterGroundColorsMin, self.underWaterGroundColorsMax):
                oldColor1 = self.m_colorTable1[i]
                oldColor2 = self.m_colorTable2[i]
                self.m_colorTable1[i] = qRgba(qRed(oldColor1), qGreen(oldColor1), qBlue(oldColor1), newAlpha)
                self.m_colorTable2[i] = qRgba(qRed(oldColor2), qGreen(oldColor2), qBlue(oldColor2), newAlpha)

            if self.m_usingPrimaryTable:
                self.m_volumeItem.setColorTable(self.m_colorTable1)
            else:
                self.m_volumeItem.setColorTable(self.m_colorTable2)

            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def setUseHighDefShader(self, enabled):
        if self.m_volumeItem is not None:
            self.m_volumeItem.setUseHighDefShader(enabled)

    def adjustAlphaMultiplier(self, value):
        if self.m_volumeItem is not None:
            if value > 100:
                mult = (value - 99) / 2.0
            else:
                mult = value / float(500 - value * 4)

            self.m_volumeItem.setAlphaMultiplier(mult)
            self.m_alphaMultiplierLabel.setText("Alpha multiplier: %.3f" % mult)

            # Re-render image labels.
            self.adjustSliceX(self.m_sliceSliderX.value())
            self.adjustSliceY(self.m_sliceSliderY.value())
            self.adjustSliceZ(self.m_sliceSliderZ.value())

    def toggleAreaAll(self, enabled):
        if enabled:
            self.m_graph.axisX().setRange(0.0, 1000.0)
            self.m_graph.axisY().setRange(-600.0, 600.0)
            self.m_graph.axisZ().setRange(0.0, 1000.0)
            self.m_graph.axisX().setSegmentCount(5)
            self.m_graph.axisY().setSegmentCount(6)
            self.m_graph.axisZ().setSegmentCount(5)

    def toggleAreaMine(self, enabled):
        if enabled:
            self.m_graph.axisX().setRange(350.0, 850.0)
            self.m_graph.axisY().setRange(-500.0, 100.0)
            self.m_graph.axisZ().setRange(350.0, 900.0)
            self.m_graph.axisX().setSegmentCount(10)
            self.m_graph.axisY().setSegmentCount(6)
            self.m_graph.axisZ().setSegmentCount(11)

    def toggleAreaMountain(self, enabled):
        if enabled:
            self.m_graph.axisX().setRange(300.0, 600.0)
            self.m_graph.axisY().setRange(-100.0, 400.0)
            self.m_graph.axisZ().setRange(300.0, 600.0)
            self.m_graph.axisX().setSegmentCount(9)
            self.m_graph.axisY().setSegmentCount(5)
            self.m_graph.axisZ().setSegmentCount(9)

    def setDrawSliceFrames(self, enabled):
        if self.m_volumeItem is not None:
            self.m_volumeItem.setDrawSliceFrames(enabled)

    def initHeightMap(self, fileName):
        heightImage = QImage(fileName)
        bits = heightImage.constBits().asarray(heightImage.byteCount())
        colorTable = heightImage.colorTable()

        layerData = bytearray(self.layerDataSize ** 2)
        index = 0

        for i in range(self.layerDataSize):
            for j in range(self.layerDataSize):
                layerData[index] = qRed(colorTable[bits[index]])
                index += 1

        return layerData

    def createVolume(self, textureSize, startIndex, count, textureData):
        # Generate volume from layer data.
        index = (startIndex * textureSize * textureSize) // 2
        endIndex = min(startIndex + count, textureSize)
        magmaHeights = bytearray(textureSize)
        waterHeights = bytearray(textureSize)
        groundHeights = bytearray(textureSize)
        multiplier = float(self.layerDataSize) / float(textureSize)

        for i in range(startIndex, endIndex):
            # Generate layer height arrays.
            for l in range(textureSize):
                layerIndex = int(i * multiplier) * self.layerDataSize + int(l * multiplier)
                magmaHeights[l] = self.m_magmaLayer[layerIndex]
                waterHeights[l] = self.m_waterLayer[layerIndex]
                groundHeights[l] = self.m_groundLayer[layerIndex]

            for j in range(textureSize // 2):
                for k in range(textureSize):
                    height = int((self.layerDataSize - (j * 2 * multiplier)) / 2)

                    if height < magmaHeights[k]:
                        # Magma layer.
                        colorIndex = int((float(height) / self.heightToColorDiv)
                                        * float(self.layerColorThickness)) + self.magmaColorsMin
                    elif height < groundHeights[k] and height < waterHeights[k]:
                        # Ground layer below water.
                        colorIndex = int((float(waterHeights[k] - height) / self.heightToColorDiv)
                                        * float(self.layerColorThickness)) + self.underWaterGroundColorsMin
                    elif height < waterHeights[k]:
                        # Water layer where water goes over ground.
                        colorIndex = int((float(height - magmaHeights[k]) / self.heightToColorDiv)
                                        * float(self.layerColorThickness)) + self.waterColorsMin
                    elif height <= groundHeights[k]:
                        # Ground above water.
                        colorIndex = int((float(height - waterHeights[k]) / self.heightToColorDiv)
                                        * float(self.layerColorThickness)) + self.aboveWaterGroundColorsMin
                    else:
                        # Rest is air.
                        colorIndex = self.airColorIndex

                    textureData[index] = colorIndex
                    index += 1

        return endIndex

    def excavateMineShaft(self, textureSize, startIndex, count, textureData):
        endIndex = min(startIndex + count, len(self.m_mineShaftArray))
        shaftSize = (self.mineShaftDiameter * textureSize) // self.lowDetailSize

        for shaftStart, shaftEnd in self.m_mineShaftArray[startIndex:endIndex]:
            shaftLen = int((shaftEnd - shaftStart).length() * self.lowDetailSize)
            dataX = int(shaftStart.x() * textureSize - (shaftSize // 2))
            dataY = int((shaftStart.y() * textureSize - (shaftSize // 2)) / 2)
            dataZ = int(shaftStart.z() * textureSize - (shaftSize // 2))
            dataIndex = dataX + (dataY * textureSize) + dataZ * (textureSize * textureSize // 2)

            if shaftStart.x() != shaftEnd.x():
                for j in range(shaftLen + 1):
                    self.excavateMineBlock(textureSize, dataIndex, shaftSize,
                            textureData)
                    dataIndex += shaftSize
            elif shaftStart.y() != shaftEnd.y():
                # Vertical shafts are half as long.
                shaftLen //= 2
                for j in range(shaftLen + 1):
                    self.excavateMineBlock(textureSize, dataIndex, shaftSize,
                            textureData)
                    dataIndex += textureSize * shaftSize
            else:
                for j in range(shaftLen + 1):
                    self.excavateMineBlock(textureSize, dataIndex, shaftSize,
                            textureData)
                    dataIndex += (textureSize * textureSize // 2) * shaftSize

        return endIndex

    @classmethod
    def excavateMineBlock(cls, textureSize, dataIndex, size, textureData):
        for k in range(size):
            for l in range(size):
                curIndex = dataIndex + ((k * textureSize * textureSize) // 2) + (l * textureSize)
                for m in range(size):
                    if textureData[curIndex] != cls.airColorIndex:
                        textureData[curIndex] = cls.mineShaftColorIndex
                    curIndex += 1

    def handleSlicingChanges(self):
        if self.m_volumeItem is not None:
            if self.m_slicingX or self.m_slicingY or self.m_slicingZ:
                # Only show slices of selected dimensions.
                self.m_volumeItem.setDrawSlices(True)
                self.m_volumeItem.setSliceIndexX(self.m_sliceIndexX if self.m_slicingX else -1)
                self.m_volumeItem.setSliceIndexY(self.m_sliceIndexY if self.m_slicingY else -1)
                self.m_volumeItem.setSliceIndexZ(self.m_sliceIndexZ if self.m_slicingZ else -1)
            else:
                # Show slice frames for all dimensions when not actually
                # slicing.
                self.m_volumeItem.setDrawSlices(False)
                self.m_volumeItem.setSliceIndexX(self.m_sliceIndexX)
                self.m_volumeItem.setSliceIndexY(self.m_sliceIndexY)
                self.m_volumeItem.setSliceIndexZ(self.m_sliceIndexZ)

    def initMineShaftArray(self):
        self.m_mineShaftArray = (
            (QVector3D(0.7, 0.1, 0.7), QVector3D(0.7, 0.8, 0.7)),
            (QVector3D(0.7, 0.7, 0.5), QVector3D(0.7, 0.7, 0.7)),
            (QVector3D(0.4, 0.7, 0.7), QVector3D(0.7, 0.7, 0.7)),
            (QVector3D(0.4, 0.7, 0.7), QVector3D(0.4, 0.7, 0.8)),
            (QVector3D(0.45, 0.7, 0.7), QVector3D(0.45, 0.7, 0.8)),
            (QVector3D(0.5, 0.7, 0.7), QVector3D(0.5, 0.7, 0.8)),
            (QVector3D(0.55, 0.7, 0.7), QVector3D(0.55, 0.7, 0.8)),
            (QVector3D(0.6, 0.7, 0.7), QVector3D(0.6, 0.7, 0.8)),
            (QVector3D(0.65, 0.7, 0.7), QVector3D(0.65, 0.7, 0.8)),
            (QVector3D(0.5, 0.6, 0.7), QVector3D(0.7, 0.6, 0.7)),
            (QVector3D(0.5, 0.6, 0.7), QVector3D(0.5, 0.6, 0.8)),
            (QVector3D(0.55, 0.6, 0.7), QVector3D(0.55, 0.6, 0.8)),
            (QVector3D(0.6, 0.6, 0.7), QVector3D(0.6, 0.6, 0.8)),
            (QVector3D(0.65, 0.6, 0.7), QVector3D(0.65, 0.6, 0.8)),
            (QVector3D(0.7, 0.6, 0.4), QVector3D(0.7, 0.6, 0.7)),
            (QVector3D(0.6, 0.6, 0.45), QVector3D(0.8, 0.6, 0.45)),
            (QVector3D(0.6, 0.6, 0.5), QVector3D(0.8, 0.6, 0.5)),
            (QVector3D(0.6, 0.6, 0.55), QVector3D(0.8, 0.6, 0.55)),
            (QVector3D(0.6, 0.6, 0.6), QVector3D(0.8, 0.6, 0.6)),
            (QVector3D(0.6, 0.6, 0.65), QVector3D(0.8, 0.6, 0.65)),
            (QVector3D(0.6, 0.6, 0.7), QVector3D(0.8, 0.6, 0.7)),
            (QVector3D(0.7, 0.7, 0.4), QVector3D(0.7, 0.7, 0.7)),
            (QVector3D(0.6, 0.7, 0.45), QVector3D(0.8, 0.7, 0.45)),
            (QVector3D(0.6, 0.7, 0.5), QVector3D(0.8, 0.7, 0.5)),
            (QVector3D(0.6, 0.7, 0.55), QVector3D(0.8, 0.7, 0.55)),
            (QVector3D(0.6, 0.7, 0.6), QVector3D(0.8, 0.7, 0.6)),
            (QVector3D(0.6, 0.7, 0.65), QVector3D(0.8, 0.7, 0.65)),
            (QVector3D(0.6, 0.7, 0.7), QVector3D(0.8, 0.7, 0.7)),
            (QVector3D(0.7, 0.8, 0.5), QVector3D(0.7, 0.8, 0.7)),
            (QVector3D(0.6, 0.8, 0.55), QVector3D(0.8, 0.8, 0.55)),
            (QVector3D(0.6, 0.8, 0.6), QVector3D(0.8, 0.8, 0.6)),
            (QVector3D(0.6, 0.8, 0.65), QVector3D(0.8, 0.8, 0.65)),
            (QVector3D(0.6, 0.8, 0.7), QVector3D(0.8, 0.8, 0.7)),
            (QVector3D(0.7, 0.1, 0.4), QVector3D(0.7, 0.7, 0.4)))

    @staticmethod
    def isOpenGLES():
        try:
            # isOpenGLES() was introduced in Qt v5.3.
            return QOpenGLContext.currentContext().isOpenGLES()
        except:
            pass

        return False


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    graph = Q3DScatter()
    container = QWidget.createWindowContainer(graph)

    screenSize = graph.screen().size()
    container.setMinimumSize(
            QSize(screenSize.width() // 3, screenSize.height() // 3))
    container.setMaximumSize(screenSize)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    container.setFocusPolicy(Qt.StrongFocus)

    widget = QWidget()
    hLayout = QHBoxLayout(widget)
    vLayout = QVBoxLayout()
    vLayout2 = QVBoxLayout()
    hLayout.addWidget(container, 1)
    hLayout.addLayout(vLayout)
    hLayout.addLayout(vLayout2)

    widget.setWindowTitle("Volumetric object example - 3D terrain")

    sliceXCheckBox = QCheckBox()
    sliceXCheckBox.setText("Slice volume on X axis")
    sliceXCheckBox.setChecked(False)
    sliceYCheckBox = QCheckBox()
    sliceYCheckBox.setText("Slice volume on Y axis")
    sliceYCheckBox.setChecked(False)
    sliceZCheckBox = QCheckBox()
    sliceZCheckBox.setText("Slice volume on Z axis")
    sliceZCheckBox.setChecked(False)

    sliceXSlider = QSlider(Qt.Horizontal)
    sliceXSlider.setMinimum(0)
    sliceXSlider.setMaximum(1024)
    sliceXSlider.setValue(512)
    sliceXSlider.setEnabled(True)
    sliceYSlider = QSlider(Qt.Horizontal)
    sliceYSlider.setMinimum(0)
    sliceYSlider.setMaximum(1024)
    sliceYSlider.setValue(512)
    sliceYSlider.setEnabled(True)
    sliceZSlider = QSlider(Qt.Horizontal)
    sliceZSlider.setMinimum(0)
    sliceZSlider.setMaximum(1024)
    sliceZSlider.setValue(512)
    sliceZSlider.setEnabled(True)

    fpsCheckBox = QCheckBox()
    fpsCheckBox.setText("Show FPS")
    fpsCheckBox.setChecked(False)
    fpsLabel = QLabel()

    textureDetailGroupBox = QGroupBox("Texture detail")

    lowDetailRB = QRadioButton()
    lowDetailRB.setText("Low (128x64x128)")
    lowDetailRB.setChecked(True)

    mediumDetailRB = QRadioButton()
    mediumDetailRB.setText("Generating...")
    mediumDetailRB.setChecked(False)
    mediumDetailRB.setEnabled(False)

    highDetailRB = QRadioButton()
    highDetailRB.setText("Generating...")
    highDetailRB.setChecked(False)
    highDetailRB.setEnabled(False)

    textureDetailVBox = QVBoxLayout()
    textureDetailVBox.addWidget(lowDetailRB)
    textureDetailVBox.addWidget(mediumDetailRB)
    textureDetailVBox.addWidget(highDetailRB)
    textureDetailGroupBox.setLayout(textureDetailVBox)

    areaGroupBox = QGroupBox("Show area")

    areaAllRB = QRadioButton()
    areaAllRB.setText("Whole region")
    areaAllRB.setChecked(True)

    areaMineRB = QRadioButton()
    areaMineRB.setText("The mine")
    areaMineRB.setChecked(False)

    areaMountainRB = QRadioButton()
    areaMountainRB.setText("The mountain")
    areaMountainRB.setChecked(False)

    areaVBox = QVBoxLayout()
    areaVBox.addWidget(areaAllRB)
    areaVBox.addWidget(areaMineRB)
    areaVBox.addWidget(areaMountainRB)
    areaGroupBox.setLayout(areaVBox)

    colorTableCheckBox = QCheckBox()
    colorTableCheckBox.setText("Alternate color table")
    colorTableCheckBox.setChecked(False)

    sliceImageXLabel = QLabel()
    sliceImageYLabel = QLabel()
    sliceImageZLabel = QLabel()
    sliceImageXLabel.setMinimumSize(QSize(200, 100))
    sliceImageYLabel.setMinimumSize(QSize(200, 200))
    sliceImageZLabel.setMinimumSize(QSize(200, 100))
    sliceImageXLabel.setMaximumSize(QSize(200, 100))
    sliceImageYLabel.setMaximumSize(QSize(200, 200))
    sliceImageZLabel.setMaximumSize(QSize(200, 100))
    sliceImageXLabel.setFrameShape(QFrame.Box)
    sliceImageYLabel.setFrameShape(QFrame.Box)
    sliceImageZLabel.setFrameShape(QFrame.Box)
    sliceImageXLabel.setScaledContents(True)
    sliceImageYLabel.setScaledContents(True)
    sliceImageZLabel.setScaledContents(True)

    alphaMultiplierSlider = QSlider(Qt.Horizontal)
    alphaMultiplierSlider.setMinimum(0)
    alphaMultiplierSlider.setMaximum(139)
    alphaMultiplierSlider.setValue(100)
    alphaMultiplierSlider.setEnabled(True)
    alphaMultiplierLabel = QLabel("Alpha multiplier: 1.0")

    preserveOpacityCheckBox = QCheckBox()
    preserveOpacityCheckBox.setText("Preserve opacity")
    preserveOpacityCheckBox.setChecked(True)

    transparentGroundCheckBox = QCheckBox()
    transparentGroundCheckBox.setText("Transparent ground")
    transparentGroundCheckBox.setChecked(False)

    useHighDefShaderCheckBox = QCheckBox()
    useHighDefShaderCheckBox.setText("Use HD shader")
    useHighDefShaderCheckBox.setChecked(True)

    performanceNoteLabel = QLabel(
            "Note: A high end graphics card is\nrecommended with the HD shader\nwhen the volume contains a lot of\ntransparent areas.")
    performanceNoteLabel.setFrameShape(QFrame.Box)

    drawSliceFramesCheckBox = QCheckBox()
    drawSliceFramesCheckBox.setText("Draw slice frames")
    drawSliceFramesCheckBox.setChecked(False)

    vLayout.addWidget(sliceXCheckBox)
    vLayout.addWidget(sliceXSlider)
    vLayout.addWidget(sliceImageXLabel)
    vLayout.addWidget(sliceYCheckBox)
    vLayout.addWidget(sliceYSlider)
    vLayout.addWidget(sliceImageYLabel)
    vLayout.addWidget(sliceZCheckBox)
    vLayout.addWidget(sliceZSlider)
    vLayout.addWidget(sliceImageZLabel)
    vLayout.addWidget(drawSliceFramesCheckBox, 1, Qt.AlignTop)
    vLayout2.addWidget(fpsCheckBox)
    vLayout2.addWidget(fpsLabel)
    vLayout2.addWidget(textureDetailGroupBox)
    vLayout2.addWidget(areaGroupBox)
    vLayout2.addWidget(colorTableCheckBox)
    vLayout2.addWidget(alphaMultiplierLabel)
    vLayout2.addWidget(alphaMultiplierSlider)
    vLayout2.addWidget(preserveOpacityCheckBox)
    vLayout2.addWidget(transparentGroundCheckBox)
    vLayout2.addWidget(useHighDefShaderCheckBox)
    vLayout2.addWidget(performanceNoteLabel, 1, Qt.AlignTop)

    modifier = VolumetricModifier(graph)
    modifier.setFpsLabel(fpsLabel)
    modifier.setMediumDetailRB(mediumDetailRB)
    modifier.setHighDetailRB(highDetailRB)
    modifier.setSliceSliders(sliceXSlider, sliceYSlider, sliceZSlider)
    modifier.setSliceLabels(sliceImageXLabel, sliceImageYLabel,
            sliceImageZLabel)
    modifier.setAlphaMultiplierLabel(alphaMultiplierLabel)
    modifier.setTransparentGround(transparentGroundCheckBox.isChecked())

    fpsCheckBox.stateChanged.connect(modifier.setFpsMeasurement)
    sliceXCheckBox.stateChanged.connect(modifier.sliceX)
    sliceYCheckBox.stateChanged.connect(modifier.sliceY)
    sliceZCheckBox.stateChanged.connect(modifier.sliceZ)
    sliceXSlider.valueChanged.connect(modifier.adjustSliceX)
    sliceYSlider.valueChanged.connect(modifier.adjustSliceY)
    sliceZSlider.valueChanged.connect(modifier.adjustSliceZ)
    lowDetailRB.toggled.connect(modifier.toggleLowDetail)
    mediumDetailRB.toggled.connect(modifier.toggleMediumDetail)
    highDetailRB.toggled.connect(modifier.toggleHighDetail)
    colorTableCheckBox.stateChanged.connect(modifier.changeColorTable)
    preserveOpacityCheckBox.stateChanged.connect(modifier.setPreserveOpacity)
    transparentGroundCheckBox.stateChanged.connect(
            modifier.setTransparentGround)
    useHighDefShaderCheckBox.stateChanged.connect(modifier.setUseHighDefShader)
    alphaMultiplierSlider.valueChanged.connect(modifier.adjustAlphaMultiplier)
    areaAllRB.toggled.connect(modifier.toggleAreaAll)
    areaMineRB.toggled.connect(modifier.toggleAreaMine)
    areaMountainRB.toggled.connect(modifier.toggleAreaMountain)
    drawSliceFramesCheckBox.stateChanged.connect(modifier.setDrawSliceFrames)

    widget.show()

    sys.exit(app.exec_())
