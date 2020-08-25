FROM python:3.7-alpine
ADD https://dl.min.io/server/minio/release/linux-amd64/minio /
ADD docker/init.sh /
ADD ./ /ml-git
ADD docker/local_server.git.tar.xz /
ADD docker/local_ml_git_config_server.git.tar.xz /
ADD docker/mlgit.tar.xz /data/

ENV MINIO_ACCESS_KEY=fake_access_key \
    MINIO_SECRET_KEY=fake_secret_key 

WORKDIR /ml-git

RUN apk add --no-cache gcc musl-dev libffi-dev libressl-dev git && \
    rm -rf docker && \
    chmod +x ../minio && \
    chmod +x ../init.sh && \
    sed -i -e 's/\r//g'  ../init.sh && \
    mkdir $HOME/.aws && \
    echo -e "[default]\naws_access_key_id = fake_access_key\naws_secret_access_key = fake_secret_key" > $HOME/.aws/credentials && \
    python setup.py install 

WORKDIR /workspace

ENTRYPOINT [ "sh", "/init.sh" ]