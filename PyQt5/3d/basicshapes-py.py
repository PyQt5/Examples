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

from PyQt5.QtCore import pyqtSlot, QObject, QSize, Qt
from PyQt5.QtGui import QColor, QQuaternion, QVector3D
from PyQt5.QtWidgets import (QApplication, QCheckBox, QCommandLinkButton,
        QHBoxLayout, QVBoxLayout, QWidget)
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import (Qt3DWindow, QConeMesh, QCuboidMesh,
        QCylinderMesh, QFirstPersonCameraController, QPhongMaterial,
        QPlaneMesh, QSphereMesh, QTorusMesh)
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DRender import QCamera


class SceneModifier(QObject):

    def __init__(self, rootEntity):
        super(SceneModifier, self).__init__()

        self.m_rootEntity = rootEntity

        # Torus shape data.
        self.m_torus = QTorusMesh()
        self.m_torus.setRadius(1.0)
        self.m_torus.setMinorRadius(0.4)
        self.m_torus.setRings(100)
        self.m_torus.setSlices(20)

        # TorusMesh transform.
        torusTransform = QTransform()
        torusTransform.setScale(2.0)
        torusTransform.setRotation(
                QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), 25.0))
        torusTransform.setTranslation(QVector3D(5.0, 4.0, 0.0))

        torusMaterial = QPhongMaterial()
        torusMaterial.setDiffuse(QColor(0xbeb32b))

        # Torus.
        self.m_torusEntity = QEntity(self.m_rootEntity)
        self.m_torusEntity.addComponent(self.m_torus)
        self.m_torusEntity.addComponent(torusMaterial)
        self.m_torusEntity.addComponent(torusTransform)

        # Cone shape data.
        cone = QConeMesh()
        cone.setTopRadius(0.5)
        cone.setBottomRadius(1)
        cone.setLength(3)
        cone.setRings(50)
        cone.setSlices(20)

        # ConeMesh transform.
        coneTransform = QTransform()
        coneTransform.setScale(1.5)
        coneTransform.setRotation(
                QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 45.0))
        coneTransform.setTranslation(QVector3D(0.0, 4.0, -1.5))

        coneMaterial = QPhongMaterial()
        coneMaterial.setDiffuse(QColor(0x928327))

        # Cone.
        self.m_coneEntity = QEntity(self.m_rootEntity)
        self.m_coneEntity.addComponent(cone)
        self.m_coneEntity.addComponent(coneMaterial)
        self.m_coneEntity.addComponent(coneTransform)

        # Cylinder shape data.
        cylinder = QCylinderMesh()
        cylinder.setRadius(1)
        cylinder.setLength(3)
        cylinder.setRings(100)
        cylinder.setSlices(20)

        # CylinderMesh transform.
        cylinderTransform = QTransform()
        cylinderTransform.setScale(1.5)
        cylinderTransform.setRotation(
                QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 45.0))
        cylinderTransform.setTranslation(QVector3D(-5.0, 4.0, -1.5))

        cylinderMaterial = QPhongMaterial()
        cylinderMaterial.setDiffuse(QColor(0x928327))

        # Cylinder.
        self.m_cylinderEntity = QEntity(self.m_rootEntity)
        self.m_cylinderEntity.addComponent(cylinder)
        self.m_cylinderEntity.addComponent(cylinderMaterial)
        self.m_cylinderEntity.addComponent(cylinderTransform)

        # Cuboid shape data.
        cuboid = QCuboidMesh()

        # CuboidMesh transform.
        cuboidTransform = QTransform()
        cuboidTransform.setScale(4.0)
        cuboidTransform.setTranslation(QVector3D(5.0, -4.0, 0.0))

        cuboidMaterial = QPhongMaterial()
        cuboidMaterial.setDiffuse(QColor(0x665423))

        # Cuboid.
        self.m_cuboidEntity = QEntity(self.m_rootEntity)
        self.m_cuboidEntity.addComponent(cuboid)
        self.m_cuboidEntity.addComponent(cuboidMaterial)
        self.m_cuboidEntity.addComponent(cuboidTransform)

        # Plane shape data.
        planeMesh = QPlaneMesh()
        planeMesh.setWidth(2)
        planeMesh.setHeight(2)

        # Plane mesh transform.
        planeTransform = QTransform()
        planeTransform.setScale(1.3)
        planeTransform.setRotation(
                QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 45.0))
        planeTransform.setTranslation(QVector3D(0.0, -4.0, 0.0))

        planeMaterial = QPhongMaterial()
        planeMaterial.setDiffuse(QColor(0xa69929))

        # Plane.
        self.m_planeEntity = QEntity(self.m_rootEntity)
        self.m_planeEntity.addComponent(planeMesh)
        self.m_planeEntity.addComponent(planeMaterial)
        self.m_planeEntity.addComponent(planeTransform)

        # Sphere shape data.
        sphereMesh = QSphereMesh()
        sphereMesh.setRings(20)
        sphereMesh.setSlices(20)
        sphereMesh.setRadius(2)

        # Sphere mesh transform.
        sphereTransform = QTransform()
        sphereTransform.setScale(1.3)
        sphereTransform.setTranslation(QVector3D(-5.0, -4.0, 0.0))

        sphereMaterial = QPhongMaterial()
        sphereMaterial.setDiffuse(QColor(0xa69929))

        # Sphere.
        self.m_sphereEntity = QEntity(self.m_rootEntity)
        self.m_sphereEntity.addComponent(sphereMesh)
        self.m_sphereEntity.addComponent(sphereMaterial)
        self.m_sphereEntity.addComponent(sphereTransform)

    @pyqtSlot(int)
    def enableTorus(self, enabled):
        self.m_torusEntity.setParent(self.m_rootEntity if enabled else None)

    @pyqtSlot(int)
    def enableCone(self, enabled):
        self.m_coneEntity.setParent(self.m_rootEntity if enabled else None)

    @pyqtSlot(int)
    def enableCylinder(self, enabled):
        self.m_cylinderEntity.setParent(self.m_rootEntity if enabled else None)

    @pyqtSlot(int)
    def enableCuboid(self, enabled):
        self.m_cuboidEntity.setParent(self.m_rootEntity if enabled else None)

    @pyqtSlot(int)
    def enablePlane(self, enabled):
        self.m_planeEntity.setParent(self.m_rootEntity if enabled else None)

    @pyqtSlot(int)
    def enableSphere(self, enabled):
        self.m_sphereEntity.setParent(self.m_rootEntity if enabled else None)


