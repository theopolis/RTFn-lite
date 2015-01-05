# INSTALL / RUN

* __Either__ download Etherpad-lite (as a submodule?):

    ```bash
$ git submodule init
$ git submodule update
    ```

* __Or__ instead of using the submodule, download Etherpad-lite to a directory that RTFn will have read/write access:

    ```bash
$ git clone https://github.com/ether/etherpad-lite.git etherpad-lite
    ```

* Install Python/Cherrypy (>3.2.0), e.g.:
    ```bash
$ apt-get install python-cherrypy3 
    ```
or
	```bash
$ pip install "CherryPy>=3.2.0"
	```

* Configure `settings.json` (copy [`settings.json.template`](https://github.com/theopolis/RTFn-lite/blob/master/settings.json.template) to `settings.json`). 
By default you only need to change the "`password`" setting.

* Create your first RTFn-lite competition. This will setup the database and copy settings from RTFn-lite to Etherpad-Lite.

    ```bash
$ python ./rlite.py --add <competition name> --key <access key>
    ```

* [Follow the directions to install Etherpad-Lite's dependencies](https://github.com/ether/etherpad-lite).

* _(Optional)_ [Install Etherpad-Lite as a service](https://github.com/ether/etherpad-lite/wiki/How-to-deploy-Etherpad-Lite-as-a-service).

* [Setup Apache to proxy Etherpad-Lite](https://github.com/ether/etherpad-lite/wiki/How-to-put-Etherpad-Lite-behind-a-reverse-Proxy). Right now RTFn-Lite expects this configuration for SSL support. Use `127.0.0.0.1` for the host.

* Start RTFn-Lite!

    ```bash
$ python ./rlite.py
    ```

##TODO

* Add two main threads
	* Webserver thread
	* Interactive competition creation
* User area, display competition access
* Remove 'admin' status
