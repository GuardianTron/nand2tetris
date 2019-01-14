from JackTokenizer import JackTokenizer
from xml.etree.ElementTree import Element,SubElement
class CompilationEngine:

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
    
        while self.__tokenizer.type == JackTokenizer.KEYWORD and self.__tokenizer.keyword() in ('field','static'):
            self.compileClassVarDec()


        self.__consume(JackTokenizer.SYMBOL,'}')    

    def compileClassVarDec(self):
        old_parent = self.__current_parent
        self.__current_parent = SubElement(old_parent,'classVarDec')
        self.__consume(JackTokenizer.KEYWORD,self.__tokenizer.keyword()) #static or field


        t_type = self.__tokenizer.type

        #varable type can be a keyword constant or class name
        if t_type == JackTokenizer.KEYWORD and self.__token.keyword() in ('int','char','boolean'):
            self.__consume(JackTokenizer.KEYWORD,self.__tokenizer.keyword())
        elif t_type == JackTokenizer.IDENTIFIER:
            self.__consume(JackTokenizer.IDENTIFIER):
            self.__consume(JackTokenizer.IDENTIFIER)
        else:
            raise Exception("Expected class identifier or boolean, int, or char declaration.  Recived: "+self.__tokenizer.raw_token)

        #consume the variable list
        #make sure their is at least one identifier
        self.__consume(JackTokenizer.IDENTIFIER)
        while self.__tokenizer.type == JackTokenizer.SYMBOL and self.__tokenizer.symbol() == ',':
            self.__consume(JackTokenizer.SYMBOL,',')
            self.__cosumer(JackTokenizer.IDENTIFIER)

        #consume ending ';'
        self.__consume(JackTokenizer.SYMBOL,';')



        #reset old parent to curent after returning
        self.__current_parent = old_parent

    def compileSubroutineDec(self):



    #note: token is passed for checking that the token matches a specific
    #expected value.  The token recorded is taken from the tokenizer
    #thus, only pre-enumerated tokens such as symbols or keywords will use the 
    #token paramenter. 
    def __consume(self,t_type,token=""):
        #todo - implement error generation

        #generate xml for token
        token_xml = SubElement(self.__current_parent,self.__tokenizer.type)
        token_xml.text = self.__tokenizer.token()
        self.__tokenizer.advance()


        
        


            
