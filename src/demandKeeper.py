from optparse import OptionParser, OptionGroup
import logging, sys, os, random
import traci, sumolib

#looks up on ../lib to import Guilherme's implementation of Dijkstra algorithm
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
if not path in sys.path: sys.path.append(path)

from search import dijkstra

optParser = OptionParser()

optParser.add_option("-n", "--net-file", dest="netfile",
                        help="define the net file (mandatory)")
optParser.add_option("-o", "--output-trip-file", dest="tripfile",
                     default="trips.trips.xml", help="define the output trip filename")
optParser.add_option("-r", "--route-file", dest="routefile",
                     help="generates route file with duarouter")
optParser.add_option("-d", "--driver-number", type="int", dest="numveh",
                     default=100, help="desired number of drivers to keep")
optParser.add_option("-b", "--begin", type="int", default=0, help="begin time")
optParser.add_option("-e", "--end", type="int", default=7200, help="end time")
optParser.add_option("-p", "--port", type="int", default=8813, help="TraCI port")
#optParser.add_option("-s", "--seed", type="int", help="random seed")
optParser.add_option("-l", "--length", action="store_true",
                     default=False, help="weight edge probability by length")
optParser.add_option("-L", "--lanes", action="store_true",
                     default=False, help="weight edge probability by number of lanes")

(options, args) = optParser.parse_args()
if not options.netfile:
    optParser.print_help()
    sys.exit()

net = sumolib.net.readNet(options.netfile)

traci.init(options.port)

#if options.begin > 0:
#    traci.simulationStep(options.begin * 1000)

for i in range(options.begin, options.end):
    traci.simulationStep()
    
    #if len(traci.vehicle.getIDList()) >= options.numveh:
     #   continue
    
    #print len(traci.vehicle.getIDList()), options.numveh
    
    #numInserted = 0
    for vehId in traci.vehicle.getIDList():
        vehLane = traci.vehicle.getLaneID(vehId)
        
        edgeId = vehLane[:vehLane.rfind('_')]
        
        #if vehicle is not on dest. edge, move on
        if  edgeId != traci.vehicle.getRoute(vehId)[-1]: 
            continue
        
        #else, assign new route to the vehicle
        congestedRoute = True
        numTries = 0
        while (congestedRoute and numTries < 10): #try to distribute load
            if numTries > 0:
                print 'Congested! Retries: ', numTries
            orig = net.getEdge(edgeId) 
            dest = random.choice(net._edges)
            
            #print '%.2f\t%.2f' % (origOcc, destOcc)
            
            theRoute = dijkstra(
                net, 
                orig, 
                dest, None, True
            ) 
            edges = [edge.getID().encode('utf-8') for edge in theRoute]
            
            congestedRoute = False
            for e in edges:
                if traci.edge.getLastStepOccupancy(e) > 0.8:
                    congestedRoute = True
                    break #the inner loop
            
            numTries += 1
        
        traci.vehicle.setRoute(vehId, edges)# add(id, id)
        print '%s\t%s\t%d' % (orig.getID(), dest.getID(), traci.simulation.getCurrentTime() / 1000)
    
        #print ['%.2f' % traci.edge.getLastStepOccupancy(e) for e in edges], traci.simulation.getCurrentTime() / 1000
        
        
traci.close()

        