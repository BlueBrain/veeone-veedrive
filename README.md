# VeeDrive
VeeDrive is VeeOne backend. Python application serves multiple purposes 
such as file system browsing, presentation persistance, thumbnail generation. 
VeeDrive can also serve static content but it is recommended to use Nginx for that purpose.
To simplify deployment docker-compose can handle all required services: veedrive, nginx and mongodb.

## Running
### Prepare environement
1. Update hostname in nginx config and docker env files:
```
$ cd deploy
deploy$ ./update_hostname.sh
```

2. Prepare docker environment file:<br>
    1. Copy deploy/prod.env file to repo root directory: ` cp deploy/prod.env .env`
    2. Add `MEDIA_PATH=path_to_media_folder` to `.env` otherwise **/nfs4/bbp.epfl.ch/media/DisplayWall**  will be used


### SSL set-up
Make sure you have certificates in `/etc/letsencrypt/live/${HOSTNAME}`. fullchain.pem and privkey.pem are required.

### Openstack VM
More on running Veedrive in Openstack VM in deploy/README.md

### Run 
```
$ make run-docker 
or
$ docker-compose up -d
```

### Volume trick
if you want to change MEDIA_PATH you need to remove a previously created volume with:
`docker volume rm media_volume`

## Running tests with coverage report
It is the easiest to run tests in a Docker container:
``` 
make run-docker-tests
```

You can run tests using pytest:
```
$ python -m  pytest -v -s--cov=veedrive
```
If you don't want to run all tests you can be selective:
```
python -m pytest tests/test_content.py::test_request_image
```
