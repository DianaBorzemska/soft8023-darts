import logging 
import time
from concurrent import futures

import grpc

from app.gameimpl import x01_match
from darts_match_pb2 import VisitResponse, RegisterResponse, FinalizeResponse, MatchResponse, WatchResponse, Player, Dart
from darts_match_pb2_grpc import DartsMatchServicer, add_DartsMatchServicer_to_server
from server.registry import MatchRegistry
from domain import darts_match, visit
from pattern import object_factory

class DartServer(DartsMatchServicer):

    def __init__(self):
        self.match_type = "X01"
        self.factory = object_factory.ObjectFactory()
        self.factory.register_builder('X01', x01_match.X01MatchBuilder())
        self.registry = MatchRegistry.get_instance()

    def ProcessVisit(self,request, context):
        print("in 'visit' for: "+str(request.matchId))
        my_visit = visit.Visit(request.visit)
        match = self.registry.get_match(request.matchId)
        result, response = match.process_visit(request.playerIndex,my_visit)
        return VisitResponse(result=result, message=response)

    def RegisterPlayer(self,request,context):
        print("in register player")
        match = self.registry.get_match(request.matchId)
        player_index = match.match.register_player(request.userName)
        print(match.match.players)
        return RegisterResponse(playerIndex=player_index)
    
    def FinalizeMatch(self, request, context):
        print("in finalize")
        self.registry.get_match(request.matchId).finalize_setup()
        return FinalizeResponse()

    def CreateMatch(self,request, context):
        print("in create match")
        new_match = self.factory.create(request.matchType)
        match = darts_match.DartsMatch()
        match.register_player(request.userName)
        new_match.set_match(match)
        match_id = self.registry.add_match(new_match)
        print("Created match: "+ str(match_id.bytes))
        return MatchResponse(matchId=match_id.bytes)
    
    def WatchMatch(self, request, context):
        my_uuid = list(MatchRegistry.get_instance().matches.keys())[0].bytes
        match = self.registry.get_match(my_uuid)

        v = 0
        for v in range(0, len(match.match.visits[0])):
            for p in range(0, len(match.match.players)):
                while len(match.match.visits[p]) < len(match.match.visits[0]):
                    time.sleep(1)
                my_visit = match.match.visits[p][v]
                yield WatchResponse(player=Player(userName=match.match.players[p],playerIndex=p),
                darts=[Dart(multiplier=my_visit.darts[0].multiplier, segment=my_visit.darts[0].segment), 
                Dart(multiplier=my_visit.darts[1].multiplier, segment=my_visit.darts[1].segment),
                Dart(multiplier=my_visit.darts[2].multiplier, segment=my_visit.darts[2].segment)], score =0)

        while True:
            if len(match.match.visits[0]) > v + 1:
                y = len(match.match.visits[0])
                for x in range(v+1, y):
                    for p in range(0, len(match.match.players)):
                        while len(match.match.visits[p]) < y:
                            time.sleep(1)
                        yield WatchResponse(player=Player(userName=match.match.players[p], playerIndex=p),
                        darts=[Dart(multiplier=match.match.visits[p][x].darts[0].multiplier,
                        segment=match.match.visits[p][x].darts[0].segment),
                        Dart(multiplier=match.match.visits[p][x].darts[1].multiplier,
                        segment=match.match.visits[p][x].darts[1].segment),
                        Dart(multiplier=match.match.visits[p][x].darts[2].multiplier,
                        segment=match.match.visits[p][x].darts[2].segment)],score=0)
                v=y-1
            time.sleep(1)

def serve():
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DartsMatchServicer_to_server(DartServer(),server)
    server.add_insecure_port('[::]:50055')
    server.start()
    server.wait_for_termination()

if __name__=='__main__':
    logging.basicConfig()
    serve()

                


