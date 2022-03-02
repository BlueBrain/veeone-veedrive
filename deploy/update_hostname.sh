#!/bin/bash
FQDN=`hostname -f`
sed -i s/__HOSTNAME__/$FQDN/g nginx/default.conf
sed -i s/__HOSTNAME__/$FQDN/g prod.env
