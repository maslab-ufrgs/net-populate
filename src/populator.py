from optparse import OptionParser, OptionGroup
import logging, sys, os, random
import traci, sumolib
from traci.vehicle import DEPART_NOW

#looks up on ../lib to import Guilherme's implementation of Dijkstra algorithm
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
if not path in sys.path: sys.path.append(path)

from search import dijkstra

optParser = OptionParser()

optParser.add_option("-n", "--net-file", dest="netfile",
                        help="define the net file (mandatory)")
optParser.add_option("-r", "--route-file", dest="routefile", default=sys.stdout,
                     help="generates route file with drivers created by the script")
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

traci.simulationStep(options.begin * 1000)

print traci.simulation.getCurrentTime()

drivers = {} #stores drivers information when they depart
for i in range(options.begin, options.end):
    traci.simulationStep()
    
    if len(traci.vehicle.getIDList()) >= options.numveh:
        continue
    
    #print len(traci.vehicle.getIDList()), options.numveh
    
    needToEmitt =  (2 * options.numveh) / (len(traci.vehicle.getIDList()) + 1) #+1 prevents div / 0
    #print needToEmitt
    if needToEmitt > len(net._edges):
        needToEmitt = len(net._edges)
    
    emitted = 0
    while emitted < needToEmitt:
        congestedRoute = True
        while (congestedRoute): #try to distribute load
            
            orig = random.choice(net._edges)
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
                if traci.edge.getLastStepOccupancy(e) > 0.7:
                    congestedRoute = True
                    break #the inner loop
        
        currTime = traci.simulation.getCurrentTime() / 1000
        
        #print currTime, i
        
        id = str(i) + '-' + str(emitted)
        traci.route.add(id, edges)
        traci.vehicle.add(id, id, currTime, 5.10, 0) #currTime +10 for run #13; triggered for #14
        emitted += 1
        
        #stores the added driver (run #10) 
#        drvid = id
#        drivers[drvid] = {
#           'depart': currTime, #currtime for run #11
#           'route': traci.vehicle.getRoute(drvid)
#        }
        
        #processes the departed list and fills in driver information
        #actual departed + currTime for run #12
        for drvid in traci.simulation.getDepartedIDList():
            drivers[drvid] = {
               'depart': currTime,#traci.simulation.getCurrentTime() / 1000,
               'route': traci.vehicle.getRoute(drvid)
            }
        
        
        #print '%s\t%s\t%d' % (orig.getID(), dest.getID(), traci.simulation.getCurrentTime() / 1000)
        #print ['%.2f' % traci.edge.getLastStepOccupancy(e) for e in edges], traci.simulation.getCurrentTime() / 1000
        
        
traci.close()

print 'Writing output...'
#sort drivers by departure time
drvKeys = sorted(drivers, key=lambda x: (drivers[x]['depart'], x))
try:
    outfile = open(options.routefile, 'w')
except TypeError:
    outfile = sys.stdout    
    
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

print 'Done.'