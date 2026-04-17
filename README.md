# YT_ELT - YouTube Data Pipeline

A robust ETL (Extract, Load, Transform) pipeline that extracts video statistics from a YouTube playlist and loads them into a PostgreSQL data warehouse with data quality checks.

## 📋 Overview

YT_ELT is an Apache Airflow-based data pipeline that:

- **Extracts** YouTube video data from a specified playlist using the YouTube API
- **Loads** raw data into a staging PostgreSQL database
- **Transforms** data from staging to a core/production schema
- **Validates** data quality using Soda framework

The pipeline runs on a daily schedule and is fully containerized with Docker Compose.

## 🏗️ Architecture

```text
YouTube API
    ↓
Extract (get_playlist_id → get_video_ids → extract_video_data)
    ↓
Save to JSON
    ↓
Load to Staging (PostgreSQL)
    ↓
Transform to Core Schema
    ↓
Data Quality Checks (Soda)
```

## 🛠️ Tech Stack

- **Orchestration:** Apache Airflow 2.9.2
- **Execution:** CeleryExecutor with Redis
- **Database:** PostgreSQL 13
- **Data Quality:** Soda Framework
- **API:** YouTube Data API v3
- **Container:** Docker & Docker Compose
- **Language:** Python 3.11+

## 📦 Prerequisites

- Docker & Docker Compose
- YouTube Data API Key
- Python 3.11+ (for local development)
- Git

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/anusorn05379/YT_ELT.git
cd YT_ELT
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:
```bash
# YouTube API Configuration
API_KEY=your_youtube_api_key
CHANNEL_HANDLE=@your_channel_handle

# PostgreSQL Configuration
POSTGRES_CONN_HOST=postgres
POSTGRES_CONN_PORT=5432
POSTGRES_CONN_USERNAME=root
POSTGRES_CONN_PASSWORD=root_password

# Airflow Metadata Database
METADATA_DATABASE_NAME=airflow_metadata
METADATA_DATABASE_USERNAME=airflow_user
METADATA_DATABASE_PASSWORD=airflow_password

# ELT Database
ELT_DATABASE_NAME=yt_elt
ELT_DATABASE_USERNAME=elt_user
ELT_DATABASE_PASSWORD=elt_password

# Celery Backend
CELERY_BACKEND_NAME=celery_backend
CELERY_BACKEND_USERNAME=celery_user
CELERY_BACKEND_PASSWORD=celery_password

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow
FERNET_KEY=your_fernet_key_here
DOCKERHUB_NAMESPACE=your_dockerhub_username
DOCKERHUB_REPOSITORY=yt_elt
```

**Get YouTube API Key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create API credentials (API Key)
5. Copy the key to `.env`

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Access Airflow Web UI

- URL: `http://localhost:8080`
- Default credentials: `airflow / airflow`

## 📊 Project Structure

```text
YT_ELT/
├── dags/                    # Airflow DAG definitions
│   └── main.py             # Main ETL DAG
├── api/                    # YouTube API integration
│   └── video_stats.py      # API functions
├── datawarehoues/          # Data warehouse logic
│   └── dwh.py              # Staging & core tables
├── dataquality/            # Data quality checks
│   └── soda.py             # Soda validation rules
├── include/                # Soda configuration
│   └── soda/               # .yml configuration files
├── tests/                  # Unit & integration tests
│   └── unit_test.py        # Test suite
├── docker/                 # Docker setup
│   └── postgres/           # PostgreSQL init scripts
├── .github/workflows/      # CI/CD pipeline
├── docker-compose.yaml     # Service orchestration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔄 DAG Workflow

### DAG: `produce_json`

Runs daily at 2 PM (14:00)

1. Get YouTube channel playlist ID
2. Extract all video IDs from playlist
3. Fetch video statistics (views, likes, etc.)
4. Save data to JSON file

### DAG: `load_data_warehouse`

Triggered after `produce_json` completes

1. Load JSON data to staging schema
2. Transform data to core schema
3. Run data quality validations

### DAG: `data_quality`

Runs data quality checks using Soda:

- Check for null values
- Validate data types
- Ensure referential integrity
- Check for duplicates

## 💻 Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
docker-compose exec airflow-webserver python -m pytest tests/
```

### View Logs

```bash
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-worker
```

## 🔗 Database Connection

**Metadata Database (Airflow):**

```text
postgresql://airflow_user:airflow_password@postgres:5432/airflow_metadata
```

**ELT Database (Data Warehouse):**

```text
postgresql://elt_user:elt_password@postgres:5432/yt_elt
```

## 🛑 Troubleshooting

### Services Won't Start

```bash
docker-compose down -v
docker-compose up -d
```

### Check Service Health

```bash
docker-compose ps
```

### View Airflow Logs

```bash
docker-compose logs airflow-scheduler
docker-compose logs airflow-worker
```

### Database Connection Issues

- Ensure PostgreSQL is running: `docker-compose logs postgres`
- Check connection string in environment variables
- Verify credentials in `.env` file

## 📝 Notes

- `.env` file should NOT be committed (it's in `.gitignore`)
- CI/CD pipeline requires GitHub Actions workflow scope permission
- Requires active YouTube API quota
- Daily schedule is UTC timezone: `0 14 * * *` (2 PM Malta time)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

- **GitHub:** [@anusorn05379](https://github.com/anusorn05379)
- **Email:** <kiwanusorn60122970122@gmail.com>
