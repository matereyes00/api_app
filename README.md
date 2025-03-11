# Django Media Tracking App

This project is a **Django-based media tracking application** that allows users to track movies, TV shows, books, board games, and video games they have watched, played, or read. It's a letterboxd, fable, and goodreads clone that features **Dockerized deployment** and **API integration** for a user to organize their media collections.

---

## 🚀 Features
- **User Authentication** (Login/Signup)
- **Watchlist & Past Consumption Tracking**
- **Custom Lists** (Public & Private, Collaboration, Ranking)
- **API Integration** (Fetching media data dynamically)
- **Django + PostgreSQL + Nginx (Dockerized Deployment)**

---

## 🛠️ Technologies Used
- **Backend**: Django, Django REST Framework
- **Frontend**: React (Planned)
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/matereyes00/api_app.git
cd api_app
```

### 2️⃣ Set Up Environment Variables
Create a `.env` file in the root directory and add:
```ini
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_NAME=postgres
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=db
DATABASE_PORT=5432
```

### 3️⃣ Build & Run with Docker
```bash
docker-compose up --build -d
```
This will:
- Build the Django app and PostgreSQL container
- Start the Nginx server for static files
- Expose the API at `http://localhost:8000/`

### 4️⃣ Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 5️⃣ Create a Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 🔥 Usage
### API Endpoints (Example)
- `POST /accounts/add_to_watchlist/<category>/<item_id>/` → Add media to watchlist
- `POST /accounts/add_to_consumed_media/<category>/<item_id>/` → Mark as watched/read
- `GET /api/lists/` → Fetch user-created lists

---

## 🔧 Troubleshooting
### ❌ Static Files Not Loading?
- Run `docker-compose exec web python manage.py collectstatic --noinput`
- Restart Nginx: `docker-compose restart nginx`

### ❌ Database Not Connecting?
- Ensure `DATABASE_HOST=db` matches the service name in `docker-compose.yml`
- Restart containers: `docker-compose down && docker-compose up -d`

---

## 📜 License
This project is licensed under the MIT License.

---

## 💡 Future Plans
✅ Improve UI with React
✅ Add list collaboration & ranking features
✅ Optimize API calls for better efficiency

---

**Contributions & feedback are welcome!** 🛠️