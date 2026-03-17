import os
import sys
import ast
import functools
import traceback
import Programa
import Consola
#import ConsolaClase_copy
import Explorador

from ConfigWindow import ConfigWindow
from VentanaAyuda import VentanaAyuda
#from Debugger_copy import Debugger
from GUI import GUI
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import Qt

"""

Clase Controlador de la Ventana Principal de nuestro IDE :

***********************************************************                  ATRIBUTOS                      ******************************************************************

programas ::             Estructura de datos lista que mantiene los programas (objeto) que tenemos abiertos/creados
consolas  ::             Estructura de datos lista que mantiene las consolas (objeto) que tenemos abiertas
contadorWidget ::        Contador para el constructor de programa, que sirve para nombrar algunos de sus atributos/widgets
contadorDocumento ::     Contador para el número de nuevos programas abiertos, ej: Sin-Titulo-1, Sin-Titulo-2, etc.
process   ::             Clase usada para iniciar y ejecutar los programas que creamos en nuestro IDE y comunicarnos con ellos
_translate ::            Renombrado de la operación para ahorrar un poco de espacio, usado principalmente en operaciones de setTabText del tabWidget
filtros   ::             La extensión de los archivos que queremos que aparezcan en nuestro explorador lateral
pathRaiz  ::             El paz raíz del explorador
indexRaiz ::             El indice (QModelIndex) raíz del explorador
pathDirectorios   ::     Estructura de datos lista que mantiene los path de los directorios en los que vamos navegando para volver al padre con el boton "Back"

"""

