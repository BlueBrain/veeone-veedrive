# VeeDrive

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
