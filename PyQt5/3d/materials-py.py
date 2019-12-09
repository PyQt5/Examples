# Copyright (C) 2016 Riverbank Computing Limited
# Copyright (C) 2014 Klaralvdalens Datakonsult AB (KDAB).
#
# Commercial License Usage
# Licensees holding valid commercial Qt licenses may use this file in
# accordance with the commercial license agreement provided with the
# Software or, alternatively, in accordance with the terms contained in
# a written agreement between you and The Qt Company. For licensing terms
# and conditions see https://www.qt.io/terms-conditions. For further
# information use the contact form at https://www.qt.io/contact-us.
#
# BSD License Usage
# Alternatively, you may use this file under the terms of the BSD license
# as follows:
#
# "Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of The Qt Company Ltd nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."


import os
import sys

from PyQt5.QtCore import (pyqtProperty, pyqtSignal, QPropertyAnimation, QSize,
        Qt, QUrl)
from PyQt5.QtGui import QColor, QGuiApplication, QMatrix4x4, QVector3D
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import (Qt3DWindow, QDiffuseMapMaterial,
        QFirstPersonCameraController, QNormalDiffuseMapAlphaMaterial,
        QNormalDiffuseMapMaterial, QNormalDiffuseSpecularMapMaterial,
        QPhongMaterial, QPlaneMesh)
from PyQt5.Qt3DRender import QCamera, QCameraLens, QMesh, QTextureImage


class PlaneEntity(QEntity):

    def __init__(self, parent=None):
        super(PlaneEntity, self).__init__(parent)

        self.m_mesh = QPlaneMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh


class RenderableEntity(QEntity):

    def __init__(self, parent=None):
        super(RenderableEntity, self).__init__(parent)

        self.m_mesh = QMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh

    def transform(self):
        return self.m_transform


class TrefoilKnot(QEntity):

    def __init__(self, parent=None):
        super(TrefoilKnot, self).__init__(parent)

        self.m_mesh = QMesh()
        self.m_transform = QTransform()
        self.m_theta = 0.0
        self.m_phi = 0.0
        self.m_position = QVector3D()
        self.m_scale = 1.0

        self.m_mesh.setSource(QUrl.fromLocalFile('assets/obj/trefoil.obj'))
        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def updateTransform(self):
        m = QMatrix4x4()
        m.translate(self.m_position)
        m.rotate(self.m_phi, QVector3D(1.0, 0.0, 0.0))
        m.rotate(self.m_phi, QVector3D(0.0, 1.0, 0.0))
        m.scale(self.m_scale)
        self.m_transform.setMatrix(m)

    thetaChanged = pyqtSignal(float)

    @pyqtProperty(float, notify=thetaChanged)
    def theta(self):
        return self.m_theta

    @theta.setter
    def theta(self, value):
        if self.m_theta != value:
            self.m_theta = value
            self.thetaChanged.emit(value)
            self.updateTransform()

    phiChanged = pyqtSignal(float)

    @pyqtProperty(float, notify=phiChanged)
    def phi(self):
        return self.m_phi

    @phi.setter
    def phi(self, value):
        if self.m_phi != value:
            self.m_phi = value
            self.phiChanged.emit(value)
            self.updateTransform()

    scaleChanged = pyqtSignal(float)

    @pyqtProperty(float, notify=scaleChanged)
    def scale(self):
        return self.m_scale

    @scale.setter
    def scale(self, value):
        if self.m_scale != value:
            self.m_scale = value
            self.scaleChanged.emit(value)
            self.updateTransform()

    positionChanged = pyqtSignal(QVector3D)

    @pyqtProperty(QVector3D, notify=positionChanged)
    def position(self):
        return self.m_position

    @position.setter
    def position(self, value):
        if self.m_position != value:
            self.m_position = value
            self.positionChanged.emit(value)
            self.updateTransform()


class RotatingTrefoilKnot(TrefoilKnot):

    def __init__(self, parent=None):
        super(RotatingTrefoilKnot, self).__init__(parent)

        self.m_thetaAnimation = QPropertyAnimation()
        self.m_thetaAnimation.setDuration(2000)
        self.m_thetaAnimation.setStartValue(0.0)
        self.m_thetaAnimation.setEndValue(360.0)
        self.m_thetaAnimation.setLoopCount(-1)
        self.m_thetaAnimation.setTargetObject(self)
        self.m_thetaAnimation.setPropertyName(b'phi')
        self.m_thetaAnimation.start()
    
        self.m_phiAnimation = QPropertyAnimation()
        self.m_phiAnimation.setDuration(2000)
        self.m_phiAnimation.setStartValue(0.0)
        self.m_phiAnimation.setEndValue(360.0)
        self.m_phiAnimation.setLoopCount(-1)
        self.m_phiAnimation.setTargetObject(self)
        self.m_phiAnimation.setPropertyName(b'theta')
        self.m_phiAnimation.start()


