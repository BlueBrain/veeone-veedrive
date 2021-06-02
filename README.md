# VeeDrive

## Running

```
export VEEDRIVE_HOST_MEDIA_PATH=path_to_media_folder
make run-docker
```

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
