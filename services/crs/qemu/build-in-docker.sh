#!/bin/bash
set -e
IMAGE="qemu-builder"
if [[ "$(docker images -q $IMAGE 2> /dev/null)" == "" || "$1" == "rebuild-image" ]]; then
  docker build . -t $IMAGE
else
  echo "Image already exists."
fi
docker run --rm -v $(pwd):/qemu --env DEB_BUILD_OPTIONS=nocheck $IMAGE
echo "Done."
