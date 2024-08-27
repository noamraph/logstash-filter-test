FROM docker.elastic.co/logstash/logstash:8.15.0

WORKDIR /repo

USER root

RUN apt-get update 

RUN apt-get install -y python3

COPY ./ .

CMD ["python3", "./logstash_filter_test.py"]
