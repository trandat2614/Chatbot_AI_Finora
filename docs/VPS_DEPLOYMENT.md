# Triển khai Finora AI Server lên VPS

Hướng dẫn này dùng Ubuntu 22.04/24.04, Docker Compose, Nginx và HTTPS. Cấu hình
khuyến nghị tối thiểu là 1 vCPU, 1 GB RAM và 10 GB ổ đĩa.

## 1. Chuẩn bị DNS và firewall

Trỏ bản ghi A của `api.example.com` tới IP VPS. Chỉ mở SSH, HTTP và HTTPS:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Port 8000 được bind vào `127.0.0.1`, không công khai trực tiếp ra Internet.

## 2. Cài Docker và Nginx

```bash
sudo apt update
sudo apt install -y ca-certificates curl nginx certbot python3-certbot-nginx
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Đăng xuất SSH rồi đăng nhập lại để quyền Docker có hiệu lực.

## 3. Đưa source lên VPS

Ưu tiên push repository lên Git provider riêng, sau đó clone:

```bash
sudo mkdir -p /opt/finora
sudo chown "$USER":"$USER" /opt/finora
git clone <REPOSITORY_URL> /opt/finora/app
cd /opt/finora/app
cp .env.example .env
nano .env
```

Cấu hình production tối thiểu:

```dotenv
GEMINI_API_KEY=<gemini-key>
GEMINI_MODEL=gemini-2.5-flash
AI_SERVER_API_KEY=<random-secret-long-value>
ALLOWED_ORIGINS=https://app.example.com
HOST=0.0.0.0
PORT=8000
```

Sinh khóa server ngẫu nhiên bằng `openssl rand -hex 32`. Không push `.env`, API
key hoặc secret lên Git.

## 4. Build, test và ingest

```bash
docker compose build
docker compose run --rm api python -m pytest -q
docker compose run --rm api python ingest.py
docker compose up -d
docker compose ps
curl http://127.0.0.1:8000/health
```

Volume `finora_vector` giữ ChromaDB qua các lần thay container. Chỉ chạy lại
`ingest.py` khi tài liệu trong `knowledge/` thay đổi hoặc embedding model đổi.

## 5. Cấu hình Nginx và HTTPS

```bash
sudo cp deploy/nginx-finora.conf /etc/nginx/sites-available/finora
sudo sed -i 's/api.example.com/api.ten-mien-cua-ban.com/g' /etc/nginx/sites-available/finora
sudo ln -s /etc/nginx/sites-available/finora /etc/nginx/sites-enabled/finora
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d api.ten-mien-cua-ban.com
```

Kiểm tra từ máy khác:

```bash
curl https://api.ten-mien-cua-ban.com/health
curl -X POST https://api.ten-mien-cua-ban.com/api/chat \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <server-api-key>' \
  -d '{"message":"Điểm hòa vốn được tính thế nào?","history":[]}'
```

## 6. Cập nhật phiên bản mới

```bash
cd /opt/finora/app
git pull --ff-only
docker compose build
docker compose run --rm api python -m pytest -q
docker compose up -d --remove-orphans
docker image prune -f
```

Nếu `knowledge/` thay đổi, chạy trước khi khởi động lại:

```bash
docker compose run --rm api python ingest.py
```

## 7. Vận hành và khôi phục

```bash
docker compose ps
docker compose logs -f --tail=200 api
docker compose restart api
docker compose down
```

`docker compose down` không xóa dữ liệu RAG. Không dùng `docker compose down -v`
trừ khi chủ động muốn xóa volume ChromaDB và ingest lại từ đầu.

Để rollback, checkout tag/commit ổn định, build lại image và chạy `docker compose
up -d`. Nên sao lưu `.env`, thư mục `knowledge/` và export/backup volume định kỳ.
