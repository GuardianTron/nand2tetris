import re

class JackTokenizer:



    def __init__(self,filename):
        with open(filename) as fh:
            self.__file = fh.read()

        #ensure rules execute in order
        self.rule_order = ("comment","integer","keyword","identifier","string","symbol","whitespace")

        self.rules = {}
        self.rules["comment"]=re.compile("(//.*\r?\n)|(/\*.*?\*/)")
        self.rules["integer"]=re.compile("\d+")
        self.rules["keyword"]=re.compile("((class)|(constructor)|(function)|(method)|(field)|(static)|(var)|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return))\s")
        self.rules["identifier"]=re.compile("[A-Za-z_]\w*")
        self.rules["string"]=re.compile("\".*?\"")
        self.rules["symbol"]=re.compile("[{}\(\)\[\]\.,;\+\-\*&\|<>=/]") 

        self.rules["whitespace"]=re.compile("\s+")
        
        for i in self.rules:
            print(self.rules[i])


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



    
    def __scan_token(self):
        match_tuple = None
        
        for rule in self.rule_order:
            match = self.rules[rule].match(self.__file,self.__start)
            if match:
                self.__start = match.end() #reset start point for matching
                match_tuple = (rule,match.group(0))
                break
        return match_tuple

    def hasMoreTokens(self):
        return self.__start < len(self.__file)

    
    @property
    def type(self):
        return self.__type

    @property 
    def raw_token(self):
        return self.__token





        
        


