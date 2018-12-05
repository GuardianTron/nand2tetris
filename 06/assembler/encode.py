from parser import Instruction
class BinaryEncoder:

    def __init__(self):

        #set up array to hold binary values
        self.bin = []
        
        #define c instruction symbols
        self.__jmp = {
            "":'000',
            'JGT':'001',
            'JEQ':'010',
            'JLT':'100',
            'JGE':'011',
            'JLE':'110',
            'JNE':'101',
            'JMP':'111'
        }

        self.__dest = {
            '':'000',
            'M':'001',
            'D':'010',
            'A':'100',
            'MD':'011',
            'AM':'101',
            'AD':'110',
            'AMD':'111'
        }

        self.__op = {
            '0':"0101010",
            '1':'0111111',
            '-1':'0111010',
            'D':'0001100',
            'A':'0110000',
            'M':'1110000',
            '!D':'0001101',
            '!A':'0110001',
            '!M':'1110001',
            '-D':'0001111',
            '-A':'0110011',
            '-M':'1110011',
            'D+1':'0011111',
            'A+1':'0110111',
            'M+1':'1110111',
            'D-1':'0001110',
            'A-1':'0110010',
            'M-1':'1110010',
            'D+A':'0000010',
            'D+M':'1000010',
            'D-A':'0010011',
            'D-M':'1010011',
            'A-D':'0000111',
            'M-D':'1000111',
            'D&A':'0000000',
            'D&M':'1000000',
            'D|A':'0010101',
            'D|M':'1010101'

        }

    def encodeA(self,address):
        
        address_int = int(address)
        #convert integer address to 16 bit text a instruction
        bin_text = ''
        while(address_int):
            i = address_int & 1 #extract lsb
            bin_text = str(i)+bin_text #add lsb to string
            address_int = address_int >> 1 #shift to next bit

        #prepend up to 16 'bits' with '0's
        for i in range(len(bin_text),16):
            bin_text = '0'+bin_text

        return bin_text
            
    def encodeC(self,operation):
        text = '111' #all c instructions start with this
        text += self.__op[operation[1]]
        text += self.__dest[operation[0]]
        text += self.__jmp[operation[2]]
        return text

    def encodeInstruction(self,instruction):
        if instruction.instruction_type == Instruction.A_INSTRUCTION:
            return self.encodeA(instruction.payload)
        elif instruction.instruction_type == Instruction.C_INSTRUCTION:
            return self.encodeC(instruction.payload)
        #is a label so had no code.
        return None

    def encodeAll(self,instructions):
        for inst in instructions:
            binary = self.encodeInstruction(inst)
            if binary is not None:
                self.bin.append(binary)
