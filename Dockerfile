# FROM --platform=$BUILDPLATFORM python:3.7-alpine
FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

WORKDIR /leo

# COPY requirements.txt /leo
COPY /requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

# COPY . /leo
COPY . ./

# ENTRYPOINT ["python3"]
# ENTRYPOINT ["python"]

# CMD ["manage.py", "runserver", "0.0.0.0:8001"]


# Alternate setup ideas nicely layed out here:
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
