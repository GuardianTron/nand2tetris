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
        self.__asm = []

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
        if type == Parser.C_PUSH:
            self.__writePush(segment,index)

        elif type == Parser.C_POP:
            self.__writePop(segment,index)

    def writeArithmetic(self,argument):
        #code to pop values
        self.__asm.append("@SP")
        self.__asm.append("AM=M-1")#get to top of stack
        self.__asm.append("D=M") #save value
        self.__asm.append("@SP")
        self.__asm.append("AM=M-1") #get second value
        self.__asm.append("A=M") #s

    def __writePush(self,segment,index):
        #handle constant
        if segment == 'constant':
            self.__asm.append('@%d'%(index)) #set constant
            self.__asm.append('D=A') #store constant in register
                
        #handle memory segments
        elif segment in CodeWriter.self.__asm_dynamic_pointers.keys():
            self.__asm.append("@%s"%(CodeWriter.self.__asm_dynamic_pointers[segment])) #set memory location
            #instructions common to all     
            self.__asm.append('D=M') #save location
            self.__asm.append('@%d'%(index) #set index
            self.__asm.append('A=D+A') #set pointer
            self.__asm.append('D=M') #get value out of memory
        elif segment == 'pointer':
            if index !='1' or index!='0':
                raise new CodeError("push pointer can only take 1 and 0 as arguments.")
            #get the address of this or that
            if index == '0':
                pointer = "@THIS"
            else:
                pointer = "@THAT"
                
            self.__asm.append(pointer)
            self.__asm.append('D=M') #save current memory address of this
            self.__asm.append('@%d'%(index))
            self.__asm.append('D=D+A') #change pointer to this/that + index

        elif segment == 'temp':
            if index > 7 or index < 0:
                raise CodeError("push temp commands must have an index between 0 and 7.")
            self.__asm.append("@R%d"%(5+index))
            self.__asm.append('D=M')
        elif segment == 'static':
            f_name = self.__current_vm_file
            self.__asm.append(self.__generateStaticLabel(index))
        else: #invalid segement passed
            raise CodeError("Segment %s is not a valid memory segment."%(segment))

        #common instructions to all push commands
        self.__asm.append('@SP') #set memory location to stack pointer
        self.__asm.append('A=M') #point to top of stack
        self.__asm.append('M=D') #set top of stack to new value
        self.__asm.append('@SP') #set new stack memory location
        self.__asm.append('M=M+1')

    
    def __writePop(self,segment,index):
        #get value at top of stack
        

        #handle this,that,arg,local segments
        if segment in CoderWriter.asm_dynamic_pointers.keys():
            mem_seg = CodeWriter.asm_dynamic_pointers[segment]
            self.__asm.append("@%d"%(index))
            self.__asm.append("D=A") #save index"
            self.__asm.append("@%s"%(mem_seg))
            self.__asm.append("M=M+D") #have segment point to locaation to be accessed to be accessed
            #set the value at the top of stack

            self.__appendStackTopASM()
                
            
            #save value to desired location
            self.__asm.append("@%s"%(mem_seg))
            self.__asm.append("A=M")
            self.__asm.append("M=D") #save value at top of stack to desired location.
            
            #restore base address
            self.__asm.append('@%d'%(index))
            self.__asm.append("D=A")
            self.__asm.append("@%s"%(mem_seg))
            self.__asm.append("M=M-D")
        elif segment == 'pointer':
            if index != 0 and index != 1:
                raise CodeError("Pop pointer commands must have an argument of 0 or 1")
            #get top of stack
            self.__appendStackTopASM()
            pointer = 'THIS'
            if index == 1:
                pointer = that
            self.__asm.append("@%s"%(pointer))
            self.__asm.append("M=D")
        elif segment == 'temp':
            if index > 7 of index < 0:
                raise CodeError("Pop temp commands may only take integers 0 through 7 as arguments.")
            self.__appendStackTopASM()
            self.__asm.append("@R%d"%(index))
            self.__asm.append("M=D")
        elif segment == "static":
            self.__appendStackTopASM()
            self.__asm.append(self.__generateStaticLabel(index))
            self.__asm.append('M=D')
        else:
            raise CodeError("pop %s is unsupported"%(segment))




    def __appendStackTopASM(self):
        self.__asm.append("@SP") 
        self.__asm.append("AM=M-1") #get pointer to top of stack and set
        self.__asm.append("D=M") #get value at top

    def __generateStaticLabel(self,index):
            return "@%s.%d"%(f_name,index)

