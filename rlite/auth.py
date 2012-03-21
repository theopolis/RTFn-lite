# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy

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

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check

def valid_user():
    return lambda: not cherrypy.request.login == None

# Controller to provide login and logout actions

class AuthController(object):
    
    def __init__(self, caller):
        self.caller = caller
    
    def check_credentials(self, username, key):
        """Verifies credentials for username and password.
        Returns None on success or a string describing the error on failure"""
        # Adapt to your needs
        c_id = self.caller.db.get_competition_from_key(key)
        if c_id is None:
            return "Invalid competition key..."
        u_id = self.caller.db.get_user(username)
        if u_id is None:
            u_id = self.caller.db.create_user(username)
        if not self.caller.db.user_in_competition(u_id[0], c_id[0]):
            self.caller.db.add_user_competition(u_id[0], c_id[0])
        return False
    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, msg="Enter login/registration information", from_page="/"):
        page = "<html><head>"
        if not self.caller.header == None:
            page += self.caller.header
        page += """</head><body onload="javascript:login_form();">
        <div id="login-warning">
            Please login
        </div>
        <div id="login-modal">
            <form method="post" action="/auth/login">
            <input type="hidden" name="from_page" value="%(from_page)s" />
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
        """ % locals()
        if not self.caller.footer == None:
            page += self.caller.footer
        return page + "</body></html>"
    
    '''def get_loginform(self, username, msg="Enter login information", from_page="/"):'''
        
    
    @cherrypy.expose
    def login(self, username=None, key=None, from_page="/"):          
        if username is None or key is None:
            return self.get_loginform("", from_page=from_page)
        
        ''''if key is not None:
            result = self.caller.db.get_competition_from_key(key)
            if result is None:
                error_msg = "Invalid registration key..."'''

        error_msg = self.check_credentials(username, key)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
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