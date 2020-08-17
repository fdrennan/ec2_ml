FROM tensorflow/tensorflow:latest-gpu

WORKDIR /root
COPY ./requirements.txt /root/requirements.txt
RUN apt-get install graphviz -y
RUN pip install --no-deps --trusted-host pypi.python.org -r requirements.txt



