import sys,os
from parser import Parser
from code_writer import CodeWriter
from errors import FileError,ParseError,CodeError

class VMTranslator:

    def __init__(self,path):
        self.__path = os.path.abspath(path)
        if os.path.isdir(path):
            print(path)
            print(Parser.getBaseFileName(path))
            self.__cw = CodeWriter(path+"/"+Parser.getBaseFileName(path))
            self.__cw.writeInit()
        elif os.path.isfile(path) and Parser.isVMFile(path):
            self.__cw = CodeWriter(Parser.getRawPath(path))
        else:
            raise FileError(path, " is not a valid vm file or directory.")
    
    def translate(self):
        if os.path.isdir(self.__path):
            #translate vm each file in the directory
            for listing in os.listdir(self.__path):
                if os.path.isfile(listing) and Parser.isVMFile(listing):
                    self.__translateFile(listing)
        else: #assume path is a vm file
            self.__translateFile(self.__path)


    def __translateFile(self,file):
        p = Parser(file)
        self.__cw.setFileName(p.base_name)

        while p.has_more_commands:
            p.advance()

            if p.commandType == Parser.C_POP or p.commandType == Parser.C_PUSH:
                self.__cw.writePushPop(p.commandType,p.arg1,p.arg2)
            elif p.commandType == Parser.C_ARITHMETIC:
                self.__cw.writeArithmetic(p.arg1)
            elif p.commandType == Parser.C_LABEL:
                self.__cw.writeLabel(p.arg1)
            elif p.commandType == Parser.C_GOTO:
                self.__cw.writeGoto(p.arg1)
            elif p.commandType == Parser.C_IF:
                self.__cw.writeIf(p.arg1)
            elif p.commandType == Parser.C_FUNCTION:
                self.__cw.writeFunction(p.arg1,p.arg2)
            elif p.commandType == Parser.C_CALL:
                self.__cw.writeCall(p.arg1,p.arg2)
            elif p.commandType == Parser.C_RETURN:
                self.__cw.writeReturn()
            else:
                raise ParseError(p.line_number,p.command_string,"An invalid command type was returned.")


    def close(self):
        self.__cw.close()


if(len(sys.argv) < 2):
    print("The translator requires the name of the file to be parsed.")
    exit()
path = sys.argv[1]




try:


    vmt = VMTranslator(path)
    vmt.translate()
    vmt.close()


except FileError as e:
    print(e)
except ParseError as e:
    print(e)
except CodeError as e:
    pe = ParseError(p.line_number,p.current_line,str(e))
    print(pe)
except IOError as e:
    errno, strerror = e.args
    print("I/O error({0}): {1}".format(errno,strerror))


