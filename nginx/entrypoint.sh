#!/bin/sh
set -e

# Replace __API_BASE_URL__ placeholder in config.js with the API_BASE_URL env var.
# Defaults to empty string (relative paths) if API_BASE_URL is not set.
sed -i "s|__API_BASE_URL__|${API_BASE_URL:-}|g" /usr/share/nginx/html/config.js

exec nginx -g 'daemon off;'
