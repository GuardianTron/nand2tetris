class Parser:

    def __init__(self,path):
        #load the file
        #pass exception to caller
        with open(path) as f:
            self.file = f.readlines()
    end


end