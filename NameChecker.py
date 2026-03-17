import ast
import builtins

"""

Clase NameChecker   ::    clase visitadora de nodos del arbol sintactico abstracto

***********************************************************                  ATRIBUTOS                      ******************************************************************


variables           ::  lista de nombres de variables, funciones, etc. que vamos declarando
nombres_importados  ::  lista de nombres de importaciones (import)
clases_definidas    ::  lista de nombres de clases declaradas
errors              ::  lista de errores, un error aparece cuando se usa un nombre pero éste no ha sido declarado previamente

"""

class NameChecker(ast.NodeVisitor):
    
    variables : list
    nombres_importados : list
    clases_definidas   : list
    errors    : list

    """
    
    Constructor     ::     Namechecker

    Inicializa los nombres de variables con los predefinidos y añade 'self' pues no  estaba como predefinido
    Inicializa a vacio los nombres importados, las clases definidas y los errores
    
    """

    def __init__(self):
        self.variables = dir(builtins)
        self.variables.append('self')
        self.nombres_importados = []
        self.clases_definidas = []
        self.errors    = []
    
    """
    
    visit Assign

    Maneja las declaraciones de variables normales
    
    """

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.generic_visit(node)

    """
    
    visit AnnAssign

    Maneja declaraciones de variables con asignaciones
    
    """

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.append(node.target.id)
        self.generic_visit(node)

    """
    
    visit For

    Maneja variables declaradas en sentencias 'for'
    
    """

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.append(node.target.id)
        self.generic_visit(node)

    """
    
    visit ClassDef

    Maneja declaraciones de nombre de clase definida
    
    """

    def visit_ClassDef(self, node):
        self.clases_definidas.append(node.name)
        self.variables.append(node.name)
        self.generic_visit(node)

    """
    
    visit Call

    Verifica si una llamada a constructor es de una clase definida
    
    """

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.clases_definidas:
            self.variables.append(node.func.id)
        self.generic_visit(node)

    """
    
    visit FunctionDef

    Maneja nombres de variables locales, parametros y argumentos en definiciones y llamadas de funciones (metodos)

    """

    def visit_FunctionDef(self, node):
        self.variables.append(node.name)

        for arg in node.args.args:
            self.variables.append(arg.arg)

        if node.args.vararg:
            self.variables.append(node.args.vararg.arg)
        if node.args.kwarg:
            self.variables.append(node.args.kwarg.arg)

        self.generic_visit(node)

    """
    
    visit With

    Maneja declaraciones en sentencias 'with'
    
    """

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.optional_vars, ast.Name):
                self.variables.append(item.optional_vars.id)
        self.generic_visit(node)

    """
    
    visit Import

    Maneja nombres de importaciones tipo:   'import ast'
    
    """

    def visit_Import(self, node):
        for alias in node.names:
            self.nombres_importados.append(alias.asname if alias.asname else alias.name.split('.')[0])
        self.generic_visit(node)

    """
    
    visit ImportFrom

    Maneja nombres de importaciones tipo:   'from os import path'
    
    """

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.nombres_importados.append(alias.asname if alias.asname else alias.name)
        self.generic_visit(node)

    """
    
    visit Name

    Maneja el resto de nombres, si se está utilizando y si no está en las listas de declaraciones variables o importaciones:
    - Se añade a la lista de errores que luego se usará para subrayar de amarillo los nombres no declarados
    
    """

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if self.variables.count(node.id) < 1 and self.nombres_importados.count(node.id) <1:
                self.errors.append((node.lineno, node.col_offset, node.id))
        self.generic_visit(node)
