import logging

from flask import Flask
from flask import request, jsonify


log = logging.getLogger(__name__)
app = Flask(__name__)


def validate_post_data(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if not data.get('name') or not isinstance(data['name'], str):
        return False
    if data.get('age') and not isinstance(data['age'], int):
        return False
    return True


@app.route('/', methods=['GET'])
def hello():
    """
    Print "hello world" on main page
    :return:
    """
    return 'Hello World!'


@app.route('/api', methods=['GET', 'POST'])
def api():
    """
    /api entpoint
    GET - returns json= {'status': 'test'}
    POST -  {
            name - str not null
            age - int optional
            }
    :return:
    """
    if request.method == 'GET':
        return jsonify({'status': 'test'})
    elif request.method == 'POST':
        if validate_post_data(request.json):
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'bad input'}), 400


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
