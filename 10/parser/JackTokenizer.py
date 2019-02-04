import re

class JackTokenizer:

    KEYWORD = "keyword"
    INT = "integerConstant"
    IDENTIFIER = "indentifier"
    STRING = "stringConstant"
    SYMBOL = "symbol"

    keywords = ["class","constructor","function","method","field","static","var","int","char","boolean","void","true","false","null","this","let","do","if","else","while","return"]


    def __init__(self,filename):
        with open(filename) as fh:
            self.__file = fh.read()



        #ensure rules execute in order
        self.__rule_order = ("comment","integerConstant","keyword","identifier","stringConstant","symbol","whitespace")

        #create the keyword regex
        key_regex = "(%s)\W"%("|".join(["(%s)"%(key) for key in self.keywords]))
        self.__rules = {}
        self.__rules["comment"]=re.compile("(//.*?\r?\n)|(/\*.*?(\*/))",re.DOTALL)
        self.__rules["integerConstant"]=re.compile("\d+")
        self.__rules["keyword"]=re.compile(key_regex)
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
                raise Exception("No valid token found\n"+self.__file[self.__start:])
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
                match_string = match.group(0)
                if rule == "keyword":
                     #Keywords will consume an extra non alphanumeric/underscore character
                    #Remove this extra character and handle the matches appropriately
                    self.__start -= 1
                    match_string = match_string[:-1]
                match_tuple = (rule,match_string)
                break
        return match_tuple

    def symbol(self):
        return self.__token

    def keyword(self):
        return self.__token.strip()

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

    @type.setter
    def type(self,t_type):
        self.__type = t_type

    @property 
    def raw_token(self):
        return self.__token

    @raw_token.setter
    def raw_token(self,token):
        self.__token = token


class JackTokenizerRewind(JackTokenizer):
    """Tokenizes Jack program files. 
        Adds ability to move backward 
        and forwad through the token stream."""

    def __init__(self,filename):
        super().__init__(filename)
        self.__tokens = []
        self.__index = -1

    def advance(self):
        "Advance to the next token"
        #revisiting already scanned tokens
        if self.__index < len(self.__tokens) - 1:
            self.__index+=1
            #set the current token for return
            self.type,self.raw_token = self.__tokens[self.__index]
            return True
        elif super().advance():
                self.__index = len(self.__tokens)
                self.__tokens.append((self.type,self.raw_token))
                return True
        return False
    
    def rewind(self):
        "Move backwards through stack. Returns true if not at bottom"
        if self.__index > 0:
            self.__index -= 1
            #set current token
            self.type, self.raw_token = self.__token[self.__index]
            return True
        return False
                


if __name__ == "__main__":
    from sys import argv
    import os.path
    from xml.etree.ElementTree import Element,SubElement,ElementTree
    from xml.etree import ElementTree as ET
    try:
        f_name = argv[1]
        tokenizer = JackTokenizer(argv[1])
        root = Element('tokens')
        while tokenizer.advance():
            token_element = SubElement(root,tokenizer.type)
            token_element.text = " "+str(tokenizer.token())+" "

        #save the xml output
        base_name = os.path.basename(f_name).split(".")[0]
        xml_name = os.path.join(os.path.dirname(f_name),base_name+"T_test.xml")
        with open(xml_name,'w') as doc:
            doc.write(ET.tostring(root,'unicode'))
    except Exception as e:
        print(e)
        raise e

        




        
        


