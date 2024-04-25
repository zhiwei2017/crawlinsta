FROM zenika/alpine-chrome:with-chromedriver
LABEL authors="zhiweizhang"

USER root
RUN apk add --no-cache python3 py3-pip && apk add gcc python3-dev musl-dev linux-headers
RUN mkdir /home/tmp && mkdir /home/work && chmod -R 777 /home

USER chrome
COPY . /home/tmp
WORKDIR /home
RUN python3 -m venv /home/venv && source /home/venv/bin/activate && pip install -e /home/tmp && pip install jupyter
EXPOSE 8888
ENTRYPOINT sh -c "source venv/bin/activate && jupyter notebook --no-browser --port 8888"