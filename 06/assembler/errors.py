class SyntaxError(Exception):

    def __init__(self,line_number,line,message=""):
        self.line = line
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return "%d: %s -- %s"%(self.line_number,self.line,self.message)