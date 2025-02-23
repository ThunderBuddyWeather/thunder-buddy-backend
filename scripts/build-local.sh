#!/bin/bash

# Build the local image
docker buildx build \
  --platform linux/arm64 \
  --load \
  -t aasimsyed/thunder-buddy:latest \
  . 