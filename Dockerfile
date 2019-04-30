FROM	python:3
MAINTAINER	cshwan@kaist.ac.kr

COPY . /usr/src/app

WORKDIR /usr/src/app
RUN	python3 -m pip install django pycryptodome django-sslserver uwsgi
RUN	apt -y update
RUN	apt install  -y nginx

EXPOSE 8000

RUN	python3 manage.py makemigrations is521_ca && \
	python3 manage.py migrate 

RUN	python3 manage.py loaddata fixtures/user.json

COPY	ssl/ca.conf /etc/nginx/sites-enabled/ca.conf
COPY	ssl/uwsgi_params /usr/src/ 

CMD	service nginx restart && uwsgi --ini ssl/wsgi.ini

