import sys

from dip.io import IFilterHints, IoManager
from dip.io.codecs.unicode import (UnicodeCodec, IUnicodeDecoder,
        IUnicodeEncoder)
from dip.io.storage.filesystem import FilesystemStorageFactory
from dip.model import (adapt, Adapter, implements, Instance, notify_observers,
        unadapted)
from dip.shell import (BaseManagedModelTool, IManagedModel, IManagedModelTool,
        IShell)
from dip.shell.shells.main_window import MainWindowShell
from dip.shell.tools.dirty import DirtyTool
from dip.shell.tools.model_manager import ModelManagerTool
from dip.shell.tools.quit import QuitTool
from dip.ui import Action, Application


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


@adapt(PythonCode, to=IManagedModel)
class PythonCodeIManagedModelAdapter(Adapter):
    """ Adapt PythonCode to the IManagedModel interface. """

    # The native format is Unicode (specifically UTF-8).
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

        return model.editor.text()


@implements(IManagedModelTool)
class PythonCodeEditorTool(BaseManagedModelTool):
    """ The PythonCodeEditorTool implements a tool for editing Python code.  It
    leaves the management of the lifecycle of the model containing the code to
    a model manager.
    """

    # The tool's identifier.
    id = 'myorganization.shell.tools.source_code_editor'

    # The action that toggles the use of line numbers by the editor.
    line_nrs = Action(text="Show Line Numbers", checked=False,
            within='dip.ui.collections.view')

    # To keep the application simple we only allow one model to be handled at a
    # time.
    model_policy = 'one'

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

    def _configure_line_nrs(self, view):
        """ Configure the state of line numbers for a view depending on the
        state of the line number action.
        """

        # Line numbers are configured by setting the width of the first margin.
        margin_width = 30 if self.line_nrs.checked else 0

        unadapted(view).setMarginWidth(0, margin_width)


# Every application needs an Application.
app = Application()

# Add our codec and support for filesystem storage.
IoManager.codecs.append(
        UnicodeCodec(format='myorganization.formats.python_code'))
IoManager.storage_factories.append(FilesystemStorageFactory())

# Define the shell.
view_factory = MainWindowShell(main_area_policy='single',
        tool_factories=[
                DirtyTool,
                lambda: ModelManagerTool(model_factories=[PythonCode]),
                PythonCodeEditorTool,
                QuitTool],
        title_template="[view][*]")

# Create the shell.
view = view_factory()

# If a command line argument was given try and open it as Python code.
if len(sys.argv) > 1:
    IShell(view).open('myorganization.shell.tools.source_code_editor',
            sys.argv[1], 'myorganization.formats.python_code')

# Make the shell visible.
view.visible = True

# Enter the event loop.
app.execute()
