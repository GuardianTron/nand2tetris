from JackTokenizer import JackTokenizer,JackTokenizerRewind
from SymbolTable import SymbolTable
from xml.etree.ElementTree import Element,SubElement
from VMWriter import VMWriter,InstructionError
class CompilationEngine:

    unary_op = {'-','~'} #mathematical and logical negation
    sub_call_op = {'.','('} #used to determine
    key_const = {'true','false','null','this'}
    ops = {'+','-','*','/','&','|','<','>','='}

    #constants
    LOOP = "LOOP"
    LOOP_END = "LOOP_END"
    IF_END = "IF_END"
    ELSE = "ELSE"

    binary_op_commands = {
        "-":"sub",
        "+":"add",
        "<":"lt",
        ">":"gt",
        "&":"and",
        "|":"or"
    }

    binary_op_functions = {
        "*":"Math.multiply",
        "/":"Math.divide"
    }

    unary_op_commands = {
        "-":"neg",
        "~":"not"
    }


    def xml_decorator(node_name):
        """ Adds xml generation code to called compilation objects.
            Manages the node tree for the function, creating a new
            subnode provided by the name and placing it as the current subnode.
            Once the decorated function is done executing, the original parent is
            restored to status of current node.
            """
        def decorator(func):
            def wrapper(self):
                old_parent = self.__current_parent
                self.__current_parent = SubElement(old_parent,node_name)
                return func(self)
                self.__current_parent = old_parent
            return wrapper
        return decorator

    def __init__(self,file):
        self.__file = file
        self.__tokenizer = JackTokenizerRewind(file)
        self.__symbol_table = SymbolTable()
        self.__vm = VMWriter(self.__file)
        #holds XML root
        self.__root = None
        #holds the current parent node
        self.__current_parent = None
        
        #holds the last xml node processed
        self.__last_node = None


        #the name of the current class
        self.__class_name = ""

        #count for generating unique labels
        self.__label_counts = {self.IF_END:0,self.ELSE:0,self.LOOP:0,self.LOOP_END:0}
        #bootstrap the compilation process
        if self.__tokenizer.advance():
            self.compileClass()

    def getXML(self):
        return self.__root

    def compileClass(self):
        self.__root = Element('class')
        self.__current_parent = self.__root
        self.__consume(JackTokenizer.KEYWORD,'class')
        self.__class_name = self.__tokenizer.token()
        self.__consume(JackTokenizer.IDENTIFIER)
        self.__consume(JackTokenizer.SYMBOL,'{')

        #process class var declarations
        while self.__tokenizer.keyword() in ('field','static'):
            self.compileClassVarDec()

        #process subroutine declarations
        while  self.__tokenizer.keyword() in ('constructor','method','function'):
            self.compileSubroutineDec()


        self.__consume(JackTokenizer.SYMBOL,'}')   

        self.__vm.close() 

    @xml_decorator("classVarDec")
    def compileClassVarDec(self):

        kind = self.__consume(JackTokenizer.KEYWORD,self.__tokenizer.keyword()) #static or field


        type = self.__consumeTypeDec()

        #consume the variable list
        #make sure their is at least one identifier
        name = self.__consume(JackTokenizer.IDENTIFIER)
        self.__symbol_table.define(name,type,kind)
        info = self.__symbol_table.varInfo(name)
        self.__last_node.set("type", info.type)
        self.__last_node.set("kind", info.kind)
        self.__last_node.set("index", str(info.index))
        while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            name = self.__consume(JackTokenizer.IDENTIFIER)
            self.__symbol_table.define(name,type,kind)
            info = self.__symbol_table.varInfo(name)
            self.__last_node.set("type", info.type)
            self.__last_node.set("kind", info.kind)
            self.__last_node.set("index", str(info.index))

        #consume ending ';'
        self.__consume(JackTokenizer.SYMBOL,';')


    @xml_decorator("subroutineDec")
    def compileSubroutineDec(self):
        self.__symbol_table.startSubroutine()

        #handle special cases for setting up constructors and methods
        subroutine_type = self.__tokenizer.token()
        if subroutine_type == "method":
            #this must be the first argument to the method,so add to symbol table
            self.__symbol_table.define("this",self.__class_name,SymbolTable.ARG)
        elif subroutine_type == "constructor":
            #allocate memory and set up this pointer on stack
            self.__vm.writeCall("Memory.alloc",self.__symbol_table.varCount(SymbolTable.FIELD))
            self.__vm.writePop("pointer",0) 


        self.__consume(JackTokenizer.KEYWORD,{'constructor','method','function'})

        #handle return type
        if self.__tokenizer.type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,{'void','int','boolean','char'})
        else:
            self.__consume(JackTokenizer.IDENTIFIER)

        #handle function name
        self.__consume(JackTokenizer.IDENTIFIER)

        #handle expressions
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileParameterList()
        self.__consume(JackTokenizer.SYMBOL,')') 

        #move onto subroutineBody
        self.compileSubroutineBody()       

    @xml_decorator("parameterList")
    def compileParameterList(self):

        #consume parameter list if any
        if self.__compileParameter() :
            #consume additional parameters
            while self.__tokenizer.token() == ",":
                self.__consume(JackTokenizer.SYMBOL,',')
                self.__compileParameter()

    def __compileParameter(self):
        #if is a parameter, consume the type declaration and the variable name
        param_keywords = {'int','boolean','char'}
        if self.__tokenizer.type == JackTokenizer.IDENTIFIER:
            type = self.__consume(JackTokenizer.IDENTIFIER)
            
        elif self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() in param_keywords:
            type = self.__consume(JackTokenizer.KEYWORD,param_keywords)
        else:  
            return False
        name = self.__consume(JackTokenizer.IDENTIFIER)

        self.__symbol_table.define(name,type,SymbolTable.ARG)
        info = self.__symbol_table.varInfo(name)
        self.__last_node.set('type',info.type)
        self.__last_node.set('kind',info.kind)
        self.__last_node.set('index',str(info.index))
        return True

    @xml_decorator("subroutineBody")
    def compileSubroutineBody(self):

        self.__consume(JackTokenizer.SYMBOL,'{')

        #handle optional variable declarations.
        while self.__tokenizer.token() == 'var':
            self.compileVarDec()  

        self.compileStatements()
             

        self.__consume(JackTokenizer.SYMBOL,'}')

    @xml_decorator("varDec")
    def compileVarDec(self):

        self.__consume(JackTokenizer.KEYWORD,'var')
        type = self.__consumeTypeDec()
        name = self.__consume(JackTokenizer.IDENTIFIER)

        self.__symbol_table.define(name,type,SymbolTable.VAR)
        info = self.__symbol_table.varInfo(name)
        self.__last_node.set('type',info.type)
        self.__last_node.set('kind',info.kind)
        self.__last_node.set('index',str(info.index))
        #handle multiple variables
        while self.__tokenizer.token() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            name = self.__consume(JackTokenizer.IDENTIFIER)
            self.__symbol_table.define(name,type,SymbolTable.VAR)
            info = self.__symbol_table.varInfo(name)
            self.__last_node.set('type',info.type)
            self.__last_node.set('kind',info.kind)
            self.__last_node.set('index',str(info.index))

        #finish declaration
        self.__consume(JackTokenizer.SYMBOL,';')

    @xml_decorator("statements")
    def compileStatements(self):

        while self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() in ('do','let','if','return','while'):
            token = self.__tokenizer.keyword()
            if token == 'do':
                self.compileDo()
            elif token == 'let':
                self.compileLet()
            elif token == 'if':
                self.compileIf()
            elif token == 'return':
                self.compileReturn()
            elif token == 'while':
                self.compileWhile()

    @xml_decorator("doStatement")
    def compileDo(self):
        self.__consume(JackTokenizer.KEYWORD,"do")
        self.compileSubroutineCall()
        #remove returned value from the stack
        self.__vm.writePop("temp",0)
        self.__consume(JackTokenizer.SYMBOL,";")
    
    @xml_decorator("letStatement")
    def compileLet(self):
        """compiles let statements."""

        #NOTE: To handle storage to arrays
        #First pop the top value returned by the 
        #expression into temp 0, store array pointer
        #in pointer 1, then push temp 0 back onto 
        #the stack and then push the value into 
        #that 0

        #get variable name
        self.__consume(JackTokenizer.KEYWORD,'let')
        name = self.__tokenizer.identifier()
        self.__consume(JackTokenizer.IDENTIFIER)

        info = self.__symbol_table.varInfo(name)
        

        #handle storing an element to a specific array index
        is_array_access = False
        if info.type == "Array" and self.__tokenizer.token() == "[":
            #place base array pointer onto the stack
            self.__vm.writePush(info.kind,info.index)
            #calculate internal expression for index
            self.__consume(JackTokenizer.SYMBOL,"[")
            self.compileExpression()
            self.__consume(JackTokenizer.SYMBOL,']')
            #add to base array pointer to get element's address
            self.__vm.writeArithmetic("add")

            is_array_access = True


        self.__consume(JackTokenizer.SYMBOL,"=")
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,";")

        #if array, store returned expression into the specified element.
        #otherwise, just store into the variable based on it's location
        #in memory

        if is_array_access:
            #save expression result off of stack 
            #so that element pointer can be accessed
            self.__vm.writePop("temp",0)

            #point to array element and save result
            self.__vm.writePop("pointer",1)
            self.__vm.writePush("temp",0)
            self.__vm.writePop("that",0)
        else:
            #simply save to location in memory specified by symbol table.
            self.__vm.writePop(info.kind,info.index)

    @xml_decorator("ifStatement")
    def compileIf(self):

        self.__consume(JackTokenizer.KEYWORD,'if')
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileExpression()

        # Negate the expression.  If the original expression 
        # is true, then negation will be false, resulting
        # in excution skipping to next line. This will 
        # result in the if statements executing, followed by a jump using 
        # goto to jump over the else statements.
        # If negation is true, then the if-goto activates jumping 
        # past the if statments to the else statements.
        self.__vm.writeArithmetic('not')
        label = self.__generateLabel(self.ELSE)
        self.__vm.writeIf(label)
        self.__consume(JackTokenizer.SYMBOL,')')
        self.__consume(JackTokenizer.SYMBOL,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,"}")

        if self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() == 'else':
            #write else label if here there is an else statement
            #use IF_END for end of full block
            #otherwise, else will be used as end of if block
            self.__vm.writeLabel(label)
            label = self.__generateLabel(self.IF_END)
            self.__consume(JackTokenizer.KEYWORD,'else')
            self.__consume(JackTokenizer.SYMBOL,'{')
            self.compileStatements()
            self.__consume(JackTokenizer.SYMBOL,'}')

        # write the final label for the block
        self.__vm.writeLabel(label)

    @xml_decorator("returnStatement")
    def compileReturn(self):
        self.__consume(JackTokenizer.KEYWORD,'return')
        #not an emptry return, so compile expression
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ';'):
            self.compileExpression()
        self.__vm.writeReturn()
        self.__consume(JackTokenizer.SYMBOL,';')

    @xml_decorator("whileStatement")
    def compileWhile(self):
        loop_label = self.__generateLabel(self.LOOP)
        loop_end_label = self.__generateLabel(self.LOOP_END)
        self.__vm.writeLabel(loop_label)
        
        self.__consume(JackTokenizer.KEYWORD,'while')
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,')')

        #if expression is false, jump to end of loop
        self.__vm.writeArithmetic("not")
        self.__vm.writeIf(loop_end_label)

        self.__consume(JackTokenizer.SYMBOL,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,'}')

        #go back to start of the loop
        self.__vm.writeGoto(loop_label)
        #end loop block
        self.__vm.writeLabel(loop_end_label)

    @xml_decorator("expressionList")
    def compileExpressionList(self):
        """Compiles a list of expressions."""
        num_args = 0
        #utilizes the fact that all expression lists are currently contained within parenthesis to test
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ')'):
            self.compileExpression()
            num_args = 1
            while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
                self.__consume(JackTokenizer.SYMBOL,',')
                self.compileExpression()
                num_args+=1
        return num_args
    
    @xml_decorator("expression")
    def compileExpression(self):
        self.compileTerm()
        while self.__tokenizer.token() in self.ops:
            op = self.__tokenizer.symbol()
            self.__consume(JackTokenizer.SYMBOL,self.ops)
            self.compileTerm()
            #handle op after term..remember call stack
            if op in self.binary_op_commands:
                self.__vm.writeArithmetic(self.binary_op_commands[op])
            elif op in self.binary_op_functions:
                self.__vm.writeCall(self.binary_op_functions[op],2)
                


    @xml_decorator("term")
    def compileTerm(self):
        """Compiles individual terms. Terms can be recursively defined"""
        t_type = self.__tokenizer.type
        if t_type == JackTokenizer.INT:
            self.__vm.writePush("constant",self.__tokenizer.integer())
            self.__consume(JackTokenizer.INT)
        elif t_type == JackTokenizer.STRING:
            string = self.__tokenizer.string()
            #initialize string object
            self.__vm.writePush("constant",len(string))
            self.__vm.writeCall("String.new",1)
            for char in string:
                self.__vm.writePush("constant",ord(char))
                self.__vm.writeCall("String.append",1)
                self.__vm.writePop("temp",0)

            self.__consume(JackTokenizer.STRING)
        elif t_type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() in self.key_const: #true,false,null,this
            #consume the keyword, but save in case it is part of a method call on 'this'
            token = self.__tokenizer.keyword()
            #obtain next token for testing if it is a method call on this
            self.__tokenizer.advance()
            next_token = self.__tokenizer.token()
            #restore keyword token for later consumption
            self.__tokenizer.rewind()
            
            if token == 'this':
                self.__vm.writePush('pointer',0)
                if next_token == '.': #method call
                    self.compileSubroutineCall()
                else: #subroutineCall consumes this after using it for determining context
                    self.__consume(JackTokenizer.KEYWORD,self.key_const)
            else: #single keyword
                if token == "true":
                    #true is -1 in the vm
                    self.__vm.writePush("constant",1)
                    self.__vm.writeArithmetic('neg')
                else:
                    self.__vm.writePush("constant",0)
                self.__consume(JackTokenizer.KEYWORD,self.key_const)

        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == '(':   #assume parenthesis by itself starts an expression
            self.__consume(JackTokenizer.SYMBOL,'(')
            self.compileExpression()
            self.__consume(JackTokenizer.SYMBOL,')')
        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() in self.unary_op: # example mathematical negation of an expression -- call term again
            op = self.__tokeni
        """Compiles a list of expressions."""ol()
            self.__consume(Jac
        """Compiles a list of expressions."""er.SYMBOL,self.unary_op)
            self.compileTerm()
        """Compiles a list of expressions."""
            self.__vm.writeArithmetic(self.unary_op_commands[op])

        elif t_type == JackTokenizer.IDENTIFIER: #can be a variable, array, or function call
            #####NOTE: Does not handle function calls on arrays!!!!!!#########
            #####NOTE: 2 Arrays are nontyped - no way for language to do this ########
            #handle pushing values/pointers onto the stack
            #NOTE: If name not found in symbol table, assume class reference for 
            #static method call
            name = self.__tokenizer.identifier()
            info = self.__symbol_table.varInfo(name)
            if info: #not in symbol table if identifier is a reference to the class
                self.__vm.writePush(info.kind,info.index)
            
            #determine if there is a method call or array access
            self.__tokenizer.advance() 

            t_type = self.__tokenizer.type
            token = self.__tokenizer.token()
            self.__tokenizer.rewind() #rewind back to identifier for processing methods to consume
            if t_type == JackTokenizer.SYMBOL: #handle array and function calls
                if token in self.sub_call_op: #handle method and function calls
                    self.compileSubroutineCall()
                elif token == "[":
                    if info.type != "Array":
                        raise CompilationError("{} is not type Array".format(name))
                    #handle array access hereYou can find in the Getting Started section all the in
                    self.__consume(JackTokenizer.IDENTIFIER)
                    self.__consume("[")
                    self.compileExpression()
                    self.__consume("]")
                    self.__vm.writeArithmetic('add')
                    self.__vm.writePop("pointer",0)
                    self.__vm.writePush("that",0)
            else:
                #just a variable, consume
                self.__consume(JackTokenizer.IDENTIFIER)
            
    def compileSubroutineCall(self):
        """
           Handles parsing of the subroutine call
        """
        is_method = True
        caller = ""
        t_type = self.__tokenizer.type
        if t_type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() == 'this': #handle this identifier
            self.__consume(JackTokenizer.KEYWORD,'this')
            caller = self.__class_name
        else: #assume an identifier
            #see if method is being invoked on a class or 
            #object instance.
            #only object instances will exist within the symbol table
            #assume Class method invocation otherwise
            caller = self.__tokenizer.identifier()
            info = self.__symbol_table.varInfo(caller)
               #set caller to be the class
            if info:
               caller = info.type
            else:
                is_method = False
                


            self.__consume(JackTokenizer.IDENTIFIER)


        if self.__tokenizer.token() == '.': #if method call, consume . and method name identifier
            self.__consume(JackTokenizer.SYMBOL,'.')
            function = self.__tokenizer.identifier()
            self.__consume(JackTokenizer.IDENTIFIER)
        #handle The code was developed against Pi 3 B, I have not tested on Pi 1. I think references to the name BCM2835 may be accidental, perhaps more accurate would be to call it BCM2837, although also possible that they sharethe actual function call portion -- Always runs
        self.__consume(JackTokenizer.SYMBOL,'(')
        args = self.compileExpressionList()
        self.__consume(JackTokenizer.SYMBOL,')')
        #if caller is a method, add the calling object as an argument
        if is_method:
            args +=1
        self.__vm.writeCall(caller+"."+function,args)
         

    def compileVariable(self):
        """Compile a variable and array declaration."""
        self.__consume(JackTokenizer.IDENTIFIER)
        t_type = self.__tokenizer.type
        if t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == '[': #arrays
            self.__consume(JackTokenizer.SYMBOL,'[')
            self.compileExpression()
            self.__consume(JackTokenizer.SYMBOL,']')




    


    #note: token is passed for checking that the token matches a specific
    #expected value.  The token recorded is taken from the tokenizer
    #thus, only pre-enumerated tokens such as symbols or keywords will use the 
    #token paramenter. 
    #token can either be a single token or an array of possible values
    def __consume(self,t_type,token=None):
        #test type
        if self.__tokenizer.type != t_type:
            raise CompilationError("%s  -- Expecting type: %s  Received type: %s"%(self.__file,t_type,self.__tokenizer.type))
        
        #if specific token(s) 
        if token:
            #if not a list or set, then wrap in set for comparison
            if not isinstance(token,(list,set)):
                token = {token}
            if self.__tokenizer.token() not in token:
                
                raise CompilationError("{} -- Expecting {} of type {}. Received {}: {}".format(self.__file,token,t_type, self.__tokenizer.type,self.__tokenizer.token()))


        #generate xml for token
        token_xml = SubElement(self.__current_parent,self.__tokenizer.type)
        token_string = str(self.__tokenizer.token())
        token_xml.text = " {} ".format(token_string)
        self.__last_node = token_xml

        self.__tokenizer.advance()
        return token_string

    #helper method for consuming type declarations
    def __consumeTypeDec(self):
        t_type = self.__tokenizer.type

        #varable type can be a keyword constant or class name
        if t_type == JackTokenizer.KEYWORD:
            return self.__consume(JackTokenizer.KEYWORD,{'int','char','boolean'})
        else:
            return self.__consume(JackTokenizer.IDENTIFIER)

    def __generateLabel(self,type):
        label = type+str(self.__label_counts[type])
        self.__label_counts[type] += 1
        return label
        





