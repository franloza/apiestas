FROM python:3.6
MAINTAINER Fran LOZANO <franloza@ucm.es>

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["scrapy", "runspider", "spiders/marcapuestas.py"]
