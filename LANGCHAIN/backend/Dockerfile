# 使用官方 Node.js 镜像作为基础镜像
FROM node:latest

# 设置工作目录
WORKDIR /backend

# 将 package.json 和 package-lock.json 复制到容器内（如果有）
COPY package*.json ./

# 安装依赖
RUN npm install

# 将整个项目目录复制到容器中
COPY . .

# 暴露服务端口
EXPOSE 3000

# 启动 Node.js 应用
CMD ["node", "server.cjs"]
