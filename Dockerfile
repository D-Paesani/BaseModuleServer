FROM alpine:3.14

RUN apk update && apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=bild-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre \
&& apk add --no-cache python3-dev 
# && apk add --no-cache build-base \
# && apk add --no-cache subversion \
# && apk add --no-cache gfortran \
# && apk add --no-cache libstdc++ \
# && apk add --no-cache libffi-dev \
# && apk add --no-cache openssl-dev \
# && apk add --no-cache lapack-dev \
# && apk add --no-cache libxml2-dev \
# && apk add --no-cache libxslt-dev \
# && apk add --no-cache libressl-dev


RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

RUN apk add --no-cache python2

WORKDIR /app

RUN mkdir -p ../logs && chmod 755 ../logs && touch ../logs/jsccmd.log

COPY . /app
RUN pip3 install -r requirements.txt --verbose | tee pip_install_log.txt 

EXPOSE 5001

CMD [ "bash","run.sh" ]


