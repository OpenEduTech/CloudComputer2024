tidb构建
```bash
docker-compose up -d
mysql -h 127.0.0.1 -P 4000 -u root
```
```sql
ALTER USER 'root'@'%' IDENTIFIED BY 'tjf04712';
FLUSH PRIVILEGES;
exit;
```
```bash
mysql -h 127.0.0.1 -P 4000 -u root -p
```
清除tidb
```bash
docker-compose down
```
提交镜像
```sh
docker buildx build --platform linux/amd64,linux/arm64 -t duringbug/rag-backend:v1.0 --push .
```