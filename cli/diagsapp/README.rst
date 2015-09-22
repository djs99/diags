=======================================
 Developing the Cinder diagnostics CLI:
=======================================

Setup
-----

Clone the cliff repository:

  $ git clone https://github.com/openstack/cliff.git

Install the cliff framework:

  $ cd cliff
  $ sudo python setup.py install

Install the additional formatter package:

  $ sudo pip install cliff-tablib

Install the Cinder Diagnostics CLI package.
Copy the diagsapp directory (and contents) into the "cliff" directory.

  $ cd diagsapp
  $ sudo python setup.py install

Usage
-----

  $ cinderdiags --help

Development
-----------

Use the code in the "demoapp" directory as a starting place for implementing new code.
After making a code change, be sure to run setup.py from the diagsapp directory.