app = QApplication(sys.argv)

view = Qt3DWindow()
view.defaultFrameGraph().setClearColor(QColor(0x4d4d4f))
container = QWidget.createWindowContainer(view)
screenSize = view.screen().size()
container.setMinimumSize(QSize(200, 100))
container.setMaximumSize(screenSize)

widget = QWidget()
hLayout = QHBoxLayout(widget)
vLayout = QVBoxLayout()
vLayout.setAlignment(Qt.AlignTop)
hLayout.addWidget(container, 1)
hLayout.addLayout(vLayout)

widget.setWindowTitle("Basic shapes")

aspect = QInputAspect()
view.registerAspect(aspect)

# Root entity.
rootEntity = QEntity()

# Camera.
cameraEntity = view.camera()

cameraEntity.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
cameraEntity.setPosition(QVector3D(0.0, 0.0, 20.0))
cameraEntity.setUpVector(QVector3D(0.0, 1.0, 0.0))
cameraEntity.setViewCenter(QVector3D(0.0, 0.0, 0.0))

# For camera controls.
camController = QFirstPersonCameraController(rootEntity)
camController.setCamera(cameraEntity)

# Scene modifier.
modifier = SceneModifier(rootEntity)

# Set root object of the scene.
view.setRootEntity(rootEntity)

# Create control widgets.
info = QCommandLinkButton(text="Qt3D ready-made meshes")
info.setDescription("Qt3D provides several ready-made meshes, like torus, "
        "cylinder, cone, cube, plane and sphere.")
info.setIconSize(QSize(0,0))

torusCB = QCheckBox(checked=True, text="Torus")
coneCB = QCheckBox(checked=True, text="Cone")
cylinderCB = QCheckBox(checked=True, text="Cylinder")
cuboidCB = QCheckBox(checked=True, text="Cuboid")
planeCB = QCheckBox(checked=True, text="Plane")
sphereCB = QCheckBox(checked=True, text="Sphere")

vLayout.addWidget(info)
vLayout.addWidget(torusCB)
vLayout.addWidget(coneCB)
vLayout.addWidget(cylinderCB)
vLayout.addWidget(cuboidCB)
vLayout.addWidget(planeCB)
vLayout.addWidget(sphereCB)

torusCB.stateChanged.connect(modifier.enableTorus)
coneCB.stateChanged.connect(modifier.enableCone)
cylinderCB.stateChanged.connect(modifier.enableCylinder)
cuboidCB.stateChanged.connect(modifier.enableCuboid)
planeCB.stateChanged.connect(modifier.enablePlane)
sphereCB.stateChanged.connect(modifier.enableSphere)

# Show the window.
widget.show()
widget.resize(1200, 800)

sys.exit(app.exec_())
