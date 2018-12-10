from parser import Parser
from errors import CodeError

class CodeWriter:

    asm_dynamic_pointers = {
        "this":"THIS",
        "that":"THAT",
        "local":'LCL',
        "argument":'ARG'
    }

    def __init__(self,output_file):
       
        #holds assembly code
        self.__assembly = []

        self.__file_name = output_file
        #holds the name of the file currently being processed
        #for namespacing purposes
        self.__current_vm_file = ''
        #current number for generating indexes for dynamically 
        #set assembly labels
        self.__current_index = 0

        self.__static_labels = {}


    def sefFileName(self,file_name):
        self.__current_vm_file = file_name

    
    def writePushPop(type,segment,index):

        if not index.isdigit():
            raise CodeError("Push and pop instructions must have an integer as their second argument.")
        index = int(index)
        asm = []
        if type == Parser.C_PUSH:
            asm = self.__writePush(segment,index)

        elif type == Parser.C_POP:
            asm = self.__writePop(segment,index)

    def writeArithmetic(self,argument):
        #code to pop values
        asm = []
        asm.append("@SP")
        asm.append("AM=M-1")#get to top of stack
        asm.append("D=M") #save value
        asm.append("@SP")
        asm.append("AM=M-1") #get second value
        asm.append("A=M") #s

    def __writePush(self,segment,index):
        asm = []
        #handle constant
        if segment == 'constant':
            asm.append('@%d'%(index)) #set constant
            asm.append('D=A') #store constant in register
                
        #handle memory segments
        elif segment in CodeWriter.asm_dynamic_pointers.keys():
            asm.append("@%s"%(CodeWriter.asm_dynamic_pointers[segment])) #set memory location
            #instructions common to all     
            asm.append('D=M') #save location
            asm.append('@%d'%(index) #set index
            asm.append('A=D+A') #set pointer
            asm.append('D=M') #get value out of memory
        elif segment == 'pointer':
            if index !='1' or index!='0':
                raise new CodeError("push pointer can only take 1 and 0 as arguments.")
            #get the address of this or that
            if index == '0':
                pointer = "@THIS"
            else:
                pointer = "@THAT"
                
            asm.append(pointer)
            asm.append('D=M') #save current memory address of this
            asm.append('@%d'%(index))
            asm.append('D=D+A') #change pointer to this/that + index

        elif segment == 'temp':
            if index > 7 or index < 0:
                raise CodeError("push temp commands must have an index between 0 and 7.")
            asm.append("@R%d"%(5+index))
            asm.append('D=M')
        elif segment == 'static':
            f_name = self.__current_vm_file
            asm.append(self.__generateStaticLabel(index))
        else: #invalid segement passed
            raise CodeError("Segment %s is not a valid memory segment."%(segment))

        #common instructions to all push commands
        asm.append('@SP') #set memory location to stack pointer
        asm.append('A=M') #point to top of stack
        asm.append('M=D') #set top of stack to new value
        asm.append('@SP') #set new stack memory location
        asm.append('M=M+1')

        return asm
    
    def __writePop(self,segment,index):
        asm = []
        #get value at top of stack
        

        #handle this,that,arg,local segments
        if segment in CoderWriter.asm_dynamic_pointers.keys():
            mem_seg = CodeWriter.asm_dynamic_pointers[segment]
            asm.append("@%d"%(index))
            asm.append("D=A") #save index"
            asm.append("@%s"%(mem_seg))
            asm.append("M=M+D") #have segment point to locaation to be accessed to be accessed
            #set the value at the top of stack

            self.__appendStackTopASM(asm)"@%s.%d"%(f_name,index)
                
            
            #save value to desired location
            asm.append("@%s"%(mem_seg))
            asm.append("A=M")
            asm.append("M=D") #save value at top of stack to desired location.
            
            #restore base address
            asm.append('@%d'%(index))
            asm.append("D=A")
            asm.append("@%s"%(mem_seg))
            asm.append("M=M-D")
        elif segment == 'pointer':
            if index != 0 and index != 1:
                raise CodeError("Pop pointer commands must have an argument of 0 or 1")
            #get top of stack
            self.__appendStackTopASM(asm)
            pointer = 'THIS'
            if index == 1:
                pointer = that
            asm.append("@%s"%(pointer))
            asm.append("M=D")
        elif segment == 'temp':
            if index > 7 of index < 0:
                raise CodeError("Pop temp commands may only take integers 0 through 7 as arguments.")
            self.__appendStackTopASM(asm)
            asm.append("@R%d"%(index))
            asm.append("M=D")
        elif segment == "static":
            self.__appendStackTopASM(asm)
            asm.append(self.__generateStaticLabel(index))
            asm.append('M=D')
        else:
            raise CodeError("pop %s is unsupported"%(segment))

        return asm



    def __appendStackTopASM(self,asm):
        asm.append("@SP") 
        asm.append("AM=M-1") #get pointer to top of stack and set
        asm.append("D=M") #get value at top

    def __generateStaticLabel(self,index):
            return "@%s.%d"%(f_name,index)

