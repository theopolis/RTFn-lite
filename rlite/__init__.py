import os, json

def error(s):
    print s
    exit(1)

class rLite(object):
    def __init__(self, db):
        self.db = db
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