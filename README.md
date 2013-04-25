# arkOS Genesis

Genesis is the server manager and interactive utility for systems running the arkOS distribution. This project is currently in development. For more information about arkOS, visit [our website](https://ark-os.org).


## Getting Started
For end-users: Genesis is already downloaded and installed on your arkOS node, running from the moment you start it up. Once your node is started and plugged into your router, simply go to `http://arkos:8000` in your browser to complete the setup and configuration process. From there, you are ready to use Genesis to manage your decentralized web!

For more information see the [Getting Started](http://ark-os.org/doc/getting-started/) page.

Running Genesis from this Github repo is advised ONLY for development purposes. See "Running outside of arkOS" below as well.


## Writing Plugins
For information on developing plugins for use with Genesis, see the development centre on https://ark-os.org. Specifically:

* [Plugin Structure](http://ark-os.org/dev/genesis/plugstruct) - Getting started with writing Genesis plugins
* [Plugin Reference](http://ark-os.org/dev/genesis/plugref) - Important classes and functions for writing plugins
* [User Interface](http://ark-os.org/dev/genesis/ux) - How to write a user interface compatible with Genesis' UX system
* [API Reference](http://ark-os.org/dev/genesis/api) - The big book of all classes and functions

Once you have a plugin, feel free to let @jacook know and testing can be arranged. If the plugin works well and contributes to arkOS' mission, it may then be included in the central plugin repository.


## Running outside of arkOS
Genesis can be run on non-arkOS distributions, but there are a few caveats to be aware of.

* The "first run" wizard should not activate if you run from the Github repo, as it is configured for an anonymous test user. Even so, if for some reason you see the "first run" wizard, do NOT enable the "Expand disk image" feature, as you may suffer data loss as a result.
* The Network plugin is configured for use with arkOS or Arch Linux platforms that use `netctl` for handling network connections. This plugin will crash on other platforms.
* All development is happening with arkOS in mind first. If support for certain plugins/core features is to be expanded to other platforms, that will occur after the fact, and packages may be made available for those platforms at that time.


## Acknowledgments
arkOS Project Contributors:
* Jacob Cook @jacook
* AJ Bahnken @ajvb

This project was forked from Ajenti, an excellent server management framework by @Eugeny located here: https://github.com/Eugeny/ajenti.
