FROM ubuntu:latest
MAINTAINER Rajdeep Dua "dua_rajdeep@yahoo.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y libmysqlclient-dev
RUN apt-get -y update && apt-get install -y libmagickwand-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["KaideeV/KaideeV.py"]
