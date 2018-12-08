import re
from errors import FileError,ParseError


class Parser:

    #define instruction constants
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8

    def __init__(self,file_path):
        self.__file_path = file_path
        #get the raw path without the extention
        self.__path_name = self.__getRawPath(file_path)
        #get the raw base name of the file
        #used for label generation
        self.__base_name = self.__getBaseFileName(self.__path_name)

        #open the file
        with open(self.__file_path) as f:
            self.__file = f.readlines()

        self.__line_number = 0
        self.__current_line = ''
        
        self.__arg1 = ''
        self.__arg2 = '' 
        self.__commandType = -1


    def advance(self):
        is_whitespace = True
        #advance until we hit a command
        while is_whitespace and self.has_more_commands:
            self.__current_line = self.__file[self.__line_number]
            self.__line_number+=1
            self.__current_line = self.__stripComments(self.__current_line)
            is_whitespace = (len(self.__current_line) == 0)

        #split the command
        command = self.__current_line.split()

        if command[0] == 'push' or command[0] == 'pop' :
            self.__parsePushPop(command)
        elif len(command) == 0 and command[0] in ['and','or','neg','not','add','sub','eq','lt','gt']: #handle logical and arithmetic commands
            self.__commandType = Parser.C_ARITHMETIC
            #no arguments
            self.__arg1 = ''
            self.__arg2 = ''

        


        #start implementing instructions
        




    @property
    def path_name(self):
        return self.__path_name

    @property
    def base_name(self):
            return self.__base_name

    @property
    def line_number(self):
        return self.__line_number

    @property
    def current_line(self):
        return self.__current_line

    @property 
    def has_more_commands(self):
        return self.__line_number < len(self.__file)

    @property 
    def commandType(self):
        return self.__commandType

    @property
    def arg1(self):
        return self.__arg1
    
    @property
    def arg2(self):
        return self.__arg2

    

    #parse commands

    def __parsePushPop(self,command):
        if len(command) != 3:
            raise ParseError(self.__line_number,self.__current_line,"Push/Pop commands must have two arguments")
        elif not command[2].isdigit():
            raise ParseError(self.__line_number,self.__current_line,"Push/Pop commands must have an integer as their final argument.")
        
        if command[0] == 'push':
            self.__commandType = Parser.C_PUSH
        elif command[0] == 'pop':
            self.__commandType = Parser.C_POP
        else: #mistakenly called on wrong type of command
            raise Exception('Parser::__parsePushPop called on invalide command: %s'%(command[0]))
            
        self.__arg1 = command[1]
        self.__arg2 = command[2]



    #utility methods

    def __getRawPath(self,path):
        parts = path.split('.')
        if len(parts) == 2 and parts[1] == 'vm':
            return parts[0]
        raise FileError(path,"Files must be of extension .vm")
    
    def __getBaseFileName(self,raw_path):
        parts = re.split(r"\|/",raw_path)
        return parts[-1]

    def __stripWhitespace(self,line):
        return line.replace('\n',"").replace('\r',"").strip()
    
    def __stripComments(self,line):
        line = self.__stripWhitespace(line)
        comment = line.find("//")
        if comment > -1:
            line = line[0:comment]
        line = self.__stripWhitespace(line)
        return line
        
        