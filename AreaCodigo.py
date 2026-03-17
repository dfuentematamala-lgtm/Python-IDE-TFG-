from PyQt5.QtCore import pyqtSlot, Qt, QRect, QSize
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QTextCharFormat
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit, QAction, QApplication
from NameChecker import NameChecker
from Highlighter import Highlighter

"""

Clase NumeroDeLinea :: Widget que contiene los números de línea del editor de texto.

"""

class NumeroDeLinea(QWidget):
    def __init__(self, area_codigo):
        QWidget.__init__(self, area_codigo)
        self.AreaCodigo = area_codigo

    def sizeHint(self):
        return QSize(self.AreaCodigo.anchura_area_NumeroDeLinea(), 0)

    def paintEvent(self, event):
        self.AreaCodigo.evento_pintar_NumeroDeLinea(event)

"""

Clase AreaCodigo    ::      Está reimplementando a QPlainTextEdit

***********************************************************                  ATRIBUTOS                      ******************************************************************


nameChecker        ::  visitador de nombres de la clase NameChecker, para cuando parseemos el código poder visitar los nombres y marcar los nombres que usamos pero no estan declarados

resaltado_sintaxis ::  para colorear y remarcar palabras reservadas, comentarios y simbolos del lenguaje y producir codigo más legible


Reimplementamos QPlainTextEdit:

-        - Para capturar los atajos de teclado más importantes y que se ejecuten mis acciones en lugar de las predeterminadas.
-        - Para resaltar la línea en la que estamos escribiendo en ese momento.
-        - Para calcular y pintar los números de línea (manejado por eventos y señales) en el widget LineNumberArea
-        - Para visitar las declaraciones de nombres en el código

"""

