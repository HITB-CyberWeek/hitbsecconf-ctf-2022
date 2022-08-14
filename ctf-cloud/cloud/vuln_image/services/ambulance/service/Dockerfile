FROM ubuntu:20.04

RUN apt update \
    && apt install -y software-properties-common libgmp-dev libmpfr-dev libmpc-dev socat \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt update && apt install -y python3.9-dev python3-pip 

RUN useradd --no-create-home --shell /bin/false --uid 1000 --user-group ambulance

RUN mkdir -p /var/ambulance/ \
    && mkdir /var/ambulance/users/ /var/ambulance/diseases/ \
    && chmod 777 /var/ambulance/users/ /var/ambulance/diseases/

WORKDIR /var/ambulance/

COPY src/requirements.txt .

RUN python3.9 -m pip install -r requirements.txt

COPY src .

USER ambulance

ENTRYPOINT [ "/bin/sh", "run.sh" ]
