FROM python:3.6.2
ENV APP_ROOT /usr/src/horse_api
ADD . $APP_ROOT
WORKDIR $APP_ROOT
RUN pip install -r requirements.txt
CMD python manage.py runserver --host 0.0.0.0 --debug --reload
