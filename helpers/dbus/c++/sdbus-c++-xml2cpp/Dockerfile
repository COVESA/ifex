FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y git build-essential cmake pkg-config libsystemd-dev libexpat-dev
COPY bashrc /root/.bashrc
COPY build.sh .
RUN ./build.sh
WORKDIR /work
CMD /sdbus-cpp/build/tools/sdbus-c++-xml2cpp
