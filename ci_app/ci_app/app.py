# coding=utf-8
import os
import sys
import logging
import logging.config
import logging.handlers

from flask import Flask
from flask import request, jsonify
import docker


log = logging.getLogger(__name__)
app = Flask(__name__)
docker_client = docker.from_env()
MY_AUTH_TOKEN = os.getenv('CI_TOKEN', None)  # Берем наш токен из переменной окружения

def init_logging():
    """
    Инициализация логгера
    :return:
    """
    log_format = f"[%(asctime)s] [ CI/CD server ] [%(levelname)s]:%(name)s:%(message)s"
    formatters = {'basic': {'format': log_format}}
    handlers = {'stdout': {'class': 'logging.StreamHandler',
                           'formatter': 'basic'}}
    level = 'INFO'
    handlers_names = ['stdout']
    loggers = {
        '': {
            'level': level,
            'propagate': False,
            'handlers': handlers_names
        },
    }
    logging.basicConfig(level='INFO', format=log_format)
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': loggers
    }
    logging.config.dictConfig(log_config)


def get_active_containers():
    """
    Получение списка запущенных контейнеров
    :return:
    """
    containers = docker_client.containers.list()
    result = []
    for container in containers:
        result.append({
            'short_id': container.short_id,
            'container_name': container.name,
            'image_name': container.image.tags,
            'created':  container.attrs['Created'],
            'status':  container.status,
            'ports':  container.ports,
        })
    return result


def get_container_name(item: dict) -> [str, str]:
    """
    Получение имени image из POST запроса
    :param item:
    :return:
    """
    if not isinstance(item, dict):
        return ''
    owner = item.get('owner')
    repository = item.get('repository')
    tag = item.get('tag', 'latest').replace('v', '')
    if owner and repository and tag:
        return f'{owner}/{repository}:{tag}', repository
    if repository and tag:
        return f'{repository}:{tag}', repository
    return '', ''


def kill_old_container(container_name: str) -> bool:
    """
    Перед запуском нового контейнера, удаляем старый
    :param container_name:
    :return:
    """
    try:
        # Получение получение контейнера
        container = docker_client.containers.get(container_name)
        # Остановка
        container.kill()
    except Exception as e:
        # На случай если такого контейнера небыло
        log.warning(f'Error while delete container {container_name}, {e}')
        return False
    finally:
        # Удаление остановленых контейнеров, чтобы избежать конфликта имен
        log.debug(docker_client.containers.prune())
    log.info(f'Container deleted. container_name = {container_name}')
    return True


def deploy_new_container(image_name: str, container_name: str, ports: dict = None):
    try:
        # Пул последнего image из docker hub'a
        log.info(f'pull {image_name}, name={container_name}')
        docker_client.images.pull(image_name)
        log.debug('Success')
        kill_old_container(container_name)
        log.debug('Old killed')
        # Запуск нового контейнера
        docker_client.containers.run(image=image_name, name=container_name, detach=True, ports=ports)
    except Exception as e:
        log.error(f'Error while deploy container {container_name}, \n{e}')
        return {'status': False, 'error': str(e)}, 400
    log.info(f'Container deployed. container_name = {container_name}')
    return {'status': True}, 200


@app.route('/', methods=['GET', 'POST'])
def MainHandler():
    """
    GET - Получение списка всех активных контейнеров
    POST - деплой сборки контейнера
    Пример тела запроса:
    {
        "owner": "gonfff",
        "repository": "ci_example",
        "tag": "v0.0.1",
         "ports": {"8080": 8080}
    }
    :return:
    """
    if request.headers.get('Authorization') != MY_AUTH_TOKEN:
        return jsonify({'message': 'Bad token'}), 401
    if request.method == 'GET':
        return jsonify(get_active_containers())
    elif request.method == 'POST':
        log.debug(f'Recieved {request.data}')
        image_name, container_name = get_container_name(request.json)
        ports = request.json.get('ports') if request.json.get('ports') else None
        result, status = deploy_new_container(image_name, container_name, ports)
        return jsonify(result), status


def main():
    init_logging()
    if not MY_AUTH_TOKEN:
        log.error('There is no auth token in env')
        sys.exit(1)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
