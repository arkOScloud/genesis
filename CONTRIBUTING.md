# Contributing

Follow this tutorial? -> https://bbs.arkos.io/t/arkos-developers-edition-2-computers/2076

Once setup you can contribute in the following order:

1. File an issue.
2. Solve the issue.
3. Commit. Push.
   * Write down the issue you've fixed it the commit message? http://docs.gitlab.com/ee/customization/issue_closing.html
4. Wait for CI to finish testing
   * If fail go back to step 2 
   * Otherwise continue with your quest.
5. File a new Merge Request.
   * Accept your own merge request to escape the clutches of angry lead programmers.
6. Profit

# Site packages

These package are required ArkOS libraries a developer would need to download 
if one would want to help develop on the ArkOS Project.

## Python Package Index (PyPI) site-packages

### Instructions
sudo pip install package 

### List
requests
cryptography
ldap3
dbus-python
flask
netifaces
psutil
ntplib

## ArkOS site-packages

### Instructions
sudo pip install git+https://git.coderouge.co/arkOS/<package_name>.git

### List
python-cryptsetup

# Code Conventions

## Rule #1 - If not tagged with code cleaning, anything goes.

I (Folatt) suggest that functional code commit merge request should trump any kind of code convention.

What I'm hoping for is that this gives newer developers something to immediately contribute to this project with.


## Python - Standard code conventions

Below are two links to a code style guide that we're not following, but I'm putting them up here anyway:

https://www.python.org/dev/peps/pep-0008/
https://www.python.org/dev/peps/pep-0257/

## Python - In-house conventions

Since I haven't read the code style guide above, I (Folatt) would like to make suggestions of my own:

Method order of a python module/class
- Constructor
- init
- other public methods
- return methods
- setter/getter methods
- private methods

Also, I've noticed that Jacob likes to word wrap during his code cleaning, 
so I'm sure that'll be part of our code convention it in the future as well.  