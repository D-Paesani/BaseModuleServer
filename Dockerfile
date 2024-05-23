FROM alpine:3.14

RUN apk update && apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=bild-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk11 \
&& apk add --no-cache python3-dev \
&& apk add --no-cache git 
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

ARG clbclient=clb-client-v1.4.2-7f0365b9

RUN git clone https://git.km3net.de/daq/shore-station/cu_tools.git /cu_tools
# RUN git clone https://git.km3net.de/cnicolau/bpd-software.git      /bpd-software 
RUN git clone --branch fix_jsendcommand2 https://git.km3net.de/cnicolau/bpd-software.git /bpd-software 
RUN curl -o ${clbclient}.tar.gz https://sftp.km3net.de/CLB_Builds/${clbclient}.tar.gz
RUN tar xzf ${clbclient}.tar.gz
RUN mv ${clbclient}/lib/remote.jar /cu_tools/NG-DUBase_java


RUN rm /cu_tools/NG-DUBase_java/java_setenv.sh 
RUN echo myjava=/usr/bin/java           >> /cu_tools/NG-DUBase_java/java_setenv.sh 
RUN echo myjavac=/usr/bin/javac         >> /cu_tools/NG-DUBase_java/java_setenv.sh 
RUN echo "export myjava"                 >> /cu_tools/NG-DUBase_java/java_setenv.sh 
RUN echo "export myjavac"                >> /cu_tools/NG-DUBase_java/java_setenv.sh 

RUN rm /cu_tools/NG-DUBase_java/execute.sh                          
RUN cp /app/toreplace/execute.sh  /cu_tools/NG-DUBase_java/execute.sh
RUN chmod +x /cu_tools/NG-DUBase_java/execute.sh

WORKDIR /cu_tools/NG-DUBase_java/
RUN sh comp_only.sh NG_BPDCmd

RUN ln -s /cu_tools/NG-DUBase_java/NG_BPDCmd.class /bpd-software/host/python/console/NG_BPDCmd.class
RUN ln -s /cu_tools/NG-DUBase_java/remote.jar /bpd-software/host/python/console/remote.jar
RUN ln -s /cu_tools/NG-DUBase_java/execute.sh /bpd-software/host/python/console/execute.sh

EXPOSE 5001

WORKDIR /app

CMD [ "bash","run.sh" ]

