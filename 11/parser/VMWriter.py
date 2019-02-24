class VMWriter:

    seg_types = set("CONST","ARG","STATIC","LOCAL","THIS","THAT","POINTER","TEMP")


    def __init__(self,filename):
        self._instructions = []

    def writePush(self,segment,index):
        self._writePushPop("push",segment,index)
        
    def writePop(self,segment,index):
        self._writePushPop("pop",segment,index)

    def _writePushPop(self,pushOrPop,segment,index)

        if pushOrPop.lower not in set("push","pop"):
            raise InstructionError("Instruction %s is not a valid instructions"%(pushOrPop))

        if segment.upper() not in self.seg_types:
            raise InstructionError("%s is not a valid memory segment"%(segment))
        

        self._instructions.append("%s %s %d"%(pushOrPop.lower(),segment.lower(),index))

        


    

class InstructionError(Exception):
    pass