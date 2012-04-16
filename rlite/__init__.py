import os, json

def error(s):
    print s
    exit(1)

class rLite(object):
    MANDATORY = {
        "defaultPadText" : "",
        "requireSession" : "true",
        "editOnly" : "false",
        "minify" : "true",
        "abiword" : "null",
        #"httpAuth" : "",
        "loglevel": "WARN"
    }     
    def __init__(self):
        self.read_settings()
        
    def read_settings(self):
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
                elite_settings = self.MANDATORY
                for key, value in self.__settings["etherpad"].items():
                    elite_settings[key] = value
                json.dump(elite_settings, open(os.path.join(self.__settings["etherpad-dir"], "settings.json"), 'w'))
            except Exception as e:
                error("Cannot parse/save etherpad settings: %s" % e)
        else:
            print os.path.join(self.__settings["etherpad-dir"], "settings.json")
            elite_settings = {}
            try:
                elite_settings = json.load(open(os.path.join(self.__settings["etherpad-dir"], "settings.json"), 'r'))
            except:
                pass
        del self.__settings["etherpad"]
        self.__elite_settings = elite_settings
        
    def api_key(self):
        """Read and return the etherpad lite API key"""
        api_name = os.path.join(self.__settings["etherpad-dir"], "APIKEY.txt")
        if not os.path.exists(api_name):
            return False
        api_fp = os.open(api_name, os.O_RDONLY)
        return os.read(api_fp, 128)
    
    def get(self, setting):
        return self.__settings[setting] if setting in self.__settings.keys() else None

    def print_settings(self):
        print self.__settings
        print self.__elite_settings