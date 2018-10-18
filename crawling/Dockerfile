FROM python:3.6
MAINTAINER Fran LOZANO <franloza@ucm.es>

# Set the working directory
COPY . /usr/src/app
WORKDIR /usr/src/app

# Install dependencies
RUN pip install pipenv
RUN pipenv install --system

CMD ["scrapy", "runspider", "crawling/spiders/marcapuestas.py"]
