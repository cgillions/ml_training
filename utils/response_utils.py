from flask import jsonify


def response(state, message, detail):
    return jsonify({
        "state": state,
        "message": message,
        "detail": detail
    })


def error(err, detail):
    return response("error", err, detail)


def success(message="Success!"):
    return response("success", message, "The call was successful.")
