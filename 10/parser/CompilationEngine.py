from JackTokenizer import JackTokenizer
from xml.etree.ElementTree import Element,SubElement
class CompilationEngine:

    unary_op = set('-','~') #mathematical and logical negation
    sub_call_op = set('.','(') #used to determine
    key_const = set('true','false','null','this')


    def __init__(self,file):
        self.__tokenizer = JackTokenizer(file)
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
        pass
    
    def compileLet(self):
        pass

    def compileIf(self):
        pass

    def compileReturn(self):
        pass

    def compileWhile(self):
        pass

    def compileSubroutineCall(self):
        pass

    def compileExpressionList(self):
        pass

    def compileExpression(self):
        pass

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
            self.__consume(JackTokenizer.KEYWORD,self.key_const)
        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == '(':   #assume parenthesis by itself starts an expression
            self.__consume(JackTokenizer.SYMBOL,'(')
            self.compileExpression()
            self.__consume(JackTokenizer.SYMBOL,')')
        elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() in self.unary_op: # example mathematical negation of an expression -- call term again
            self.__consume(JackTokenizer.SYMBOL,self.unary_op)
            self.compileTerm()
        elif t_type == JackTokenizer.IDENTIFIER: #can be a variable, array, or function call
            self.__consume(JackTokenizer.IDENTIFIER) #if a variable, rest of conditionals will fall through
            t_type = self.__tokenizer.type
            if t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() in self.sub_call_op: #handle method and function calls
                #handle class identifier if '.' avaiable
                #by consuming token and then consuming and identifier
                #then handle the actual function/method call by consuming parenthesis and 
                #callind compileExpressionlist
                if self.__tokenizer.symbol() == '.':
                    self.__consume(JackTokenizer.SYMBOL,'.')
                    self.__consume(JackTokenizer.IDENTIFIER)

                self.__consume(JackTokenizer.SYMBOL,'(')
                self.compileExpressionList()
                self.__consume(JackTokenizer.SYMBOL,')')
            elif t_type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == '[': #arrays
                self.__consume(JackTokenizer.SYMBOL,'[')
                self.compileExpression()
                self.__consume(JackTokenizer.SYMBOL,']')
             
                
            


        self.__current_parent = old_parent


    #note: token is passed for checking that the token matches a specific
    #expected value.  The token recorded is taken from the tokenizer
    #thus, only pre-enumerated tokens such as symbols or keywords will use the 
    #token paramenter. 
    #token can either be a single token or an array of possible values
    def __consume(self,t_type,token=""):
        #todo - implement error generation

        #generate xml for token
        token_xml = SubElement(self.__current_parent,self.__tokenizer.type)
        token_xml.text = self.__tokenizer.token()
        self.__tokenizer.advance()

    #helper method for consuming type declarations
    def __consumeTypeDec(self):
        t_type = self.__tokenizer.type

        #varable type can be a keyword constant or class name
        if t_type == JackTokenizer.KEYWORD:
            self.__consume(JackTokenizer.KEYWORD,('int','char','boolean'))
        else:
            self.__consume(JackTokenizer.IDENTIFIER)



        
    