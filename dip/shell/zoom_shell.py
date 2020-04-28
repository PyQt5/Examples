from dip.model import Bool, Float, implements, Model, unadapted
from dip.shell import ITool
from dip.shell.shells.main_window import MainWindowShell
from dip.shell.tools.quit import QuitTool
from dip.ui import Action, ActionCollection, Application


@implements(ITool)
class ZoomTool(Model):
    """ The ZoomTool class implements a simple shell tool that zooms in and out
    of its view.
    """

    # The increment (decrement) when zooming in (out).
    increment = Float(1.25)

    # This action shows if the view is at its normal size and toggles between
    # its normal size and previous size.
    normal_size = Action(checked=True)

    # The collection of actions.  By specifying 'text' we are hinting to the
    # toolkit that we would like the actions to be placed in a sub-menu.
    zoom = ActionCollection('zoom_in', 'normal_size', 'zoom_out', text="Zoom",
            within='dip.ui.collections.tools')

    # The Zoom In action.
    zoom_in = Action()

    # The Zoom Out action.
    zoom_out = Action()

    # The current font size.
    _current_size = Float()

    # The default, i.e. normal, font size.
    _default_size = Float()

    # The previous, non-default font size.
    _previous_size = Float()

    # Set if the font uses pixels rather than points.
    _uses_pixels = Bool()

    @normal_size.triggered
    def normal_size(self):
        """ Invoked when the Normal Size action is triggered. """

        self._set_size(
                self._default_size if self.normal_size.checked
                else self._previous_size)

    @ITool.views.default
    def views(self):
        """ Invoked to return the default views. """

        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QLabel

        return [QLabel("Hello world", alignment=Qt.AlignCenter)]

    @zoom_in.triggered
    def zoom_in(self):
        """ Invoked when the Zoom In action is triggered. """

        self._set_size(self._current_size * self.increment)

    @zoom_out.triggered
    def zoom_out(self):
        """ Invoked when the Zoom Out action is triggered. """

        self._set_size(self._current_size / self.increment)

    @_current_size.default
    def _current_size(self):
        """ Invoked to return the default current font size. """

        return self._default_size

    @_default_size.default
    def _default_size(self):
        """ Invoked to return the default default font size. """

        from PyQt5.QtWidgets import QApplication

        font = QApplication.font()

        # Remember if the default size is in pixels or points.
        default_size = font.pointSizeF()
        if default_size < 0:
            default_size = font.pixelSize()
            self._uses_pixels = True
        else:
            self._uses_pixels = False

        return default_size

    @_previous_size.default
    def _previous_size(self):
        """ Invoked to return the default previous font size. """

        return self._default_size

    def _set_size(self, new_size):
        """ Set the font size of all views and update the internal state. """

        # Set the size.
        for view in self.views:
            # Get the toolkit specific widget.
            qview = unadapted(view)

            font = qview.font()

            if self._uses_pixels:
                font.setPixelSize(round(new_size))
            else:
                font.setPointSizeF(new_size)

            qview.setFont(font)

        # See if setting to the default size.
        if abs(new_size - self._default_size) < 0.0001:
            self.normal_size.checked = True
        else:
            self.normal_size.checked = False

        # Only remember the previous size if it isn't the default.
        if abs(self._current_size - self._default_size) > 0.0001:
            self._previous_size = self._current_size

        self._current_size = new_size


# Every application needs an Application.
app = Application()

# Define the shell.  Every shell created by the factory will have QuitTool and
# ZoomTool instances.
view_factory = MainWindowShell(main_area_policy='single',
        tool_factories=[QuitTool, ZoomTool], title="Zoom Shell")

# Create the shell.
view = view_factory()

# Make the shell visible.
view.visible = True

# Enter the event loop.
app.execute()
