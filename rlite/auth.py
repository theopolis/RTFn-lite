# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
import time

SESSION_KEY = '_rtfn_u'

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def valid_user():
    return lambda: not cherrypy.request.login == None

# Controller to provide login and logout actions
class AuthController(object):
    
    def __init__(self, caller):
        self.caller = caller
    
    def check_credentials(self, username, key):
        """
        Authentication is done by key, if the key is valid, create an entry in the users table.
        This does not authenticate a returning user to their entry.
        
        username - Selected by the user, this is what they would like to be called while editing.
        key      - must match a competition key, and must be active.
        """
        c_data = self.caller.db.get_competition_from_key(key)
        if c_data["db"] is None:
            return {"error": "Invalid competition key..."}
        """If a user does not yet exist, create one"""
        u_data = self.caller.db.get_user(username)
        if u_data["db"] is None:
            u_data = self.caller.db.create_user(username)
        """If they are not yet part of this competition, add them"""
        if not self.caller.db.user_in_competition(username, key):
            self.caller.db.add_user_competition(username, key)
        admin = self.caller.db.is_admin(username)
        """Send c_data and u_data because they contain e-lite authorID, groupID"""
        return {"admin": admin, "error": None, "c_data": c_data, "u_data": u_data}
    
    def on_login(self, username, key, creds):
        """Called on successful login"""
        # Set etherpad lite's sessionID cookie
        """Send both canonical username/key for display and e-lite authorID, groupID"""
        session_response = self.caller.elite.createSession(creds["c_data"]["gid"], creds["u_data"]["uid"], int(time.time())+7800)
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = {
            "user":  (username, creds["u_data"]["uid"]), 
            "comp":   (creds["c_data"]["db"][1], creds["c_data"]["gid"]), 
            "admin": creds["admin"],
            "sessionID": session_response["data"]["sessionID"] if session_response["data"] is not None else ""
        }
    
    def on_logout(self, username):
        """Called on logout"""
        if 'sessionID' in cherrypy.response.cookie:
            cherrypy.response.cookie['sessionID']['expires'] = 0
    
    def get_loginform(self, username, msg="Enter login/registration information", from_page="/view"):
        page = "<html><head>"
        if not self.caller.header == None:
            page += self.caller.header
        page += """</head><body onload="javascript:login_form();">
        <div id="login-warning">
            Please login
        </div>
        <div id="login-modal">
            <form method="post" action="/auth/login">
            <input type="hidden" name="from_page" value="/view" />
            <div>%(msg)s</div>
            <div id="login-type">
                <div>Username:</div>
                <div id="password-type">Key:</div>
                <!--<div id="register-type">Confirm:</div>-->
            </div>
            <div id="login-box">
                <div><input type="text" name="username" value="%(username)s" /></div>
                <div id="password-box"><input type="text" name="key" /></div>
                <!--<div id="register-box"><input type="password" name="key" /></div>-->
            </div>
            <div id="login-button"><input type="submit" value="Log in" /> <!--or <input class="flip" type="button" value="Register" /></div>-->
            <!--<div id="register-button"><input type="submit" value="Register" /> or <input type="button" class="flip" value="Log in" /></div>-->
            </form>
        </div>
        """ % {"username": username, "msg": msg}
        if not self.caller.footer == None:
            page += self.caller.footer
        return page + "</body></html>"
    
    '''def get_loginform(self, username, msg="Enter login information", from_page="/"):'''
        
    
    @cherrypy.expose
    def login(self, username=None, key=None, from_page="/"):   
        import re
        """Make sure data was entered"""
        if username is None or key is None:
            return self.get_loginform("", from_page=from_page)
        """Make sure it was alpha-numeric"""
        check= re.compile("^[\w-]+$")
        if check.match(username) is None or check.match(key) is None:
            return self.get_loginform("", msg="Invalid characters in username or key", from_page=from_page)
        """Check the data they entered, at this time, just a valid key"""
        creds = self.check_credentials(username, key)
        if creds["error"] is not None:
            return self.get_loginform(username, creds["error"], from_page)
        else:
            """Will set the cookie"""
            self.on_login(username, key, creds)
            raise cherrypy.HTTPRedirect(from_page or "/")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")