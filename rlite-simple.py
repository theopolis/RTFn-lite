import sys, os
import json
import re
import cherrypy

HOST = "put ip here"
DB = "var/dirty.db"
NAME_DB = "var/names.db"

BREAK_ON=5

PADS= []
NAMES= {}

def error(s):
    print s
    exit(1)

def main():
    if not os.path.exists(DB):
        error("Cannot open DB: %s" % DB)
    if not os.path.exists(NAME_DB):
        ndb = open(NAME_DB, 'w')
        ndb.write('')
        ndb.close()
    n_db = file(NAME_DB)
    pad_db = file(DB)
    for i in n_db:
        if i.find(":") > -1:
            NAMES[i.split(":")[0]] = i.split(":")[1:]
    for i in pad_db:
        obj = json.loads(i)
        #print obj["key"]
        if re.match("^pad:\w*$", obj["key"]) and not obj["key"] in PADS:
            PADS.append(obj["key"])
            
        #if re.match("^pad:\w*:revs:3", obj["key"]):
            #    print obj
            #print obj["key"]

def no_tags(e):
    return e.replace("<", "").replace(">", "")

def update_names():
    output = ""
    for n, p in NAMES.items():
        output += "%s:%s\n" % (n, ":".join(p))
    ndb = open(NAME_DB, 'w')
    ndb.write(output)
    ndb.close()

current_dir = os.path.dirname(os.path.abspath(__file__))

class RTFn(object):
    def css(self):
        return '''
            body { font-family: arial, helvetica, clean; margin:0px;}
            a, a:hover, a:visited { text-decoration: none; color: white; font-weight: bold; }
            
            .topbar {width:100%; height:20px; padding:3px; margin-bottom:10px; background-color:black;color:white;}    
            .box { background-color: grey; border: 2px solid black; max-width: 300px; float: left; padding: 5px; margin:3px; color:white; }
            .box:hover {background-color:black;}
        '''
    def js(self):
        return '''    
            function e(me) {
                me.previousSibling.previousSibling.style.display='none';
                me.nextSibling.nextSibling.style.display='inline';
                me.style.display='none';
            }
            function sub(me, e) {
                var keycode;
                if (window.event) keycode = window.event.keyCode;
                else if (e) keycode = e.which;
                else return true;
                if (keycode == 13) {
                    me.form.submit();
                    return false;
                }
                else
                    return true;
                }
            function go2Random() {
                window.location = "//%s/p/" + randomPadName();
            }

            function randomPadName() {
                var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
                var string_length = 10;
                var randomstring = '';
                for (var i = 0; i < string_length; i++)
                {
                    var rnum = Math.floor(Math.random() * chars.length);
                    randomstring += chars.substring(rnum, rnum + 1);
                }
                return randomstring;
            }
            function showme(me) {
                me.nextSibling.style.display='block';
                me.style.display='none';
            }
        ''' % HOST
        
    def index(self, loc=None):
        main()
        page = '''
            <html><head>
            <title>RTFn (eLite) Pads</title>
            <link rel="stylesheet" type="text/css" href="/css" />
            <script src="/js" type="text/javascript"></script>
            </head>
            <body>
                <div class="topbar">
                    <a href="//%s:9001">Home</a>
                    <a href="javascript:go2Random()" style="margin-left: 10px;">Create New</a>
                </div>
                <div style="float: right;">Usage:<br />
                Hit the 'e' to rename a pad.<br />
                Double click the status to change.<br />
                Click the name to start working on the pad.
                </div>
                <form method="POST" action='/submit' name="form">
        ''' % HOST
        l_ = ['','','','']
        if loc and loc.find(":9001/p") > -1:
            l_[0] = loc[loc.find(":9001/p")+8:]
            #page += l_[0]
        count = 1
        for p in PADS:
            p = p.split(":")[1]
            name = p if not p in NAMES else NAMES[p][0]
            kind = "None" if not p in NAMES else NAMES[p][1]
            status = "In progress..." if not p in NAMES else NAMES[p][2]
            style= ""#background-color:darkgreen"
            if status.find("Complete") > -1:
                style="background-color: darkgreen;"
            if p == l_[0]:
                l_[1] = "<b>"
                l_[2] = "</b>"
                l_[3] = "<div style='color:white'>You were here...</div>"
            page += '''
                <div class="box" style="%s">%s
                %s<a href="//%s:9001/p/%s">%s</a>%s
                <input type="button" onclick="javascript:e(this);" value="e" />
                <span style="display:none">
                <input type="text" name="%s" length="30" value="%s" onKeyPress="return sub(this,event);" />
                <!--<input type="submit" name="sub_%s" value="Update" />-->
                </span>
                <div ondblclick="javascript:showme(this);">%s</div><div style="display:none"><select name="%s_status">
                    <option value="In progress...">In progress...</option>
                    <option value="Very hard">Very hard</option>
                    <option value="Complete">Complete</option>
                    </select><input type=submit name="%s_go" value="Go" /></div>
                </div>
            ''' % (style, l_[3], l_[1], HOST, p, no_tags(name), l_[2], p, name, p, status, p, p)
            l_[1] = ""
            l_[2] = ""
            l_[3] = ""
            if count % BREAK_ON == 0:
                page += "<div style='clear:left'></div>"
            count += 1
        page += '''
            <br />
            <div style="clear:both"></div>
            </body></html>'''
        return page
    
    def submit(self, **vars):
        page =""
        for p in PADS:
            p = p.split(":")[1]
            if "%s" % p in vars:
                val = vars[p].replace(":", "").strip()
                if not p in NAMES:
                    val = [val, 'None', 'In progress...']
                    #val = ":".join(val)
                else:
                    val = [val, NAMES[p][1], NAMES[p][2]]
                NAMES[p] = val
                update_names()
            if "%s_go" % p in vars and "%s_status" % p in vars and vars["%s_status" % p] in ["In progress...", "Complete", "Very hard..."]:
                val = vars["%s_status" % p]
                if not p in NAMES:
                    val = [p, 'None', val]
                    #val = ":".join(val)
                else:
                    val = [NAMES[p][0], NAMES[p][1], val]
                NAMES[p] = val
                update_names()
        #page += "<div>Updated</div>"
    
        return page + self.index()
                
    index.exposed = submit.exposed = css.exposed = js.exposed = True

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cherrypy.root = RTFn()
    cherrypy.config.update({'server.environment': 'production', 'server.socketPort': 9000})
    #cherrypy.quickstart(RTFn, '/')
    cherrypy.server.start()
    
    