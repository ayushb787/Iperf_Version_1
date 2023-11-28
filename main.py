from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QRadioButton, QVBoxLayout, \
    QLabel, QScrollArea, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import os
import subprocess
import sys


def conn_check(server_ip, server_port, protocol):
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    iperf_path = os.path.join(bundle_dir, 'iperf3.exe')

    print(f'Bundle Directory: {bundle_dir}')
    print(f'iperf Path: {iperf_path}')

    if os.path.exists(iperf_path):
        subprocess.run([iperf_path])
    else:
        print("Error: iperf3.exe not found in the same directory.")

    iperf_command = [iperf_path, "-c", server_ip, "-p", server_port, "-t", "5", "-V"]
    if protocol == "UDP":
        iperf_command.extend(["-u"])

    try:
        result = subprocess.run(iperf_command, capture_output=True, text=True, check=True)
        print("iperf Result:")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running iperf command:")
        print(e.stderr)
        return e.stderr


class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, server_ip, server_port, protocol):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol = protocol

    def run(self):
        result = conn_check(server_ip=self.server_ip, server_port=self.server_port, protocol=self.protocol)
        self.finished.emit(result)


class InputDialog(QDialog):
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 400)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        saveButton = QPushButton("Save", self)

        layout = QFormLayout(self)

        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])

        self.protocol_radio_tcp = QRadioButton("TCP", self)
        self.protocol_radio_udp = QRadioButton("UDP", self)
        self.protocol_radio_tcp.setChecked(True)

        protocol_layout = QVBoxLayout()
        protocol_layout.addWidget(self.protocol_radio_tcp)
        protocol_layout.addWidget(self.protocol_radio_udp)
        layout.addRow("Protocol:", protocol_layout)

        scroll_area = QScrollArea(self)
        self.result_label = QLabel(self)
        self.result_label.setWordWrap(True)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.result_label)
        layout.addRow(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.addWidget(buttonBox)
        button_layout.addWidget(saveButton)
        layout.addRow(button_layout)

        buttonBox.accepted.connect(self.on_accepted)
        buttonBox.rejected.connect(self.reject)
        saveButton.clicked.connect(self.save_result)

        self.worker_thread = None

    def on_accepted(self):
        inputs = self.getInputs()
        print(inputs[0], inputs[1])

        if self.protocol_radio_tcp.isChecked():
            protocol = "TCP"
        elif self.protocol_radio_udp.isChecked():
            protocol = "UDP"
        else:
            protocol = "TCP"

        self.worker_thread = WorkerThread(server_ip=inputs[0], server_port=inputs[1], protocol=protocol)
        self.worker_thread.finished.connect(self.show_result)
        self.worker_thread.start()

        self.result_label.setText("Please wait...")

    def show_result(self, result):
        self.result_label.setText(result)

    def getInputs(self):
        server_ip = self.inputs[0].text()
        server_port = self.inputs[1].text()

        if not server_port:
            server_port = "5201"

        return server_ip, server_port

    def save_result(self):
        result_text = self.result_label.text()
        if result_text:
            downloads_path = str(Path.home() / "Downloads")
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Result", downloads_path, "Text Files (*.txt)")
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(result_text)

    def closeEvent(self, event):
        if self.worker_thread is not None and self.worker_thread.isRunning():
            self.worker_thread.finished.disconnect(self.show_result)
            self.worker_thread.quit()
            self.worker_thread.wait()

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    dialog = InputDialog(labels=["Server IP", "Server Port"])

    if dialog.exec():
        sys.exit(app.exec_())
