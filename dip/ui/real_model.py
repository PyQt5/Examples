from PyQt5.QtWidgets import QHBoxLayout, QWidget

from dip.model import Int, Model, Str, unadapted
from dip.ui import Application, Form, SpinBox


# Define the model.
class ExampleModel(Model):

    # The name.
    name = Str(tool_tip="The person's full name")
    
    # The age in years.
    age = Int(minimum=0, maximum=120)


# Every application needs an Application.
app = Application()

# Create the model.
model = ExampleModel()

# Define the sub-view.
subview_factory = Form('name', SpinBox('age', suffix=" years"))

# Create two instances of the sub-view bound to the same model.
subview_left = subview_factory(model, top_level=False)
subview_right = subview_factory(model, top_level=False)

# Create a regular PyQt widget showing the two sub-views side by side.
layout = QHBoxLayout()
layout.addLayout(unadapted(subview_left))
layout.addLayout(unadapted(subview_right))

view = QWidget(windowTitle="Real Model")
view.setLayout(layout)
view.show()

# Enter the event loop.
app.execute()

# Show the value of the model.
print("Name:", model.name)
print("Age:", model.age)
