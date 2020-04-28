from dip.shell.shells.main_window import MainWindowShell
from dip.ui import Application


# Every application needs an Application.
app = Application()

# Define the shell.
view_factory = MainWindowShell(title="Trivial Shell")

# Create the shell.
view = view_factory()

# Make the shell visible.
view.visible = True

# Enter the event loop.
app.execute()
