# 使用官方的 Nginx 镜像作为基础镜像
FROM nginx:latest

RUN rm -rf /etc/nginx/conf.d/*

# 将 dist 目录复制到镜像中的 /usr/share/nginx/html
COPY ./dist /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80