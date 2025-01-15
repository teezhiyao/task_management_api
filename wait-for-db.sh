#!/bin/bash

set -e

# Database connection details
host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for database at $host:$port..."

# Loop until the database responds to a connection
until mysqladmin ping -h "$host" --silent; do
  echo "Database is unavailable - retrying..."
  sleep 5
done

echo "Database is up - executing command"
exec $cmd