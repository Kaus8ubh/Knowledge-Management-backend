#!/bin/bash
if [ -d "app" ]; then
  cd app
  uvicorn main:app --host 0.0.0.0 --port $PORT
else
  echo "Error: app directory not found"
  exit 1
fi