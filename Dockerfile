FROM python:3.6.2
ENV APP_ROOT /usr/src/horse_api
ADD . $APP_ROOT
WORKDIR $APP_ROOT
RUN pip install -r requirements.txt

EXPOSE 3031
ENTRYPOINT uwsgi --ini myapp.ini
