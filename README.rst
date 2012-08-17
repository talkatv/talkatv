-----------------------
What may desqus become?
-----------------------

Primarily, desqus will provide a way for people to embed comments on static pages. Secondarily, desqus will investigate the possibilities to federate the comments via e.g. OStatus or XMPP.

------------
Installation
------------

To install desqus, run::

    # Clone the repository
    git clone git://github.com/desqus/desqus.git
    # cd into the desqus repository and create a new virtualenv
    cd desqus && (virtualenv --system-site-packages . || virtualenv .)
    # Activate the virtualenv
    . bin/activate
    # Install the required dependencies into the virtualenv
    python setup.py develop

To run desqus::

    python run.py


----------
Contribute
----------

Send a pull request on `<https://github.com/desqus/desqus>`_ or join us in `#desqus`_ on Freenode!

.. _`#desqus`: http://webchat.freenode.net/?channels=desqus
