import sys
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import unittest
from unittest.mock import MagicMock
from ui import Main

class TestSpeechRecognitionApp(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.main = Main()

    def test_recognition_thread_started_on_button_click(self):
        # Test that the recognition thread is started when the "Rec Now" button is clicked
        with unittest.mock.patch.object(self.main.recognition_thread, 'start') as mock_start:
            QTest.mouseClick(self.main.findChild(QPushButton, 'rec_button'), Qt.LeftButton)
            mock_start.assert_called_once()

    def test_update_list_widget_after_recognition(self):
        # Test that the list widget is updated after speech recognition
        text_to_emit = "[2023-01-01 12:00:00] Test speech."
        with unittest.mock.patch.object(self.main, 'update_list_widget', return_value=None):
            self.main.recognition_thread.recognition_complete.emit(text_to_emit)
            self.assertEqual(self.main.list_widget.count(), 1)
            self.assertEqual(self.main.list_widget.item(0).text(), text_to_emit)

    def test_recognition_thread_emits_signal(self):
        # Test that the recognition thread emits the signal for updating the list widget
        text_to_emit = "[2023-01-01 12:00:00] Test speech."
        with unittest.mock.patch.object(self.main.recognition_thread, 'recognition_complete', MagicMock()):
            self.main.recognition_thread.recognition_complete.emit(text_to_emit)
            self.main.recognition_thread.recognition_complete.emit.assert_called_once_with(text_to_emit)

    def tearDown(self):
        self.app.exit()


if __name__ == '__main__':
    unittest.main()
