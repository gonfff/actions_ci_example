# Playing with github actions
## 0. Why
Пробуем создвть свой CI/CD пайплайн для домашнего проекта при помощи Python и GitHub Actions<br/>


## 1. Requirements
Для запуска этого проекта потребуется:
- VPS/VDS/VM с *nix ОС, куда будут деплоится контейнеры (проверено на Ubuntu Server 18.04)
- Белый IP адрес (проброшеный порт, иной способ получения веб хука)
- Python 3.8
- Docker
- git
## 2. Get Started
#####Установка серверной части на чистой Ubuntu Server 18.04
```shell script
sudo apt update
$ git clone https://github.com/dementevda/actions_ci_example.git
$ cd actions_ci_example/ci_app/
$ sudo apt install python3-pip
$ sudo python3 setup.py install
$ sudo cp ../ci_example.service /etc/systemd/system/ci_example.service
# dont forget to add token in ci_example.service
$ sudo systemctl daemon-reload
$ sudo systemctl enable ci_example.service
$ sudo systemctl start ci_example.service
```

Проверить то что веб сервер запустился и работает можно с помощью команд
```shell script
sudo systemctl status ci_example.service
```
или
```shell script
curl 0.0.0.0:5000
```
#####В Github аккаунте
Подключите Actions: https://github.com/features/actions<br/>
После этого вы можете писать свои действия в .github/workflows и смотреть как они выполняются во вкладке actions

## 3. Usage
При пуше нового кода в любую ветку будет запущена задача тестирования test_on_push, где будут проведены все тесты указанные в src/tests.py<br/>
При релизе (создании тэга) будет выполены действия из pub_on_release. А именно проход по всем тестам из src/tests.py. Если тесты будут пройдены успешно, то запустится процесс 
сборки докер образа, который будет отправлен в docker hub. Если пуш в регистри закончился успешно,
то будет отправлен вебхух на ранее установленный вебсервер, который и задеплоит наш контейнер

6a7daf8ced4066bcdc402328e612e79d9a5a6d57