set -ex

docker build -t issuecker.build .
docker run -v "${PWD}/build:/app/build" -it issuecker.build
