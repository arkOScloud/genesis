#!/usr/bin/env python2

import base64
import ConfigParser
import glob
import json
import nginx
import os
import re
import shutil
import tarfile
import urllib2

def start():
	print "====================================="
	print "arkOS Genesis 0.6 Migration Script"
	print "====================================="
	print ""
	print "This script will help you transition to the new Genesis 0.6 from an existing installation."
	print "It makes no warranties as to the state or accuracy of your installation after the migration, as the best way is to run a fresh install."
	print "Please press any key to begin, or Ctrl+C to quit."
	raw_input()

def sitedata():
	print "STEP 1: Migrating your site metadata and certificates..."
	for x in os.listdir('/etc/nginx/sites-available'):
		f = nginx.loadf(os.path.join('/etc/nginx/sites-available', x))
		rtype = re.compile('GENESIS ((?:[a-z][a-z]+))', flags=re.IGNORECASE)
		stype = re.match(rtype, f.filter('Comment')[0].comment).group(1)
		c = ConfigParser.RawConfigParser()
		c.add_section("website")
		c.set("website", "name", x)
		c.set("website", "stype", stype)
		ssl = ""
		for y in glob.glob("/etc/ssl/certs/genesis/*.gcinfo"):
			cfg = ConfigParser.RawConfigParser()
			cfg.read(y)
			if x+" ("+stype+")" in cfg.get("cert", "assign").split("\n"):
				ssl = cfg.get("cert", "name")
				break
		version = None
		if stype in ["Wallabag"]:
			version = "1.6"
		dbengine = ""
		if stype in ["Wallabag", "WordPress", "ownCloud"]:
			dbengine = "MariaDB"
		elif os.path.exists('/var/lib/sqlite3') and x+".db" in os.listdir('/var/lib/sqlite3'):
			dbengine = "SQLite3"
		c.set("website", "ssl", ssl)
		c.set("website", "version", version)
		c.set("website", "dbengine", dbengine)
		c.set("website", "dbname", x if dbengine else "")
		c.set("website", "dbuser", x if dbengine == "MariaDB" else "")
		c.write(open(os.path.join('/etc/nginx/sites-available', '.'+x+'.ginf'), 'w'))

def pluginssl():
	print "STEP 2: Migrating your certificate assignments..."
	for x in glob.glob("/etc/ssl/certs/genesis/*.gcinfo"):
		cfg = ConfigParser.RawConfigParser()
		cfg.read(x)
		for y in cfg.get("cert", "assign").split("\n"):
			if y in ["Mailserver", "XMPP Chat"]:
				c = ConfigParser.RawConfigParser()
				c.read("/etc/genesis/genesis.conf")
				c.add_section("ssl_%s" % ("email" if y == "Mailserver" else "xmpp"))
				c.set("ssl_%s" % ("email" if y == "Mailserver" else "xmpp"), "cert", cfg.get("cert", "name"))
				c.write(open("/etc/genesis/genesis.conf"), "w")

def newplugins():
	print "STEP 3: Removing old plugins and downloading latest versions..."
	for x in glob.glob("/var/lib/genesis/plugins/*"):
		name = os.path.split(x)[-1]
		shutil.rmtree(x)
		if name in ["notepad", "supervisor", "terminal", "shell", 
			"taskmgr", "advusers", "cron", "pkgman"]:
			continue
		req = urllib2.Request("https://grm.arkos.io/")
		req.add_header("Content-type", "application/json")
		resp = urllib2.urlopen(req, json.dumps({"get": "plugin", "id": name}))
		resp = json.loads(resp.read())
		if resp["status"] == 200:
			open('/var/lib/genesis/plugins/plugin.tar.gz', 'wb').write(base64.b64decode(resp["info"]))
			t = tarfile.open('/var/lib/genesis/plugins/plugin.tar.gz', 'r:gz')
			t.extractall('/var/lib/genesis/plugins')
			t.close()
			os.unlink('/var/lib/genesis/plugins/plugin.tar.gz')
		else:
			print "ERROR - Couldn't fetch %s: %s. You'll have to download and install manually it from within the app" % (name, resp["info"])

def updreposvr():
	print "STEP 4: Updating repository server address"
	c = ConfigParser.RawConfigParser()
	c.read("/etc/genesis/genesis.conf")
	c.set("genesis", "update_server", "grm.arkos.io")
	c.write(open("/etc/genesis/genesis.conf"), "w")


if __name__ == '__main__':
    start()
    sitedata()
    pluginssl()
    newplugins()
    updreposvr()
    print "Finished migration!"
