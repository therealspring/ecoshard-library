FROM python:3.8.3-buster

RUN apt update && apt upgrade -y
RUN apt install -y \
    python3-pip

SHELL ["/bin/bash", "-c"]

WORKDIR /usr/local/gcloud-sdk
RUN wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-284.0.0-linux-x86_64.tar.gz && tar -xvzf google-cloud-sdk-284.0.0-linux-x86_64.tar.gz
RUN ./google-cloud-sdk/install.sh
RUN source /usr/local/gcloud-sdk/google-cloud-sdk/completion.bash.inc
RUN source /usr/local/gcloud-sdk/google-cloud-sdk/path.bash.inc
RUN echo "export PATH=$PATH:/usr/local/gcloud-sdk/google-cloud-sdk/bin" >> /root/.bashrc

WORKDIR /usr/local/expand_drive_service
COPY . /usr/local/expand_drive_service
RUN pip3 install -r requirements.txt

EXPOSE ${DISK_RESIZE_SERVICE_PORT}
ENTRYPOINT ["./launch_expand_drive_service.sh"]
