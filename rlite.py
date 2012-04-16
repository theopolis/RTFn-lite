import os, json, sys
from rlite import rLite
from rlite.db import DB
from rlite.auth import AuthController, valid_user
from rlite.etherpad import EtherpadLiteClient

import cherrypy

class ViewController(object):    
    _cp_config = {
        'auth.require': [valid_user()]
    }
    
    def __init__(self, caller=None):
        self.caller = caller
        self.header = self.caller.header + """<div class="topbar">
            <a href="/view">Home</a>
            <a href="/view/create" style="margin-left: 10px;">Create New</a>
        </div>"""
        self.footer = self.caller.footer
        
    @cherrypy.expose    
    def index(self):
        # Find all competition pads
        pads_response = self.caller.elite.listPads(cherrypy.request.login["key"])
        page = ""
        
        # on error, say so
        if pads_response["message"] is not "ok":
            return self.header + """<div id="Login-warning">
                Problem listing challenges :(
            </div>""" + self.footer
        
        # otherwise, display each challenge
        for pad_id in pads_response["data"]["padIDs"]:
            page += """<div class="box">%(pad_name)s</div>
                """ % {"url": self.caller.rtfn.get("etherpad-url"), "pad_name": pad_id}
        return self.header + page + self.footer
    
    @cherrypy.expose
    def create(self, name=None):
        if name is not None:
            self.caller.elite.createGroupPad(cherrypy.request.login["key"], name, "Created by %s" % cherrypy.request.login["username"])
            return self.index()
        
        """Todo: Add a form to create a pad"""
    
    @cherrypy.expose
    def admin(self):
        """Show create comeptition page"""
        if not cherrypy.request.login["admin"]:
            return self.header + """<div id="Login-warning">
                You are not an admin :(
            </div>""" + self.footer
        """Todo: add admin panel, autheticate via static value in config, not via DB."""

class RootController(object):
    def __init__(self, db, rtfn, elite):
        self.db = db
        self.elite = elite
        self.rtfn = rtfn
    
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
        self.view = ViewController(self)
    
    @cherrypy.expose
    def index(self):
        return self.header + """<div id="login-warning">
            RTFn-lite (<a href="/view">Go!</a>)
        </div>""" + self.footer

def main():
    # Read settings used by etherpad client
    rtfn = rLite()
    
    # Start etherpad lite client
    apiKey = rtfn.api_key()
    baseUrl = rtfn.get("etherpad-url")
    print "[rlite//Debug]: Starting with api key: %s, elite hosted at: %s" % (apiKey, baseUrl)
    elite = EtherpadLiteClient(apiKey, baseUrl)
    
    # rLite's DB management hooks etherpad lite API calls
    db = DB(elite)
    
    # Start web interface
    current_dir = os.path.dirname(os.path.abspath(__file__))
    #cherrypy.root = Root
    config = {"/static": {
        #'server.environment': 'development', 
        'tools.staticdir.on': True,
        'tools.staticdir.dir': current_dir + "/static"

    }}
    cherrypy.config.update('rtfn.ini')
    # Web interface uses DB (authentication), and elite (pad lists/info)
    cherrypy.quickstart(RootController(db, rtfn, elite), "/", config=config)

if __name__ == '__main__':
    #sys.path.append('.')
    main()
