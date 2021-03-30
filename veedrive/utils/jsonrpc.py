import json


def prepare_response(data, result):
    obj = {"id": data["id"], "result": result}
    return json.dumps(obj)


def prepare_error(data, error_code, error_description=""):
    obj = {"id": data["id"]}
    error = {"code": int(error_code), "message": error_description}
    obj["error"] = error
    return json.dumps(obj)


def prepare_error_code(data, exception):
    obj = {"id": data["id"]}
    error = {"code": int(exception.code), "message": str(exception)}
    obj["error"] = error
    return json.dumps(obj)


def validate_jsonrpc(required_param):
    """Decorator meant to verify if JSON-RPC member object 'params'
        includes the specfied key

    :param required_param: required key of 'params'
    :type required_param: str
    """

    def validator(func):
        async def wrapper(*args, **kwargs):
            try:
                args[0]["params"][required_param]
            except:
                return prepare_error(args[0], 400)
            result = await func(*args, **kwargs)
            return result

        return wrapper

    return validator
