[[_TOC_]]

## VeeDrive
VeeDrive is VeeOne backend. Python application serves multiple purposes 
such as file system browsing, presentation persistance, thumbnail generation. 
VeeDrive can also serve static content but it is recommended to use Nginx for that purpose.
To simplify deployment docker-compose can handle all required services: veedrive, nginx and mongodb.

## Development

### Docker
In order to run docker compose locally, you need to create docker-compose.override.yml. You will find an example file in the repo.

#### Run dev docker compose with postgresql instance
```
docker compose build
docker compose up
```

#### Run tests with the same configuration
```
make run-docker-tests
```
### Run w/o docker

You can run tests using pytest outside of docker container. 
NB you need to make sure postgresql instance is running and all env vars are set.

```
export VEEDRIVE_DB_TYPE=postgres VEEDRIVE_DB_PASSWORD=example VEEDRIVE_DB_USERNAME=postgres VEEDRIVE_DB_NAME=postgres VEEDRIVE_DB_HOST=localhost 
```

```
$ python -m  pytest -v -s--cov=veedrive
```
If you don't want to run all tests you can be selective:
```
python -m pytest tests/test_content.py::test_request_image
```

Run veedrive
```
python3 -m veedrive.main
```

## Running in production environment
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

### Openstack VM details
More on running Veedrive in Openstack VM in deploy/README.md

### Run 
```
$ VEEDRIVE_IMAAGE_TAG=0.2.0 VEEDRIVE_DB_PASSWORD=db_password docker-compose up
  or
$ VEEDRIVE_IMAAGE_TAG=0.2.0 VEEDRIVE_DB_PASSWORD=db_password make openstack-up
```

### Volume trick
if you want to change MEDIA_PATH you need to remove a previously created volume with:
`docker volume rm media_volume`

