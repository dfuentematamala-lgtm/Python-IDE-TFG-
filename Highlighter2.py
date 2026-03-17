import builtins
import keyword
from PyQt5.QtCore import (QRegularExpression, Qt)
from PyQt5.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont)

"""

Clase Highlighter    ::      Está reimplementando a QSyntaxHighlighter

***********************************************************                  ATRIBUTOS                      ******************************************************************


builtins    ::  Funciones y constantes predefinidas como print, len o True/False, etc.
keyWords    ::  Palabras reservadas del lenguaje como import, las sentencias, class y def

"""

class Highlighter(QSyntaxHighlighter):

    builtins : list = dir(builtins)
    keyWords : list = keyword.kwlist

    """
    
    Constructor ::  Highlighter

    Definimos un formato para las keyWords, builtins, braces, literales como class, self y def, los nombres en la declaracion de funciones, strings, numeros y comentarios,
    -   Los comentarios multilinea de tres comillas se colorean igual que los strings

    Añadimos a una estructura de datos _mappings las expresiones regulares que queremos capturar (literales, keywords, comentarios multilinea, etc.), el indice desde donde empieza y el
    -   formato que queremos aplicar como una tupla en cada posicion
    Después reconstruimos _mappings para que las expresiones regulares sean de tipo QRegularExpresion y nos permitan usar los métodos necesarios para resaltar en highlightBlock

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.formato_kw       = QTextCharFormat()
        self.formato_bi       = QTextCharFormat()
        self.formato_defClass = QTextCharFormat()
        self.formato_defFunc  = QTextCharFormat()
        self.formato_string   = QTextCharFormat()
        self.formato_resto  = QTextCharFormat()
        self.formato_self     = QTextCharFormat()

        self.formato_kw.setFontWeight(QFont.Bold)
        self.formato_kw.setForeground(QColor("#d533ff"))
        self.formato_bi.setFontWeight(QFont.Bold)
        self.formato_bi.setForeground(QColor("#2ecc71").darker(155))
        self.formato_defClass.setFontWeight(QFont.Bold)
        self.formato_defClass.setForeground(Qt.blue)
        self.formato_defFunc.setFontWeight(QFont.Bold)
        self.formato_defFunc.setFontItalic(True)
        self.formato_defFunc.setForeground(QColor("#f4ed14"))
        self.formato_string.setForeground(QColor("#f27800").darker(115))
        self.formato_resto.setForeground(Qt.darkYellow)
        self.formato_self.setForeground(QColor("#29b6f6").darker(150))
        self.comment_triSingle = (QRegularExpression("'''"), 1, self.formato_string)
        self.comment_triDouble = (QRegularExpression('"""'), 2, self.formato_string)

        self._mappings = [(r'->(.*)', 0, self.formato_resto)]
        
        for pattern in self.keyWords:
            if pattern != 'class' and pattern != 'def':
                patron = rf'\b{pattern}\b'
                self._mappings.append((patron, 0, self.formato_kw))

        for pattern in self.builtins:
            patron = rf'\b{pattern}\b'
            self._mappings.append((patron, 0, self.formato_bi))

        self._mappings += [
            (r'\bself\b', 0, self.formato_self),
            (r'\bclass\b', 0, self.formato_defClass),
            (r'\bdef\b', 0, self.formato_defClass),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.formato_string),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.formato_string),
            (r'(?<=\bdef\s)\w+', 0, self.formato_defFunc),
            ]

        self._mappings = [(QRegularExpression(pat), index, fmt)
            for (pat, index, fmt) in self._mappings]

    """
    
    highlight    Block

    @param  text    ::  El código (texto) del AreaCodigo

    Resalta el texto  (código) del AreaCodigo de un programa, es llamado cada vez que se produce un match (expresiones regulares) y se necesita resaltar texto
    -   Busca coincidencias con los patrones guardados en _mappings y le aplica el formato correspondiente.
    -   Si el patron coincide con el de un string se omiten las comillas triples dentro de la cadena
    -   comillasTriples_pos almacenará las posiciones de las comillas triples en el texto,
    el indice que no se encuentre en esta lista se le aplicara el formato correspondiente, el formato de comillas triples se aplica en las llamadas a
    match_multiline

    """

    def highlightBlock(self, text):
        self.comillasTriples_pos = []

        for expresion, nth, formato in self._mappings:
            match_iterator = expresion.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                index = match.capturedStart(nth)
                
                if expresion.pattern() in [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]:
                    inner_match_tri_single = self.comment_triSingle[0].match(text, index + 1)
                    inner_match_tri_double = self.comment_triDouble[0].match(text, index + 1)
                    
                    if inner_match_tri_single.hasMatch():
                        inner_index = inner_match_tri_single.capturedStart()
                    elif inner_match_tri_double.hasMatch():
                        inner_index = inner_match_tri_double.capturedStart()
                    else:
                        inner_index = -1

                    if inner_index != -1:
                        comillasTriples_indices = range(inner_index, inner_index + 3)
                        self.comillasTriples_pos.extend(comillasTriples_indices)

                if index in self.comillasTriples_pos:
                    continue

                length = match.capturedLength(nth)
                self.setFormat(index, length, formato)

        self.setCurrentBlockState(0)                   #   < ------   Indica que no estamos dentro de un comentario multilinea

        in_multiline = self.match_multiline(text, *self.comment_triSingle)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.comment_triDouble)

    """
    
    match   multiline

    @param  text            ::  El codigo (texto) del AreaCodigo
    @param  expReg          ::  Expresion regular de comillas triples
    @param  inicio_bloque   ::  Entero unico que representa el cambio de estado del bloque
    @param  formato         ::  Formato de comentario
    
    Maneja el resaltado de comentarios multilinea, triples comillas simples/dobles ('/")
    -   Busca un delimitador de apertura en la linea actual, si lo encuentra busca el de cierre y aplica el formato al texto entre delimitadores
    -   Gestiona el estado del bloque para saber si seguimos dentro de un comentario multilinea

    @return bool    ::  True si seguimos en comentario multilinea y False en caso contrario

    """

    def match_multiline(self, text, expReg, inicio_bloque, formato):

        # Si el bloque anterior estaba dentro de un comentario multilinea, empieza desde 0
        if self.previousBlockState() == inicio_bloque:
            inicio = 0
            add = 0
        # Si no, buscar delimitador de apertura en la linea actual
        else:
            expReg_match = expReg.match(text)
            inicio = expReg_match.capturedStart()
            add = expReg_match.capturedLength()

            # Omite comillas triples dentro de cadenas de texto
            if inicio in self.comillasTriples_pos:
                return False

        # Mientras haya delimitador de apertura en esta linea:
        while inicio >= 0:
            
            # Buscar delimitador de cierre
            expReg_match = expReg.match(text, inicio + add)
            end = expReg_match.capturedStart()

            # Delimitador de cierre en la misma linea ?
            if end >= add:
                length = end - inicio + add + expReg_match.capturedLength()
                self.setCurrentBlockState(0)

            # No; Seguimos en multilinea
            else:
                self.setCurrentBlockState(inicio_bloque)
                length = len(text) - inicio + add

            # Aplica formato de comentario multilinea
            self.setFormat(inicio, length, formato)

            # Busca la siguiente coincidencia
            expReg_match = expReg.match(text, inicio + length)
            inicio = expReg_match.capturedStart()

        return self.currentBlockState() == inicio_bloque

