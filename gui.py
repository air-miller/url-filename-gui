# GUI url-filename input provider
# 2023 Vladimir Kravchuk
#
# pip install pyqt6 validators
# (consider venv)
#
# camelCase used to maintain uniformity w/PyQt
#
# v 0.2
#
# Free for non-commercial use


DESTINATION_FOLDER_PATH = "Downloads"
DEFAULT_FILENAME_PREFIX = "New download"
FILENAME_EXTENSION = "" # No leading dot (prepended automatically). Leave empty or set to None to ignore

DEFAULT_FILENAME_TIMESTAMP_SECONDS_SEPARATOR = "-" # Universal, for *nix/MacOS/Windows. You may use ":" if the OS supports it.

def resultHandler(url: str, filename: str):
	''' Once user clicks OK button with valid input, results are passed here'''
	print(f"Url: {url}, filename: {filename}")
	

def filenameFormatValidator(filename: str) -> bool:
	''' Use it to validate a user-provided file name however you'd like '''
	return len(filename) > 0


# Window text

WINDOW_TITLE = "Downloader GUI"

PASTE_URL_LABEL = "Paste URL here:"
ENTER_DESTINATION_FILENAME_LABEL = "Enter filename:"
CLEAR_INPUT_BUTTON_TITLE = "Clear all"
OK_BUTTON_TITLE = "OK"


# Make sure you know what you are doing before changing the code below 

from PyQt6.QtWidgets import (
	QApplication,
	QFormLayout,
	QHBoxLayout,
	QLineEdit, 
	QPushButton,
	QLabel,
	QWidget
	)

from validators import url as urlValidator
import os

class UrlFilenameGUI:

	def __init__(self, resultHandler, filenameFormatValidator = None):

		# UI state variables
		self.okButtonEnabled = False
		self.clearInputButtonEnabled = False
		self.__isFilenameInputEmpty = True
		self.__isUiEnabled = True

		# Data variables ;)
		self.url = None
		self.__filename = None

		# Handler
		self.resultHandler = resultHandler
		self.filenameFormatValidator = filenameFormatValidator

		self.app = QApplication([])

		formLayout = QFormLayout()

		urlLineEdit = QLineEdit()
		urlLineEdit.placeholderText = PASTE_URL_LABEL
		urlLineEdit.textChanged.connect(self.urlLineEditTextChanged)
		formLayout.addRow(PASTE_URL_LABEL, urlLineEdit)

		self.urlLineEdit = urlLineEdit


		destinationFilenameLineEdit = QLineEdit()
		destinationFilenameLineEdit.placeholderText = ENTER_DESTINATION_FILENAME_LABEL
		destinationFilenameLineEdit.textChanged.connect(self.destinationFilenameLineEditTextChanged)
		formLayout.addRow(ENTER_DESTINATION_FILENAME_LABEL, destinationFilenameLineEdit)

		self.destinationFilenameLineEdit = destinationFilenameLineEdit

		okButton = QPushButton(OK_BUTTON_TITLE)
		okButton.setEnabled(False)
		okButton.clicked.connect(self.okButtonClicked)
		formLayout.addRow(okButton)

		self.okButton = okButton

		clearInputButton = QPushButton(CLEAR_INPUT_BUTTON_TITLE)
		clearInputButton.setEnabled(False)
		clearInputButton.clicked.connect(self.clearInputButtonClicked)

		self.clearInputButton = clearInputButton

		rootLayout = QHBoxLayout()
		rootLayout.addLayout(formLayout)
		rootLayout.addWidget(clearInputButton)

		window = QWidget()
		window.setWindowTitle(WINDOW_TITLE)
		window.setLayout(rootLayout)

		self.window = window


	def show(self):

		self.window.show()
		self.app.exec()


	@property
	def valid_input_present(self) -> bool:

		return bool(
			self.url and
			(self.__isFilenameInputEmpty or self.__filename)
			)

	@property
	def filename(self):

		# If a user was generous, just use the value they provided
		if self.__filename:
			base_filename = self.__filename
		else:
			# Otherwise, generate a default
			from datetime import datetime
			now = datetime.now().strftime(f"%Y-%m-%d %H{DEFAULT_FILENAME_TIMESTAMP_SECONDS_SEPARATOR}%M{DEFAULT_FILENAME_TIMESTAMP_SECONDS_SEPARATOR}%S")

			base_filename = f"{DEFAULT_FILENAME_PREFIX} {now}" if DEFAULT_FILENAME_PREFIX else now

		filename = f"{base_filename}.{FILENAME_EXTENSION}" if FILENAME_EXTENSION else base_filename

		return os.path.join(DESTINATION_FOLDER_PATH, filename) if DESTINATION_FOLDER_PATH else filename


	def updateUI(self, isUiEnabled: bool = None): #, needOkButtonEnabled: bool, needClearInputButtonEnabled: bool):

		def updateButtonIfNeeded(newState: bool, currentState: bool, button: QPushButton):

			if newState != currentState:
				button.setEnabled(newState)
			return newState

		
		if isUiEnabled is not None:

			self.urlLineEdit.setEnabled(isUiEnabled)
			self.destinationFilenameLineEdit.setEnabled(isUiEnabled)

			if not isUiEnabled:
				self.okButtonEnabled = updateButtonIfNeeded(False, self.okButtonEnabled, self.okButton)
				self.clearInputButtonEnabled = updateButtonIfNeeded(False, self.clearInputButtonEnabled, self.clearInputButton)
				return

			# Otherwise, let routines determine the restoration state

		# Ok button is enabled when valid data is present
		self.okButtonEnabled = updateButtonIfNeeded(self.valid_input_present, self.okButtonEnabled, self.okButton)

		# If there's any user input, we have soemthing to clear
		haveSomethingToClear = len(self.urlLineEdit.text()) > 0 or len(self.destinationFilenameLineEdit.text()) > 0
		self.clearInputButtonEnabled = updateButtonIfNeeded(haveSomethingToClear, self.clearInputButtonEnabled, self.clearInputButton)


	def urlLineEditTextChanged(self, userInputText: str):

		text = userInputText.strip()
		textPresent = len(text) > 0

		# Validate input and update URL as needed
		validUrlPresent = textPresent and (urlValidator(text) == True)
		self.url = text if validUrlPresent else None

		# Update UI
		self.updateUI()


	def destinationFilenameLineEditTextChanged(self, userInputText: str):

		def filename_is_valid(filename: str):
			return self.filenameFormatValidator(filename) if self.filenameFormatValidator else True
		
		inputPresent = len(userInputText) > 0

		text = userInputText.strip()
		textPresent = len(text) > 0
		
		inputIsEmpty = not textPresent # Uncomment this line to disregard spaces at all
		# inputIsEmpty = not inputPresent # Uncomment this line to treat spaces as non-empty input
		self.__isFilenameInputEmpty = inputIsEmpty

		self.__filename = text if not inputIsEmpty and filename_is_valid(text) else None
		
		self.updateUI()


	def clearInputButtonClicked(self):
		
		self.urlLineEdit.setText("")
		self.destinationFilenameLineEdit.setText("")


	def okButtonClicked(self):

		assert self.url is not None, "Valid url should be present when ok button clicked"

		self.updateUI(isUiEnabled = False)
		self.resultHandler(self.url, self.filename)
		self.updateUI(isUiEnabled = True)


if __name__ == '__main__':

	urlFilenameUI = UrlFilenameGUI(
		resultHandler = resultHandler,
		filenameFormatValidator = filenameFormatValidator
		)
	urlFilenameUI.show()

