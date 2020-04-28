from dip.settings import SettingsManager
from dip.ui import Application, Dialog, SpinBox


# Every application needs an Application.
app = Application()

# Load the application's settings.
SettingsManager.load('riverbankcomputing.com')

# Create the model.
model = dict(name="Joe User", age=30)

# Define the view.
view_factory = Dialog('name', SpinBox('age', suffix=" years"), id='example',
        title="Dialog with Settings")

# Create an instance of the view bound to the model.
view = view_factory(model)

# Restore the geometry from the settings.
SettingsManager.restore(view.all_views())

# Enter the dialog's modal event loop.
view.execute()

# Save the geometry to the settings.
SettingsManager.save(view.all_views())

# Show the value of the model.
print("Name:", model['name'])
print("Age:", model['age'])
