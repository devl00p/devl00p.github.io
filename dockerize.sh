#!/bin/bash
set -e

docker build -t my-jekyll .

# Run
docker run --rm -it \
  -v "$PWD":/srv/jekyll \
  -p 4000:4000 \
  my-jekyll