class Barrel(RenderableEntity):

    # DiffuseColor
    (
        Red,
        Blue,
        Green,
        RustDiffuse,
        StainlessSteelDiffuse
    ) = range(5)

    diffuseColorsName = (
        'red',
        'blue',
        'green',
        'rust',
        'stainless_steel'
    )

    # SpecularColor
    (
        RustSpecular,
        StainlessSteelSpecular,
        None_
    ) = range(3)

    specularColorsName = (
        '_rust',
        '_stainless_steel',
        ''
    )

    # Bumps
    (
        NoBumps,
        SoftBumps,
        MiddleBumps,
        HardBumps
    ) = range(4)

    bumpsName = (
        'no_bumps',
        'soft_bumps',
        'middle_bumps',
        'hard_bumps'
    )

    def __init__(self, parent=None):
        super(Barrel, self).__init__(parent)

        self.m_bumps = Barrel.NoBumps
        self.m_diffuseColor = Barrel.Red
        self.m_specularColor = Barrel.None_
        self.m_material = QNormalDiffuseSpecularMapMaterial()
        self.m_diffuseTexture = self.m_material.diffuse()
        self.m_normalTexture = self.m_material.normal()
        self.m_specularTexture = self.m_material.specular()
        self.m_diffuseTextureImage = QTextureImage()
        self.m_normalTextureImage = QTextureImage()
        self.m_specularTextureImage = QTextureImage()

        self.mesh().setSource(
                QUrl.fromLocalFile('assets/metalbarrel/metal_barrel.obj'))
        self.transform().setScale(0.03)

        self.m_diffuseTexture.addTextureImage(self.m_diffuseTextureImage)
        self.m_normalTexture.addTextureImage(self.m_normalTextureImage)
        self.m_specularTexture.addTextureImage(self.m_specularTextureImage)

        self.setNormalTextureSource()
        self.setDiffuseTextureSource()
        self.setSpecularTextureSource()
        self.m_material.setShininess(10.0)
        self.addComponent(self.m_material)

    def setDiffuse(self, diffuse):
        if self.m_diffuseColor != diffuse:
            self.m_diffuseColor = diffuse
            self.setDiffuseTextureSource()

    def diffuse(self):
        return self.m_diffuseColor

    def setSpecular(self, specular):
        if self.m_specularColor != specular:
            self.m_specularColor = specular
            self.setSpecularTextureSource()

    def specular(self):
        return self.m_specularColor

    def setBumps(self, bumps):
        if self.m_bumps != bumps:
            self.m_bumps = bumps
            self.setNormalTextureSource()

    def bumps(self):
        return self.m_bumps

    def setShininess(self, shininess):
        if self.m_material.shininess() != shininess:
            self.m_material.setShininess(shininess)

    def shininess(self):
        return self.m_material.shininess()

    def setNormalTextureSource(self):
        self.m_normalTextureImage.setSource(
                QUrl.fromLocalFile('assets/metalbarrel/normal_' + Barrel.bumpsName[self.m_bumps] + '.webp'))

    def setDiffuseTextureSource(self):
        self.m_diffuseTextureImage.setSource(
                QUrl.fromLocalFile('assets/metalbarrel/diffus_' + Barrel.diffuseColorsName[self.m_diffuseColor] + '.webp'))

    def setSpecularTextureSource(self):
        self.m_specularTextureImage.setSource(
                QUrl.fromLocalFile('assets/metalbarrel/specular' + Barrel.specularColorsName[self.m_specularColor] + '.webp'))


