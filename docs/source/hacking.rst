=================
Hacking on desqus
=================


------------
Installation
------------

You will need Python and git to be able to install desqus.

On Debianoid systems, run::

    sudo apt-get install python python-setuptools python-virtualenv git-core 


Set up desqus
-------------

Clone the git repository::

    git clone git://github.com/desqus/desqus.git

cd into the desqus git repository and create a new virtualenv::

    cd desqus && (virtualenv --system-site-packages . || virtualenv .)

fetch all the dependencies and install them in the virtualenv::

    ./bin/python setup.py develop

----------
Run desqus
----------

If you have activated the virtualenv, you may just ron::

    python run.py

otherwise you will have to run::

    ./bin/python run.py
