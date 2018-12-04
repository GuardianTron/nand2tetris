
class Parser:

    def __init__(self,path):
        #load the file
        #pass exception to caller
        with open(path) as f:
            self.file = f.readlines()
        #initialize the tracking of instruction numbers
        self.instruction_number=0
        #used for keeping track of the line being parsed
        self.line_number=0
        self.processed = []
    
    def parseLine(self):
        self.line = self.file[self.line_number]
        self.line_number+=1
         #strip comments
        self.stripWhiteSpace()
        comment = self.line.find("//")
        if comment==0: #whole line is a comment so skip
            return
        elif comment > 0:
            #remove comment
            self.line = self.line[0:comment]
        
        self.stripWhiteSpace()
        if len(self.line)==0:    # line is empty
            return
        #save processed file for debugging
        self.processed.append(self.line)
        

    def parse(self):
        while self.line_number < len(self.file):
            self.parseLine()


    def stripWhiteSpace(self):
        self.line = self.line.replace('\n','').replace('\r','').strip()
