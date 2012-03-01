import os, json, sys

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

def install_etherpad():
    pass	

def setup():
    """1. Check if etherpad exists, if not prompt user	
	   2. Edit settings file for etherpad
	   3. Roll with it!"""
    if not os.path.exists('etherpad-lite'):
        install_etherpad()

def main():
    rtfn = RTFn()
    rtfn.read_settings()
    rtfn.print_settings()
    #from auth import *
    from rlite.db import DB
    db = DB()
    db.create_tables()

if __name__ == '__main__':
    #sys.path.append('.')
    main()
