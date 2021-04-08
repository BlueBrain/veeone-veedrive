# VeeDrive

### Running tests
It is the easiest to run tests in a Docker container:
``` 
make run-docker-tests
```

You can run test using pytest:
```
python -m pytest
```
If you don't want to run all tests you can be selective:
```
python -m pytest tests/test_content.py::test_request_image
```

