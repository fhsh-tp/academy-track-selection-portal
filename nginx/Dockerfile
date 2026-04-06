FROM nginx:alpine

# Copy frontend static files (build context is project root)
COPY frontend/ /usr/share/nginx/html/

# Copy nginx config and entrypoint
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
