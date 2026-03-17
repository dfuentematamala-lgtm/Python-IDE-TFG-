from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from Highlighter2 import Highlighter

"""

Clase Consola    ::     contiene los "objetos" consola que creamos al producirse un error del entorno o se inicia una ejecución de un programa

***********************************************************                  ATRIBUTOS                      ******************************************************************


tab ::                  Cada programa está asociado a una pestaña del tabwidget de la ventana principal

verticalLayout ::       Layout vertical que contendrá nuestro AreaCodigo, necesario para redimensionarla al "estirar" la ventana o "encogerla"

consola ::          El QTextEdit donde se escriben los programas de nuestro IDE

contadorWidget ::       Contador que recibe a través del constructor, simplemente utilizado para añadirlo a los nombres (ej: tab_1, area_codigo2)


"""

class Consola:

    tab = qtw.QWidget
    verticalLayout = qtw.QVBoxLayout
    contadorWidget : int
    ruta_archivo : str
    debug : bool
    _translate = qtc.QCoreApplication.translate
    
    """
    
    Constructor :: Programa

    @param contadorWidget ::    Le pasamos el contador que tenemos en la ventana principal, de nuevo, simplemente para nombrar cosas
    
    """

    def __init__(self, ruta_archivo:str,contadorWidget:int, debug:bool, claridad):

        self.contadorWidget = contadorWidget -1
        self.ruta_archivo = ruta_archivo.rpartition('/')[2]
        self.debug = debug
        self.claridad = claridad

        self.tab = qtw.QWidget()
        self.tab.setObjectName("tab_"+str(contadorWidget))
        self.verticalLayout = qtw.QVBoxLayout(self.tab)

        self.consola = qtw.QTextEdit(self.tab)
        self.consola.setReadOnly(True)

        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout_2")

        self.setEstilo(self.claridad)

        self.consola.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)
        self.consola.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)
        self.consola.setSizeAdjustPolicy(qtw.QAbstractScrollArea.AdjustToContents)
        self.consola.setLineWrapMode(qtw.QTextEdit.NoWrap)
        self.consola.setObjectName("area_codigo"+str(contadorWidget))
        self.verticalLayout.addWidget(self.consola)
        self.resaltado_sintaxis = Highlighter()
        self.highlight_code()

        if self.debug == True:
            self.gridLayout = qtw.QGridLayout()

            self.continueButton = qtw.QPushButton()
            self.continueButton.setMaximumSize(qtc.QSize(110, 30))
            self.continueButton.setObjectName("continueButton")
            self.continueButton.setText(self._translate("Consola", "Continuar"))

            self.nextButton = qtw.QPushButton()
            self.nextButton.setMaximumSize(qtc.QSize(100, 30))
            self.nextButton.setObjectName("nextButton")
            self.nextButton.setText(self._translate("Consola", "Next"))

            self.stepButton = qtw.QPushButton()
            self.stepButton.setMaximumSize(qtc.QSize(100, 30))
            self.stepButton.setObjectName("stepButton")
            self.stepButton.setText(self._translate("Consola", "Step"))

            self.stopButton = qtw.QPushButton()
            self.stopButton.setMaximumSize(qtc.QSize(100, 30))
            self.stopButton.setObjectName("stopButton")
            self.stopButton.setText(self._translate("Consola", "Stop"))

            self.gridLayout.addWidget(self.continueButton, 0, 0, qtc.Qt.AlignRight)
            self.gridLayout.addWidget(self.nextButton, 0, 1)
            self.gridLayout.addWidget(self.stepButton, 0, 2)
            self.gridLayout.addWidget(self.stopButton, 0, 3)
            self.gridLayout.setSpacing(0)

            self.verticalLayout.addLayout(self.gridLayout)
            self.verticalLayout.setSpacing(0)

    def get_consola(self) -> qtw.QTextEdit:
        return self.consola

    def isDebug(self) -> bool :
        return self.debug

    """
    
    highlight  code

    El resaltador de sintaxis apunta al documento de AreaCodigo
    
    """

    def highlight_code(self):
        self.resaltado_sintaxis.setDocument(self.consola.document())

    """
    
    set Estilo
    
    """

    def setEstilo(self, estilo:bool):

        self.claridad = estilo

        if  self.claridad == True:
            self.consola.setStyleSheet("background-color: #C0C0C0;"
                                        "color: #1a1a1a;"
                                        "font-size: 15px")
            
        else:
            self.consola.setStyleSheet("background-color: #17202a;"
                                        "color: #DCDCDC;"
                                        "font-size: 15px")