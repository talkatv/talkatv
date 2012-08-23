=================
Hacking on talkatv
=================


------------
Installation
------------

You will need Python and git to be able to install talkatv.

On Debianoid systems, run::

    sudo apt-get install python python-setuptools python-virtualenv git-core 


Set up talkatv
--------------

Clone the git repository::

    git clone git://github.com/talkatv/talkatv.git

cd into the talkatv git repository and create a new virtualenv::

    cd talkatv && (virtualenv --system-site-packages . || virtualenv .)

fetch all the dependencies and install them in the virtualenv::

    ./bin/python setup.py develop

-----------
Run talkatv
-----------

If you have activated the virtualenv, you may just ron::

    python run.py

otherwise you will have to run::

    ./bin/python run.py
