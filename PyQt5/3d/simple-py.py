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


import sys

from PyQt5.QtCore import (pyqtProperty, pyqtSignal, qFuzzyCompare, QObject,
        QPropertyAnimation)
from PyQt5.QtGui import QGuiApplication, QMatrix4x4, QQuaternion, QVector3D
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QCamera
from PyQt5.Qt3DExtras import (Qt3DWindow, QOrbitCameraController,
        QPhongMaterial, QSphereMesh, QTorusMesh)


class OrbitTransformController(QObject):

    def __init__(self, parent=None):
        super(OrbitTransformController, self).__init__(parent)

        self.m_target = None
        self.m_matrix = QMatrix4x4()
        self.m_radius = 1.0
        self.m_angle = 0.0

    targetChanged = pyqtSignal()

    @pyqtProperty(QTransform, notify=targetChanged)
    def target(self):
        return self.m_target

    @target.setter
    def target(self, target):
        if self.m_target is not target:
            self.m_target = target
            self.targetChanged.emit()

    radiusChanged = pyqtSignal()

    @pyqtProperty(float, notify=radiusChanged)
    def radius(self):
        return self.m_radius

    @radius.setter
    def radius(self, radius):
        if not qFuzzyCompare(self.m_radius, radius):
            self.m_radius = radius
            self.updateMatrix()
            self.radiusChanged.emit()

    angleChanged = pyqtSignal()

    @pyqtProperty(float, notify=angleChanged)
    def angle(self):
        return self.m_angle

    @angle.setter
    def angle(self, angle):
        if not qFuzzyCompare(self.m_angle, angle):
            self.m_angle = angle
            self.updateMatrix()
            self.angleChanged.emit()

    def updateMatrix(self):
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(0.0, 1.0, 0.0))
        self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)


def createScene():
    # Root entity.
    rootEntity = QEntity()

    # Material.
    material = QPhongMaterial(rootEntity)

    # Torus.
    torusEntity = QEntity(rootEntity)
    torusMesh = QTorusMesh()
    torusMesh.setRadius(5)
    torusMesh.setMinorRadius(1)
    torusMesh.setRings(100)
    torusMesh.setSlices(20)

    torusTransform = QTransform()
    torusTransform.setScale3D(QVector3D(1.5, 1.0, 0.5))
    torusTransform.setRotation(
            QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 45.0))

    torusEntity.addComponent(torusMesh)
    torusEntity.addComponent(torusTransform)
    torusEntity.addComponent(material)

    # Sphere.
    sphereEntity = QEntity(rootEntity)
    sphereMesh = QSphereMesh()
    sphereMesh.setRadius(3)

    sphereTransform = QTransform()
    controller = OrbitTransformController(sphereTransform)
    controller.target = sphereTransform
    controller.radius = 20.0

    sphereRotateTransformAnimation = QPropertyAnimation(sphereTransform)
    sphereRotateTransformAnimation.setTargetObject(controller)
    sphereRotateTransformAnimation.setPropertyName(b'angle')
    sphereRotateTransformAnimation.setStartValue(0)
    sphereRotateTransformAnimation.setEndValue(360)
    sphereRotateTransformAnimation.setDuration(10000)
    sphereRotateTransformAnimation.setLoopCount(-1)
    sphereRotateTransformAnimation.start()

    sphereEntity.addComponent(sphereMesh)
    sphereEntity.addComponent(sphereTransform)
    sphereEntity.addComponent(material)

    return rootEntity


app = QGuiApplication(sys.argv)
view = Qt3DWindow()

scene = createScene()

# Camera.
camera = view.camera()
camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
camera.setPosition(QVector3D(0.0, 0.0, 40.0))
camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))

# For camera controls.
camController = QOrbitCameraController(scene)
camController.setLinearSpeed(50.0)
camController.setLookSpeed(180.0)
camController.setCamera(camera)

view.setRootEntity(scene)
view.show()

sys.exit(app.exec_())
