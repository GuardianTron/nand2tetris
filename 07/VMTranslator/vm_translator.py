import sys
from parser import Parser
from code_writer import CodeWriter
from errors import FileError,ParseError,CodeError
if(len(sys.argv) < 2):
    print("The translator requires the name of the file to be parsed.")
    exit()
path = sys.argv[1]


try:
    p = Parser(path)
    c = CodeWriter(p.path_name)
    c.setFileName(p.base_name)
    while p.has_more_commands:
        p.advance()
        
        if p.commandType == Parser.C_POP or p.commandType == Parser.C_PUSH:
            c.writePushPop(p.commandType,p.arg1,p.arg2)
        elif p.commandType == Parser.C_ARITHMETIC:
            c.writeArithmetic(p.commandType)

    c.close()


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
