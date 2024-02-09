FROM alpine:3.14

RUN apk update && apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=bild-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre 

RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

RUN apk add --no-cache python2

WORKDIR /app
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5001

CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "5001" ]


