# Genesis

Genesis is the interactive server management application for systems running the arkOS distribution. This project is currently in development. For more information about arkOS, visit [our website](https://arkos.io).


## Getting Started
For end-users: Genesis is already downloaded and installed on your arkOS node, running from the moment you start it up. Once your node is started and plugged into your router, simply go to `http://arkos:8000` in your browser to complete the setup and configuration process. From there, you are ready to use Genesis to manage your decentralized web!

For more information see the [Getting Started](http://arkos.io/doc/getting-started/) page.

Running Genesis from this Github repo is advised ONLY for development purposes. If you do this you will need the following Python modules: `pyOpenSSL`, `gevent`, `lxml`, `ntplib`, `python-iptables`, and `pyparsing`. Once you've cloned this repo, just run `genesis-panel` with root privileges to run a server live in stdout. `genesis-panel -d` and `genesis-panel -s` manually starts and stops the daemon respectively.


## Writing Plugins
For information on developing plugins for use with Genesis, see the development centre on https://arkos.io. Specifically:

* [Webapp and Databases Structure](https://arkos.io/dev/genesis/apps-dbs) - Getting started with including new webapp and database types in Genesis
* [Plugin Structure](https://arkos.io/dev/genesis/plugstruct) - Getting started with writing general Genesis plugins
* [User Interface](https://arkos.io/dev/genesis/ux) - How to write a user interface compatible with Genesis' UX system
* [Icon Reference](https://arkos.io/dev/genesis/iconref) - Choosing iconfont classes to use in your plugins
* [General API Reference](https://arkos.io/dev/genesis/api) - The big book of all classes and functions

Once you have a plugin, feel free to let @jacook know and testing can be arranged. If the plugin works well and contributes to arkOS' mission, it may then be included in the central plugin repository.


## Acknowledgments
Genesis is developed by:
* Jacob Cook @jacook

With a big thanks to those who have made contributions!
* AJ Bahnken @ajvb
* Jasper van Loenen @javl
* Miguel Moitinho @mamoit
* Steven Nelson @StevenNelson
* Timothy Farrell @explorigin
* Will Wilson @wwilson

This project was forked from Ajenti, an excellent server management framework by @Eugeny located here: https://github.com/Eugeny/ajenti.
