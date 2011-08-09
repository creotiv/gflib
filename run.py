#!/usr/bin/python2.6
from gevent import monkey;monkey.patch_all()
from optparse import OptionParser
from gflib.server.daemon import Server
import sys
import yaml


parser = OptionParser()

parser.add_option("-c", "--config", action="store", dest="config",
    help="YAML configuration file", type="string")
parser.add_option("-n", "--name", action="store", dest="name",
    help="YAML configuration file", type="string")
parser.add_option("-m", "--module", action="store", dest="app",
    help="Application packet", type="string")
parser.add_option("-p", "--proc", action="store", dest="proc_num",
    help="Number of processes to run", type="int", default=1)
parser.add_option("-a","--act", action="store", dest="action",
    help="Command to the daemon", type="string")
parser.add_option("--uid", action="store", dest="uid",
    help="Set user id", type="int", default=0)
parser.add_option("--gid", action="store", dest="gid",
    help="Set group id", type="int", default=0)
parser.add_option("--umask", action="store", dest="umask",
    help="Set user mask", type="int", default=0)
parser.add_option("--dir", action="store", dest="dir",
    help="Set base dir", type="string", default=None)


(options, args) = parser.parse_args(sys.argv)

if options.app:
    
    app = __import__(options.app)

    app = getattr(app,'Application')

    name = options.name

    app = app(name, options.config, root_path=options.dir)

    # Initializing the daemon
    DAEMON = Server(app, options.proc_num, uid=options.uid, gid=options.gid,
                    umask=options.umask,chdir=options.dir)

    cmd = options.action
      
    if cmd == "start":	
        print "Starting the Daemon..."
        DAEMON.start()

    elif cmd == "stop":
        print "Stopping the Daemon..."
        DAEMON.stop()
        sys.exit("Daemon stopped.")

    elif cmd == "restart":
        print "Restarting the Daemon..."
        DAEMON.restart()
        
    elif cmd == "reload":
        print "Reloading the Daemon configuration..."
        conf = options.config
        if not conf:
            conf = 'config.yaml'
        try:
            stream = file(conf, 'r')
            data = yaml.load(stream)
            stream.close()
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print "Config error at position: (%s:%s)" % (mark.line+1, mark.column+1)
            sys.exit(0)
        DAEMON.reload_config()

    elif cmd == "debug":
        DAEMON.debug()

    else:	
        sys.exit("Usage: %s --help" % sys.argv[0])

