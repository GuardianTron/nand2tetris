class JackTokenizer:

    def __init__(self,filename):
        with open(filename) as fh:
            self.__file = fh.read()
        #initialize the parser fsm
        self.fsm = {}
    