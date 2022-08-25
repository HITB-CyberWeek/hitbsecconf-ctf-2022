set -ex

docker build -f Dockerfile.build -t issuecker.build .
docker run --rm -v "${PWD}/server:/app/server" issuecker.build

sudo chown -R "$(id -nu):$(id -ng)" "${PWD}/server"
