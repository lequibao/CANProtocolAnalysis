import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from mainwindow import Ui_MainWindow
from PyQt5.QtGui import QTextCursor
from protocalFile import Protocal

protocal = Protocal()  # The custom Protocal class defines various protocol parsing methods.
# Define the dictionary that maps protocol types to their processing methods.
protocal_dict = {
    '1808F456(CML)': protocal.cmlPileMaximumOutputCapability,  # CML charging pile maximum output capability message
    '181056F4(BCL)': protocal.bclBatteryChargingDemand,        # BCL battery charging demand message
    '1826F456(CHM)': protocal.chmHandshake,                    # CHM charger handshake message
    '182756F4(BHM)': protocal.bhmHandshake,                    # BHM vehicle handshake message
    '1801F456(CRM)': protocal.crm_identify,                    # CRM charger identification message
    '100956F4(BRO)': protocal.broCarReadyOk,                   # BRO vehicle ready message
    '100AF456(CRO)': protocal.croChargerReadyOk,               # CRO charger ready message
    '1812F456(CCS)': protocal.ccsChargerState,                 # CCS charger state message
    '181356F4(BSM)': protocal.bsmBatteryStatus,                # BSM power battery status message
    'BCS Multi Packet Message': protocal.bcsMulPackets,                 # BCS multipacket data message (2 packets)
    '101956F4(BST)': protocal.bstEndCharge,                    # BMS stop charging reason message (BST)
    '101AF456(CST)': protocal.cstEndCharge,                    # Charger stop charging message (CST)
    'BMV Multi Packet Message': protocal.bmvMulitiPackets,              # Single battery voltage message (BMV)
    'BCP Multi Packet Message': protocal.bcpChargePamrameters,          # Power battery charging parameters message (BCP)
    'BMT Multi Packet Message': protocal.bmtMultiPackes,                # Power battery temperature message (BMT)
    'BRM Multi Packet Message': protocal.brmMuitiPackes,                # BMS and vehicle identification message (BRM)
    '181C56F4(BSD)': protocal.bsd,                             # BMS statistical data message (BSD)
    '181DF456(CSD)': protocal.csd,                             # Charger statistical data message (CSD)
    '081E56F4(BEM)': protocal.bem,                             # Charger error message (BEM)
    '081FF456(CEM)': protocal.cem                              # Charger error message (CEM)
}

# GUI display class
class Win_Form(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super(Win_Form, self).setupUi(MainWindow)
        # self.cmbx_protocalType.setEditable(True)
        self.pbtn_Analysis.clicked.connect(self.process)
        self.btnClear.clicked.connect(self.clear)

    # Slot function when clicking the Analyze button: Get the protocol type and data, use the methods in the custom Protocal class to parse the protocol.
    def process(self):
        type = self.cmbx_protocalType.currentText()     # Get the protocol type
        data = self.txtEdt_protocalData.toPlainText()   # Get the protocol data
        result = protocal_dict[type](data) + '\n'       # Parse the protocol, append a newline character to the result
        self.txtEdt_result.append(result)               # Display the parsing result on the interface
        QApplication.processEvents()
        self.txtEdt_result.moveCursor(QTextCursor.End)  # Scroll the result display box to the bottom to show the latest parsing information.
        QApplication.processEvents()

    # Slot function when clicking the Clear button: Clear the content in the parsing result box.
    def clear(self):
        self.txtEdt_result.clear()
        QApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()

    ui = Win_Form()
    ui.setupUi(win)

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
