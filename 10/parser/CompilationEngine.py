from JackTokenizer import JackTokenizer,JackTokenizerRewind
from xml.etree.ElementTree import Element,SubElement
class CompilationEngine:

    unary_op = set('-','~') #mathematical and logical negation
    sub_call_op = set('.','(') #used to determine
    key_const = set('true','false','null','this')
    ops = set('+','-','*','/','&','|','<','>')


    def __init__(self,file):
        self.__tokenizer = JackTokenizerRewind(file)
        #holds XML root
        self.__root = None
        #holds the current parent node
        self.__current_parent = None

        #bootstrap the compilation process
        if self.__tokenizer.advance():
            self.compileClass()

    def compileClass(self):
        self.__root = Element('class')
        self.__current_parent = self.__root
        self.__consume(JackTokenizer.KEYWORD,'class')
        self.__consume(JackTokenizer.IDENTIFIER,self.__tokenizer.identifier())
        self.__consume(JackTokenizer.SYMBOL,'{')

        #process class var declarations
        while self.__tokenizer.keyword() in ('field','static'):
            self.compileClassVarDec()

        #process subroutine declarations
        while  self.__tokenizer.keyword() in ('constructor','method','function'):
            self.compileSubroutineDec()


        self.__consume(JackTokenizer.SYMBOL,'}')    

    def compileClassVarDec(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'classVarDec')
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



        #reset old parent to curent after returning
        self.__current_parent = old_parent

    def compileSubroutineDec(self):
        #save parent context for caller
        old_parent = self.__current_parent

        self.__current_parent = SubElement(self.__current_parent,'subroutineDec')
        self.__consume(JackTokenizer.KEYWORD,('constructor','method','function'))

        #handle return type
        if self.__tokenizer.type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,'void')
        else:
            self.__consume(JackTokenizer.IDENTIFIER)

        #handle expressions
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileParameterList()
        self.__consume(JackTokenizer.SYMBOL,')') 

        #move onto subroutineBody
        self.compileSubroutineBody()       

        #restore parent context for caller
        self.__current_parent = old_parent

    def compileParameterList(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(self.__current_parent,'paramaterList')

        #consume parameter list if any
        if self.__tokenizer.type == JackTokenizer.IDENTIFIER:
            self.__consume(JackTokenizer.IDENTIFIER)
            #consume additional parameters
            while self.__tokenizer.token() == ",":
                self.__consume(JackTokenizer.SYMBOL,',')
                self.__consume(JackTokenizer.IDENTIFIER)


        self.__current_parent = old_parent

    def compileSubroutineBody(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(self.__current_parent,'subroutineBody')
        self.__consume(JackTokenizer.SYMBOL,'{')

        #handle optional variable declarations.
        while self.__tokenizer.token() == 'var':
            self.compileVarDec()  

        self.compileStatements()
             

        self.__consume(JackTokenizer.SYMBOL,'}')
        self.__current_parent = old_parent

    def compileVarDec(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(self.__current_parent,'varDec')
        self.__consume(JackTokenizer.KEYWORD,'var')
        self.__consumeTypeDec()
        self.__consume(JackTokenizer.IDENTIFIER)
        #handle multiple variables
        while self.__tokenizer.token() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            self.__consume(JackTokenizer.IDENTIFIER)

        #finish declaration
        self.__consume(JackTokenizer.SYMBOL,';')


        self.__current_parent = old_parent

    def compileStatements(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(self.__current_parent,'statements')
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

        self.__current_parent = old_parent

    def compileDo(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,"doStatement")

        self.__consume(JackTokenizer.SYMBOL,"do")
        self.compileSubroutineCall()
        self.__consume(JackTokenizer.SYMBOL,";")


        self.__current_parent = old_parent
    
    def compileLet(self):
        """compiles let statements.""""
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'letStatement')
        
        self.__consume(JackTokenizer.KEYWORD,'let')
        self.compileVariable()
        self.__consume(JackTokenizer.SYMBOL,"=")
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,";")

        self.__current_parent = old_parent

    def compileIf(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'ifStatement')

        self.__consume(JackTokenizer.KEYWORD,'if')
        self.__consume(JackTokenizer.SYMBOL,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,"}")

        if self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() == 'else':
            self.__consume(JackTokenizer.KEYWORD,'else')
            self.__consume(JackTokenizer.SYMBOL,'{')
            self.compileStatements()
            self.__consume(JackTokenizer.SYMBOL,'}')

        self.__current_parent = old_parent

    def compileReturn(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'returnStatement')

        self.__consume(JackTokenizer.KEYWORD,'return')
        #not an emptry return, so compile expression
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ';'):
            self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,';')


        self.__current_parent = old_parent

    def compileWhile(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'whileStatement')

        self.__consume(JackTokenizer.KEYWORD,'while')
        self.__consume(JackTokenizer.SYMBOL,'(')
        self.compileExpression()
        self.__consume(JackTokenizer.SYMBOL,')')
        self.__consume(JackTokenizer.STRING,'{')
        self.compileStatements()
        self.__consume(JackTokenizer.SYMBOL,'}')

        self.__current_parent = old_parent 

    def compileExpressionList(self):
        """Compiles a list of expressions."""
        #utilizes the fact that all expression lists are currently contained within parenthesis to test
        if not (self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ')':
            self.compileExpression()
            while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
                self.__consume(JackTokenizer.SYMBOL,',')
                self.compileExpression()

    def compileExpression(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'expression')

        self.compileTerm()
        while self.__tokenizer.token in self.ops:
            self.__consume(JackTokenizer.SYMBOL,self.ops)
            self.compileTerm()


        self.__current_parent = old_parent

    def compileTerm(self):
        """Compiles individual terms. Terms can be recursively defined"""
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'term')
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
            
             
                
            


        self.__current_parent = old_parent

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
            raise CompilationError("Expecting type: %s"%(t_type))
        
        #if specific token(s) 
        if token:
            #if not a list or set, then wrap in set for comparison
            if not isinstance(token,(list,set)):
                token = set(token)
            if self.__tokenizer.token() not in token:
                raise CompilationError("Expectaing {0} of type {1}".format(token,t_type))


        #generate xml for token
        token_xml = SubElement(self.__current_parent,self.__tokenizer.type)
        token_xml.text = self.__tokenizer.token()
        self.__tokenizer.advance()

    #helper method for consuming type declarations
    def __consumeTypeDec(self):
        t_type = self.__tokenizer.type

        #varable type can be a keyword constant or class name
        if t_type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,set('int','char','boolean'))
        else:
            self.__consume(JackTokenizer.IDENTIFIER)


    def __isPossibleTerm(self):
        "Tests to see if the token could be the start of a term"



class CompilationError(Exception):
    pass    
    