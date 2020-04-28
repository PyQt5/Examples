from dip.model import Enum, Int, Model, Str
from dip.ui import (Application, Dialog, DialogController, GroupBox,
        MessageArea, SpinBox)


class Person(Model):
    """ The Person class encapsulates the data held about an individual. """

    # The person's name.
    name = Str(required='stripped', tool_tip="The person's name",
            whats_this="The name of the person. It must be at least two "
                    "characters and can include spaces.")

    # The person's gender.
    gender = Enum('female', 'male')

    # The person's age.
    age = Int(1, minimum=1)

    # The number of the children the person has had.  It is only applicable if
    # the person is female.
    children = Int()

    # The person's driving license number.  A person must be 17 or older to
    # hold a driving license.
    driving_license = Str(tool_tip="The person's driving license number")


class PersonController(DialogController):
    """ The PersonController class implements a controller for a view that
    allows the update of a Person instance.
    """

    def validate_view(self):
        """ Validate the data in the view.

        :return:
            a string which will be empty if the view is valid, otherwise it
            will explain why the view is invalid.
        """

        if self.view.driving_license.value != '' and self.view.age.value < 17:
            invalid_reason = "A person must be at least 17 years old " \
                    "to hold a driving license."
        else:
            invalid_reason = ''

        return invalid_reason

    def update_view(self):
        """ Update the state of the view. """

        # The 'children' editor is only enabled if the gender is female.
        self.view.children.enabled = (self.view.gender.value == 'female')

        super().update_view()


# Every application needs an Application.
app = Application()

# Create the model.
model = Person()

# Define the view.
view_factory = Dialog(
        GroupBox(
            'name',
            SpinBox('age', suffix=" years"),
            'gender',
            'children',
            'driving_license',
            title="Person Record"
        ),
        MessageArea(),
        controller_factory=PersonController,
        title="Validate"
    )

# Create an instance of the view bound to the model.
view = view_factory(model)

# Enter the dialog's modal event loop.
view.execute()

# Show the attributes of the model.
print("Name:", model.name)
print("Gender:", model.gender)
print("Age:", model.age)
print("Children:", model.children)
print("Driving license:", model.driving_license)
