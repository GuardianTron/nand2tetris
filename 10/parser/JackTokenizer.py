import re

class JackTokenizer:


    rules = {
        "comment":re.compile("(//.*\r?\n)|(/\*.*?\*/)"),
        "integer":re.compile("\d+"),
        "identifier":re.compile("[A-Za-z_]\w*"),
        "string":re.compile("\"*.*?\""),
        "symbol":re.compile("[{}\(\)\[\]\.,;\+\-\*&\|<>=]"),
        "keyword":re.compile("(class)|(constructor)|(function)|(method)|(field)|(static)|(var)|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return)"),
        "whitespace":re.compile("\s+")


    }

    def __init__(self,filename):
        with open(filename) as fh:
            self.__file = fh.read()

        #initialize values for scanner
        self.__start = 0
        self.__type = ""
        self.__token = None

    def advance(self):
        current_type = ""
        current_token = ""
        while self.__start < len(self.__file) and (current_type == "" or current_type == "whitepsace" or current_type == "comment"):
            match = self.__scan_token()
            if not match:
                raise Exception("No valid token found")
            current_type = match[0]
            current_token =  match[1]


        self.__type = current_type
        self.__token = current_token



    
    def __scan_token(self):
        match_tuple = None
        
        for rule in self.__class__.rules.keys():
            match = re.match(self.__class__.rules[rule],self.__file,self.__start)
            if match:
                self.__start = match.end() #reset start point for matching
                match_tuple = (rule,match.group(0))
                break
        return match_tuple





        
        


