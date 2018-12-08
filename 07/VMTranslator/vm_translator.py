import sys
from parser import Parser
from errors import FileError,ParseError

if(len(sys.argv) < 2):
    print("The translator requires the name of the file to be parsed.")
    exit()
path = sys.argv[1]


try:
    p = Parser(path)
    while p.advance:
        info = (p.line_number,p.current_line,p.commandType,p.arg1,p.arg2)
        print("%d:  %s -- (%s,%s,%s)"%info)

except FileError as e:
    print(e)
except ParseError as e:
    print(e:)
except IOError as e:
    errno, strerror = e.args
    print("I/O error({0}): {1}".format(errno,strerror))
