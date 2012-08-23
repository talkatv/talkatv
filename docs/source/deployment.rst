=================
Deploying talkatv
=================

.. todo::
    Provide a more elaborate description

This page is a draft.

-----------
WSGI server
-----------

To be able to receive requests via FCGI::

    bin/python wsgi.py

---------------------------
nginx example configuration
---------------------------

nginx.conf::

    server {
      listen 80;
      sendfile on;
    
      # Gzip
      gzip on;
      gzip_min_length 1024;
      gzip_buffers 4 32k;
      gzip_types text/plain text/html application/x-javascript text/javascript text/xml text/css;
    
      # The DNS name that this config should be a vhost for.
      server_name = talka.tv;
    
      # Add shortcut for desqus.js
      location /desqus.js {
        alias /srv/talka.tv/talkatv/talkatv/static/js/desqus.js;
      }
      
      # Forward requests via FCGI to the running wsgi.py server script
      # that is provided with talkatv.
      location / {
        fastcgi_pass 127.0.0.1:45474;
        include fastcgi_params;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
      }
    }
