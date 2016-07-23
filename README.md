# Genesis

[![build status](https://git.coderouge.co/folatt/genesis/badges/master/build.svg)](https://git.coderouge.co/folatt/genesis/commits/master)

Genesis is the interactive server management application for systems running arkOS server software. This project is currently in development. For more information about arkOS, visit [our website](https://arkos.io).

## Prerequisites

You will need the following things properly installed on your computer.

* [Git](http://git-scm.com/)
* [Node.js](http://nodejs.org/) (with NPM)
* [Bower](http://bower.io/)
* [Ember CLI](http://www.ember-cli.com/)
* [PhantomJS](http://phantomjs.org/)

You will also need a running installation of both [the core libraries](https://git.coderouge.co/arkOS/core) and the [Kraken REST API](https://git.coderouge.co/arkOS/kraken), on the same machine or a location that can be designated in `config/environment.js`.


## Installation

* `git clone <repository-url>` this repository
* change into the new directory
* `npm install`
* `bower install`

## Running / Development

* `ember server`
* Visit your app at [http://localhost:4200](http://localhost:4200).

### Code Generators

Make use of the many generators for code, try `ember help generate` for more details

### Running Tests

* `ember test`
* `ember test --server`

### Building

* `ember build` (development)
* `ember build --environment production` (production)

## Further Reading / Useful Links

* [ember.js](http://emberjs.com/)
* [ember-cli](http://www.ember-cli.com/)
* Development Browser Extensions
  * [ember inspector for chrome](https://chrome.google.com/webstore/detail/ember-inspector/bmdblncegkenkacieihfhpjfppoconhi)
  * [ember inspector for firefox](https://addons.mozilla.org/en-US/firefox/addon/ember-inspector/)

