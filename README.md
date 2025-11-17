# Sumble Backend Project

A Python backend project with Postgres, Docker, and Docker Compose setup.

## Prerequisites

- Docker and Docker Compose (✅ Already installed)
- Python 3.11+ (if running locally without Docker)
- pgAdmin4 (✅ Already installed) for database queries

## Setup Instructions

### 1. Environment Configuration

The `.env` file has been created with default database credentials. You can modify them if needed.

### 2. Start the Database

Start the Postgres database using Docker Compose:
```bash
docker compose up -d
```

This will:
- Start a Postgres 15 container
- Create a database named `sumble_db` (or as specified in `.env`)
- Expose Postgres on port 5432

### 3. Verify Database is Running

Check that the container is running:
```bash
docker compose ps
```

You should see the `sumble-postgres` container running.

### 4. Connect with pgAdmin4

To connect to the database using pgAdmin4:

1. Open pgAdmin4
2. Right-click on "Servers" → "Create" → "Server"
3. In the "General" tab:
   - Name: `Sumble Local`
4. In the "Connection" tab:
   - Host name/address: `localhost`
   - Port: `5432`
   - Maintenance database: `sumble_db`
   - Username: `postgres` (or your `POSTGRES_USER` from `.env`)
   - Password: `postgres` (or your `POSTGRES_PASSWORD` from `.env`)
5. Click "Save"

### 5. Set Up Python Environment

Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
# venv\Scripts\activate  # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python src/main.py
```

The application will test the database connection on startup.

## Docker Commands

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose down
```

### Stop and remove volumes (⚠️ deletes data)
```bash
docker compose down -v
```

### View logs
```bash
docker compose logs -f postgres
```

### Execute SQL in the container
```bash
docker compose exec postgres psql -U postgres -d sumble_db
```

## Project Structure

```
sumble/
├── src/
│   └── main.py              # Main application entry point
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Application Docker image
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Database Connection

The application uses the `psycopg2` library to connect to Postgres. Connection details are read from environment variables:

- `POSTGRES_USER`: Database user (default: `postgres`)
- `POSTGRES_PASSWORD`: Database password (default: `postgres`)
- `POSTGRES_DB`: Database name (default: `sumble_db`)
- `POSTGRES_HOST`: Database host (default: `localhost`)
- `POSTGRES_PORT`: Database port (default: `5432`)

## Dependencies

- `psycopg`: PostgreSQL adapter for Python (version 3, compatible with Python 3.14+)
- `python-dotenv`: Load environment variables from `.env` file

## Next Steps

1. ✅ Database is running
2. ✅ Application can connect to the database
3. ✅ You can query the database using pgAdmin4
4. Ready to start building your backend features!

## Building for Production

Build and run the Docker container:
```bash
docker build -t sumble-backend .
docker run --env-file .env -p 3000:3000 sumble-backend
```

## Troubleshooting

### Port already in use
If port 5432 is already in use, change `POSTGRES_PORT` in your `.env` file to a different port (e.g., `5433`).

### Cannot connect to database
- Ensure Docker Compose is running: `docker compose ps`
- Check database logs: `docker compose logs postgres`
- Verify your `.env` file has the correct credentials

### Database connection timeout
- Make sure the database container is healthy: `docker compose ps`
- Wait a few seconds after starting the container for it to fully initialize

### ModuleNotFoundError
- Ensure your virtual environment is activated: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
