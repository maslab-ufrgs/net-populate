import sys

class Emitter(object):
    """Emitter object. Associated with a lane, creates vehicles regularly
    in order to keep it occupied"""
    
    laneId = None
    laneNo = 0
    startTime = 0
    endTime = 0
    emissionInterval = 0
    currentLane = 0
    numLanes = 0
    departEdge = None
    #traciClient = None
    
    def __init__(self, laneId=None, startTime=0, endTime=0, emissionInterval=0):
        if laneId is None:
            raise Exception("Lane ID cannot be null.");
        
        if emissionInterval <= 0:
            raise Exception("Emission interval must be positive. Given: %d" % emissionInterval)
        
        self.laneId         = laneId
        self.startTime      = int(startTime)
        self.endTime        = endTime if endTime > 0 else sys.maxint
        self.emissionInterval = int(emissionInterval)
        
        #calculates the number of the lane on the edge and the street name
        #lane number is the number after the last _ on it's id
        #edge name is the part before the last _
        self.laneNo = self.laneId[self.laneId.rfind('_')+1:]
        self.departEdge = self.laneId[:self.laneId.rfind('_')]
        
    def createVehicle(self,traciClient,vehId):
        """Adds a vehicle to the simulation via TraCI.
        """
         
        #if departEdge is not set, queries the simulator for it
        #if(self.departEdge is None):
        #    self.departEdge=traciClient.lane.getEdgeID(self.laneId)
        
        traciClient.vehicle.add(
            vehId, self.getRouteId(),traciClient.vehicle.DEPART_NOW, 
            pos=0, speed=3, lane=int(self.laneNo)
        )
        
        
    def isAllowedToCreateVehicle(self, currentTimestep):
        """Returns whether it is time for this emitter to create a new vehicle.
        It will return true when currentTimestep is between start/end times and 
        emission interval has passed
        """
        return (
            self.startTime <= currentTimestep 
            and currentTimestep <= self.endTime
            and ((currentTimestep - self.startTime) % self.emissionInterval == 0)
        )
        
    def getRouteId(self):
        """Returns the ID of the route related to this emitter -- EMT_[DepartEdgeID]"""
        return "EMT_" + self.departEdge
        
            
        
        
        
class RoutedEmitter(Emitter):
    """Routed vehicles emitter object. Associated with a lane and a 
    destination edge, creates vehicles regularly
    in order to keep the route occupied"""
    
    arrivalEdge = None
    
    def __init__(self, laneId=None, arrivalEdge=None, startTime=0, endTime=0, emissionInterval=0):
        Emitter.__init__(self,laneId,startTime,endTime,emissionInterval)
        if arrivalEdge is None:
            raise Exception("Arrival Edge ID cannot be null.")        
        #TODO calculate a route and add it via TRACI if needed
        #use EMT_from_to to identify emitter routes and avoid doubles
        self.arrivalEdge = arrivalEdge
        
        
    def createVehicle(self,traciClient,vehId):
        """Adds a vehicle to the simulation via TraCI. Assumes that
        a route identified by EMT_[DepartEdgeID]_[ArrivalEdgeID] exists 
        in the simulation.
        """
         
        #if departEdge is not set, queries the simulator for it
        if(self.departEdge is None):
            self.departEdge=traciClient.lane.getEdgeID(self.laneId)
        
        
        traciClient.vehicle.add(
            vehId, self.getRouteId(),traciClient.vehicle.DEPART_NOW, 
            pos=0, speed=3, lane=int(self.laneNo)
        )     
        
    def getRouteId(self):
        """Returns the ID of the route related to this emitter 
        which is EMT_[DepartEdgeID]-[ArrivalEdgeID]"""
        return "EMT_" + self.departEdge + "-" + self.arrivalEdge
        
import xml.etree.ElementTree as ET
        
class EmittersParser(object):
    """Parses the emitters input file. Each emitter is associated with a LANE
    In order to the emitters to work properly, SUMO default name convention must
    be used in the network file: if an edge ID is 'THE_EDGE_ID' the lanes ID's will
    be named 'THE_EDGE_ID_x' where x ranges from 0 to num_lanes - 1"""
    
    @staticmethod
    def parse(inputFile):
        """Parses the emitters input file, creating a list of emitters"""
        tree = ET.parse(inputFile)
        root = tree.getroot();
        emitters = []
        for element in root:
            #creates a single-edge vehicle emitter or a routed vehicle emitter
            #depending on the 'arrivalEdge' attribute
            if element.get('arrivalEdge') is None:
                emitter = Emitter(
                    element.get('laneId'), 
                    element.get('start', 0),
                    element.get('end', 0),
                    element.get('interval')
                )
                
            else:
                emitter = RoutedEmitter(
                    element.get('laneId'), 
                    element.get('arrivalEdge'),
                    element.get('start', 0),
                    element.get('end',0),
                    element.get('interval')
                )
            emitters.append(emitter)
        
        return emitters
        
        
    