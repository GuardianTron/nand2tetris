
class Parser:

    IGNORE = -1
    LABEL = 0
    A_INSTRUCTION = 1
    C_INSTRUCTION = 2

    def __init__(self,path):
        #load the file
        #pass exception to caller
        with open(path) as f:
            self.file = f.readlines()
       
        #used for keeping track of the line being parsed
        self.line_number=0
        self.processed = []

    
    #returns the address of the last instruction processed
    @property
    def current_address(self):
        return len(self.processed) - 1

    
    #returns the current instruction
    @property 
    def current_instruction(self):
        return self.processed[self.current_address][1]

    #returns true if the file has been fully processed
    @property
    def complete(self):
        return len(self.file) == self.line_number
    
    #parse the line and return the type of instruction found
    def parseLine(self):
        self.line = self.file[self.line_number]
        self.line_number+=1

         #strip comments
        
        if self.stripComments() == 0:
             return Parser.IGNORE

        #return the type of command found
        #also parse it
        if self.line[0] == '(':
            instruction_type = Parser.LABEL
            instruction = self.line.replace('(','').replace(')','')
        elif self.line[0] == '@':
            instruction_type = Parser.A_INSTRUCTION
            instruction = self.line[1:]
        else:
            instruction_type = Parser.C_INSTRUCTION
            instruction = self.line


       
        #save processed file for debugging
        self.processed.append((instruction_type,instruction))

        return instruction_type


    def parse(self):
        while self.line_number < len(self.file):
            self.parseLine()


    def stripWhiteSpace(self):
        self.line = self.line.replace('\n','').replace('\r','').strip()

    #returns length command string left after comments and white space
    #are removed.
    def stripComments(self):
        self.stripWhiteSpace()
        comment = self.line.find("//")
        if comment==0: #whole line is a comment so skip
            return 0
        elif comment > 0:
            #remove comment
            self.line = self.line[0:comment]
        
        self.stripWhiteSpace()
        return len(self.line)
        
