import sys
from parser import Parser,Instruction
from encode import BinaryEncoder,SymbolTable

if(len(sys.argv) < 2):
    print("The assembler requires the name of the asm file to be compiled.")
    exit()
path = sys.argv[1]
try:
    p = Parser(path)
    p.parse()
    b = BinaryEncoder()
    b.encodeAll(p.processed)


    #add labels to the symbol table
    sym = SymbolTable().table
    curr_address = 0
    for inst in p.processed:
        #only increment address for actual instructions
        if inst.instruction_type == Instruction.LABEL:
            #add if not in symbol table
            if inst.payload not in sym:
                sym[inst.payload] = curr_address
        else:
            #not a label, so move on to next address
            curr_address += 1
                



    
    #save compiled hack file
    path = path.replace('.asm','')+'.hack'
    with open(path,'w') as f:
        f.write('\n'.join(b.bin))

except IOError as e:
    errno, strerror = e.args
    print("I/O error({0}): {1}".format(errno,strerror))


    

    
    

finally:
    exit()