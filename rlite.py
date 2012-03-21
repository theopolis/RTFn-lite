import os, json, sys
from rlite import rLite
from rlite.db import DB
from rlite.auth import AuthController, require, valid_user

import cherrypy

MANDATORY = {
    "defaultPadText" : "",
    "requireSession" : "true",
    "editOnly" : "false",
    "minify" : "true",
    "abiword" : "null",
    #"httpAuth" : "",
    "loglevel": "WARN"
}

class ViewController(object):
    
    _cp_config = {
        'auth.require': [valid_user()]
    }
        
    @cherrypy.expose    
    def index(self):
        return """Member only area: %s""" % cherrypy.request.login

class RootController(object):
    
    def __init__(self, rtfn):
        self.rtfn = rtfn
        self.db = rtfn.db
    
        self.header = '''
            <link type='text/css' href='/static/css/basic.css' rel='stylesheet' media='screen' />
        '''
        self.footer = '''
            <script type='text/javascript' src='/static/js/jquery.js'></script>
            <script type='text/javascript' src='/static/js/jquery.simplemodal.js'></script>
            <script type='text/javascript' src='/static/js/basic.js'></script>
        '''
    
        self._cp_config = {'tools.sessions.on': True, 'tools.auth.on': True}
        
        self.auth = AuthController(self)
        self.view = ViewController()
    
    @cherrypy.expose
    def index(self):
        return """Welcome!"""

def main():
    db = DB()
    rtfn = rLite(db)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    #cherrypy.root = Root
    config = {"/static": {
        #'server.environment': 'development', 
        'tools.staticdir.on': True,
        'tools.staticdir.dir': current_dir + "/static"

    }}
    cherrypy.config.update('rtfn.ini')
    cherrypy.quickstart(RootController(rtfn), config=config)
    #cherrypy.server.start()


if __name__ == '__main__':
    #sys.path.append('.')
    main()
