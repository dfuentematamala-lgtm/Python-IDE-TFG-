import  sys

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QSize

"""

Clase ConfigWindow    ::      Está reimplementando a QDialog

***********************************************************                  ATRIBUTOS                      ******************************************************************

pathLabel       ::     str para cambiar el Qlabel que muestra el pathRaiz actual

Reimplementamos QDialog:

-        - Para darle nuestro propio estilo
-        - Cambiar entre estilo claro y estilo oscuro del area_codigo
-        - Cambiar la ruta raíz del explorador desde aqui


"""

class ConfigWindow(QDialog):

    pathRaiz : str
    boxActual : str
    cambiosReflejados = pyqtSignal(list)

    """
    
    Constructor   ::    ConfigWindow

    -
    
    """

    def __init__(self, path:str, claridad:bool, parent=None):
        super().__init__(parent)
        self.pathRaiz = path
        if claridad == True:
            self.boxActual = "Claro"
        else:
            self.boxActual = "Oscuro"
        self.setupIU()

    def setupIU(self):

        self.setStyleSheet("""
                            QDialog {
                                        background-color: #C0C0C0;
                                        color: #1a1a1a;
                                        border: 1px solid #555;
                            }
                            QDialog QLabel {
                                        font-size: 14px;
                            }
                            QDialog QLabel#custom {
                                        font-size: 12px
                            }
                            """)

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()

        self.combo_label = QLabel(self)
        self.combo_label.setText("Tema seleccionado:")
        layout.addWidget(self.combo_label)

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["Oscuro", "Claro"])
        self.combo_box.setCurrentText(self.boxActual)
        layout.addWidget(self.combo_box)

        self.combo_box.currentTextChanged.connect(self.set_boxActual)

        path_layout = QHBoxLayout()

        self.layout_label = QLabel(self)
        self.layout_label.setText("Path Raiz:")
        layout.addWidget(self.layout_label)

        self.path_label = QLabel(self.pathRaiz, self)
        self.path_label.setObjectName("custom")
        self.path_label.setWordWrap(True)
        path_layout.addWidget(self.path_label)

        browse_button = QPushButton("...", self)
        browse_button.setMaximumSize(QSize(40, 30))
        browse_button.clicked.connect(self.open_file_dialog)
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("Aceptar", self)
        cancel_button = QPushButton("Cancelar", self)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(ok_button, 0, Qt.AlignVCenter)
        buttons_layout.addWidget(cancel_button, 0, Qt.AlignVCenter)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setWindowTitle('Configuración')
        self.setGeometry(718, 480, 500, 150)
        self.setFixedSize(self.size())        

    def open_file_dialog(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", "")
        if folder_path:
            self.pathRaiz = folder_path
            self.path_label.setText(f"Ruta actual: {folder_path}")

    def set_boxActual(self, text:str):
        self.boxActual = text

    def accept(self):
        super().accept()
        self.cambiosReflejados.emit([self.pathRaiz, self.boxActual])

    def reject(self):
        super().reject()

if __name__ == '__main__':

    app = QApplication([])

    ventanaPrincipal = ConfigWindow("E:\Daniel\LA UNIVERSIDAD MOLA\TFG\Código y Pruebas\ConfigWindow.py",  False)
    ventanaPrincipal.show()

    sys.exit(app.exec_())
