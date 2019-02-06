from JackTokenizer import JackTokenizer,JackTokenizerRewind
from xml.etree.ElementTree import Element,SubElement
class CompilationEngine:

    unary_op = {'-','~'} #mathematical and logical negation
    sub_call_op = {'.','('} #used to determine
    key_const = {'true','false','null','this'}
    ops = {'+','-','*','/','&','|','<','>'}


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
                func(self)
                self.__current_parent = old_parent
            return wrapper
        return decorator

    def __init__(self,file):
        self.__tokenizer = JackTokenizerRewind(file)
        #holds XML root
        self.__root = None
        #holds the current parent node
        self.__current_parent = None

        #bootstrap the compilation process
        if self.__tokenizer.advance():
            self.compileClass()

    def getXML(self):
        return self.__root

    def compileClass(self):
        self.__root = Element('class')
        self.__current_parent = self.__root
        self.__consume(JackTokenizer.KEYWORD,'class')
        self.__consume(JackTokenizer.IDENTIFIER)
        self.__consume(JackTokenizer.SYMBOL,'{')

        #process class var declarations
        while self.__tokenizer.keyword() in ('field','static'):
            self.compileClassVarDec()

        #process subroutine declarations
        while  self.__tokenizer.keyword() in ('constructor','method','function'):
            self.compileSubroutineDec()


        self.__consume(JackTokenizer.SYMBOL,'}')    

    @xml_decorator("classVarDec")
    def compileClassVarDec(self):

        self.__consume(JackTokenizer.KEYWORD,self.__tokenizer.keyword()) #static or field


        self.__consumeTypeDec()

        #consume the variable list
        #make sure their is at least one identifier
        self.__consume(JackTokenizer.IDENTIFIER)
        while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            self.__consume(JackTokenizer.IDENTIFIER)

        #consume ending ';'
        self.__consume(JackTokenizer.SYMBOL,';')


    @xml_decorator("subroutineDec")
    def compileSubroutineDec(self):

        self.__consume(JackTokenizer.KEYWORD,{'constructor','method','function'})

        #handle return type
        if self.__tokenizer.type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,'void')
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
        if self.__tokenizer.type == JackTokenizer.IDENTIFIER:
            self.__consume(JackTokenizer.IDENTIFIER)
            #consume additional parameters
            while self.__tokenizer.token() == ",":
                self.__consume(JackTokenizer.SYMBOL,',')
                self.__consume(JackTokenizer.IDENTIFIER)

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
        self.__consumeTypeDec()
        self.__consume(JackTokenizer.IDENTIFIER)
        #handle multiple variables
        while self.__tokenizer.token() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            self.__consume(JackTokenizer.IDENTIFIER)

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
        self.__consume(JackTokenizer.SYMBOL,"do")
        self.compileSubroutineCall()
        self.__consume(JackTokenizer.SYMBOL,";")
    
    @xml_decorator("letStatement")
    def compileLet(self):
        """compiles let statements."""

        self.__consume(JackTokenizer.KEYWORD,'let')
        self.compileVariable()
        self.__consume(JackTokenizer.SYMBOL,"=")
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,";")

    @xml_decorator("ifStatement")
    def compileIf(self):

        self.__consume(JackTokenizer.KEYWORD,'if')
        self.__consume(JackTokenizer.SYMBOL,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,"}")

        if self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() == 'else':
            self.__consume(JackTokenizer.KEYWORD,'else')
            self.__consume(JackTokenizer.SYMBOL,'{')
            self.compileStatements()
            self.__consume(JackTokenizer.SYMBOL,'}')

    @xml_decorator("returnStatement")
    def compileReturn(self):
        self.__consume(JackTokenizer.KEYWORD,'return')
        #not an emptry return, so compile expression
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ';'):
            self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,';')

    @xml_decorator("whileStatement")
    def compileWhile(self):
        self.__consume(JackTokenizer.KEYWORD,'while')
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,')')
        self.__consume(JackTokenizer.STRING,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,'}')

    @xml_decorator("expressionList")
    def compileExpressionList(self):
        """Compiles a list of expressions."""
        #utilizes the fact that all expression lists are currently contained within parenthesis to test
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ')'):
            self.compileExpression()
            while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
                self.__consume(JackTokenizer.SYMBOL,',')
                self.compileExpression()
    
    @xml_decorator("expression")
    def compileExpression(self):
        self.compileTerm()
        while self.__tokenizer.token in self.ops:
            self.__consume(JackTokenizer.SYMBOL,self.ops)
            self.compileTerm()

    @xml_decorator("term")
    def compileTerm(self):
        """Compiles individual terms. Terms can be recursively defined"""
        t_type = self.__tokenizer.type
        if t_type == JackTokenizer.INT:
            self.__consume(JackTokenizer.INT)
        elif t_type == JackTokenizer.STRING:
            self.__consume(JackTokenizer.STRING)
        elif t_type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() in self.key_const: #true,false,null,this
            #consume the keyword, but save in case it is part of a method call on 'this'
            token = self.__tokenizer.keyword()
            #obtain next token for testing if it is a method call on this
            self.__tokenizer.advance()
            next_token = self.__tokenizer.token()
            #restore keyword token for later consumption
            self.__tokenizer.rewind()
            
            if token == 'this' and  next_token == '.': #method call
                self.compileSubroutineCall()
            else: #single keyword
                self.__consume(JackTokenizer.KEYWORD,self.key_const)

        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == '(':   #assume parenthesis by itself starts an expression
            self.__consume(JackTokenizer.SYMBOL,'(')
            self.compileExpression()
            self.__consume(JackTokenizer.SYMBOL,')')
        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() in self.unary_op: # example mathematical negation of an expression -- call term again
            self.__consume(JackTokenizer.SYMBOL,self.unary_op)
            self.compileTerm()
        elif t_type == JackTokenizer.IDENTIFIER: #can be a variable, array, or function call
            self.__tokenizer.advance() #if a variable, rest of conditionals will fall through
            t_type = self.__tokenizer.type
            token = self.__tokenizer.token()
            self.__tokenizer.rewind() #rewind back to identifier for processing methods to consume
            if t_type == JackTokenizer.SYMBOL and token in self.sub_call_op: #handle method and function calls
               self.compileSubroutineCall()
            else: #if not a method call, assume variable or array
                self.compileVariable()

    def compileSubroutineCall(self):
        """
           Handles parsing of the subroutine call
        """
        t_type = self.__tokenizer.type
        if t_type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() == 'this': #handle this identifier
            self.__consume(JackTokenizer.KEYWORD,'this')
        else: #assume an identifier
            self.__consume(JackTokenizer.IDENTIFIER)


        if self.__tokenizer.token() == '.': #if method call, consume . and method name identifier
            self.__consume(JackTokenizer.SYMBOL,'.')
            self.__consume(JackTokenizer.IDENTIFIER)
        #handle The code was developed against Pi 3 B, I have not tested on Pi 1. I think references to the name BCM2835 may be accidental, perhaps more accurate would be to call it BCM2837, although also possible that they sharethe actual function call portion -- Always runs
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileExpressionList()
        self.__consume(')')

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
        print("{} {}".format(t_type,self.__tokenizer.type))
        #test type
        if self.__tokenizer.type != t_type:
            raise CompilationError("Expecting type: %s  Received type: %s"%(t_type,self.__tokenizer.type))
        
        #if specific token(s) 
        if token:
            #if not a list or set, then wrap in set for comparison
            if not isinstance(token,(list,set)):
                token = {token}
            if self.__tokenizer.token() not in token:
                
                raise CompilationError("Expectaing {0} of type {1}. Received {2}: {3}".format(token,t_type, self.__tokenizer.type,self.__tokenizer.token()))


        #generate xml for token
        token_xml = SubElement(self.__current_parent,self.__tokenizer.type)
        token_xml.text = self.__tokenizer.token()
        self.__tokenizer.advance()

    #helper method for consuming type declarations
    def __consumeTypeDec(self):
        t_type = self.__tokenizer.type

        #varable type can be a keyword constant or class name
        if t_type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,{'int','char','boolean'})
        else:
            self.__consume(JackTokenizer.IDENTIFIER)




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
    from xml.etree import ElementTree as ET
    try:
        for file in get_jack_files(argv[1]):
            compiler = CompilationEngine(file)
            xml = compiler.getXML()
            with open(create_xml_path(file),'w') as doc:
                doc.write(ET.tostring(xml,'unicode'))     

    except IOError as e:
        print(e)
    except NotValidJackFileError as e:
        print(e)