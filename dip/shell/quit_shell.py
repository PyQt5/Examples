from dip.shell.shells.main_window import MainWindowShell
from dip.shell.tools.quit import QuitTool
from dip.ui import Application


# Every application needs an Application.
app = Application()

# Define the shell.  Every shell created by the factory will have a QuitTool
# instance.
view_factory = MainWindowShell(tool_factories=[QuitTool], title="Quit Shell")

# Create the shell.
view = view_factory()

# Make the shell visible.
view.visible = True

# Enter the event loop.
app.execute()
