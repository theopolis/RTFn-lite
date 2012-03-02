import os, json, sys
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

def error(s):
    print s
    exit(1)

class RTFn(object):
    def __init__(self, db):
        self.__db = db
        self.read_settings()
        
    def read_settings(self):
        global MANDATORY
        settings = {}
        """We use the same json-type configuration file as etherpad-lite"""
        if not os.path.exists("settings.json"):
            error("Cannot find settings.json")
        try:
            settings = json.load(open("settings.json", 'r'))
        except:
            error("Cannot parse settings.json")
        self.__settings = settings

        """Merge settings with etherpad's"""
        if not os.path.exists("%s/settings.json" % self.__settings["etherpad-dir"]):
            if not os.path.exists("%s/settings.json.template" % self.__settings["etherpad-dir"]):
                error("Cannot find settings.json or settings.json.template in etherpad-dir: %s" % self.__settings["etherpad-dir"])
            try:
                #elite_settings = json.load(open("%s/settings.json.template" % self.__settings["etherpad-dir"], 'r'))
                elite_settings = MANDATORY
                for key, value in self.__settings["etherpad"].items():
                    elite_settings[key] = value
                json.dump(elite_settings, open("%s/settings.json" % self.__settings["etherpad-dir"], 'w'))
            except Exception as e:
                error("Cannot parse/save etherpad settings: %s" % e)
        else:
            elite_settings = json.load(open("%s/settings.json" % self.__settings["etherpad-dir"], 'r'))
        del self.__settings["etherpad"]
        self.__elite_settings = elite_settings
        
    def create_pad(self, group):
        pass
    
    def create_user(self):
        pass
    
    def create_competition(self, name, key):
        pass
    
    def add_user_group(self):
        pass

    def print_settings(self):
        print self.__settings
        print self.__elite_settings

class ViewController(object):
    
    _cp_config = {
        'auth.require': [valid_user()]
    }
        
    @cherrypy.expose    
    def index(self):
        return """Member only area: %s""" % cherrypy.request.login

class RootController(object):
    
    _cp_config = {'tools.sessions.on': True, 'tools.auth.on': True}
    
    auth = AuthController()
    view = ViewController()
    
    @cherrypy.expose
    def index(self):
        return """Welcome!"""

def main():
    db = DB()
    rtfn = RTFn(db)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    #cherrypy.root = Root
    #cherrypy.config.update({'server.environment': 'development', 'server.socketPort': 9000})
    cherrypy.quickstart(RootController())
    #cherrypy.server.start()


if __name__ == '__main__':
    #sys.path.append('.')
    main()