class CompilationError(Exception):
    pass    

class NotValidJackFileError(Exception):
    pass

import os
def get_jack_files(filename):
    """ Returns a generator that enumerate all jack files in a directory.
        Returns a generator with the jack file is the path is a jack file.
        Throws NoValidJackFile if no jack files found.
    """
    if os.path.isfile(filename):
        if comp_extension(filename,"jack"):
            yield filename
        else:
            raise NotValidJackFileError(filename)
    elif os.path.isdir(filename):
        #loop through files and return jack files
        constains_jack_file = False #flags if no jack files found
        dirs = os.listdir(filename)
        for file in dirs:
            file = os.path.join(filename,file)
            if os.path.isfile(file) and comp_extension(file,"jack"):
                constains_jack_file = True
                yield file

        if not constains_jack_file:
            raise NotValidJackFileError(filename)
    else:
        raise NotValidJackFileError(filename)

def comp_extension(filename,extension):
    return os.path.basename(filename).split(".")[-1] == extension

def create_xml_path(filename):
    directory = os.path.dirname(filename)
    file = os.path.basename(filename).split(".")[0]
    xml_file = file+"_output.xml"
    return os.path.join(directory,xml_file)

if __name__ == "__main__":
    from sys import argv
    #from xml.etree import ElementTree as ET
    try:
        for file in get_jack_files(argv[1]):
            compiler = CompilationEngine(file)
            #xml = compiler.getXML()
            #with open(create_xml_path(file),'w') as doc:
            #    doc.write(ET.tostring(xml,'unicode'))     

    except IOError as e:
        print(e)
    except NotValidJackFileError as e:
        print(e)