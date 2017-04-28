FROM ubuntu:latest
MAINTAINER Rajdeep Dua "dua_rajdeep@yahoo.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y libmysqlclient-dev
COPY . /KaideeV
WORKDIR /KaideeV
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["KaideeV/kaideeV.py"]
