class FileError(Exception):

    def __init__(self,path,message):
        self.path = path
        self.message = message

    def __str__(self):
        return "%s : %s"%(self.message,self.path)

class ParseError(Exception):

    def __init__(self,line_number,command_string,error_message):
        self.__line_number = line_number
        self.__command = command_string
        self.__error_message = error_message

    def __str__(self):
        return "%d:\t%s -- %s"%(self.__line_number,self.__command,self.__error_message)