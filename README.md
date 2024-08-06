# AskTech

AskTech is a free and open source website whose main focus is on digital currency. Django REST API technology is used in
the back-end of this site. This project is still under development. After
completion, additional information about this project will be announced.

## Authors

- [@AbolfazlKameli](https://github.com/AbolfazlKameli/) (back-end dev)

## Run Locally

install required packages

```shell
sudo apt install erlang rabbitmq-server
```

start rabbitmq-server service

```shell
sudo systemctl start rabbitmq-server
```

Clone the project

```shell
git clone https://github.com/AbolfazlKameli/Q-A-Forum.git
```

Go to the project directory

```shell
cd Q-A-Forum/
```

make a virtual environment

```shell
python3 -m venv .venv
```

activate virtual environment

```shell
source .venv/bin/activate 
```

install requirements

```shell
pip install -r requirements.txt
```

start celery project

```shell
celery -A forum worker -l INFO  
```

start the django server

```shell
python manage.py runserver
```