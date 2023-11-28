import subprocess
def conn_check(server_ip, server_port):
    # server_ip = "10.129.2.46"
    iperf_command = ["iperf-3.1.3-win64\iperf3.exe", "-c", server_ip, "-p",  server_port]

    try:
        result = subprocess.run(iperf_command, capture_output=True, text=True, check=True)
        print("iperf Result:")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running iperf command:")
        print(e.stderr)
        return e.stderr


from PyQt5.QtWidgets import QApplication, QLineEdit, QDialogButtonBox, QFormLayout, QDialog
from typing import List


class InputDialog(QDialog):
    def __init__(self, labels: List[str], parent=None):
        super().__init__(parent)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        layout = QFormLayout(self)

        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = InputDialog(labels=["Server IP", "Server Port"])

    if dialog.exec():
        inputs = dialog.getInputs()
        print(inputs[0], inputs[1])
        result = conn_check(server_ip=inputs[0], server_port=inputs[1])
    exit(0)



# import iperf3
#
#
# def conn_check():
#     client = iperf3.Client()
#     client.duration = 1
#     # client.bind_address = '10.0.0.1'
#     client.server_hostname = '10.129.2.46'
#     client.port = 5201
#     client.protocol = 'udp'
#     result = client.run()
#
#     if result.error:
#         print(result.error)
#     else:
#         print('')
#         print('Test completed:')
#         print('  started at         {0}'.format(result.time))
#         print('  bytes transmitted  {0}'.format(result.bytes))
#         print('  jitter (ms)        {0}'.format(result.jitter_ms))
#         print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))
#
#         print('Average transmitted data in all sorts of networky formats:')
#         print('  bits per second      (bps)   {0}'.format(result.bps))
#         print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
#         print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
#         print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
#         print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     conn_check()



import subprocess
from PyQt5.QtWidgets import QApplication, QLineEdit, QDialogButtonBox, QFormLayout, QDialog, QLabel, \
    QRadioButton, QVBoxLayout, QScrollArea
from typing import List
import os
import sys
import platform


def conn_check(server_ip, server_port, protocol):
    # iperf_command = ["iperf-3.1.3-win64\iperf3.exe", "-c", server_ip, "-p", server_port, "-t", "5", "-V"]
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


class InputDialog(QDialog):
    def __init__(self, labels: List[str], parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 400)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
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

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.on_accepted)
        buttonBox.rejected.connect(self.reject)

    def on_accepted(self):
        inputs = self.getInputs()
        print(inputs[0], inputs[1])

        if self.protocol_radio_tcp.isChecked():
            protocol = "TCP"
        elif self.protocol_radio_udp.isChecked():
            protocol = "UDP"
        else:
            protocol = "TCP"

        result = conn_check(server_ip=inputs[0], server_port=inputs[1], protocol=protocol)

        self.result_label.setText(result)

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    dialog = InputDialog(labels=["Server IP", "Server Port"])

    if dialog.exec():
        sys.exit(app.exec_())

