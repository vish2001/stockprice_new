FROM python:3.9-slim-buster
RUN apt-get update
RUN pip3 install rpyc requests pandas scikit-learn
CMD [ "/bin/bash", "-c", "while true; do bash -l; done" ]