class HousePlant(QEntity):

    # PotShape
    (
        Cross,
        Square,
        Triangle,
        Sphere
    ) = range(4)

    potNames = (
        'cross',
        'square',
        'triangle',
        'sphere'
    )

    # Plant
    (
        Bamboo,
        Palm,
        Pine,
        Spikes,
        Shrub
    ) = range(5)

    plantNames = (
        'bamboo',
        'palm',
        'pine',
        'spikes',
        'shrub'
    )

    def __init__(self, parent=None):
        super(HousePlant, self).__init__(parent)

        self.m_pot = RenderableEntity(self)
        self.m_plant = RenderableEntity(self.m_pot)
        self.m_cover = RenderableEntity(self.m_pot)

        self.m_potMaterial = QNormalDiffuseMapMaterial()
        self.m_plantMaterial = QNormalDiffuseMapAlphaMaterial()
        self.m_coverMaterial = QNormalDiffuseMapMaterial()

        self.m_potImage = QTextureImage()
        self.m_potNormalImage = QTextureImage()
        self.m_plantImage = QTextureImage()
        self.m_plantNormalImage = QTextureImage()
        self.m_coverImage = QTextureImage()
        self.m_coverNormalImage = QTextureImage()

        self.m_plantType = HousePlant.Bamboo
        self.m_potShape = HousePlant.Cross

        self.m_pot.transform().setScale(0.03)
        self.m_pot.addComponent(self.m_potMaterial)
        self.m_plant.addComponent(self.m_plantMaterial)
        self.m_cover.addComponent(self.m_coverMaterial)
    
        self.m_potMaterial.diffuse().addTextureImage(self.m_potImage)
        self.m_potMaterial.normal().addTextureImage(self.m_potNormalImage)
        self.m_plantMaterial.diffuse().addTextureImage(self.m_plantImage)
        self.m_plantMaterial.normal().addTextureImage(self.m_plantNormalImage)
        self.m_coverMaterial.diffuse().addTextureImage(self.m_coverImage)
        self.m_coverMaterial.normal().addTextureImage(self.m_coverNormalImage)
    
        self.updatePlantType()
        self.updatePotShape()
    
        self.m_coverImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/cover.webp'))
        self.m_coverNormalImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/cover_normal.webp'))
        self.m_potImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/pot.webp'))
        self.m_potNormalImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/pot_normal.webp'))
    
        self.m_potMaterial.setShininess(10.0)
        self.m_potMaterial.setSpecular(QColor.fromRgbF(0.75, 0.75, 0.75, 1.0))
    
        self.m_plantMaterial.setShininess(10.0)
    
        self.m_coverMaterial.setSpecular(QColor.fromRgbF(0.05, 0.05, 0.05, 1.0))
        self.m_coverMaterial.setShininess(5.0)

    def setPotShape(self, shape):
        if self.m_potShape != shape:
            self.m_potShape = shape
            self.updatePotShape()

    def potShape(self):
        return self.m_potShape

    def setPlantType(self, plant):
        if self.m_plantType != plant:
            self.m_plantType = plant
            self.updatePlantType()

    def plantType(self):
        return self.m_plantType

    def setPosition(self, pos):
        self.m_pot.transform().setTranslation(pos)

    def position(self):
        return self.m_pot.transform().translation()

    def setScale(self, scale):
        self.m_pot.transform().setScale(scale)

    def scale(self):
        return self.m_pot.transform().scale()

    def updatePotShape(self):
        self.m_pot.mesh().setSource(
                QUrl.fromLocalFile('assets/houseplants/' + HousePlant.potNames[self.m_potShape] + '-pot.obj'))
        self.m_plant.mesh().setSource(
                QUrl.fromLocalFile('assets/houseplants/' + HousePlant.potNames[self.m_potShape] + '-' + HousePlant.plantNames[self.m_plantType] + '.obj'))

    def updatePlantType(self):
        self.m_plant.mesh().setSource(
                QUrl.fromLocalFile('assets/houseplants/' + HousePlant.potNames[self.m_potShape] + '-' + HousePlant.plantNames[self.m_plantType] + '.obj'))

        self.m_plantImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/' + HousePlant.plantNames[self.m_plantType] + '.webp'))
        self.m_plantNormalImage.setSource(
                QUrl.fromLocalFile('assets/houseplants/' + HousePlant.plantNames[self.m_plantType] + '_normal.webp'))


# Change to the directory containing the example so that the path to the assets
# is correct.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = QGuiApplication(sys.argv)

view = Qt3DWindow()

# Scene root.
sceneRoot = QEntity()

# Scene camera.
basicCamera = view.camera()
basicCamera.setProjectionType(QCameraLens.PerspectiveProjection)
basicCamera.setAspectRatio(view.width() / view.height())
basicCamera.setUpVector(QVector3D(0.0, 1.0, 0.0))
basicCamera.setViewCenter(QVector3D(0.0, 3.5, 0.0))
basicCamera.setPosition(QVector3D(0.0, 3.5, 25.0))

# Camera controls.
camController = QFirstPersonCameraController(sceneRoot)
camController.setCamera(basicCamera)

# Scene floor.
planeEntity = PlaneEntity(sceneRoot)
planeEntity.mesh().setHeight(100.0)
planeEntity.mesh().setWidth(100.0)
planeEntity.mesh().setMeshResolution(QSize(20, 20))

normalDiffuseSpecularMapMaterial = QNormalDiffuseSpecularMapMaterial()
normalDiffuseSpecularMapMaterial.setTextureScale(10.0)
normalDiffuseSpecularMapMaterial.setShininess(80.0)
normalDiffuseSpecularMapMaterial.setAmbient(QColor.fromRgbF(0.2, 0.2, 0.2, 1.0))

diffuseImage = QTextureImage()
diffuseImage.setSource(
        QUrl.fromLocalFile('assets/textures/pattern_09/diffuse.webp'))
