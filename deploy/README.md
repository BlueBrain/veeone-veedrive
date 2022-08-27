### Deployment to Openstack VM extra steps (WIP)

``` $ docker login bbpgitlab.epfl.ch:5050```
```

root# chown root:bbp-user-visualization /etc/letsencrypt/live/`hostname -f`/privkey.pem
FIXME in puppet:
root#  mv `which docker-credential-secretservice` /usr/bin/docker-credential-secretservice.bkp
```
