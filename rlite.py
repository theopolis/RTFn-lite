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
        self.header = self.caller.header + """<body onload="javascript: pad_list(); "><div class="topbar">
            <div class="main">
            <a href="/view">Home</a>
            <a id="create-challenge" style="margin-left: 10px;">Create New</a>
            |
            <a href="/auth/logout">Logout</a>
            </div>
            <div id="actions" class="actions">
            <a id="upload-file">Upload</a>
            |
            <a id="show-files">Show Files</a>
            </div>
            <div class="clear"></div>
            
            <div id="create-modal">
                <form method="post" action="/view/create">
                <div>In the form of ^[\w]+$ please.</div>
                <input type="hidden" name="from_page" value="/view" />
                <div id="login-type">
                    <div>Challenge Name:</div>
                </div>
                <div id="login-box">
                    <div><input type="text" name="name" /></div>
                </div>
                <div id="login-button"><input type="submit" value="Create" /></div>
                </form>
            </div>
            
            <div id="upload-modal">
                <form method="post" enctype="multipart/form-data" action="/view/upload">
                <div>Select file to upload:</div>
                <input type="hidden" name="from_page" value="/view" />
                <div>Upload location: <span id="upload-location"> </span></div>
                <input type="hidden" id="upload-location-data" name="location" value="" />
                <input type="file" name="file" value="" />
                <div id="login-button"><input type="submit" value="Upload" /></div>
                </form>
            </div>
            
            <div id="files-modal">
                <iframe id="files-frame" src="" frameborder=""></iframe>
            </div>
            
        </div>"""
        self.footer = "</body>" + self.caller.footer
        
    @cherrypy.expose    
    def index(self, name=None, from_page="/view"):
        """Set etherpad cookie if none found"""
        cookies = cherrypy.request.cookie
        if "sessionID" not in cookies.keys():
            cherrypy.response.cookie["sessionID"] = cherrypy.request.login["sessionID"]
            cherrypy.response.cookie["sessionID"]["path"] = "/"
        
        if name is not None:
            self.create(name)
        # Find all competition pads
        pads_response = self.caller.elite.listPads(cherrypy.request.login["comp"][1])
        page = ""
        
        # on error, say so
        if pads_response["data"] is None:
            return self.header + """<div id="Login-warning">
                Problem listing challenges :(
            </div>""" + self.footer
        
        # otherwise, display each challenge
        for pad_id in pads_response["data"]["padIDs"]:
            page += self.print_pad(pad_id)
        page += """
            <div id="delete-modal">
                <form method="post" action="/view/delete">
                <div>Are you sure you want to delete: </div>
                <div id="delete-pad-name"> </div>
                <input type="hidden" name="from_page" value="/view" />
                <input type="hidden" id="delete-pad-input" name="name" value="" />
                <div id="login-button"><input type="submit" value="Delete" /></div>
                </form>
            </div>
        """
        return self.header + page + self.footer

    @cherrypy.expose
    def files(self, id=None):
        if id is None:
            return "No files found (no id)..."
        
        dir_name = id
        if not id == "main":
            pads_response = self.caller.elite.listPads(cherrypy.request.login["comp"][1])
            pad_name = ""
            for pad in pads_response["data"]["padIDs"]:
                if id == pad:
                    pad_name = pad.split("$")[1]
            if pad_name is "":
                return "No files found (bad id)..."
            dir_name = pad_name
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_path = os.path.abspath(os.path.join(current_dir, "static/uploads", dir_name))
        if not os.path.exists(upload_path):
            return "No files found (no dir)..."
        
        page = ""
        for file in os.listdir(upload_path):
            page += """<div><a href="/static/uploads/%(dir)s/%(file)s" target="_blank">%(file)s</a></div>""" % {"dir": dir_name, "file": file}
        return page
            
    
    @cherrypy.expose
    def upload(self, location=None, file=None, from_page="/view"):
        """Uploaded a file to ./static, expecting current_dir var set in main"""
        if file is None or file.file is None:
            return self.index()
        
        print "uploading:", location, file.filename
        """If we are trying to save to a specific pad, check to make sure that pad exists"""
        dir_name = location
        if not location == "main":
            print "uploading:", "searching for pad"
            pads_response = self.caller.elite.listPads(cherrypy.request.login["comp"][1])
            pad_name = ""
            for pad in pads_response["data"]["padIDs"]:
                if location == pad:
                    pad_name = pad.split("$")[1]
            if pad_name is "":
                return self.index()
            """Pad name was found, set the real location"""
            print "location:", pad_name
            dir_name = pad_name
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_path = os.path.abspath(os.path.join(current_dir, "static/uploads"))
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)
        loc_path = os.path.abspath(os.path.join(upload_path, dir_name))
        if not os.path.exists(loc_path):
            os.mkdir(loc_path)
        
        fp = os.open(os.path.join(loc_path, file.filename), os.O_CREAT | os.O_WRONLY)
        while True:
            data = file.file.read(4096)
            if not data:
                os.close(fp)
                break
            os.write(fp, data)
        raise cherrypy.HTTPRedirect('/view' if location =="main" else '/view/pad/?id=%s' % location)

    @cherrypy.expose
    def create(self, name, from_page="/view"):
        import re
        if name is not None and re.match("^[\w]+$", name) is not None:
            self.caller.elite.createGroupPad(cherrypy.request.login["comp"][1], name, "Created by %s" % cherrypy.request.login["user"][0])
        raise cherrypy.HTTPRedirect('/view')
        pass
    
    @cherrypy.expose
    def pad(self, id):
        """id - pad id with groupID"""
        page = """
            <iframe src="%(url)s/p/%(pad_id)s" frameborder="0" style="width: 100%%; height:100%%"></iframe>
        """ % {"url": self.caller.rtfn.get("etherpad-url"), "pad_id": id}
        return self.header % {"comp": cherrypy.request.login["comp"][0]} + page + self.footer
    
    def print_pad(self, pad_id):
        pad_display = """
            <div class="box">
                <a href="/view/pad?id=%(pad_id)s">%(pad_name)s</a>
                <div class="delete" onclick="javascript:delete_pad({'%(pad_name)s':'%(pad_id)s'}); "> </div>
                <div class="solve"> </div>
                <div class="move"> </div>
            </div>
        """ % {
            "pad_id": pad_id,
            "url": self.caller.rtfn.get("etherpad-url"), 
            "pad_name": pad_id.split("$")[1]
        }
        return pad_display
        pass
    
    @cherrypy.expose
    def delete(self, name=None, from_page="/view"):
        """Removes pad name"""
        if name is not None and cherrypy.request.login["admin"]:
            self.caller.elite.deletePad(name)
        raise cherrypy.HTTPRedirect('/view')
    
    
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
