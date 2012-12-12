from optparse import OptionParser, OptionGroup
import logging, sys, os, random
import traci, sumolib

#looks up on ../lib to import Guilherme's implementation of Dijkstra algorithm
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
if not path in sys.path: sys.path.append(path)

from search import dijkstra

class LoadKeeper(object):
    exclude     = None
    roadNetwork = None
    drivers     = []
    outFileName = None
    
    def __init__(self, roadNetwork, outFile = None, exclude = None):
        self.roadNetwork    = roadNetwork
        self.exclude        = exclude
        self.drivers        = {}
        self.outFileName    = outFile
    
    def act(self):
        '''Must be called at each timestep. Stores the drivers that departed for 
        writing them later in an output file
        '''
        
        thisTs = traci.simulation.getCurrentTime() / 1000
        for drvid in traci.simulation.getDepartedIDList():
            if self.exclude is not None and self.exclude in drvid:
                continue
            
            drivers[drvid] = {
               'depart': thisTs,
               'route': traci.vehicle.getRoute(drvid)
            }
        
        #if len(traci.vehicle.getIDList()) >= options.numveh:
        #   continue
        
    #    print len(traci.vehicle.getIDList()), options.numveh
        
        #numInserted = 0
        for vehId in traci.simulation.getArrivedIDList():
            
            if self.exclude is not None and self.exclude in vehId:
                #print vehId, ' not replaced.'
                continue
            #assign new route to the vehicle
            congestedRoute = True
            numTries = 0
            while (congestedRoute and numTries < 100): #try to distribute load
                #if numTries > 0:
                #    print 'Congested! Retries: ', numTries
                orig = random.choice(net._edges) 
                dest = random.choice(net._edges)
                
                #print '%.2f\t%.2f' % (origOcc, destOcc)
                
                #will consider unique weight
                theRoute = dijkstra(net, orig, dest, lambda e: 300, True)
                 
                edges = [edge.getID().encode('utf-8') for edge in theRoute]
                
                #TODO: parametrize min length
                if len(edges) > 4: #at least 4 hops per trip
                    congestedRoute = False
                    for e in edges:
                        if traci.edge.getLastStepOccupancy(e) > 0.7:
                            congestedRoute = True
                            break #the inner loop
                
                numTries += 1
            
            vehId = str(thisTs) + '-' + vehId
            traci.route.add(vehId, edges)
            traci.vehicle.add(vehId, vehId, traci.vehicle.DEPART_NOW, 5.10, 0)
            
            #print '%s\t%s\t%d' % (orig.getID(), dest.getID(), traci.simulation.getCurrentTime() / 1000)
        
            #print ['%.2f' % traci.edge.getLastStepOccupancy(e) for e in edges], traci.simulation.getCurrentTime() / 1000
        
    def writeOutput(self):
        '''Writes the stored drivers into an output file
        '''
        #print 'Writing output...'
        
        if self.outFileName is None:
            print 'Error: no valid file to write.'
            return
        
        #sort drivers by departure time
        drvKeys = sorted(drivers, key=lambda x: (drivers[x]['depart'], x))
        #try:
        outfile = open(self.outFileName, 'w')
        #except TypeError:
        #    outfile = sys.stdout    
            
        outfile.write('<routes>\n')
        #for key,data in drivers.iteritems():
        #    outfile.write('    <vehicle id="%s" depart="%d">\n' % (key, data['depart']))
        #    outfile.write('        <route edges="%s" />\n' % ' '.join(data['route']))
        #    outfile.write('    </vehicle>\n')
            
        for key in drvKeys:
            outfile.write('    <vehicle id="%s" depart="%d">\n' % (key, drivers[key]['depart']))
            outfile.write('        <route edges="%s" />\n' % ' '.join(drivers[key]['route']))
            outfile.write('    </vehicle>\n')
            
        outfile.write('</routes>')
        
        #print 'Done.'        
        
        
if __name__ == '__main__':
    optParser = OptionParser()
    
    optParser.add_option("-n", "--net-file", dest="netfile",
                            help="define the net file (mandatory)")
    optParser.add_option("-r", "--route-file", dest="routefile",
                         help="route file to be generated")
    optParser.add_option("-d", "--driver-number", type="int", dest="numveh",
                         default=100, help="desired number of drivers to keep")
    optParser.add_option("-b", "--begin", type="int", default=0, help="begin time")
    optParser.add_option("-e", "--end", type="int", default=7200, help="end time")
    optParser.add_option("-p", "--port", type="int", default=8813, help="TraCI port")
    optParser.add_option("-x", "--exclude", type="string", default=None, dest='exclude',
                         help="Exclude replacing drivers whose ID have the given value")
    #optParser.add_option("-s", "--seed", type="int", help="random seed")
    
    (options, args) = optParser.parse_args()
    if not options.netfile or not options.routefile:
        optParser.print_help()
        sys.exit()
    
    net = sumolib.net.readNet(options.netfile)
    
    traci.init(options.port)
    
    drivers = {} #stores drivers information when they depart
    
    if options.begin > 0:
        print 'Skipping %d timesteps.' % options.begin
        traci.simulationStep(options.begin * 1000)
        
        for drvid in traci.simulation.getDepartedIDList():
            drivers[drvid] = {
               'depart': traci.simulation.getCurrentTime() / 1000,
               'route': traci.vehicle.getRoute(drvid)
            }
    
    print 'From ts %d to %d, will replace vehicles' % (options.begin, options.end)
    
    #creates the loadkeeper and initializes it with the drivers already recorded
    loadkeeper = LoadKeeper(net, options.routefile, options.exclude)
    loadkeeper.drivers = drivers
    
    for i in range(options.begin, options.end):
        traci.simulationStep()
        loadkeeper.act()
    
    print 'Now, simulating until all drivers leave the network'
    while (True): #simulates the remaining steps till the end
        traci.simulationStep()
        if len(traci.vehicle.getIDList()) == 0:
            break
        
    traci.close()
    
    if options.routefile:
        print 'Writing output...'
        loadkeeper.writeOutput()
        
    print 'DONE.'