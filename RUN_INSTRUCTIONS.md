# SimWorld Platform - Setup & Run Instructions

## Prerequisites

- **Docker & Docker Compose** (for PostgreSQL, Redis, and Neo4j)
- **Python 3.12+**
- **Node.js v18+ & npm** (for the Next.js Frontend)

---

## 1. Environment Setup

First, navigate to the backend directory and configure your environment variables.

```bash
cd ~/development/projects/simworld/backend
cp ../.env.example .env
```

**Crucial Step:** Open the `.env` file and insert your actual `LLM_API_KEY` (e.g., an OpenAI key) to enable the agents and graph extraction to work.

## 2. Start the Infrastructure (Database, Redis, Graph)

From the root project directory, spin up the Docker containers:

```bash
cd ~/development/projects/simworld
docker-compose up -d
```

_(This starts PostgreSQL 16, Redis 7, and Neo4j 5 in the background.)_

## 3. Initialize the Backend & Database

Open a terminal, navigate to the backend, set up the virtual environment, and initialize the schema:

```bash
cd ~/development/projects/simworld/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Initialize the database tables
python init_db.py
```

## 4. Run the API Server

Keep the backend terminal open and start the FastAPI server:

```bash
uvicorn api.main:app --reload --port 8000
```

_(The API is now running at `http://localhost:8000/api`)_

## 5. Run the Celery Worker

Open a **new terminal window** to run the background worker (which processes simulations and report generation):

```bash
cd ~/development/projects/simworld/backend
source .venv/bin/activate

# Start the Celery worker
celery -A workers.celery_app worker --loglevel=info
```

## 6. Run the Frontend Dashboard

Open a **third terminal window** to start the Next.js frontend:

```bash
cd ~/development/projects/simworld/frontend
npm install
npm run dev
```

_(The frontend is now running at `http://localhost:3001/login`)_

---

## Testing it Out

1. **Create an Organization:** Before logging in, you need an organization in the database. I've created a script to do this for you:

   ```bash
   cd ~/development/projects/simworld
   source backend/.venv/bin/activate
   python demo.py
   ```

   _(This will create "Acme Corp" in your database)._

2. **Login:** Go to `http://localhost:3001/login` and log in with:
   - **Username:** `Acme Corp`
   - **Password:** _(any password works for this demo environment)_

3. **Use the Platform:**
   - Create a World.
   - Upload a text file as "Seed Material" to build your knowledge graph.
   - Click "Generate AI Agents" to populate your world.
   - Click "Run Simulation" to execute the OASIS engine and read the generated report!
