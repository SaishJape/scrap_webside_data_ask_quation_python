# AI Chatbot Widget API

A FastAPI-based chatbot system that can crawl websites, store content as embeddings, and provide intelligent responses using Google's Gemini AI.

## Project Structure

```
project-root/
│
├── app/                          # 🔧 Main app code
│   ├── main.py                   # 🚀 FastAPI app entrypoint
│   ├── config.py                 # ⚙️ Centralized config & .env loader (Pydantic)
│   │
│   ├── api/                      # 📡 FastAPI endpoints (grouped by feature)
│   │   ├── routes.py             # All routes defined here
│   │   └── __init__.py
│   │
│   ├── db/                       # 🛢️ Database layer
│   │   ├── mysql.py              # MySQL connector & queries
│   │   ├── quadrant.py           # QuadrantDB SDK or API logic
│   │   └── models.py             # Pydantic/SQLAlchemy models
│   │
│   ├── services/                 # 🤖 Business logic / integrations
│   │   ├── gemini.py             # LLM service using Gemini API
│   │   ├── llm.py                # Wrapper for using other LLMs
│   │   ├── key_manager.py        # Handles all API key loading/rotation
│   │   └── __init__.py
│   │
│   └── utils/                    # 🧰 Utility functions
│       ├── logger.py             # Logger config
│       ├── common.py             # Reusable logic/helpers
│       └── __init__.py
│
├── .env                          # 🔐 All secret keys (NEVER push to GitHub)
├── requirements.txt              # 📦 Dependencies
└── README.md                     # 📘 Project documentation
```

## Features

- **Website Crawling**: Automatically crawls websites and extracts content
- **Semantic Search**: Uses sentence transformers to create embeddings for intelligent search
- **Vector Database**: Stores embeddings in Qdrant for fast similarity search
- **AI Responses**: Generates contextual responses using Google Gemini
- **Session Management**: Maintains separate collections for different chat sessions
- **API Key Management**: Supports multiple API keys with rotation capabilities
- **Modular Architecture**: Clean separation of concerns for easy maintenance

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd project-root
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Qdrant database**
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or install locally - visit https://qdrant.tech/documentation/quick-start/
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Update the `.env` file with your configuration:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=http://localhost:6333

# Optional - for multiple API keys
GEMINI_API_KEY_1=backup_key_1
GEMINI_API_KEY_2=backup_key_2
```

## Usage

1. **Start the application**
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

2. **Initialize a chat session with a website**
```bash
curl -X POST "http://localhost:8000/embed" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

3. **Chat with the content**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is this website about?", "session_id": "your_session_id"}'
```

## API Endpoints

### POST /embed
Initialize a chat session by crawling and processing a website.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Content successfully processed and stored",
  "data": {
    "session_id": "uuid-session-id",
    "url": "https://example.com",
    "statistics": {
      "total_chunks": 150,
      "average_chunk_size": 45.2,
      "total_words": 6780,
      "processed_urls": 12,
      "total_urls_found": 15
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### POST /chat
Send a message and get an AI-powered response based on the website content.

**Request Body:**
```json
{
  "query": "What services do you offer?",
  "session_id": "uuid-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Response generated successfully",
  "data": {
    "session_id": "uuid-session-id",
    "query": "What services do you offer?",
    "response": "Based on the website content, we offer..."
  },
  "timestamp": "2024-01-15T10:31:00"
}
```

## Development

### Adding New LLM Providers

1. Create a new provider class in `app/services/llm.py`
2. Implement the `LLMProvider` interface
3. Add API key configuration to `app/services/key_manager.py`
4. Update environment variables in `.env`

### Adding MySQL Support

1. Implement connection logic in `app/db/mysql.py`
2. Add MySQL models to `app/db/models.py`
3. Update configuration in `app/config.py`

### Extending Functionality

- **Custom Text Processing**: Modify functions in `app/utils/common.py`
- **Enhanced Logging**: Update `app/utils/logger.py`
- **New API Endpoints**: Add routes to `app/api/routes.py`

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | None | Yes |
| `QDRANT_URL` | Qdrant database URL | http://localhost:6333 | Yes |
| `CHUNK_SIZE` | Text chunk size for processing | 500 | No |
| `SEARCH_LIMIT` | Number of similar chunks to retrieve | 3 | No |
| `LOG_LEVEL` | Logging level | INFO | No |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   - Ensure Qdrant is running on the specified URL
   - Check firewall settings

2. **Gemini API Issues**
   - Verify API key is valid
   - Check API quotas and limits

3. **Website Crawling Issues**
   - Some websites may block automated crawling
   - Check robots.txt and respect rate limits

### Support

For support and questions, please open an issue on GitHub or contact the development team.