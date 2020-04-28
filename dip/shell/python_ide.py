import sys

from dip.io import IFilterHints, IoManager
from dip.io.codecs.unicode import UnicodeCodec, IUnicodeDecoder, IUnicodeEncoder
from dip.io.codecs.xml import XmlCodec, IXmlDecoder, IXmlEncoder
from dip.io.storage.filesystem import FilesystemStorageFactory
from dip.model import (adapt, Adapter, implements, Instance, List, Model,
        notify_observers, observe, Str, unadapted)
from dip.shell import (BaseManagedModelTool, IManagedModel, IManagedModelTool,
        IShell)
from dip.shell.shells.main_window import MainWindowShell
from dip.shell.tools.dirty import DirtyTool
from dip.shell.tools.form import FormTool
from dip.shell.tools.model_manager import ModelManagerTool
from dip.shell.tools.quit import QuitTool
from dip.ui import (Action, Application, Controller, IDisplay, MessageArea,
        IView)


class PythonCode(object):
    """ The PythonCode class encapsulates the code that implements a single
    Python module.
    """

    def __init__(self):
        """ Invoked to return the default editor widget. """

        from PyQt5.Qsci import QsciLexerPython, QsciScintilla

        editor = QsciScintilla()

        # Configure the editor for Python.
        editor.setUtf8(True)
        editor.setLexer(QsciLexerPython(editor))
        editor.setFolding(QsciScintilla.PlainFoldStyle, 1)
        editor.setIndentationGuides(True)
        editor.setIndentationWidth(4)

        self.editor = editor


@implements(IDisplay)
class PythonCodeFactory(Model):
    """ A PythonCode factory that implements the IDisplay interface. """

    # The model type name used in model manager dialogs and wizards.
    name = "Python code"

    def __call__(self):
        """ Invoked by the model manager to create the model instance. """

        return PythonCode()


@adapt(PythonCode, to=IManagedModel)
class PythonCodeIManagedModelAdapter(Adapter):
    """ Adapt PythonCode to the IManagedModel interface. """

    # The native format.
    native_format = 'myorganization.formats.python_code'

    def __init__(self):
        """ Initialise the adapter. """

        # Convert the Qt signal to the corresponding dip attribute change.
        self.adaptee.editor.modificationChanged.connect(
                lambda modified: notify_observers(
                        'dirty', self, modified, not modified))

    @IManagedModel.dirty.getter
    def dirty(self):
        """ Invoked to get the dirty state. """

        return self.adaptee.editor.isModified()

    @dirty.setter
    def dirty(self, value):
        """ Invoked to set the dirty state. """

        self.adaptee.editor.setModified(value)


@adapt(PythonCode, to=[IFilterHints, IUnicodeDecoder, IUnicodeEncoder])
class PythonCodeCodecAdapter(Adapter):
    """ Adapt PythonCode to the IFilterHints, IUnicodeDecoder and
    IUnicodeEncoder interfaces.
    """

    # The filter to use if the code is being stored in a file.
    filter = "Python source files (*.py *.pyw)"

    def set_unicode(self, model, data):
        """ Set the code from a unicode string object. """

        model.editor.setText(data)
        model.editor.setModified(False)

        return model

    def get_unicode(self, model):
        """ Return the code as a unicode string object. """

        # Note that Python v2 will require this to be wrapped in a call to
        # unicode().
        return model.editor.text()


@implements(IManagedModelTool, IDisplay)
class PythonCodeEditorTool(BaseManagedModelTool):
    """ The PythonCodeEditorTool implements a tool for editing Python code.  It
    leaves the management of the lifecycle of the model containing the code to
    a model manager.
    """

    # The tool's identifier.
    id = 'myorganization.shell.tools.source_code_editor'

    # The action that toggles the use of line numbers by the editor.
    line_nrs = Action(text="Show Line Numbers", checked=False, enabled=False,
            within='dip.ui.collections.view')

    # The Python code editor name used in model manager dialogs and wizards.
    name = "Python source code editor"

    def create_views(self, model):
        """ Invoked to create the views for a model. """

        # We have chosen to use the editor widget to hold the code so the view
        # is actually in the model.
        view = model.editor

        # Configure the view according to the state of the action.
        self._configure_line_nrs(view)

        return [view]

    def handles(self, model):
        """ Check that the tool can handle the model. """

        # Because the application only has one type of model we could just
        # return True.
        return isinstance(model, PythonCode)

    @line_nrs.triggered
    def line_nrs(self):
        """ Invoked when the line number action is triggered. """

        self._configure_line_nrs(self.current_view)

    @observe('current_view')
    def __current_view_changed(self, change):
        """ Invoked when the tool's current view changes. """

        self.line_nrs.enabled = (change.new is not None)

    def _configure_line_nrs(self, view):
        """ Configure the state of line numbers for a view depending on the
        state of the line number action.
        """

        # Line numbers are configured by setting the width of the first margin.
        margin_width = 30 if self.line_nrs.checked else 0

        unadapted(view).setMarginWidth(0, margin_width)