class Controlador(qtw.QMainWindow):

    programas : list[Programa.Programa] = []
    consolas  : list[Consola.Consola] = []
    errores   : list[SyntaxError] = []
    filtros   : list[str] = ['*.py']
    #pathRaiz  : str = "E:\Daniel\LA UNIVERSIDAD MOLA\TFG\Código y Pruebas"
    pathRaiz = os.path.expanduser("~")
    indexRaiz : qtc.QModelIndex
    pathDirectorios : list[str] = [pathRaiz]
    contadorWidget = 0
    contadorDocumento = 0
    process : QProcess
    _translate = qtc.QCoreApplication.translate
    claridad : bool

    """
     
     Constructor    ::   IDEMainWWindow

     @param         ::   Recibe todos los widgets, atributos y funciones inicializadas en la clase prototipo2gui.py
     
     Monta la interfaz de usuario, el modelo de archivos (QFileSystemModel)
     -    Llamos a setupExplorador para montar el Explorador de archivos y directorios
     -    Llamo a setupEnables para añadir los enables de las acciones de los menús predeterminados al abrir la aplicación
     -    Llamo a setupConnects para 'conectar' las acciones y botones que disparan los metodos deseados

    """

    def __init__(self,  *args, **kwargs):
          super().__init__(*args, **kwargs)

          self.ui = GUI()
          self.ui.setupIU(self)

          self.claridad = False
          self.process = QProcess(self)
          self.timer = qtc.QTimer()
          self.timer.setSingleShot(True)
          self.clipboard = qtw.QApplication.clipboard()
          self.modeloArchivos = qtw.QFileSystemModel()
          self.indexRaiz = self.modeloArchivos.setRootPath(self.pathRaiz)
          self.modeloArchivos.setNameFilters(self.filtros)
          self.modeloArchivos.setNameFilterDisables(False)

          self.setupConfiguracion()
          
          self.setupExplorador()

          self.setupEnables()

          self.setupConnects()

    """
    
    setup Configuracion
    
    Creo la ventana de configuracion y la añado al menu bar de la ventana principal

    """

    def setupConfiguracion(self):

          self.configWindow = ConfigWindow(self.pathRaiz, self.claridad)
          self.accionConfig = qtw.QAction('Configuración', self)
          
          self.configWindow.cambiosReflejados.connect(lambda cambios: self.cambiar_configuracion(cambios))
          self.accionConfig.triggered.connect(self.abrir_configuracion)
          self.ui.menubar.addAction(self.accionConfig)

          self.ventanaAyuda = VentanaAyuda()
          self.actionAyuda = qtw.QAction('Ayuda', self)
          self.ui.menubar.addAction(self.actionAyuda)
          self.actionAyuda.triggered.connect(self.abrir_ayuda)

    def abrir_ayuda(self):
         self.ventanaAyuda.show()

    """
    
    Abrir Configuracion

    Abre la ventana de configuracion

    """

    def abrir_configuracion(self):

          self.configWindow.exec_()

    """
    
    Cambiar Configuracion

    """

    def cambiar_configuracion(self, cambios):
         
          path = cambios[0]
          estilo = cambios[1]

          if estilo == "Oscuro" and self.claridad == True:
               self.switch_estilo()
          elif estilo == "Claro" and self.claridad == False:
               self.switch_estilo()
          self.switch_path(path)

    """
    
    setup Explorador

    Crea el explorador de archivos y directorios con 2 botones:
    -     Boton Raiz ::  Para volver al directorio raíz de nuestro explorador
    -     Boton Back ::  Para volver al directior anterior, gracias a una estructura de datos donde almaceno los paths 'pathDirectorios'

    """

    def setupExplorador(self):

          self.explorador = Explorador.Explorador(self.modeloArchivos, self.ui.frame_2)
          self.explorador.setMaximumSize(qtc.QSize(16777215, 9000))
          self.explorador.setObjectName("explorador")
          self.ui.verticalLayout_3.addWidget(self.explorador)
          self.horizontalLayout_3 = qtw.QHBoxLayout()
          self.horizontalLayout_3.setContentsMargins(-1, 0, 120, -1)
          self.horizontalLayout_3.setSpacing(0)
          self.horizontalLayout_3.setObjectName("horizontalLayout_4")
          self.BackButton = qtw.QPushButton(self.ui.frame_2)
          self.BackButton.setMaximumSize(qtc.QSize(40, 30))
          icon = qtg.QIcon.fromTheme("go-home")
          self.BackButton.setIcon(icon)
          self.BackButton.setObjectName("pushButton_2")
          self.BackButton.setText(self._translate("MainWindow", "Back"))
          self.horizontalLayout_3.addWidget(self.BackButton, 0, qtc.Qt.AlignLeft)
          self.RaizButton = qtw.QPushButton(self.ui.frame_2)
          self.RaizButton.setMaximumSize(qtc.QSize(40, 30))
          icon = qtg.QIcon.fromTheme("go-previous")
          self.RaizButton.setIcon(icon)
          self.RaizButton.setObjectName("pushButton")
          self.RaizButton.setText(self._translate("MainWindow", "Raíz"))
          self.horizontalLayout_3.addWidget(self.RaizButton, 0, qtc.Qt.AlignLeft)
          self.ui.verticalLayout_3.addLayout(self.horizontalLayout_3)

          self.explorador.setModel(self.modeloArchivos)
          self.explorador.setRootIndex(self.indexRaiz)
          self.explorador.setColumnHidden(1, True)
          self.explorador.setColumnHidden(2, True)
          self.explorador.setColumnWidth(0, 220)
          self.explorador.setColumnWidth(3, 150)

    """
    
    setup Enables

    Añado los enables de las acciones de los menús predeterminados al abrir la aplicación
    
    """

    def setupEnables(self):
         
         self.ui.actionGuardar.setEnabled(False)
         self.ui.actionGuardar_como.setEnabled(False)
         self.ui.actionGuardar_todo.setEnabled(False)
         self.ui.actionCerrar.setEnabled(False)
         self.ui.actionCerrar_todo.setEnabled(False)
         self.ui.actionCopiar.setEnabled(False)
         self.ui.actionCortar.setEnabled(False)
         self.ui.actionPegar.setEnabled(False)
         self.ui.actionSeleccionar_todo.setEnabled(False)
         self.ui.actionDeshacer.setEnabled(False)
         self.ui.actionRehacer.setEnabled(False)

    """
    
    setup Connects

    Conecto los botones y acciones para que disparen los metodos deseados
    
    """

    def setupConnects(self):
         
          self.ui.tabWidget.currentChanged.connect(lambda index: self.tab_cambiada(index))
          self.ui.tabWidget.tabBar().tabMoved.connect(lambda destino, origen: self.tab_movida(destino, origen))
          self.ui.actionNuevo.triggered.connect(self.nuevo_programa)
          self.ui.actionAbrir.triggered.connect(self.abrir_programa)
          self.ui.actionGuardar.triggered.connect(self.guardar_programa)
          self.ui.actionGuardar_como.triggered.connect(self.guardarComo_programa)
          self.ui.actionGuardar_todo.triggered.connect(self.guardarTodos_programas)
          self.ui.actionCerrar.triggered.connect(lambda index: self.cerrar_programa(index))
          self.ui.actionCerrar_todo.triggered.connect(self.cerrarTodos_programas)
          self.ui.tabWidget.tabCloseRequested.connect(lambda index: self.cerrar_programa(index))
          self.ui.actionDeshacer.triggered.connect(self.deshacer)
          self.ui.actionRehacer.triggered.connect(self.rehacer)
          self.ui.actionCortar.triggered.connect(self.cortar)
          self.ui.actionCopiar.triggered.connect(self.copiar)
          self.ui.actionPegar.triggered.connect(self.pegar)
          self.ui.actionSeleccionar_todo.triggered.connect(self.seleccionar_todo)
          self.ui.Ejecutar.pressed.connect(self.ejecutar_programa)
          self.ui.Debug.pressed.connect(self.depurar_programa)
          self.BackButton.pressed.connect(self.explorador_indiceBack)
          self.RaizButton.pressed.connect(self.explorador_indiceRaiz)
          self.explorador.doubleClicked.connect(self.explorador_clickado)
          self.explorador.accionAbrir.triggered.connect(lambda: self.explorador_clickado(self.explorador.currentIndex()))
          self.explorador.accionPath.triggered.connect(lambda: self.explorador_getPath(self.explorador.currentIndex()))
          self.explorador.accionPathRel.triggered.connect(lambda: self.explorador_getPathRel(self.explorador.currentIndex()))
          self.explorador.renombrado.connect(lambda cambios: self.renombrar_programa(cambios))
          self.explorador.eliminado.connect(lambda path: self.eliminar_programa(path))

    """
    
    switch Estilo

    Cambia el estilo del código de claro a oscuro o viceversa

    """

    def switch_estilo(self):
         
         self.claridad = not self.claridad

         for programa in self.programas:
              programa.area_codigo.setEstilo(self.claridad)

         for consola in self.consolas:
              consola.setEstilo(self.claridad)

    """
    
    switch Path

    Cambia el Path Raíz del IDE y cambia el explorador para reflejar los cambios

    """

    def switch_path(self, path:str):
         
         self.pathDirectorios.clear()
         self.pathRaiz = path
         self.pathDirectorios.append(self.pathRaiz)
         self.indexRaiz = self.modeloArchivos.setRootPath(self.pathRaiz)
         self.explorador.setRootIndex(self.indexRaiz)

    """

    Pestaña Cambiada 
    
    @param index   ::   indice de la pestaña del tabWidget

    Acción disparada cuando cambia la pestaña seleccionada, el indice de la pestaña del tabwidget corresponde con el indice de programas[]
    así, al cambiar la pestaña la señal pasa el nuevo índice a este método que se utiliza para cargar los enables del programa de la nueva pestaña

    """

    def tab_cambiada(self, index:int):
         programa_actual = self.programas[index]
         self.enable_editar(programa_actual)

    """
     
    Pestaña movida

    @param origen ::  indice donde se encontraba la pestaña antes de moverla
    @param destino :: indice donde se encuentra ahora la pestaña

    Acción disparada al mover una pestaña de sitio, hacemos pop a la posición del programa movido en la estructura de datos programas[]
    y volvemos a insertarlo en el destino donde hemos movido la pestaña para que el indice de tabWidget siga coincidiendo con el de programas[]
     
    """

    def tab_movida(self, destino:int, origen:int):
         programa_movido = self.programas[origen]
         self.programas.pop(origen)
         self.programas.insert(destino, programa_movido)

    """
     
    Programa modificado

    @param index ::   indice del programa de programas[]

    Acción disparada al modificar el texto del area_codigo del programa_actual
    Si el programa es nuevo, cambiamos únicamente cambiamos modificado a True
    Si el programa es uno abierto (Tiene ruta_archivo); 
    -              si tenía modificado = False, cambia el nombre de la pestaña del tabWidget para señalar que está modificado con '*' y modificado <- True
    -              si el contenido actual de area_codigo coincide con su contenido_original eliminamos el '*' para señalar que no está modificado y modificado <- False
    Finalmente se cargan de nuevo sus enables

    """

    def programa_modificado(self, index:int):
          programa_actual = self.programas[index]

          if programa_actual.ruta_archivo != '' and programa_actual.modificado == False:
            self.ui.tabWidget.setTabText(index, self._translate('MainWindow', str(self.ui.tabWidget.tabText(index))+'*'))
            programa_actual.modificado = True
          else:
            programa_actual.modificado = True

          if programa_actual.ruta_archivo != '' and programa_actual.es_contenidoOriginal():
            self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), self._translate('MainWindow', programa_actual.ruta_archivo.rpartition('/')[2]))
            programa_actual.modificado = False        

          self.enable_editar(programa_actual)
 
          self.timer.singleShot(1500, functools.partial(self.parsear_codigo, programa_actual))

    """
     
    Acciones set_Enabled

    @param enable  ::   True/False

    Inicialmente al abrir la aplicación todas están a False
    Al abrir un programa se habilitan enable = True
    Al no tener ningun programa abierto se deshabilitan enable = False

    """

    def acciones_setEnabled(self, enable):
        self.ui.actionGuardar.setEnabled(enable)
        self.ui.actionGuardar_como.setEnabled(enable)
        self.ui.actionGuardar_todo.setEnabled(enable)
        self.ui.actionCerrar.setEnabled(enable)
        self.ui.actionCerrar_todo.setEnabled(enable)
        self.ui.actionPegar.setEnabled(enable)
        self.ui.actionSeleccionar_todo.setEnabled(enable)

    """
     
    Enable editar

    @param programa_actual   ::   programa_actual proporcionado por otra función

    Se llama a este programa para cargar los enables que tiene disponibles de las acciones del menú editar:
    -    Si la acción ya está habilitada (para no pasar siempre por estas lineas de codigo) y el area_codigo no está vacía se puede copiar y cortar
    -    Se cargan los enables de Deshacer/Rehacer haciendo uso de las señales isUndoAvailable y isRedoAvailable

    """

    def enable_editar(self, programa_actual:Programa.Programa):
         
         if not self.ui.actionCopiar.isEnabled() and programa_actual.area_codigo.toPlainText() != '':
            self.ui.actionCopiar.setEnabled(True)
            self.ui.actionCortar.setEnabled(True)

         if programa_actual.area_codigo.toPlainText() == '':
            self.ui.actionCopiar.setEnabled(False)
            self.ui.actionCortar.setEnabled(False)

         if programa_actual.area_codigo.document().isUndoAvailable():
            self.ui.actionDeshacer.setEnabled(True)
         else:
            self.ui.actionDeshacer.setEnabled(False)

         if programa_actual.area_codigo.document().isRedoAvailable():
            self.ui.actionRehacer.setEnabled(True)
         else:
            self.ui.actionRehacer.setEnabled(False) 

    """
     
    Conectar Area_codigo

    @param programa ::  programa actual

    Al abrir un archivo o crear uno nuevo se conecta su area_codigo para disparar la acción programa_modificado cuando cambia su texto

    """

    def conectarArea_codigo(self, programa:Programa.Programa):
        try:
          programa.area_codigo.textChanged.connect(lambda: self.programa_modificado(self.programas.index(programa)))
        except ValueError:
          pass

    """
    
    Parsear codigo

    @param programa_actual  ::  Programa actual en el que el texto ha cambiado

    limpiar errores previos (consolas) y parsea en busca de errores de sintaxis, si no hay errores de sintaxis:
    - se visitan los nodos (nombres) del arbol abstracto sintactico en busca de nombres que se quieren utilizar pero no han sido declarados y llama para resaltarlos (amarillo)
    - si encuentra un error de sintaxis, captura la excepción y resalta el error en rojo.

    No se resaltan todos los errores de sintaxis, solo se resalta el primero que se encuentra parseando el codigo hasta el final
    
    """

    def parsear_codigo(self, programa_actual:Programa.Programa):

         area_codigo = programa_actual.area_codigo

         area_codigo.blockSignals(True)

         self.limpiar_errores(area_codigo)

         try:
              arbol = ast.parse(area_codigo.toPlainText())
              visitador = area_codigo.construir_nameChecker()

              visitador.visit(arbol)
              if visitador.errors:
                    for lineno, col_offset, nombre in visitador.errors:
                         self.resaltar_nombreNoDeclarado(area_codigo, lineno, col_offset, nombre)

         except SyntaxError as e:
              self.resaltar_error(e, area_codigo)

         finally:
              area_codigo.blockSignals(False)
              
    """
    
    Resaltar nombre no declarado

    @param  area_codigo  ::   el codigo (texto) del programa que tenemos abierto y hemos editado por último
    @param  lineno       ::   número de línea donde se encuentra el nombre
    @param  col_offset   ::   número de columna donde empieza el nombre
    @param  nombre       ::   nombre (texto) no declarado

    Posicionamos el cursor seleccionando el nombre no declarado (down hasta su linea, right a partir de donde empieza y hasta la longitud del nombre)
    Creamos un formato (subrayado amarillo oscuro) y añadimos la seleccion a extraselections de area_codigo

    """

    def resaltar_nombreNoDeclarado(self, area_codigo:Programa.AreaCodigo, lineno:int, col_offset:int, nombre:str):
         
         selecciones = []
         seleccion = qtw.QTextEdit.ExtraSelection()

         seleccion.format.setUnderlineStyle(qtg.QTextCharFormat.SpellCheckUnderline)
         seleccion.format.setUnderlineColor(Qt.darkYellow)

         seleccion.cursor = area_codigo.textCursor()
         seleccion.cursor.clearSelection()
         seleccion.cursor.movePosition(qtg.QTextCursor.Start)

         for _ in range(lineno - 1):
            seleccion.cursor.movePosition(qtg.QTextCursor.Down)

         seleccion.cursor.movePosition(qtg.QTextCursor.Right, qtg.QTextCursor.MoveAnchor, col_offset)
         seleccion.cursor.movePosition(qtg.QTextCursor.Right, qtg.QTextCursor.KeepAnchor, len(nombre))

         selecciones.append(seleccion)

         area_codigo.setExtraSelections(selecciones)

    """
    
    Resaltar error

    @param error_msg   :: error del SyntaxError del parser para recuperar la posición donde se ha producido y el tipo de error cometido
    @param area_codigo :: el codigo (texto) del programa que tenemos abierto y hemos editado por último

    Posicionamos el cursor seleccionando el error de sintaxis (down hasta su linea, right a partir de donde empieza y hasta donde acaba tanto right como down)
    Creamos un formato (subrayado rojo) y lo añadimos a extraselections de area_codigo con la seleccion
    Creamos una consola de error de sintaxis para mostrar el tipo de error cometido y su información relacionada, si ya existe una consola de error de sintaxis la cerramos
    
    """

    def resaltar_error(self, error_msg:SyntaxError, area_codigo:Programa.AreaCodigo):
         
         selecciones = area_codigo.extraSelections()
         seleccion = qtw.QTextEdit.ExtraSelection()

         seleccion.format.setUnderlineStyle(qtg.QTextCharFormat.SpellCheckUnderline)
         seleccion.format.setUnderlineColor(Qt.red)

         seleccion.cursor = area_codigo.textCursor()
         seleccion.cursor.clearSelection()
         seleccion.cursor.movePosition(qtg.QTextCursor.Start)

         for _ in range(error_msg.lineno - 1):
            seleccion.cursor.movePosition(qtg.QTextCursor.Down)

         seleccion.cursor.movePosition(qtg.QTextCursor.Right, qtg.QTextCursor.MoveAnchor, error_msg.offset -1)
         seleccion.cursor.movePosition(qtg.QTextCursor.Right, qtg.QTextCursor.KeepAnchor, error_msg.end_lineno-1)

         selecciones.append(seleccion)

         area_codigo.setExtraSelections(selecciones)

         tipo = 'Error de Sintaxis'

         for consola in self.consolas:
              if tipo == consola.ruta_archivo:
                   self.cerrar_consola(self.consolas.index(consola))

         self.crear_consola(tipo)
         self.consolas[-1].consola.insertPlainText("Error en linea: "+ str(error_msg.lineno) + "\n" + error_msg.msg + "\n" + error_msg.text)

    """
    
    Limpiar errores

    Eliminamos todas las selecciones de area_codigo y seleccionamos todos el texto con el cursor y quitamos el subrayado
    Si existe una consola de error de sintaxis la eliminamos

    """

    def limpiar_errores(self, area_codigo:Programa.AreaCodigo):

        selecciones = area_codigo.extraSelections()
        
        selecciones.clear()

        seleccion = qtw.QTextEdit.ExtraSelection()
        seleccion.cursor = area_codigo.textCursor()

        seleccion.format.setUnderlineStyle(qtg.QTextCharFormat.NoUnderline)
        seleccion.cursor.movePosition(qtg.QTextCursor.Start)
        seleccion.cursor.movePosition(qtg.QTextCursor.End, qtg.QTextCursor.KeepAnchor)

        selecciones.append(seleccion)

        area_codigo.setExtraSelections(selecciones)

        for consola in self.consolas:
           if consola.ruta_archivo == 'Error de Sintaxis':
               self.cerrar_consola(self.consolas.index(consola))

    """
     
     Acción    Nuevo

     Crea un nuevo programa "Sin-Titulo- + (contadorDocumento)"
     -    Llama al constructor y lo añade al final de la estructura programas[]
     -    Añade la pestaña del programa al tabWidget
     -    Nombra la pestaña
     -    Conecta su area_codigo
     -    Si las acciones de archivo no están habilitadas, las habilita
     -    Pone el foco en el nuevo

    """

    def nuevo_programa(self):
        self.contadorWidget += 1
        self.contadorDocumento += 1

        self.programas.append(Programa.Programa('', self.contadorWidget, self.claridad))

        self.ui.tabWidget.addTab(self.programas[-1].tab, '')
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.programas[-1].tab), self._translate('MainWindow', 'Sin-Titulo-'+str(self.contadorDocumento)))

        self.conectarArea_codigo(self.programas[-1])

        if not self.ui.actionGuardar.isEnabled():
          self.acciones_setEnabled(True)

        self.ui.tabWidget.setCurrentWidget(self.programas[-1].tab)

    """
     
     Acción    Abrir

     @param path :: ruta proporcionada por el explorador, si no se proporciona:
     -         Abre un programa.py existente haciendo uso de QFileDialog, abre una ventana de selección de archivo nativa para archivos python *py *pyw

     Ejecuta las mismas acciones que cuando creamos uno Nuevo y además:
     -    Carga en su area_codigo los contenidos del archivo fuente
     -    Inicializa su contenido_original (set_contenidoOriginal())
     -    Si el programa ya estaba abierto, cambia el foco a la pestaña que contiene el programa ya abierto y no hace nada más

    """

    def abrir_programa(self, path:str =''):
        programa_abierto:bool = False
        programa_actual:Programa.Programa

        try:
            if path == "" or path == False:
                    ruta_archivo, _ = QFileDialog.getOpenFileName(self.ui.tabWidget, 'Abrir archivo fuente Python', self.pathRaiz, 'Python File (*py *pyw)')
            else:     
                    ruta_archivo = path

            for programa in self.programas:
                 if ruta_archivo == programa.ruta_archivo:
                      programa_abierto = True
                      programa_actual = programa
            if not programa_abierto:
                with open(ruta_archivo, 'r') as doc:
                    self.contadorWidget += 1

                    self.programas.append(Programa.Programa(ruta_archivo, self.contadorWidget, self.claridad))

                    self.ui.tabWidget.addTab(self.programas[-1].tab, '')
                    self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.programas[-1].tab), self._translate('MainWindow', ruta_archivo.rpartition('/')[2]))

                    self.programas[-1].area_codigo.document().setUndoRedoEnabled(False)
                    self.programas[-1].area_codigo.setPlainText(doc.read())
                    self.programas[-1].set_contenidoOriginal()
                    self.conectarArea_codigo(self.programas[-1])
                    if not self.ui.actionGuardar.isEnabled():
                         self.acciones_setEnabled(True)

                    self.ui.tabWidget.setCurrentWidget(self.programas[-1].tab)
                    self.parsear_codigo(self.programas[-1])
                    self.programas[-1].area_codigo.document().setUndoRedoEnabled(True)
            else:
                 self.ui.tabWidget.setCurrentWidget(programa_actual.tab)

        except FileNotFoundError:
                    pass
        except Exception:
               tipo = 'Error al abrir el programa'

               for consola in self.consolas:
                    if tipo == consola.ruta_archivo:
                         self.cerrar_consola(self.consolas.index(consola))

               self.crear_consola(tipo)
               error_msg = 'Error, no se pudo abrir el archivo especificado\n'     
               self.consolas[-1].consola.insertPlainText(error_msg)

    """
     
     Acción    Guardar

     Guarda el programa actual, programa/pestaña que tiene el foco
     -    Si el programa no está modificado no hace nada (no hace falta guardarlo)
     -    Si el programa es un archivo nuevo (no tiene ruta), se ejecuta en su lugar -> guardarComo_programa()
     -    En cualquier otro caso, se abre el archivo haciendo uso de su ruta y se escribe en el, se cambia el nombre de la pestaña a no modificado (sin '*')
     -    y se carga su nuevo contenido original y modificado <- False

    """

    def guardar_programa(self):
        programa_actual = self.programas[self.ui.tabWidget.currentIndex()]

        if programa_actual.ruta_archivo == '':
             self.guardarComo_programa()

        if programa_actual.modificado == False:
             return
        
        else:
            try:
                with open(programa_actual.ruta_archivo, 'w') as doc:
                    doc.write(programa_actual.area_codigo.toPlainText())
                    self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), self._translate('MainWindow', programa_actual.ruta_archivo.rpartition('/')[2]))
                    programa_actual.set_contenidoOriginal()
                    programa_actual.modificado = False

            except FileNotFoundError:
                 pass
            except Exception:
               tipo = 'Error de Guardado'

               for consola in self.consolas:
                    if tipo == consola.ruta_archivo:
                         self.cerrar_consola(self.consolas.index(consola))

               self.crear_consola(tipo)
               error_msg = 'Error, no se pudo guardar el archivo especificado\n'     
               self.consolas[-1].consola.insertPlainText(error_msg)

    """
     
     Acción    Guardar como

     Guarda el programa actual, programa/pestaña que tiene el foco haciendo uso de QFileDialog
     -    Si el programa es nuevo (no tiene ruta_archivo), se añade '.py' al final de su nombre para guardarlo y se guarda en una ruta_archivo auxiliar
     -    Si no, no se añade .py pues ya debería tenerlo al ser un archivo abierto
     -    En cualquier caso, si ruta archivo contiene el nombre (no hemos cancelado la operación), se abre el documento y se escribe en él y se llevan a cabo
     -    las mismas operaciones que en Guardar

    """

    def guardarComo_programa(self):
        programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
        if programa_actual.ruta_archivo  == '':
            ruta_archivo, _ = qtw.QFileDialog.getSaveFileName(self.ui.tabWidget, 'Guardar Archivo', self.pathRaiz + '/' + self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())+'.py', 'Python File (*py *pyw)')
        else:
            ruta_archivo, _ = qtw.QFileDialog.getSaveFileName(self.ui.tabWidget, 'Guardar Archivo', self.pathRaiz + '/' + self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()).removesuffix('*'), 'Python File (*py *pyw)')
        try:
          if ruta_archivo:
               with open(ruta_archivo, 'w') as doc:
                    doc.write(programa_actual.area_codigo.toPlainText())
                    self.programas[self.ui.tabWidget.currentIndex()].ruta_archivo = ruta_archivo
                    self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), self._translate('MainWindow', programa_actual.ruta_archivo.rpartition('/')[2]))
                    programa_actual.set_contenidoOriginal()
                    programa_actual.modificado = False

        except FileNotFoundError:
             pass
        except Exception:
               tipo = 'Error de Guardado'

               for consola in self.consolas:
                   if tipo == consola.ruta_archivo:
                        self.cerrar_consola(self.consolas.index(consola))

               self.crear_consola(tipo)
               error_msg = 'Error, no se pudo guardar el archivo especificado\n'
               self.consolas[-1].consola.insertPlainText(error_msg)

    """
     
     Acción Guardar Todo

     Se itera por la lista programas[] y se llama a guardar uno a uno

    """

    def guardarTodos_programas(self):
         for programa in self.programas:
              self.ui.tabWidget.setCurrentWidget(programa.tab)
              self.guardar_programa()

    """
    
    Acción Depurar Programa


    
    """

    def depurar_programa(self):

         try:
               programa_actual = self.programas[self.ui.tabWidget.currentIndex()]

               for consola in self.consolas:
                         if programa_actual.ruta_archivo.rpartition('/')[2] == consola.ruta_archivo:
                              self.cerrar_consola(self.consolas.index(consola))
                    
               if not programa_actual.es_contenidoOriginal() or programa_actual.ruta_archivo == '':
                         self.guardar_programa()
                    
               if not programa_actual.ruta_archivo == '':
                         #self.crear_consolaDebug(programa_actual.ruta_archivo)
                         #self.consolas[-1].consola.insertPlainText("python.exe: Debug "+ '"'+ programa_actual.ruta_archivo +'"\n\n')
                         self.crear_consola(programa_actual.ruta_archivo, True)
                         self.consolas[-1].consola.insertPlainText("python.exe "+ '"'+ programa_actual.ruta_archivo +'"\n\n')
                         self.consolas[-1].continueButton.pressed.connect(self.debug_continuar)
                         self.consolas[-1].nextButton.pressed.connect(self.debug_next)
                         self.consolas[-1].stepButton.pressed.connect(self.debug_step)
                         self.consolas[-1].stopButton.pressed.connect(self.debug_stop)

                         programa_actual.area_codigo.blockSignals(True) #Igual esto más adelante te sobra?


                         #debugger = Debugger(programa_actual.area_codigo.toPlainText())
                         self.process.start("python", ['-m', 'pdb', f'{programa_actual.ruta_archivo}'])
                         self.process.readyReadStandardOutput.connect(self.mostrar_salida)
                         self.process.readyReadStandardError.connect(self.mostrar_error)
                         #self.process.write(("n\n".encode('utf-8')))
                         #debugger.get_numeroLineas(programa_actual.ruta_archivo)
                         #MATA AL QPROCESS AL ACABAR

         except Exception as e:
              if len(self.programas) != 0:
                   error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
              else:
                   error_msg = 'Error, no hay ningún programa abierto'     
              
              tipo = 'Error de Depuración'

              for consola in self.consolas:
                   if tipo == consola.ruta_archivo:
                        self.cerrar_consola(self.consolas.index(consola))

              self.crear_consola(tipo)
              self.consolas[-1].consola.insertPlainText(error_msg)

         finally:
              if len(self.programas) != 0:
                    programa_actual.area_codigo.blockSignals(False)

    """
    
    debug continuar
    
    """

    def debug_continuar(self):
          self.process.write(("c\n".encode('utf-8')))

    """
    
    debug next
    
    """

    def debug_next(self):
         self.process.write(("n\n".encode('utf-8')))

    """
    
    debug step
    
    """

    def debug_step(self):
         self.process.write(("s\n".encode('utf-8')))

    """
    
    debug stop
    
    """

    def debug_stop(self):
         self.process.write(("q\n".encode('utf-8')))
         consola = self.consolas[self.ui.tabWidget_2.currentIndex()]
         consola.continueButton.setEnabled(False)
         consola.nextButton.setEnabled(False)
         consola.stepButton.setEnabled(False)
         consola.stopButton.setEnabled(False)

    """

     Acción Ejecutar Programa

     Acción que ejecuta el código actual al pulsar el botón y muestra el resultado o error/es por consola
     Se itera por la lista de consolas por si hubiese una ejecución ya abierta del mismo programa, se cierra y se vuelve a abrir para no tener varias instancias de ejecución
     del mismo programa
    
    """
     
    def ejecutar_programa(self):
         
         try:
              programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
              for consola in self.consolas:
                   if programa_actual.ruta_archivo.rpartition('/')[2] == consola.ruta_archivo:
                        self.cerrar_consola(self.consolas.index(consola))
              
              if not programa_actual.es_contenidoOriginal() or programa_actual.ruta_archivo == '':
                   self.guardar_programa()
              
              if not programa_actual.ruta_archivo == '':
                    self.crear_consola(programa_actual.ruta_archivo)
                    self.consolas[-1].consola.insertPlainText("python.exe "+ '"'+ programa_actual.ruta_archivo +'"\n\n')
              
                    self.process.start("python", [programa_actual.ruta_archivo])
                    self.process.readyReadStandardOutput.connect(self.mostrar_salida)
                    self.process.readyReadStandardError.connect(self.mostrar_error)

         except Exception as e:
              if len(self.programas) != 0:
                   error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
              else:
                   error_msg = 'Error, no hay ningún programa abierto'     
              
              tipo = 'Error de Ejecución'

              for consola in self.consolas:
                   if tipo == consola.ruta_archivo:
                        self.cerrar_consola(self.consolas.index(consola))

              self.crear_consola(tipo)
              self.consolas[-1].consola.insertPlainText(error_msg)

    """
    
    Acción mostrar_salida

    Muestra el resultado de los programas por su consola de ejecución correspondiente
    
    """

    def mostrar_salida(self):
         data = self.process.readAllStandardOutput().data()
         try:
               output = data.decode('utf-8')
         except UnicodeDecodeError:
               output = data.decode('latin-1')
         if self.consolas[-1].isDebug()  and output.__contains__("> <string>(1)<module>()->None"):
              self.debug_stop()
         else:
              self.consolas[-1].consola.insertPlainText(output)
         self.ui.tabWidget_2.setCurrentWidget(self.consolas[-1].tab)

    """
    
    Acción mostrar_error

    Muestra los errores de los programas por su consola de ejecución correspondiente
    
    """

    def mostrar_error(self):
         data = self.process.readAllStandardError().data()
         try:
            error_msg = data.decode('utf-8')
         except UnicodeDecodeError:
            error_msg = data.decode('latin-1')
         if self.consolas[-1].isDebug()  and error_msg.__contains__("> <string>(1)<module>()->None"):
              self.debug_stop()
         else:
              self.consolas[-1].consola.insertPlainText(error_msg)
         self.ui.tabWidget_2.setCurrentWidget(self.consolas[-1].tab) 

    """

     Crear Consola

     @param tipo :     Contiene el nombre del programa para identificar cada ejecución (consola) con su programa o el nombre error en la etiqueta de la pestaña

     Si no existen consolas se crea el tabwidget_2 para contenerlas
     Se añaden a la lista consolas y se añade su pestaña correspondiente, por último se nombra la pestaña de la consola con el mismo nombre que el programa para identificarlo
    
    """

    def crear_consola(self, tipo:str, debug=False):
         
         self.contadorWidget += 1

         if len(self.consolas) == 0 :
            self.ui.tabWidget_2 = qtw.QTabWidget(self.ui.frame)
            self.ui.tabWidget_2.setMaximumSize(qtc.QSize(16777215, 230))
            self.ui.tabWidget_2.setDocumentMode(True)
            self.ui.tabWidget_2.setTabsClosable(True)
            self.ui.tabWidget_2.setMovable(False)
            self.ui.tabWidget_2.setTabBarAutoHide(False)
            self.ui.tabWidget_2.setObjectName("tabWidget_2")
            self.ui.verticalLayout.addWidget(self.ui.tabWidget_2)
            self.ui.tabWidget_2.setCurrentIndex(-1)

            self.ui.tabWidget_2.tabCloseRequested.connect(lambda index: self.cerrar_consola(index))

         self.consolas.append(Consola.Consola(tipo, self.contadorWidget, debug, self.claridad))
         
         self.ui.tabWidget_2.addTab(self.consolas[-1].tab, '')
         self.ui.tabWidget_2.setTabText(self.ui.tabWidget_2.indexOf(self.consolas[-1].tab), self._translate('MainWindow', self.consolas[-1].ruta_archivo))
         self.ui.tabWidget_2.setCurrentWidget(self.consolas[-1].consola)

    """
    
    Crear consola de Debug

    @param tipo :     Contiene el nombre del programa para identificar cada depuración (consola) con su programa

    Si no existen consolas se crea el tabwidget_2 para contenerlas
    Se añaden a la lista consolas y se añade su pestaña correspondiente, por último se nombra la pestaña de la consola con el mismo nombre que el programa para identificarlo



    def crear_consolaDebug(self, tipo:str):

          self.contadorWidget += 1

          if len(self.consolas) == 0 :
               self.ui.tabWidget_2 = qtw.QTabWidget(self.ui.frame)
               self.ui.tabWidget_2.setMaximumSize(qtc.QSize(16777215, 230))
               self.ui.tabWidget_2.setDocumentMode(True)
               self.ui.tabWidget_2.setTabsClosable(True)
               self.ui.tabWidget_2.setMovable(False)
               self.ui.tabWidget_2.setTabBarAutoHide(False)
               self.ui.tabWidget_2.setObjectName("tabWidget_2")
               self.ui.verticalLayout.addWidget(self.ui.tabWidget_2)
               self.ui.tabWidget_2.setCurrentIndex(-1)

               self.ui.tabWidget_2.tabCloseRequested.connect(lambda index: self.cerrar_consola(index))

          self.consolas.append(ConsolaClase_copy.Consola(tipo, self.contadorWidget))
          
          self.ui.tabWidget_2.addTab(self.consolas[-1].consola, '')
          self.ui.tabWidget_2.setTabText(self.ui.tabWidget_2.indexOf(self.consolas[-1].consola), self._translate('MainWindow', tipo))
          self.ui.tabWidget_2.setCurrentWidget(self.consolas[-1].consola)
          """    

    """

     Cerrar consola

     @param index :      indice de la consola actual

     Pop de consolas[] y elimina la pestaña de tabWidget si no quedan pestañas se elimina el tabwidget entero para dejar el espacio completo para el area del codigo
     Si la consola es de debug, es posible que tengamos un QProcess abierto así que lo terminamos y esperamos a que termine
     
    """

    def cerrar_consola(self, index:int):
         
         consola_actual = self.consolas[index]

         self.ui.tabWidget_2.removeTab(index)
         if consola_actual.isDebug():
              self.process.kill()
              self.process.waitForFinished()
         self.consolas.pop(index)

         if self.ui.tabWidget_2.currentIndex() == -1:
              self.ui.tabWidget_2.deleteLater()

    """
    
    Cerrar todas las consolas

    Cierra todas las consolas/pestañas
     -    Itera por la estructura consolas[] desde el final hasta el principio
     -    Pone el foco en la consola (último hasta el primero) y llama a cerrar_consola
    
    """

    def cerrarTodas_consolas(self):
         
         for consola in range(len(self.consolas)-1, -1, -1):
             self.ui.tabWidget_2.setCurrentWidget(self.consolas[consola].get_consola())
             self.cerrar_consola(self.consolas.index(self.consolas[consola]))

    """
    
    Renombrar programa

    @param cambios:    El path y el nuevo nombre para renombrar, recuperados de la señal emitida por el Explorador

    Al renombrar un programa desde el explorador, lo cambiamos también en la ruta archivo del programa dentro de la estructura programas[] y en el tab si lo tenemos abierto
    
    """

    def renombrar_programa(self, cambios):
         
         path = cambios[0]
         nuevo_nombre = cambios[0].rpartition('/')[0] + "/" + cambios[1]

         for programa in self.programas:
              if programa.ruta_archivo == path:
                   programa.set_ruta_archivo(nuevo_nombre)
                   self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(programa.tab), self._translate('MainWindow', programa.ruta_archivo.rpartition('/')[2]))


    """
    
    Eliminar programa

    @param path:    El path del programa a eliminar recuperado de la señal emitida por el Explorador

    Cuando borramos un programa desde el explorador, lo eliminamos también de la estructura programas[] y eliminamos el tab si lo teniamos abierto

    """

    def eliminar_programa(self, path):
         
         for programa in self.programas:
             if programa.ruta_archivo == path:
                  self.cerrar_programa(self.programas.index(programa))


    """
    
    Explorador clickado

    Si el elemento doble clickado es un archivo lo abre con abrir_programa al que le pasamos la ruta

    Si es una carpeta se expanden sus contenidos como nueva raiz del explorador (navegación del directorio)
    -     también se añade el path de la carpeta a la lista de directorios
    
    """ 

    def explorador_clickado(self, index):
         
         path_clickado = self.modeloArchivos.filePath(index)

         if os.path.isfile(path_clickado):
              self.abrir_programa(path_clickado)
         else:
              indice = self.modeloArchivos.setRootPath(path_clickado)
              self.explorador.setRootIndex(indice)
              self.pathDirectorios.append(path_clickado)

    """
    
    explorador get Path

    @param  index   ::   Indice recuperado (QModelIndex) del explorador

    Añadimos al portapapeles el path absoluto recuperado del archivo o directorio a través del indice proporcionado por el explorador

    """

    def explorador_getPath(self, index):
          
         self.clipboard.setText(self.modeloArchivos.filePath(index))

    """
    
    explorador get Path Relativo

    @param  index   ::   Indice recuperado (QModelIndex) del explorador

    Añadimos al portapapeles el path relativo recuperado del archivo o directorio a través del indice proporcionado por el explorador

    """

    def explorador_getPathRel(self, index):
         self.clipboard.setText(self.modeloArchivos.filePath(index).rpartition('/')[2])

    """
    
    Explorador indice Back

    Acción que se ejecuta al pulsar el botón "Back" para volver a la carpeta padre del directorio actual en el que nos encontramos
    -     si es el directorio raíz no se sube más
    -     pop de la lista de directorios y carpeta padre como nueva raíz del explorador
    
    """

    def explorador_indiceBack(self):
         
         if len(self.pathDirectorios) > 1:
               self.pathDirectorios.pop()
               indice = self.modeloArchivos.setRootPath(self.pathDirectorios[-1])
               self.explorador.setRootIndex(indice)

    """
    
    Explorador indice Raiz

    Acción que se ejecuta al pulsar el botón "Raíz" para volver a la carpeta raíz del directorio del explorador
    
    """

    def explorador_indiceRaiz(self):
         
         self.modeloArchivos.setRootPath(self.pathRaiz)
         self.explorador.setRootIndex(self.indexRaiz)

    """

     Ventana Confirmación

     @param index :      Indice programa

     Ventana que se abre al cerrar un programa con modificaciones sin guardar
     -    Muestra las opciones y un mensaje de confirmación

    """

    def mostrar_dialogo(self, index:int):
         dialogWindow = QMessageBox(self)
             
         dialogWindow.setStyleSheet("""
                                   QMessageBox {
                                             background-color: #C0C0C0;
                                             color: #1a1a1a;
                                             border: 1px solid #555;
                                   }
                                   QMessageBox QLabel {
                                             font-size: 14px;
                                   }
                                   """)

         
         dialogWindow.setWindowTitle('Confirmacion')
         dialogWindow.setIcon(QMessageBox.Question)
         dialogWindow.setText('El archivo ha sido modificado.')
         dialogWindow.setInformativeText('¿Guardar cambios en el archivo\n"'+self.ui.tabWidget.tabText(index)+'"?')
         dialogWindow.setStandardButtons(QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
         botonGuardar = dialogWindow.button(QMessageBox.Save)
         botonGuardar.setText('Guardar')
         botonNoGuardar = dialogWindow.button(QMessageBox.Discard)
         botonNoGuardar.setText('No guardar')
         botonCancelar = dialogWindow.button(QMessageBox.Cancel)
         botonCancelar.setText('Cancelar')

         dialogWindow.buttonClicked.connect(functools.partial(self.opciones_dialogo, index))

         dialogWindow.exec_()

    """
     
     Opciones ventana confirmación

     @param index :           Indice programa
     @param dialog_button :   Botón que se ha pulsado en el dialogo de confirmación

     Comprueba que opción se ha pulsado y:
     -    Guardar :           Guarda el programa y llama a borrar_programa() (pop de programas[] y elimina la pestaña de tabWidget)
     -    No guardar :        Solo llama a borrar_programa()
     -    Cancelar   :        Cancela y no hace nada
     
    """

    def opciones_dialogo(self, index, dialog_button):
         match dialog_button.text():
              case 'Guardar':
                   self.guardar_programa()
                   self.borrar_programa(index)
              case 'No guardar':
                   self.borrar_programa(index)
              case 'Cancelar' :
                   pass

    """
     
     Borrar programa

     @param index :      indice del programa actual

     Pop de programas[] y elimina la pestaña de tabWidget

    """

    def borrar_programa(self, index:int):
         self.ui.tabWidget.removeTab(index)
         self.programas.pop(index).area_codigo.textChanged.disconnect()

    """
     
    Acción     Cerrar

     @param index :      indice del programa actual

     Cierra la pestaña actual y borra el programa de programas[]
     -    Si el programa es un modificado no guardado, muestra el dialogo de confirmación por si se quiere guardar
     -    Si no, llama a borrar_programa()
     -    Si tabWidget no tiene pestañas después de cerrar la última, se desactivan los enables

    """

    def cerrar_programa(self, index:int):
         if self.ui.tabWidget.tabText(index).endswith('*') or self.programas[index].ruta_archivo == '' and self.programas[index].area_codigo.toPlainText() != '':
              self.mostrar_dialogo(index)
         else:
              self.borrar_programa(index)
         if self.ui.tabWidget.currentIndex() == -1:
              self.acciones_setEnabled(False)
              self.ui.actionCortar.setEnabled(False)
              self.ui.actionCopiar.setEnabled(False)
              self.ui.actionDeshacer.setEnabled(False)
              self.ui.actionRehacer.setEnabled(False)

    """
     
     Acción    Cerrar todo

     Cierra todos los programas/pestañas
     -    Itera por la estructura programas[] desde el final hasta el principio
     -    Pone el foco en el programa (último hasta el primero) y llama a cerrar_programa para ese programa
     -    Como no quedan pestañas, se desactivan los enables

    """

    def cerrarTodos_programas(self):
         for programa in range(len(self.programas)-1, -1, -1):
              self.ui.tabWidget.setCurrentWidget(self.programas[programa].tab)
              self.cerrar_programa(self.programas.index(self.programas[programa]))
         self.acciones_setEnabled(False)
         self.ui.actionCortar.setEnabled(False)
         self.ui.actionCopiar.setEnabled(False)
         self.ui.actionDeshacer.setEnabled(False)
         self.ui.actionRehacer.setEnabled(False)

    """
     
     Acción    Deshacer

     Si está habilitado, se ejecuta la nativa 'undo()' de QTextEdit

    """

    def deshacer(self):
         if self.ui.actionDeshacer.isEnabled():
               programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
               programa_actual.area_codigo.undo()

    """
     
     Acción    Rehacer

     Si está habilitado, se ejecuta la nativa 'redo()' de QTextEdit

    """

    def rehacer(self):
         if self.ui.actionRehacer.isEnabled():
               programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
               programa_actual.area_codigo.redo()

    """
     
     Acción    Cortar

     Se ejecuta la nativa 'cut()' de QTextEdit

    """

    def cortar(self):
         programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
         programa_actual.area_codigo.cut()

    """
     
     Acción    Copiar

     Se ejecuta la nativa 'copy()' de QTextEdit

    """

    def copiar(self):
         programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
         programa_actual.area_codigo.copy()

    """
     
    Acción     Pegar

     Se ejecuta la nativa 'paste()' de QTextEdit

    """

    def pegar(self):
         programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
         programa_actual.area_codigo.paste()

    """
     
     Acción    Seleccionar todo

     Se ejecuta la nativa 'selectAll()' de QTextEdit

    """

    def seleccionar_todo(self) :
         programa_actual = self.programas[self.ui.tabWidget.currentIndex()]
         programa_actual.area_codigo.selectAll()

    """
     
     Ventana Confirmación (Salir de la Aplicación)

     @param event :      Evento de cierre

     Ventana que se abre cuando se quiere salir de la aplicación y existen cambios en al menos un documento sin guardar
     -    Muestra las opciones y un mensaje de confirmacion

    """

    def mostrar_dialogo_closeEvent(self, event:qtc.QEvent):
         dialogWindow = QMessageBox(self)

         dialogWindow.setStyleSheet("""
                                   QMessageBox {
                                             background-color: #C0C0C0;
                                             color: #1a1a1a;
                                             border: 1px solid #555;
                                   }
                                   QMessageBox QLabel {
                                             font-size: 14px;
                                   }
                                   """)
         
         dialogWindow.setWindowTitle('CONFIRMACION')
         dialogWindow.setIcon(QMessageBox.Question)
         dialogWindow.setText('¿Está seguro de que desea salir de la aplicacion?')
         dialogWindow.setInformativeText('Existen cambios en documento/s\n¿Guardar cambios antes de salir?')
         dialogWindow.setStandardButtons(QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
         botonGuardar = dialogWindow.button(QMessageBox.Save)
         botonGuardar.setText('Guardar')
         botonNoGuardar = dialogWindow.button(QMessageBox.Discard)
         botonNoGuardar.setText('No Guardar')
         botonCancelar = dialogWindow.button(QMessageBox.Cancel)
         botonCancelar.setText('Cancelar')

         dialogWindow.buttonClicked.connect(functools.partial(self.opciones_dialogo_closeEvent, event))

         dialogWindow.exec_()

    """
     
     Opciones  Ventana Confirmación (Salir de la Aplicación)

     @param event :           Evento de cierre
     @param dialog_button :   Botón pulsado en el diágolo de confirmación

     Comprueba que opción se ha pulsado y:
     -    Guardar :           Llama a guardarTodos_programas y acepta el evento de cierre
     -    No guardar :        Solo acepta el evento de cierre sin guardar
     -    Cancelar   :        Cancela e ignora el evento de cierre

    """

    def opciones_dialogo_closeEvent(self, event:qtc.QEvent, dialog_button):
         match dialog_button.text():
              case 'Guardar':
                   self.guardarTodos_programas()
                   return event.accept()
              case 'No guardar':
                   return event.accept()
              case 'Cancelar' :
                   return event.ignore()

    """
     
     Evento    Cierre

     -    Si existen programas modificados muestra el diálogo de confirmación del evento de cierre
     -    Si no, cierra la aplicación directamente

    """

    def closeEvent(self, event:qtc.QEvent):
         self.cerrarTodas_consolas()
         pedir_confirmacion:bool = False
         for programa in self.programas:
              if self.ui.tabWidget.tabText(self.programas.index(programa)).endswith('*') or programa.ruta_archivo == '' and programa.area_codigo.toPlainText() != '':
                    pedir_confirmacion = True
         if pedir_confirmacion:
              self.mostrar_dialogo_closeEvent(event)

"""

***********************************************************                  MAIN                      ******************************************************************

Crea una aplicación, muestra la ventana principal del IDE y se ejecuta

"""

if __name__ == '__main__':
      app = qtw.QApplication([])

      ventanaPrincipal = Controlador()
      ventanaPrincipal.show()

      sys.exit(app.exec_())
