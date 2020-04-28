from dip.automate import Robot
from dip.ui import Application, Dialog, SpinBox


# Every application needs an Application.
app = Application()

# Create the model.
model = dict(name='', age=0)

# Define the view.
view_factory = Dialog('name', SpinBox('age', suffix=" years"),
        id='dialog.person', title="Dialog Example")

# Create an instance of the view for the model.
view = view_factory(model)

# Create a robot with a default delay of 200ms between events.
robot = Robot(delay=200)

# Enter data into the two editors.
robot.record('dialog.person:name', 'set', "Joe User")
robot.record('dialog.person:age', 'set', 30)

# Click the Ok button.
robot.record('dialog.person', 'click', 'ok')

# Play the commands as soon as the event loop starts.
robot.play(after=0)

# Enter the dialog's modal event loop.
view.execute()

# Show the value of the model.
print("Name:", model['name'])
print("Age:", model['age'])
