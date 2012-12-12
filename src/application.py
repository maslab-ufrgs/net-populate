from optparse import OptionParser, OptionGroup
import logging, sys, os
import traci, sumolib
from emitter import EmittersParser

#looks up on ../lib to import Guilherme's implementation of Dijkstra algorithm
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
if not path in sys.path: sys.path.append(path)

from search import dijkstra

class Application(object):
    """Application object. Manages the command-line options and 
    controls the execution flow"""
    
    DEFAULT_PORT = 8813
    DEFAULT_LOG_FILE = 'netpopulate.log'
    LOGGER_NAME = 'netpopulate'
    
    cmdLineOptions = None
    port = None
    netFile = None
    network = None
    
    
    def __init__(self,argv):
        self.logger = logging.getLogger(self.LOGGER_NAME)
        (self.cmdLineOptions, args) = self.__readOptions(argv)
        self.__initOptions(self.cmdLineOptions)        
        self.logger.info('Finished parsing command line parameters.')
        
    def run(self):
        vehCount = 0
        
        emitters = EmittersParser.parse(self.cmdLineOptions.emittersInput)
        self.logger.info('Finished parsing emitters input file.')
        
        traci.init(self.port)
        #adds one-edge routes via TraCI for each emitter
        self.__addRoutes(emitters)
        self.logger.info('Finished adding routes to the simulation.')
        
        for i in range(1000):
            traci.simulationStep()
            
            for e in emitters:
                
                if e.isAllowedToCreateVehicle(i):
                    e.createVehicle(traci,str(vehCount))
                    vehCount += 1
                #TODO alternate lanes, use DEPART_NOW
                
    
        traci.close()
    
    def __addRoutes(self, emitters):
        """Adds routes to the simulation for each edge found in the emitters' list
        """
        routes = {}
        for e in emitters:
            #uses edgeId as key to ensure that no route will be inserted twice
            #if emitter is for only one edge, uses this edge as the route
            #otherwise, get the route via Dijkstra
            if not hasattr(e, "arrivalEdge"):
                routes[e.getRouteId()] = [e.departEdge]
            else:
                #tests whether a network was parsed    
                if self.network is None:
                    raise Exception("No network file supplied. Use -n or --net-file to inform the network file")
                
                #obtains the departure and arrival edges from traci and uses them to route
                
                dijkstraRoute = dijkstra(
                    self.network, 
                    self.network.getEdge(e.departEdge), 
                    self.network.getEdge(e.arrivalEdge), None, True
                ) 
                
                routes[e.getRouteId()] = [edge.getID().encode('utf-8') for edge in dijkstraRoute]
            

        #now adds the one-edge routes via traci
        for rid,route in routes.items():
            traci.route.add(rid,route)
            
                 
        
    def __readOptions(self, argv):
        """Reads and verifies command line options.
        """
        parser = OptionParser()
        self.__registerOptions(parser)
        (options, args) = parser.parse_args(argv)
        self.__checkOptions(options, args, parser)
        
        return (options, args)

    
    def __registerOptions(self, parser):
        parser.add_option(
          '-p', '--port', dest='port', type='int',
          default = self.DEFAULT_PORT,
          help = 'the port used to communicate with the TraCI server'
        )
        
        parser.add_option(
          '--emitters-input', dest='emittersInput', type='string',
          default=None, help = 'the xml file with the emitters definition'
        )
        
        parser.add_option(
          '-n','--net-file', dest='netFile', type='string',
          default=None, help = 'the .net.xml file with the network definition'
        )
        
        logging = OptionGroup(parser, 'Logging')
        logging.add_option('--log.level', dest='logLevel', default='INFO',
                           help='level of messages logged: DEBUG, INFO, '
                                'WARNING, ERROR or CRITICAL (with decreasing '
                                'levels of detail) [default: %default]')
        logging.add_option('--log.file', dest='logFile', metavar='FILE',
                           help='File to receive log output [default: ]'
                                + self.DEFAULT_LOG_FILE)
        logging.add_option('--log.stdout', dest='logStdout', 
                           action='store_true', default=True, 
                           help='Write log to the standard output stream.')
        logging.add_option('--log.stderr', dest='logStderr',
                           action='store_true', default=False,
                           help='Write log to the standard error stream.')
        parser.add_option_group(logging)
        
    def __initOptions(self, options):
        """Initializes the command-line options.
        
        All attributes initialized are directly from
        the command line options added by __registerOptions.
        """
        # Initialize logging
        if options.logStdout:
            handler = logging.StreamHandler(sys.stdout)
        elif options.logStderr:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(options.logFile or Application.DEFAULT_LOG_FILE)

        self.logger.setLevel(options.logLevel)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(module)s - %(message)s"))
        self.logger.addHandler(handler)

        # Initialize the port and road network, if a network file was supplied
        self.port = options.port or Application.DEFAULT_PORT
        if options.netFile is not None:
            # Load the edges of the network
            try:
                self.network = sumolib.net.readNet(options.netFile)
            except IOError as err:
                print 'Error reading net file:', err
                sys.exit(1)
        
        
        
    def __checkOptions(self, options, args, parser):
        if options.emittersInput == None:
            parser.error("The option '--emitters-input' is required.")

        # Only one of the logging output options may be used at a time
        if len( filter(None, (options.logFile, 
                             options.logStdout, 
                             options.logStderr)) ) > 1:
            parser.error("No more than one logging output may be given.")

        # Verify the logging level
        strLevel = options.logLevel
        options.logLevel = getattr(logging, strLevel, None)
        if not isinstance(options.logLevel, int):
            parser.error('Invalid log level: %s', strLevel)
