import glob
import os

from dip.model import List, Model, observe, Str
from dip.ui import (Application, FilesystemLocationEditor, Form, HBox,
        ListEditor, MessageArea, PushButton, Stretch, VBox, Wizard,
        WizardController, WizardPage)


class LineCounterWizardController(WizardController):
    """ The LineCounterWizardController class is a controller that handles the
    interactions between the filters editor and the push buttons that add and
    remove filters from the list.
    """

    @observe('view.add_filter.value')
    def __on_add_filter_changed(self, change):
        """ Invoked when the button to add a filter is pressed. """

        self.view.filters.append_new_element()

    @observe('view.remove_filter.value')
    def __on_remove_filter_changed(self, change):
        """ Invoked when the button to remove a filter is pressed. """

        self.view.filters.remove_selected_element()

    @observe('view.filters.selection')
    def __on_filters_selection_changed(self, change):
        """ Invoked when the selection of the filters editor changes. """

        # Only enable the button to remove a filter if a filter is selected.
        self.view.remove_filter.enabled = (change.new >= 0)


class LineCounter(Model):
    """ The LineCounter class is a combined model and view for counting the
    total number of lines in a set of files.
    """

    # The name of the root directory.
    root_directory = Str()

    # The list of glob-like filters to apply to names of files in the directory
    # hierachy.  If the list is empty then all files are processed.
    filters = List(Str(required='stripped'))

    # The wizard used to get the input from the user.  Note that this is an
    # ordinary class attribute.
    wizard = Wizard(
            WizardPage(
                VBox (
                    Form(
                        FilesystemLocationEditor('root_directory',
                                mode='directory', required=True)
                    ),
                    Stretch(),
                    MessageArea()
                ),
                title="Directory name",
                subtitle="Enter the name of the directory containing the "
                        "files whose lines are to be counted."
            ),
            WizardPage(
                VBox(
                    HBox (
                        ListEditor('filters'),
                        VBox (
                            PushButton(id='add_filter'),
                            PushButton(id='remove_filter', enabled=False),
                            Stretch()
                        ),
                    ),
                    MessageArea()
                ),
                title="File filters",
                subtitle="Enter the glob-like filters to apply to the file "
                        "names."
            ),
            controller_factory=LineCounterWizardController,
            title="Line counter"
        )

    def populate(self):
        """ Populate the model with input from the user.

        :return:
            ``True`` if the user didn't cancel.
        """

        wizard = self.wizard(self)

        return wizard.execute()

    def perform(self):
        """ Count the number of lines and display the total. """

        filepaths = []

        for dirpath, _, filenames in os.walk(self.root_directory):
            if len(self.filters) == 0:
                # There are no filters so look at each file.
                for filename in filenames:
                    filepaths.append(os.path.join(dirpath, filename))
            else:
                # Apply the filters.
                for filter in self.filters:
                    filepaths.extend(glob.glob(os.path.join(dirpath, filter)))

        # Count the files in each file.
        line_count = 0

        for filepath in filepaths:
            try:
                with open(filepath) as fh:
                    line_count += len(fh.readlines())
            except UnicodeDecodeError:
                # Assume it is a binary file and ignore it.
                pass
            except EnvironmentError as err:
                Application.warning("Line counter",
                        "There was an error reading the file <tt>{0}</tt>."
                                .format(filepath),
                        detail=str(err))

        # Tell the user.
        Application.information("Line counter",
                "There were {0} lines in {1} files.".format(line_count,
                        len(filepaths)))


# Every application needs an Application.
app = Application()

# Create the model/view.
line_counter = LineCounter()

# Populate the model with input from the user.
if line_counter.populate():
    # Perform the task, i.e. count the lines.
    line_counter.perform()