normalDiffuseSpecularMapMaterial.diffuse().addTextureImage(diffuseImage)

specularImage = QTextureImage()
specularImage.setSource(
        QUrl.fromLocalFile('assets/textures/pattern_09/specular.webp'))
normalDiffuseSpecularMapMaterial.specular().addTextureImage(specularImage)

normalImage = QTextureImage()
normalImage.setSource(
        QUrl.fromLocalFile('assets/textures/pattern_09/normal.webp'))
normalDiffuseSpecularMapMaterial.normal().addTextureImage(normalImage)

planeEntity.addComponent(normalDiffuseSpecularMapMaterial)

# Chest.
chest = RenderableEntity(sceneRoot)
chest.transform().setScale(0.03)
chest.mesh().setSource(QUrl.fromLocalFile('assets/chest/Chest.obj'))
diffuseMapMaterial = QDiffuseMapMaterial()
diffuseMapMaterial.setSpecular(QColor.fromRgbF(0.2, 0.2, 0.2, 1.0))
diffuseMapMaterial.setShininess(2.0)

chestDiffuseImage = QTextureImage()
chestDiffuseImage.setSource(QUrl.fromLocalFile('assets/chest/diffuse.webp'))
diffuseMapMaterial.diffuse().addTextureImage(chestDiffuseImage)

chest.addComponent(diffuseMapMaterial)

# Trefoil Knot.
trefoil = RotatingTrefoilKnot(sceneRoot)
trefoil.position = QVector3D(0.0, 3.5, 0.0)
trefoil.scale = 0.5

phongMaterial = QPhongMaterial()
phongMaterial.setDiffuse(QColor(204, 205, 75))
phongMaterial.setSpecular(Qt.white)

trefoil.addComponent(phongMaterial)

# Barrels.
basicBarrel = Barrel(sceneRoot)
basicBarrel.transform().setTranslation(QVector3D(8.0, 0.0, 0.0))

rustyBarrel = Barrel(sceneRoot)
rustyBarrel.setDiffuse(Barrel.RustDiffuse)
rustyBarrel.setSpecular(Barrel.RustSpecular)
rustyBarrel.setBumps(Barrel.HardBumps)
rustyBarrel.transform().setTranslation(QVector3D(10.0, 0.0, 0.0))

blueBarrel = Barrel(sceneRoot)
blueBarrel.setDiffuse(Barrel.Blue)
blueBarrel.setBumps(Barrel.MiddleBumps)
blueBarrel.transform().setTranslation(QVector3D(12.0, 0.0, 0.0))

greenBarrel = Barrel(sceneRoot)
greenBarrel.setDiffuse(Barrel.Green)
greenBarrel.setBumps(Barrel.SoftBumps)
greenBarrel.transform().setTranslation(QVector3D(14.0, 0.0, 0.0))

stainlessBarrel = Barrel(sceneRoot)
stainlessBarrel.setDiffuse(Barrel.StainlessSteelDiffuse)
stainlessBarrel.setBumps(Barrel.NoBumps)
stainlessBarrel.setSpecular(Barrel.StainlessSteelSpecular)
stainlessBarrel.setShininess(150.0)
stainlessBarrel.transform().setTranslation(QVector3D(16.0, 0.0, 0.0))

# Plants.
squareBamboo = HousePlant(sceneRoot)
squareBamboo.setPotShape(HousePlant.Square)
squareBamboo.setPosition(QVector3D(4.0, 0.0, 0.0))

trianglePalm = HousePlant(sceneRoot)
trianglePalm.setPlantType(HousePlant.Palm)
trianglePalm.setPotShape(HousePlant.Triangle)
trianglePalm.setPosition(QVector3D(0.0, 0.0, 4.0))

spherePine = HousePlant(sceneRoot)
spherePine.setPlantType(HousePlant.Pine)
spherePine.setPotShape(HousePlant.Sphere)
spherePine.setPosition(QVector3D(-4.0, 0.0, 0.0))

crossSpikes = HousePlant(sceneRoot)
crossSpikes.setPlantType(HousePlant.Spikes)
crossSpikes.setPosition(QVector3D(0.0, 0.0, -4.0))

crossPalm = HousePlant(sceneRoot)
crossPalm.setPlantType(HousePlant.Palm)
crossPalm.setPosition(QVector3D(0.0, 0.0, -8.0))
crossPalm.setScale(0.05)

crossShrub = HousePlant(sceneRoot)
crossShrub.setPlantType(HousePlant.Shrub)
crossShrub.setPosition(QVector3D(0.0, 0.0, 8.0))
crossShrub.setScale(0.05)

view.setRootEntity(sceneRoot)
view.show()

sys.exit(app.exec_())
