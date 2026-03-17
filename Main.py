import sys

from PyQt5.QtWidgets import QApplication
from Controlador import Controlador


app = QApplication([])

ventanaPrincipal = Controlador()
ventanaPrincipal.show()

sys.exit(app.exec_())
