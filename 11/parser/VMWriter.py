class VMWriter:

    seg_types = {"CONSTANT","ARGUMENT","STATIC","LOCAL","THIS","THAT","POINTER","TEMP"}
    arithmetic_commands = {"ADD","SUB","NEG","EQ","GT","LT","AND","OR","NOT"}


    def __init__(self,filename):
        self._instructions = []
        self._vm_filename = filename.split('.')[0]+".vm"

    def writePush(self,segment,index):
        self._writePushPop("push",segment,index)
        
    def writePop(self,segment,index):
        self._writePushPop("pop",segment,index)

    def _writePushPop(self,pushOrPop,segment,index):

        if pushOrPop.lower() not in {"push","pop"}:
            raise InstructionError("Instruction %s is not a valid instructions"%(pushOrPop))

        if segment.upper() not in self.seg_types:
            raise InstructionError("%s is not a valid memory segment"%(segment))
        

        self._instructions.append("%s %s %d"%(pushOrPop.lower(),segment.lower(),index))

        
    def writeArithmetic(self,command):
        if command.upper() not in self.arithmetic_commands:
            raise InstructionError("%s is an invalid arithmetic instructions"%(command))

        self._instructions.append(command.lower())

    def writeLabel(self,label):
        self._instructions.append("label %s"%(label))


    def writeGoto(self,label):
        self._instructions.append("goto %s"%(label))

    def writeIf(self,label):
        self._instructions.append("if-goto %s"%(label))

    def writeCall(self,name,numArgs):
        self._instructions.append("call %s %d"%(name,numArgs))

    def writeFunction(self,name,numLocals):
        self._instructions.append("function %s %d"%(name,numLocals))    

    def writeReturn(self):
        self._instructions.append("return")

    def close(self):
        with open(self._vm_filename,'w') as f:
            for instruction in self._instructions:
                f.write(instruction+"\n")
            


    

class InstructionError(Exception):
    pass