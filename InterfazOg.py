from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from new_window import NewWindow
from parking_client import getQR, registerUser, sendQR 
import cv2
import os

url = "http://localhost:80"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz de usuario")

        # Labels
        L1 = QLabel('Id: ')
        L2 = QLabel('Contraseña: ')
        L3 = QLabel('Rol: ')
        L4 = QLabel("Programa: ")

        # Campos de entrada
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()
        self.e4 = QLineEdit()

        # Botones
        b1 = QPushButton('Obtener QR')
        b2 = QPushButton('Registrar Usuario')
        b3 = QPushButton('Ver Parqueadero (Admin)')
        b4 = QPushButton('Escanear QR')

        b1.clicked.connect(self.GetQr)
        b2.clicked.connect(self.RegisterUser)
        b3.clicked.connect(self.ParqueaderoAdmin)
        b4.clicked.connect(self.SendQr)

        gridLayout = QGridLayout()

        gridLayout.addWidget(L1, 0, 0)
        gridLayout.addWidget(L2, 1, 0)
        gridLayout.addWidget(L3, 2, 0)
        gridLayout.addWidget(L4, 3, 0)

        gridLayout.addWidget(self.e1, 0, 1)
        gridLayout.addWidget(self.e2, 1, 1)
        gridLayout.addWidget(self.e3, 2, 1)
        gridLayout.addWidget(self.e4, 3, 1)

        gridLayout.addWidget(b1, 0, 3, 1, 3)
        gridLayout.addWidget(b2, 1, 3, 1, 3)
        gridLayout.addWidget(b3, 2, 3, 1, 3)
        gridLayout.addWidget(b4, 3, 3, 1, 3)

        widget = QWidget()
        widget.setLayout(gridLayout)
        self.setCentralWidget(widget)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)

    def GetQr(self):
        id = self.e1.text()
        password = self.e2.text()

        if len(id) and len(password):
            imgBytes = getQR(url, id, password)

            if type(imgBytes) is bytes and len(imgBytes):
                self.nw = NewWindow(imgBytes)
                self.nw.show()

                self.qr_filename = os.path.join(os.getcwd(), "temp_qr.png")
                with open(self.qr_filename, "wb") as f:
                    f.write(imgBytes)

                self.Q1 = QPushButton("Guardar en el escritorio")
                self.Q1.clicked.connect(self.guardaimagen)

                gridLayout2 = QGridLayout()
                gridLayout2.addWidget(self.Q1, 1, 3, 1, 3)
                widget2 = QWidget()
                widget2.setLayout(gridLayout2)
                self.setCentralWidget(widget2)
            else:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Usuario no Existe o Contraseña Incorrecta")
                msgBox.setWindowTitle("Alerta")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()

    def RegisterUser(self):
        id = self.e1.text()
        password = self.e2.text()
        rol = self.e3.text()
        programa = self.e4.text()

        if len(id) and len(password) and len(rol) and len(programa):
            Usuario = registerUser(url, id, password, programa, rol)

            msgBox = QMessageBox()
            if Usuario == "User succesfully registered":
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Usuario Registrado")
                msgBox.setWindowTitle("Mensaje informativo")
            else:
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Usuario ya existe")
                msgBox.setWindowTitle("Alerta")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()

    def ParqueaderoAdmin(self):
        id = self.e1.text().strip()
        password = self.e2.text().strip()
        rol = self.e3.text().strip().lower()
        programa = self.e4.text().strip().lower()
        url_camara = "http://192.168.197.226:8080/video"

        if id == "1234" and password == "1234" and rol == "admin" and programa == "electronica":
            video = cv2.VideoCapture(url_camara)
            if not video.isOpened():
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText("No se pudo abrir la cámara del parqueadero.")
                msgBox.setWindowTitle("Error de conexión")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()
                return

            while True:
                ret, frame = video.read()
                if not ret:
                    msgBox = QMessageBox()
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setText("Error al leer el video.")
                    msgBox.setWindowTitle("Error de lectura")
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec()
                    break

                cv2.imshow("Vista del Parqueadero", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            video.release()
            cv2.destroyAllWindows()
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Credenciales inválidas. Acceso denegado.")
            msgBox.setWindowTitle("Acceso restringido")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()

    def SendQr(self):
        from qrscan import MainApp
        self.scanner_window = MainApp()
        self.scanner_window.show()

# Crea la aplicación principal
app = QApplication([])
ex = MainWindow()
ex.show()
app.exec()
