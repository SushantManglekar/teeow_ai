# 🧠 Teeow AI – AI Assistant Service

A FastAPI-based microservice providing AI-powered chat functionality with conversation history and user management.

## 🚀 Features

- **FastAPI Backend**: High-performance API with async support
- **AI Integration**: Seamless integration with LLaMA models via Ollama
- **Database**: PostgreSQL for persistent storage of chat history and user data
- **RESTful API**: Well-documented endpoints with Swagger UI
- **Environment Configuration**: Easy setup with `.env` configuration
- **Containerized**: Ready for Docker deployment

## 🏗️ Project Structure

```
teeow_ai/
├── AI_assistant/             # Main application package
│   ├── app/                  # Application code
│   │   ├── api/              # API routes
│   │   ├── core/             # Core functionality
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic models
│   │   └── main.py           # Application entry point
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Example environment variables
├── .github/workflows/        # GitHub Actions workflows
├── docker/                   # Docker configuration
├── docs/                     # Documentation
└── README.md                # This file
```

## 🛠️ Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker (optional, for containerized deployment)
- Ollama (for local model serving)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/monaresh/teeow_ai.git
cd teeow_ai
```

### 2. Set Up Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r AI_assistant/requirements.txt
```

### 3. Database Setup

1. Create a new PostgreSQL database
2. Execute the SQL script to set up the schema:
   ```bash
   psql -U your_username -d your_database -f AI_assistant/schema.sql
   ```

### 4. Configuration

1. Copy the example environment file:
   ```bash
   cp AI_assistant/.env.example AI_assistant/.env
   ```
2. Update the `.env` file with your database credentials and other settings

### 5. Start Ollama with LLaMA Model

```bash
# Install Ollama (if not already installed)
# Download from https://ollama.ai/

# Pull and run the LLaMA model
ollama pull llama3.2
ollama run llama3.2
```

### 6. Run the Application

```bash
cd AI_assistant
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📚 API Documentation

Once the application is running, access the interactive API documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 🐳 Docker Deployment

```bash
# Build the Docker image
docker build -t teeow-ai .

# Run the container
docker run -p 8000:8000 --env-file AI_assistant/.env teeow-ai
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Ollama](https://ollama.ai/)
- [LLaMA](https://ai.meta.com/llama/)
- [PostgreSQL](https://www.postgresql.org/)

