import re

class JackTokenizer:

    KEYWORD = "keyword"
    INT = "integerConstant"
    IDENTIFIER = "indentifier"
    STRING = "stringConstant"
    SYMBOL = "symbol"


    def __init__(self,filename):
        with open(filename) as fh:
            self.__file = fh.read()

        #ensure rules execute in order
        self.__rule_order = ("comment","integerConstant","keyword","identifier","stringConstant","symbol","whitespace")

        self.__rules = {}
        self.__rules["comment"]=re.compile("(//.*\r?\n)|(/\*.*?\*/)")
        self.__rules["integerConstant"]=re.compile("\d+")
        self.__rules["keyword"]=re.compile("((class)|(constructor)|(function)|(method)|(field)|(static)|(var)|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return))\s")
        self.__rules["identifier"]=re.compile("[A-Za-z_]\w*")
        self.__rules["stringConstant"]=re.compile("\".*?\"")
        self.__rules["symbol"]=re.compile("[{}\(\)\[\]\.,;\+\-\*&\|<>=/~]") 
        self.__rules["whitespace"]=re.compile("\s+")


        #initialize values for scanner
        self.__start = 0
        self.__type = ""
        self.__token = None

    def advance(self):
        current_type = ""
        current_token = ""
        while self.__start < len(self.__file) and (current_type == "" or current_type == "whitespace" or current_type == "comment"):
            match = self.__scan_token()
            if not match:
                raise Exception("No valid token found")
            current_type = match[0]
            current_token =  match[1]


        self.__type = current_type
        self.__token = current_token

        return self.__start < len(self.__file) and (current_type != 'whitespace' and current_type != 'comment')



    
    def __scan_token(self):
        match_tuple = None
        
        for rule in self.__rule_order:
            match = self.__rules[rule].match(self.__file,self.__start)
            if match:
                self.__start = match.end() #reset start point for matching
                match_tuple = (rule,match.group(0))
                break
        return match_tuple

    def symbol(self):
        return self.__token

    def keyword(self):
        return self.__token.trim()

    def identifier(self):
        return self.__token

    def string(self):
        return self.__token[1:-1]

    def integer(self):
        return int(self.__token)

    #convience method for returing the token
    def token(self):
        if self.__type == JackTokenizer.INT:
            return self.integer()
        elif self.__type == JackTokenizer.STRING:
            return self.string()
        elif self.__type == JackTokenizer.KEYWORD:
            return self.keyword()
        else:
            return self.raw_token
    
    @property
    def type(self):
        return self.__type

    @property 
    def raw_token(self):
        return self.__token





        
        