class AreaCodigo(QPlainTextEdit):

    """
    
    Constructor ::  AreaCodigo

    Creamos un QPlainTextEdit con super y:
    -     - Definimos un estilo "claro".
    -     - Creamos nuestro resaltador de sintaxis y llamamos a highlightcode para que el resaltador apunte al documento de area_codigo.
    -     - Creamos nuestro widget NumeroDeLinea y conectamos señales cuando añadimos o eliminamos un nuevo bloque de texto, actualizar el numero de linea y resaltar la linea
    -     actual (en la que se encuentra el cursor).
    -     - Llamamos para inicializar la anchura del widget y resaltar la linea actual nada más abrir el documento, después se actualizará el número de línea y la anchura del widget
    -     una vez que insertemos texto en nuestro AreaCodigo

    """
    nameChecker : NameChecker
    resaltado_sintaxis : Highlighter


    def __init__(self, claridad:bool):
        super().__init__()

        self.claridad = claridad

        self.resaltado_sintaxis = Highlighter()
        self.highlight_code()

        self.setEstilo(claridad)

        self.area_NumeroDeLinea = NumeroDeLinea(self)
        self.blockCountChanged[int].connect(lambda newBlockCount: self.actualizar_anchura_area_NumeroDeLinea(newBlockCount))
        self.updateRequest[QRect, int].connect(lambda rect, dy: self.actualizar_area_NumeroDeLinea(rect, dy))
        self.cursorPositionChanged.connect(self.resaltar_lineaActual)

        self.actualizar_anchura_area_NumeroDeLinea(0)
        self.resaltar_lineaActual()

    """
    
    set Estilo
    
    """

    def setEstilo(self, estilo:bool):

        self.claridad = estilo

        if  self.claridad == True:
            self.setStyleSheet("background-color: #C0C0C0;"
                                        "color: #1a1a1a;"
                                        "font-size: 15px")
            
        else:
            self.setStyleSheet("background-color: #17202a;"
                                        "color: #DCDCDC;"
                                        "font-size: 15px")


    """
    
    highlight  code

    El resaltador de sintaxis apunta al documento de AreaCodigo
    
    """

    def highlight_code(self):
        self.resaltado_sintaxis.setDocument(self.document())

    """
    
    construir  NameChecker

    Llamada a Constructor y devuelve el visitador
    
    """

    def construir_nameChecker(self):
        self.nameChecker = NameChecker()
        return self.nameChecker

    """
   
    anchura_area_NumeroDeLinea

    @return space :: Espacio medido en función de los digitos del numero de linea

    Devuelve la anchura actual del widget para los eventos de reespaciado de la anchura del widget NumeroDeLinea

    La anchura crece en función del número de cifras del número de línea
   
    """

    def anchura_area_NumeroDeLinea(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num *= 0.1
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    """
    
    resizeEvent

    @param  e   ::  Evento

    Reimplementado de resize event

    Devuelve el área del area_codigo (menos la anchura) + la anchura calculada de nuevo en función del número de cifras del número de línea

    para calcular el nuevo rectangulo que contiene el widget NumeroDeLinea y lo redimensiona
    
    """

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        width = self.anchura_area_NumeroDeLinea()
        rect = QRect(cr.left(), cr.top(), width, cr.height())
        self.area_NumeroDeLinea.setGeometry(rect)

    """
    
    evento_pintar_NumeroDeLinea

    @param  event   ::  Evento

    Crea un QPainter a raíz del evento de NumeroDeLinea paintEvent, calcula el area_NumeroDeLinea y pinta el número de
    -   línea. El bucle es para cuando abrimos un archivo fuente y tenemos por tanto que pintar varios bloques.
    -   Al terminar, cerramos el QPainter.


    """

    def evento_pintar_NumeroDeLinea(self, event):
        painter = QPainter(self.area_NumeroDeLinea)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = int(self.blockBoundingGeometry(block).translated(offset).top())
        bottom = int(top + self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                width = self.area_NumeroDeLinea.width()
                height = self.fontMetrics().height()
                painter.drawText(0, top, width, height, Qt.AlignRight, number)

            block = block.next()
            top = int(bottom)
            bottom = int(top + self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    """
    
    keyPressEvent

    @param event ::  Evento

    Reimplementado de resize event

    Para que se ejecuten las acciones que he implementado en lugar de las acciones nativas para:

    -       - Deshacer.
    -       - Rehacer.
    -       - Pegar
    
    """

    def keyPressEvent(self, event):
        if event.modifiers() & QApplication.keyboardModifiers() == QApplication.keyboardModifiers():
            key = event.key()
            if key == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
                self.parent().parent().parent().parent().parent().parent().ui.actionDeshacer.trigger()
                return
            if key == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
                self.parent().parent().parent().parent().parent().parent().ui.actionRehacer.trigger()
                return
            if key == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
                self.parent().parent().parent().parent().parent().parent().ui.actionPegar.trigger()
                return
            else:
                super().keyPressEvent(event)

    """
    
    contextMenuEvent

    @param  event   ::  Evento

    Reimplementado de contextMenuEvent

    Para que se muestren y ejecuten las acciones que he implementado con sus atajos de teclado en  lugar de las nativas

    """

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        menu.clear()

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

        accionDeshacer  = QAction("Deshacer", self)
        accionDeshacer.setShortcut("Ctrl+Z")
        accionDeshacer.triggered.connect(self.undo)
        menu.addAction(accionDeshacer)
        
        accionRehacer  = QAction("Rehacer", self)
        accionRehacer.setShortcut("Ctrl+Y")
        accionRehacer.triggered.connect(self.redo)
        menu.addAction(accionRehacer)
        menu.addSeparator()

        accionCortar = QAction("Cortar", self)
        accionCortar.setShortcut("Ctrl+X")
        accionCortar.triggered.connect(self.cut)
        menu.addAction(accionCortar)

        accionCopiar = QAction("Copiar", self)
        accionCopiar.setShortcut("Ctrl+C")
        accionCopiar.triggered.connect(self.copy)
        menu.addAction(accionCopiar)

        accionPegar = QAction("Pegar", self)
        accionPegar.setShortcut("Ctrl+V")
        accionPegar.triggered.connect(self.paste)
        menu.addAction(accionPegar)

        accionSeleccionarTodo = QAction("Seleccionar todo")
        accionSeleccionarTodo.setShortcut("Ctrl+A")
        accionSeleccionarTodo.triggered.connect(self.selectAll)
        menu.addAction(accionSeleccionarTodo)

        menu.exec_(event.globalPos())

    """
    
    Slot    actualizar_anchura_area_NumeroDeLinea

    @param  newBlockCount    ::  Numero de bloques (lineas) actual

    Cuando cambia el numero de bloques si cambia la anchura del widget NumeroDeLinea es necesario redimensionar sus margenes (a parte del resize event reimplementado)
    
    """

    @pyqtSlot()
    def actualizar_anchura_area_NumeroDeLinea(self, newBlockCount):
        self.setViewportMargins(self.anchura_area_NumeroDeLinea(), 0, 0, 0)

    """
    
    Slot    actualizar_area_NumeroDeLinea

    @param  rect    ::  Rectangulo que contiene al widget NumeroDeLinea
    @param  dy      ::  Pixeles a desplazar hacia abajo el widget

    -       - Si llegamos al final del desplazamiento del widget se desplaza hacia abajo dy pixeles
    -       - En otro caso se actualiza el rectangulo que contiene al widget por si ha cambiado la anchura
    -       - Si el nuevo rectangulo contiene la zona visible del widget, se llama a actualizar la anchura
    
    """

    @pyqtSlot()
    def actualizar_area_NumeroDeLinea(self, rect, dy):
        if dy:
            self.area_NumeroDeLinea.scroll(0, dy)
        else:
            width = self.area_NumeroDeLinea.width()
            self.area_NumeroDeLinea.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.actualizar_anchura_area_NumeroDeLinea(0)

    """
    
    Slot    resaltar_lineaActual

    setExtraSelections recibe un array, es por ello que creamos la variable selecciones. Esta función será la que finalmente "pinte" el fondo de la línea actual.

    Creamos nuestra seleccion, la estructura que nos permite especificar el formato, en este caso de la linea actual.
    -   Formateamos la seleccion dandole un color amarillo de fondo para resaltarla con anchura máxima y hacemos que apunte al cursor de texto
    -   que señala la línea actual.
    
    """

    @pyqtSlot()
    def resaltar_lineaActual(self):
        selecciones = self.extraSelections()
        
        for seleccion in selecciones:
            if seleccion.format.underlineStyle() != QTextCharFormat.SpellCheckUnderline:
                seleccion.format.clearBackground()

        seleccion = QTextEdit.ExtraSelection()
        line_color = QColor(Qt.yellow).lighter(185)
        
        seleccion.format.setBackground(line_color)
        seleccion.format.setProperty(QTextFormat.FullWidthSelection, True)

        seleccion.cursor = self.textCursor()
        seleccion.cursor.clearSelection()

        selecciones.append(seleccion)

        self.setExtraSelections(selecciones)
