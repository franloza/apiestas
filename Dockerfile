FROM python:3.6
LABEL maintainer="franloza@ucm.es"

# Install pipenv
RUN pip install pipenv

# Optimize dockerfile caching dependencies
ADD Pipfile Pipfile.lock /usr/src/app/
WORKDIR /usr/src/app
RUN pipenv install --system --deploy --ignore-pipfile

# Add project files
ADD . /usr/src/app
