FROM ubuntu

RUN apt update
RUN apt install -y socat screen python3
RUN useradd mypack
EXPOSE 3777/tcp
WORKDIR /home/service
#CMD sleep 100000000
CMD ./runserver.sh
