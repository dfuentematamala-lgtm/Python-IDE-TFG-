import sys
import os
from PyQt5.QtWidgets import QApplication, QTreeView, QFileSystemModel,QMenu, QInputDialog, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from send2trash import send2trash

"""

Clase Explorador    ::      Está reimplementando a QTreeView

***********************************************************                  ATRIBUTOS                      ******************************************************************

accionAbrir       ::     QAction para abrir ficheros desde el menu contextual del explorador
accionPath        ::     QAction para copiar el path absoluto del fichero desde el menu contextual del explorador
accionPathRel     ::     QAction para copiar el path relativo del fichero desde el menu contextual del explorador
accionEliminar    ::     QAction para Eliminar el fichero desde el menu contextual del explorador
accionRenombrar   ::     QAction para renombrar el fichero desde el menu contextual del explorador

Reimplementamos QTreeView:

-        - Para darle nuestro propio estilo y crear un menu contextual (click derecho) y añadir las acciones descritas arriba
-        - Las acciones renombrar y eliminar se conectan a métodos definidos aquí, las otras es necesario conectarlas en la ventana principal


"""

class Explorador(QTreeView):

    accionAbrir     : QAction
    accionPath      : QAction
    accionPathRel   : QAction
    accionEliminar  : QAction
    accionRenombrar : QAction
    renombrado = pyqtSignal(list)
    eliminado = pyqtSignal(str)

    """
    
    Constructor   ::    Explorador

    @param modelo   ::  Le pasamos el QFileSystemModel, modelo de archivos y directorios para usarlo en los metodos de renombrar y eliminar

    Creamos un QPlainTextEdit con super y:
    -     - Inicializamos el modelo
    -     - Llamamos para definir el estilo del explorador

    """

    def __init__(self, modelo:QFileSystemModel, parent=None):
        super().__init__(parent)

        self.modelo = modelo
        self.accionAbrir = QAction("Abrir")
        self.accionPath = QAction("Copiar Path")
        self.accionPathRel = QAction("Copiar Path Relativo")

        self.setEstilo()

    """
    
    get Modelo

    @return  ::  modelo QFileSystemModel
    
    """

    def getModelo(self):

        return self.modelo

    """
    
    set Estilo

    Le damos un estilo neutro a nuestro explorador
    
    """

    def setEstilo(self):

        self.setStyleSheet("background-color: #C0C0C0;"
                                    "color: #1a1a1a;"
                                    "font-size: 15px")

    """
    
    contextMenuEvent

    Creamos un menu para el evento de menu contextual (click derecho) y:
    -     - Le damos el mismo estilo y añadimos uno especial para resaltar el que estamos seleccionando con el raton
    -     - Añadimos las acciones con separadores y conectamos a los metodos de renombrar y eliminar

    """

    def contextMenuEvent(self, event):

        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        
        menu = QMenu(self)

        menu.setStyleSheet("""
                QMenu {
                    background-color: #C0C0C0;
                    color: #1a1a1a;
                    border: 1px solid #555;
                }
                QMenu::item {
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #0078d7;
                    color: #ffffff;
                }
                """)

        menu.addAction(self.accionAbrir)
        menu.addSeparator()
        menu.addAction(self.accionPath)
        menu.addAction(self.accionPathRel)
        menu.addSeparator()

        self.accionRenombrar = QAction("Renombrar", self)
        self.accionRenombrar.triggered.connect(lambda: self.renombrar(index))
        menu.addAction(self.accionRenombrar)

        self.accionEliminar = QAction("Eliminar", self)
        self.accionEliminar.triggered.connect(lambda: self.mover_a_papelera(index))
        menu.addAction(self.accionEliminar)

        menu.exec_(event.globalPos())

    """
    
    mover a papelera

    @param  index   ::   Indice recuperado (QModelIndex) del explorador

    Obtenemos el path del archivo o directorio a través del indice recuperado del explorador
    Mostramos un QMessageBox para confirmar que se desea eliminar el fichero o directorio y se elimina en caso afirmativo
    Utiliza la funcion send2trash! util para moverlo a la papelera de reciclaje, si usaramos os.remove eliminariamos el enlace de la estructura de directorios directamente

    """

    def mover_a_papelera(self, index):
        file_path = os.path.abspath(self.modelo.filePath(index))
        emit_path = self.modelo.filePath(index)
        
        if os.path.isfile(file_path) or os.path.isdir(file_path):
            reply = QMessageBox.question(self, "Mover a la Papelera", f"Está seguro de que desea enviar {file_path} a la papelera?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                send2trash(file_path)
                self.eliminado.emit(emit_path)

    """
    
    @param  index   ::   Indice recuperado (QModelIndex) del explorador

    Obtenemos el path del archivo o directorio a través del indice recuperado del explorador
    Creamos y mostramos un QInputDialog para ingresar el nuevo nombre y en caso de proporcionarlo y pulsar ok se renombra

    """

    def renombrar(self, index):
        file_path = self.modelo.filePath(index)
        inputDialog = QInputDialog()
        inputDialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        new_name, ok = inputDialog.getText(self, "Renombrar", "Introduce Nuevo Nombre:", text=os.path.basename(file_path), flags=inputDialog.windowFlags())

        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_path)
            self.renombrado.emit([file_path, new_name])
