import sys

from PyQt5.QtWidgets import (QApplication, QFormLayout, QLineEdit, QSpinBox,
        QWidget)

from dip.ui import Bindings


# Every application needs an QApplication.
app = QApplication(sys.argv)

# Create the model.
model = dict(name="Joe User", age=30)

# Create the view programmatically.
layout = QFormLayout()
layout.addRow("Name", QLineEdit(objectName='name_editor'))
layout.addRow("Age", QSpinBox(objectName='age_editor'))

toolkit_view = QWidget(windowTitle="Bindings")
toolkit_view.setLayout(layout)

# Define the bindings.
bindings = Bindings(name_editor='name', age_editor='age')

# Bind the view to the model.
bindings.bind(toolkit_view, model)

# Make the instance of the view visible.
toolkit_view.show()

# Enter the event loop.
app.exec()

# Show the value of the model.
print("Name:", model['name'])
print("Age:", model['age'])
