from dip.model import Bool, Model, observe, Str
from dip.ui import (Application, Action, Controller, Form, Menu, MenuBar,
        ToolButton, VBox)
from dip.ui.actions import QuitAction


class ExampleModel(Model):

    # The name.
    name = Str()

    # The gender.
    male = Bool()


class ExampleController(Controller):

    @observe('view.quit.trigger')
    def __on_quit_triggered(self, change):
        """ Invoked when the action it is bound to is triggered. """

        Application().quit()

    @observe('view.toggle_quit.trigger')
    def __on_toggle_quit_triggered(self, change):
        """ Invoked when the action it is bound to is triggered. """

        # Get the toolkit independent object that implements the Quit action.
        action = self.view.quit

        # Toggle the action's state.
        action.enabled = not action.enabled


# Every application needs an Application.
app = Application()

# Create the model.
model = ExampleModel(name="Joe User", male=True)

# Define the view.
view_factory = VBox(
    MenuBar(
        Menu(QuitAction(id='quit'), title="&File"),
        Menu(Action(id='toggle_quit'), Menu(Action('male'), title="Sub-menu"),
                title="&Examples")),
    Form('name'),
    ToolButton(action='quit'),
    controller_factory=ExampleController)

# Create an instance of the view bound to the model.
view = view_factory(model)

# Make the instance of the view visible.
view.visible = True

# Enter the event loop.
app.execute()

# Show the value of the model.
print("Name:", model.name)
print("Male?:", model.male)
