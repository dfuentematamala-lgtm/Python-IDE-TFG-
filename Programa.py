import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QApplication, QVBoxLayout, QAbstractScrollArea
from  AreaCodigo import AreaCodigo

"""

Clase Programa   ::   contiene los "objetos" programa que creamos al abrir un archivo nuevo o existente desde la ventana principal

***********************************************************                  ATRIBUTOS                      ******************************************************************


tab ::                  Cada programa está asociado a una pestaña del tabwidget de la ventana principal

verticalLayout ::       Layout vertical que contendrá nuestro AreaCodigo, necesario para redimensionarla al "estirar" la ventana o "encogerla"

area_codigo ::          El QPlainTextEdit donde se escriben los programas de nuestro IDE

contadorWidget ::       Contador que recibe a través del constructor, simplemente utilizado para añadirlo a los nombres (ej: tab_1, area_codigo2)

modificado ::           Booleano para controlar si el programa está guardado. El nombre de la pestaña cambia si es un archivo abierto (no es nuevo) y modificado == True -
-                       También para controlar el comportamiento al guardar el programa.

ruta_archivo ::         Contiene en String la ruta absoluta al archivo abierto. Si es nuevo está vacía

contenido_original ::   Contiene en String el contenido del archivo abierto para compararlo con el area_codigo. Si es nuevo está vacío


"""

class Programa:

    tab = QWidget
    verticalLayout = QVBoxLayout
    area_codigo = AreaCodigo
    contadorWidget : int
    modificado : bool
    ruta_archivo : str
    contenido_original : str

    """
    
    Constructor :: Programa

    @param ruta_archivo ::      Si es un archivo abierto, le pasamos la ruta absoluta del archivo cuando lo abramos con QFileDialog
    @param contadorWidget ::    Le pasamos el contador que tenemos en la ventana principal, de nuevo, simplemente para nombrar cosas
    
    """

    def __init__(self, ruta_archivo:str, contadorWidget:int, claridad:bool):
        self.ruta_archivo = ruta_archivo
        self.contadorWidget = contadorWidget -1
        self.contenido_original = ''
        self.modificado =  False

        self.tab = QWidget()
        self.tab.setObjectName("tab_"+str(contadorWidget))
        self.verticalLayout = QVBoxLayout(self.tab)
        self.area_codigo = AreaCodigo(claridad)

        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout_2")

        self.area_codigo.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.area_codigo.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.area_codigo.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.area_codigo.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.area_codigo.setObjectName("area_codigo"+str(contadorWidget))
        self.verticalLayout.addWidget(self.area_codigo)

    """
    
    Set ruta_archivo
    
    """

    def set_ruta_archivo(self, path:str):
        self.ruta_archivo = path

    """
    
    Set contenido_original  ::  self.area_codigo -> contenido_original
    
    Para cuando cargamos el programa en la estructura de datos programas : list[] de la ventana principal -
    -    cuando guardamos el programa, tenemos que actualizarlo

    """

    def set_contenidoOriginal(self):
        self.contenido_original = self.area_codigo.toPlainText()

    """
    
    Es contenido_original
    @return bool    ::  Devuelve True/False si el contenido de area_codigo es el contenido_original del archivo
    -                   Si es un archivo nuevo, su contenido original es vacío
    Usado para comprobar el contenido y cambiar el nombre de la pestaña correspondiente al programa abierto en función de si está modificado o corresponde con el original
    
    """

    def es_contenidoOriginal(self) -> bool:
        if self.contenido_original == '' and self.area_codigo.toPlainText() == '':
            return True
        else:
            return self.contenido_original == self.area_codigo.toPlainText()
        

"""

Main para probar el editor de texto solo

"""

if __name__ == '__main__':

    app = QApplication([])
    editor = AreaCodigo()
    editor.setWindowTitle("Code Editor Example")
    editor.show()
    sys.exit(app.exec())
