import sys

from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
        QFormLayout, QLineEdit, QSpinBox, QVBoxLayout)


class Dialog(QDialog):
    """ Create a dialog allowing a person's name and age to be entered. """

    def __init__(self, model):
        """ Initialise the dialog. """

        super().__init__(objectName='dialog.person')

        self._model = model

        # Create the dialog contents.
        dialog_layout = QVBoxLayout()

        form_layout = QFormLayout()

        self._name_editor = QLineEdit(objectName='name')
        self._name_editor.setText(self._model['name'])
        form_layout.addRow("Name", self._name_editor)

        self._age_editor = QSpinBox(objectName='age', suffix=" years")
        self._age_editor.setValue(self._model['age'])
        form_layout.addRow("Age", self._age_editor)

        dialog_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                accepted=self._on_accept, rejected=self.reject)
        dialog_layout.addWidget(button_box)

        self.setLayout(dialog_layout)

    def _on_accept(self):
        """ Invoke when the dialog is accepted. """

        self._model['name'] = self._name_editor.text()
        self._model['age'] = self._age_editor.value()

        self.accept()


# Every PyQt GUI application needs a QApplication.
app = QApplication(sys.argv)

# Create the model.
model = dict(name='', age=0)

# Create the dialog.
ui = Dialog(model)

# Enter the dialog's modal event loop.
ui.exec()

# Show the value of the model.
print("Name:", model['name'])
print("Age:", model['age'])
