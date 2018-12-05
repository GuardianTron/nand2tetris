from parser import Instruction
class BinaryEncoder:

    def __init__(self,symbol_table):

        #set up array to hold binary values
        self.bin = []

        #holds symbols
        self.__symbols = symbol_table

        #contains memory address for next
        #user defined symbol
        #@todo...add core to ensure that address 
        #does not go above RAM limit
        self.__mem_address = 16

        #max ram address 
        self.__max_address = 16383
        
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

    def __getAddressInteger(self,address):
         #if user defined symbol, 
        #replace with memory address
        if not address.isdigit():
            #add new symbol if not already present
            if address not in self.__symbols:

                #rais error is memory address larger than data ram
                if self.__mem_address >= self.__max_address:
                    raise Exception("Maximum data ram limit reached")
                self.__symbols[address] = str(self.__mem_address)
                self.__mem_address += 1
            #translate symbol
            address = self.__symbols[address]

        return int(address)


    def encodeA(self,address):

        
        address_int = self.__getAddressInteger(address)
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
                
class SymbolTable:

    def __init__(self):
        #predefined symbols
        self.table ={
            'SP':'0',
            'LCL':'1',
            'ARG':'2',
            'THIS':'3',
            'THAT':'4',
            'SCREEN':'16384',
            'KBD':'24576'
        }

        #add R0-R15
        for i in range(0,16):
            self.table["R%d"%(i)]=i
    
