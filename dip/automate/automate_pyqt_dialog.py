from dip.automate import AutomationCommands


class AutomateName(AutomationCommands):
    """ This automation command will set the 'name' widget in the dialog. """

    def record(self, robot):
        robot.record('dialog.person:name', 'set', self.value)


class AutomateAge(AutomationCommands):
    """ This automation command will set the 'age' widget in the dialog. """

    def record(self, robot):
        robot.record('dialog.person:age', 'set', self.value)


class AutomateOk(AutomationCommands):
    """ This automation command will click the Ok button of the dialog. """

    def record(self, robot):
        robot.record('dialog.person', 'click', 'ok')


# Create the command sequence.
automation_commands = (AutomateName("Joe User"), AutomateAge(30), AutomateOk())
