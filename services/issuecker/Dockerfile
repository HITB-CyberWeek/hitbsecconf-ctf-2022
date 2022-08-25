FROM ubuntu:22.04

RUN apt update && apt install apache2 -y

RUN a2enmod cgi
RUN service apache2 restart

CMD /usr/sbin/apache2ctl -D FOREGROUND
