from abc import ABC

class ParserMachine:

    def __init__(self):
        self.__fsm = {}
        self.__cur = ""
        self.__state_change = False

        self.__token_type = ""
        self.__token = ""

    def register_state(self,label,state,cur_state = False):
        self.__fsm[label] = state
        state.fsm = self
        if cur_state:
            self.__cur = label


    def consume(self,character):
        #reset change state flage to see if the state has changed
        #change state method will be called by sate 
        #and set flag to true
        self.__state_change = False
        self.__fsm[self.__cur].process(character)
        return self.__state_change

    def change_state(self,label,character)

        #save token information for caller
        state = self.__fsm[self.__cur]
        self.__token_type = state.get_type()
        self.__token = state.token

        #change state
        state.exit()
        self.__state_change = True
        self.__cur = label
        self.__fsm[self.__cur].enter(character)
    
    
    @property 
    def type(self):
        return self.__token_type

    @property 
    def token(self):
        return self.__token



class ParserState(ABC):

    def __init__(self):
        self.token = ""
        self.fsm = None
        

    def enter(self,character=""):
        self.token = character

    @abstractmethod
    def process(self,character):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def get_type(self):
        pass


class WhiteSpaceState(ParserState):

    def process(self,character):
        assert fsm != None
        




    

