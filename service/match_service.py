from abc import ABC, abstractmethod

class MatchManager(ABC):

    def __init__(self):
        self.match = None
        
    def set_match(self, match):
        self.match = match
        self.post_init()
        
    def end_match(self):
        self.match.active = False
        
    @abstractmethod
    def post_init(self):
        pass
        
class MatchVisitTemplate(ABC):
    
    def process_visit(self, player_index, visit):
        status, message = self.validate_visit(player_index, visit)
        if status is False:
            return -1, message
        result = self.check_winning_condition(player_index,visit)
        self.record_statistics(player_index,visit,result)
        
        return result, self.format_summary(player_ndex, visit)
    
    @abstractmethod
    def validate_visit(self, player_index, visit):
        pass
        
    @abstractmethod
    def check_winning_condition(self, player_index, visit):
        pass
        
    @abstractmethod
    def record_statistics(self, player_index, visit, result):
        pass
        
    @abstractmethod
    def format_summary(self, player_index, visit):
        pass
        
    