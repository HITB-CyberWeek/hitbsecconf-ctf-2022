set -ex

docker build -t issuecker.build .
docker run -v "${PWD}/build:/app/build" issuecker.build

sudo chmod -R $USER:$USER "${PWD}/build"