class Project(Model):
    """ The Project class encapsulates a project. """

    # The name of the project.
    name = Str(required='stripped')

    # A multi-line description of the project.
    description = Str()

    # The storage locations containing the source code that makes up the
    # project.
    contents = List(Str())


@implements(IDisplay)
class ProjectFactory(Model):
    """ A Project factory that implements the IDisplay interface. """

    # The model type name used in model manager dialogs and wizards.
    name = "Project"

    def __call__(self):
        """ Invoked my the model manager to create the model instance. """

        return Project()


@adapt(Project, to=IManagedModel)
class ProjectIManagedModelAdapter(Adapter):
    """ Adapt Project to the IManagedModel interface. """

    # The native format.
    native_format = 'myorganization.formats.project'


@adapt(Project, to=[IFilterHints, IXmlDecoder, IXmlEncoder])
class ProjectCodecAdapter(Adapter):
    """ Adapt Project to the IFilterHints, IXmlDecoder and IXmlEncoder
    interfaces.
    """

    # The filter to use if the project is being stored in a file.
    filter = "Project files (*.prj)"


class ProjectEditorController(Controller):
    """ The ProjectEditorController implements the controller for the default
    project editor view.
    """

    @observe('view.add_file.value')
    def __on_add_file_changed(self, change):
        """ Invoked when the button to add a file is pressed. """

        self.view.contents.append_new_element()

    @observe('view.remove_file.value')
    def __on_remove_file_changed(self, change):
        """ Invoked when the button to remove a file is pressed. """

        self.view.contents.remove_selected_element()

    @observe('view.contents.selection')
    def __on_contents_selection_changed(self, change):
        """ Invoked when the selection of the contents editor changes. """

        # Only enable the button to remove a file if a file is selected.
        self.view.remove_file.enabled = (change.new >= 0)


@implements(IDisplay)
class ProjectEditorTool(FormTool):
    """ The ProjectEditorTool implements a tool for editing a project.  It
    leaves the management of the lifecycle of the model containing the code to
    a model manager.
    """

    # The tool's identifier.
    id = 'myorganization.shell.tools.project_editor'

    # The sub-class of Model that the tool can handle.
    model_type = Project

    # The project editor name used in model manager dialogs and wizards.
    name = "Project editor"

    # The controller factory for the view.
    controller_factory = ProjectEditorController

    @FormTool.view_factory.default
    def view_factory(self):
        """ Invoked to return the default view factory. """

        from dip.ui import (Form, HBox, ListEditor, StorageLocationEditor,
                PushButton, Stretch, TextEditor, VBox)

        return Form(
            'name',
            TextEditor('description'),
            HBox(
                ListEditor(
                    'contents',
                    editor_factory=StorageLocationEditor(
                        filter_hints="Python source files (*.py *.pyw)",
                        format='myorganization.formats.python_code',
                        title="Choose project contents"
                    )
                ),
                VBox(
                    PushButton(id='add_file'),
                    PushButton(id='remove_file', enabled=False),
                    Stretch()
                )
            ),
            MessageArea()
        )


# Every application needs an Application.
app = Application()

# Add our codecs and support for filesystem storage.
IoManager.codecs.append(
        UnicodeCodec(format='myorganization.formats.python_code'))
IoManager.codecs.append(XmlCodec(format='myorganization.formats.project'))
IoManager.storage_factories.append(FilesystemStorageFactory())

# Define the shell.
view_factory = MainWindowShell(
        tool_factories=[
                DirtyTool,
                lambda: ModelManagerTool(
                        model_factories=[ProjectFactory(),
                                PythonCodeFactory()]),
                ProjectEditorTool,
                PythonCodeEditorTool,
                QuitTool],
        title="Python IDE[*]")

# Create the shell.
view = view_factory()

# If a command line argument was given try and open it as a project.
if len(sys.argv) > 1:
    IShell(ui).open('myorganization.shell.tools.project_editor', sys.argv[1],
            'myorganization.formats.project')

# Make the shell visible.
view.visible = True

# Enter the event loop.
app.execute()
