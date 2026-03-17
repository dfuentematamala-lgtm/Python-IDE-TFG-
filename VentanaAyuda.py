from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget


"""

Clase VentanaAyuda    ::     contiene la ventana de Ayuda dell boton de la barra de menus.


"""

class VentanaAyuda(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayuda del IDE")
        self.resize(800, 600)

        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.texto_ayuda = QTextEdit(self)
        self.texto_ayuda.setReadOnly(True)

        contenido = """
        <h1>Manual de Usuario</h1>
        <ol>
        <li><strong>Iniciar el programa:</strong><br>
        Hacer doble clic sobre el icono del programa.</li>
        
        <li><strong>Configuración:</strong><br>
        Pulsar en <em>[Configuración]</em>, elegir tema claro u oscuro, y cambiar el directorio raíz según se desee.</li>
        
        <li><strong>Crear un programa nuevo:</strong><br>
        Menú <em>[Archivo > Nuevo]</em> (Atajo: Ctrl+N).</li>
        
        <li><strong>Abrir un programa existente:</strong><br>
        Menú <em>[Archivo > Abrir]</em> (Atajo: Ctrl+F).</li>
        
        <li><strong>Guardar un programa:</strong><br>
        Menú <em>[Archivo > Guardar]</em> (Ctrl+G) o <em>[Archivo > Guardar como]</em> (Ctrl+S) o [Archivo > Guardar todo] con Ctrl+Shift+S.</li>
        
        <li><strong>Navegar por el explorador:</strong><br>
        Usar los botones <em>Raíz</em> y <em>Back</em> para volver al directorio superior o al raíz, doble clic en carpetas o ficheros para navegar o abrir. Menú contextual para operaciones adicionales.</li>
        
        <li><strong>Navegar por las ventanas de resultados:</strong><br>
        Seleccionar la pestaña para cambiar entre pestañas de ejecución, cerrar con la equis roja.</li>
        
        <li><strong>Navegar por las ventanas de edición:</strong><br>
        Seleccionar la pestaña para cambiar entre pestañas de programas abiertos. Cerrar programas con [Archivo > Cerrar] Ctrl+W o cerrar todo con [Archivo > Cerrar todo] Ctrl+Shift+W.</li>
        
        <li><strong>Editar un archivo Python:</strong><br>
        Escribir código en el editor. Errores de sintaxis se subrayan en rojo, nombres no declarados en amarillo.</li>
        
        <li><strong>Ejecutar un programa:</strong><br>
        Pulsar el botón <em>Ejecutar</em>. La salida o errores se mostrarán en una ventana de resultados.</li>
        
        <li><strong>Depurar un programa:</strong><br>
        Pulsar el botón <em>Debug</em>. Usar los botones <em>Continuar, Next, Step</em> y <em>Stop</em> para controlar la depuración.</li>
        </ol>
        """
        self.texto_ayuda.setHtml(contenido)
        layout.addWidget(self.texto_ayuda)

        self.setCentralWidget(widget)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    ayuda = VentanaAyuda()
    ayuda.show()
    sys.exit(app.exec_())
