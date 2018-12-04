
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
        #holds processed instructions
        #instructions are stored in tuples as (type,instructions)
        #C-instuctions are further broken down into a sub tuple
        #(destination, operation, jump)
        self.processed = []

    
    #returns the current instruction
    @property 
    def current_instruction(self):
        return self.processed[len(self.processed)-1][1]

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
            instruction = self.parseC()


       
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

    #break c instructions into components and return tuple
    #(destination, operation,jump)
    #if field is missing, it will be filled
    #with a null string
    def parseC(self):
        destination = ''
        operation = ''
        jump = ''

        #destination only present if equal sign present
        splitup = self.line.split("=")
        if len(splitup) == 2:
            destination = splitup[0]
            splitup = splitup[1]
        else:
            splitup = splitup[0]
        
        #jump present only if ; present
        splitup = splitup.split(";")
        operation = splitup[0]
        if len(splitup) == 2:
            jump = splitup[1]
        
        #return tuple
        return (destination,operation,jump)
        