class BinaryEncoder:

    def __init__(self):
        
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
            


