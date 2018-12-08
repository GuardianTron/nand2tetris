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
            self.__file = f.readLines()

        self.__line_number = 0
        
        self.__arg1 = ''
        self.__arg2 = '' 
        self.__commandType = -1


    def advance(self):
        is_whitespace = True
        #advance until we hit a command
        while is_whitespace and self.has_more_commands:
            
            self.__current_line = self.__file[self.__line_number]
            self.__line_number+=1
            current_line = self.__stripComments(current_line)
            is_whitespace = (len(current_line) == 0)

        #split the command
        command = self.current_line.split(' ')
        if command[0] == 'push' or command[0] == 'pop' :
            self.__parsePushPop(command)

            

        


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
        if len(command) != 2:
            raise ParseError(self.__line_number,self.__current_line,"Push commands must have two arguments")
        elif not command[2].isdigit()
            raise ParseError(self.__line_number,self.__current_line,"Push commands must have an integer as their final argument.")
        
        if command[0] == 'push':
            self.__commandType = C_PUSH
        elif command[0] == 'pop':
            self.__commandType = C_POP
        else: #mistakenly called on wrong type of command
            raise Exception('Parser::__parsePushPop called on invalide command: %s'%(command[0]))
            
        self.__arg1 = command[1]
        self.__arg2 = command[2]



    #utility methods

    def __getRawPath(self,path):
        parts = path.split('.')
        if len(parts) == 2 and part[1] == '.vm':
            return parts[0]
        raise new FileError(path,"")
    
    def __getBaseFileName(self,raw_path):
        parts = raw_path.split('/').split('\')
        return parts[-1]

    def __stripWhitespace(self,line):
        return line.replace("\n","").replace("\r","").strip()
    
    def __stripComments(self,line):
        self.__stripWhitespace(line)
        comment = line.find("//")
        if comment > -1:
            line = line[0:comment]
        self.__stripWhitespace(line):
        return line
        
        