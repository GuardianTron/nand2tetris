class BinaryEncoder:

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
            


