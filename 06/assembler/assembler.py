import sys
from parser import Parser

if(len(sys.argv) < 2):
    print("The assembler requires the name of the asm file to be compiled.")
    exit()

try:
    p = Parser(sys.argv[1])
    

except IOError as e:
    errno, strerror = e.args
    print("I/O error({0}): {1}".format(errno,strerror))

else:
    p.parse()
    for i in p.processed:
        print(str(i))

finally:
    exit()