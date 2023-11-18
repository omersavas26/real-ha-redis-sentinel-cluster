FROM nginx

RUN apt-get update --fix-missing
RUN apt-get install docker.io -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip3 install redis requests --break-system-packages
