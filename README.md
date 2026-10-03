# FastAPI Postgres API

REST API (FastAPI + SQLAlchemy async + asyncpg) đọc/ghi dữ liệu PostgreSQL, xác thực bằng JWT.

## Cấu trúc

```
app/
├── main.py                 # Tạo app, CORS, /health
├── core/                   # config (.env), security (JWT, bcrypt), logging
├── db/                     # engine, session, Base
├── models/                 # SQLAlchemy models (map với bảng trong DB)
├── schemas/                # Pydantic request/response
├── repositories/           # Truy vấn DB
└── api/
    ├── deps.py             # DB session, get_current_user, phân quyền
    └── v1/endpoints/       # auth, users, items
scripts/create_superuser.py # Tạo bảng api_users + tài khoản admin
```

## Chạy

```bash
cp .env.example .env            # sửa thông tin DB và JWT_SECRET_KEY
docker compose up -d --build
docker compose exec api python -m scripts.create_superuser admin
```

Swagger UI: http://localhost:8000/docs (bấm **Authorize** để đăng nhập). Đổi cổng: `API_PORT=8010 docker compose up -d`.

**Dùng Postgres có sẵn:** xoá service `db` (và `depends_on`) trong `docker-compose.yml`, đặt `POSTGRES_HOST` trong `.env`
(`host.docker.internal` nếu DB chạy trên máy bạn).

Chạy local không cần Docker:

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints (`/api/v1`)

| Method | Path | Quyền | Mô tả |
|---|---|---|---|
| POST | `/auth/login` | public | Form `username`, `password` → JWT |
| GET | `/auth/me` | user | Thông tin user hiện tại |
| POST | `/users` | superuser | Tạo user |
| GET | `/items` | user | Danh sách, filter qua query (`name`, `min_price`, `max_price`, `sort_by`, `sort_order`, `skip`, `limit`) |
| POST | `/items/search` | user | Giống GET nhưng filter gửi trong JSON body |
| GET | `/items/{id}` | user | Lấy 1 bản ghi |
| POST | `/items` | user | Tạo bản ghi |
| GET | `/health` | public | Kiểm tra kết nối DB |

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/v1/auth/login -d "username=admin&password=..." | jq -r .access_token)
curl -H "Authorization: Bearer $TOKEN" "localhost:8000/api/v1/items?min_price=100000&sort_by=price"
```

## Thêm bảng mới

1. `app/models/<ten>.py` — khai báo model khớp với bảng có sẵn (`__tablename__`, cột).
2. `app/schemas/<ten>.py` — schema Read/Create/Query.
3. `app/repositories/<ten>_repo.py` — truy vấn.
4. `app/api/v1/endpoints/<ten>.py` — router, thêm `dependencies=[Depends(get_current_user)]`.
5. Đăng ký router trong `app/api/v1/router.py`.

## Lưu ý production

- `JWT_SECRET_KEY` phải là chuỗi ngẫu nhiên dài; không commit `.env`.
- Đặt `DOCS_ENABLED=false` nếu không muốn public Swagger.
- Nên dùng user DB chỉ có quyền cần thiết (SELECT/INSERT trên các bảng API dùng).
- Chạy sau reverse proxy (nginx/Traefik) có HTTPS; số worker chỉnh qua `WEB_CONCURRENCY`.
