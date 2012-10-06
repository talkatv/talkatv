=========
 talkatv
=========
:Spelling: talkatv
:Pronounciation:  /ˈtôkətiv/ - like "talkative"
:Author: talkatv contributors, see AUTHORS
:License: AGPLv3 or later

------------------
 What is talkatv?
------------------
talkatv is a comment service much like DISQUS or IntenseDebate.

talkatv is open source and free to use.

talkatv is embedded on any page and uses `XMLHttpRequest level 2`_ and
`Cross-Origin Resource Sharing`_ to post the comment back to the server.

.. _`XMLHttpRequest level 2`: http://www.w3.org/TR/XMLHttpRequest/
.. _`Cross-Origin Resource Sharing`: http://www.w3.org/TR/cors/

talkatv requires JavaScript, but has a non-javascript fallback which is a link
to the talkatv server with an optional but recommended ``?uri={{ page_uri }}``
argument. If the ``uri`` argument is not provided, talkatv will try to get the
page URI from the `HTTP Referer`_ header.

.. _`HTTP Referer`: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.36

talkatv supports OpenID authentication.


--------------
 Installation
--------------

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

Then initiate the database::

    ./dbupdate.py

To run talkatv::

    python run.py

.. warning::
    You have to run both dbupdate and run.py from within your virtualenv.


----------
Contribute
----------

Send a pull request on `<https://github.com/talkatv/talkatv>`_ or join us in `#talka.tv`_ on Freenode!

.. _`#talka.tv`: http://webchat.freenode.net/?channels=talka.tv
