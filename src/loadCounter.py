import sys
import traci
print sys.argv[1]
traci.init(int(sys.argv[1]))

highestLane = ''
highestVeh = 0
while True:
    traci.simulationStep()
    
    #print max(traci.edge.getLastStepVehicleNumber(edgeID))
    maxLane = ''
    maxVeh = 0
    for laneID in traci.lane.getIDList():
        if traci.lane.getLastStepVehicleNumber(laneID) > maxVeh:
            maxVeh = traci.lane.getLastStepVehicleNumber(laneID) 
            maxLane = laneID
            
            if maxVeh > highestVeh:
                highestVeh = maxVeh
                highestLane = maxLane
        
    print "curr(%s): %d -- highest(%s): %d" % (maxLane, maxVeh, highestLane, highestVeh)
    