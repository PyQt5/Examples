from dip.automate import Robot
from dip.ui import Application, Form


# Every application needs an Application.
app = Application()

# Create the model.
model = dict(name='')

# Define the view.
view_factory = Form(title="Simple Example")

# Create an instance of the view bound to the model.
view = view_factory(model)

# Make the instance of the view visible.
view.visible = True

# Simulate the events to set the name.
Robot.simulate('name', 'set', "Joe User", delay=200)

# Show the value of the model.
print("Name:", model['name'])
