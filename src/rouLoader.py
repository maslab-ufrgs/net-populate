from optparse import OptionParser, OptionGroup
import logging, sys, os, random
import xml.etree.ElementTree as ET
import traci, sumolib
from traci.vehicle import DEPART_NOW

#looks up on ../lib to import Guilherme's implementation of Dijkstra algorithm
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
if not path in sys.path: sys.path.append(path)

from search import dijkstra

optParser = OptionParser()

optParser.add_option("-n", "--net-file", dest="netfile",
                        help="define the net file (mandatory)")
optParser.add_option("-o", "--output-trip-file", dest="tripfile",
                     default="trips.trips.xml", help="define the output trip filename")
optParser.add_option("-r", "--route-file", dest="routefile", default=sys.stdout,
                     help="generates route file with drivers created by the script")
optParser.add_option("-d", "--driver-number", type="int", dest="numveh",
                     default=100, help="desired number of drivers to keep")
optParser.add_option("-b", "--begin", type="int", default=0, help="begin time")
optParser.add_option("-e", "--end", type="int", default=7200, help="end time")
optParser.add_option("-p", "--port", type="int", default=8813, help="TraCI port")

(options, args) = optParser.parse_args()
if not options.netfile:
    optParser.print_help()
    sys.exit()

tree = ET.parse(options.routefile)
root = tree.getroot()

traci.init(options.port)

drivers = []

#loads all drivers then performs the steps
for element in root:
    for route in element:
        edgeList = route.get('edges').split(" ")

    traci.route.add(element.get('id'), edgeList)
    traci.vehicle.add(
        element.get('id'), 
        element.get('id'), 
        int(element.get('depart')), 
        5.10, 
        0
    )
#for i in range(0, options.end):
traci.simulationStep(options.end * 1000)
    
traci.close()