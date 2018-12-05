import sys
from parser import Parser,Instruction
from encode import BinaryEncoder

if(len(sys.argv) < 2):
    print("The assembler requires the name of the asm file to be compiled.")
    exit()
path = sys.argv[1]
try:
    p = Parser(path)
    p.parse()
    b = BinaryEncoder()
    b.encodeAll(p.processed)
    
    #save compiled hack file
    path = path.replace('.asm','')+'.hack'
    with open(path,'w') as f:
        f.write('\n'.join(b.bin))

except IOError as e:
    errno, strerror = e.args
    print("I/O error({0}): {1}".format(errno,strerror))


    

    
    

finally:
    exit()