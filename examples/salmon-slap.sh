#!/bin/bash
curl -X POST -H 'Content-Type: application/atom+xml' \
    --data-binary '@examples/salmon-slap.xml'\
    localhost:4547/salmon/replies
