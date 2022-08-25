set -ex

docker build -f Dockerfile.build -t issuecker.build .
docker run -v "${PWD}/build:/app/build" issuecker.build

sudo chown -R "$(id -nu):$(id -ng)" "${PWD}/build"
