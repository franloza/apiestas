FROM python:3.6
LABEL maintainer="franloza@ucm.es"

# Install pipenv
RUN pip install pipenv

# Set the working directory
COPY . /usr/src/app
WORKDIR /usr/src/app

# Install dependencies
RUN pipenv install --system --deploy