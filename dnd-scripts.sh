#!/bin/bash

DOCKER_IMAGE="dndscripts:latest"
main() {
  if [ "$#" -lt 1 ]; then
    echo "$#"
    echo "Usage: $0 [alcreatures <pdf> | crop | pdf ]"
    exit 2
  fi

  $@
}

crop() {
  docker run -v $PWD:/opt -w /opt $DOCKER_IMAGE python3 /app/crop_circles.py 
}

pdf() {
  docker run -v $PWD:/opt -w /opt $DOCKER_IMAGE python3 /app/topdf.py
}

alcreatures() {
  docker run -v $PWD:/opt -e OPENAI_API_KEY=$OPENAI_API_KEY -w /opt $DOCKER_IMAGE python3 /app/alcreatures.py "$*"
}

main "$@"
