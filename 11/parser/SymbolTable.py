from collections import namedtuple



class SymbolTable:

    """ 
        Maintains a symbol table for variable declarations 
        for the compipler
    """

    #static variables are shared in a global memory space
    #maintain a number to keep track of all static variables
    #in the program to prevent allocation collisions
    static_count = 0  

    # kind consants
    STATIC = "STATIC"
    FIELD = "FIELD"
    ARG = "ARG"
    VAR = "VAR"



    #container for variable information
    Info = namedtuple('Info',['type','kind','index'])

    def __init__(self):
        self._class_table = {}

        self._var_counts = {self.FIELD: 0,self.ARG: 0,self.VAR:0}

    def startSubroutine(self):
        "Creates a new scope when a function is being compiled."
        self._func_table = {}
        self._var_counts[self.ARG] = 0
        self._var_counts[self.VAR] = 0

    def define(self,name, type, kind):
        """
            Adds a new variable to the symbol table.
            name: String - the variable's name
            type: String - the variable's datatype
            kind: const - Argument, local var, instance member, class member 

        """
        if kind == self.STATIC:
            self._class_table[name] = self.Info(type,kind,self.static_count)
            self.static_count +=1
        elif kind == self.FIELD:
            self._class_table = self.Info(type,kind,self._var_counts[self.FIELD])
            self._var_counts[self.FIELD] +=1
        else: #assume it's a parameter or local variable
            self._func_table[name] = self.Info(type,kind,self._var_counts[kind])
            self._var_counts[kind] += 1

    def varCount(self,kind):
        "Returns the number of the variables of the given type in the current scope"
        if kind == self.STATIC:
            return self.static_count 
        else:
            return self._var_counts[kind]

    def varInfo(self,name):
        """
            Returns a named tuple enumerating the type,
            kind, and index of the variable. Returns none of the 
            variable does not exist in the table
            name: String - the name ofthe variable
        """
        if name in self._func_table:
            return self._func_table[name]
        elif name in self._class_table:
            return self._class_table[name]
        else:
            return None

    #the following methods are added for compatibility with the suggested interface
    def kindOf(self,name):
        """ Returns the scope of the named variable."""
        info = self.varInfo(name)

        if info:
            return info.kind

        return None

    def typeOf(self,name):
        """Returns the datatype of the variable"""
        info = self.varInfo(name)
        if info:
            return info.type
        return None

    def indexOf(self,name):
        """Returns the index of the variable"""

        info = self.varInfo(name)

        if info:
            return info.index
        return None



    




    

    
