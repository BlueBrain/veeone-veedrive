# VeeDrive

## Running

```
export MEDIA_PATH=path_to_media_folder # if ommited, tests/sandbox_folder will be used
make run-docker
```
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
