------------------------
What may talkatv become?
------------------------

Primarily, talkatv will provide a way for people to embed comments on static pages. Secondarily, talkatv will investigate the possibilities to federate the comments via e.g. OStatus or XMPP.

------------
Installation
------------

To install talkatv, run::

    # Clone the repository
    git clone git://github.com/talkatv/talkatv.git
    # Install the dependencies
    sudo apt-get install python-dev python-virtualenv
    pip install Flask sqlalchemy wtforms
    # cd into the talkatv repository and create a new virtualenv
    cd talkatv && (virtualenv --system-site-packages . || virtualenv .)
    # Activate the virtualenv
    . bin/activate
    # Install the required dependencies into the virtualenv
    python setup.py develop

To run talkatv::

    python run.py


----------
Contribute
----------

Send a pull request on `<https://github.com/talkatv/talkatv>`_ or join us in `#talka.tv`_ on Freenode!

.. _`#talka.tv`: http://webchat.freenode.net/?channels=talka.tv
