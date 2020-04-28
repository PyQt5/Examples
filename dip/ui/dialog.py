from dip.ui import Application, Dialog, SpinBox


# Every application needs an Application.
app = Application()

# Create the model.
model = dict(name="Joe User", age=30)

# Define the view.
view_factory = Dialog('name', SpinBox('age', suffix=" years"), title="Dialog")

# Create an instance of the view bound to the model.
view = view_factory(model)

# Enter the dialog's modal event loop.
view.execute()

# Show the value of the model.
print("Name:", model['name'])
print("Age:", model['age'])
