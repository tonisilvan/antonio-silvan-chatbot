# Antonio Silván Chatbot Backend

This is the FastAPI backend for the Antonio Silván AI chatbot that integrates with his personal website.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Add curriculum data (optional):**
   - Place your LinkedIn PDF as `data/linkedin.pdf`
   - Add a summary text file as `data/summary.txt`
   - If not provided, the system will use default data

4. **Run the server:**
   ```bash
   python app.py
   # or
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /chat` - Chat endpoint with evaluation system

## Features

- **Chat System**: AI-powered chat acting as Antonio Silván
- **Evaluation System**: Quality control using Gemini AI
- **Context Management**: Maintains conversation history
- **Error Handling**: Graceful fallbacks and error responses
- **CORS Support**: Ready for frontend integration

## Integration with Frontend

The frontend (index.html) communicates with this backend via:
- WebSocket-like HTTP requests to `/chat`
- Real-time typing indicators
- Message history management
- Error handling and user feedback

## Environment Variables

- `OPENAI_API_KEY`: Required for ChatGPT integration
- `GOOGLE_API_KEY`: Required for Gemini evaluation system

## Railway Deployment

This project is fully configured for Railway deployment. See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed instructions.

### Quick Deploy to Railway

1. **Push to Git:**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to https://railway.com
   - Click "New Project"
   - Connect your Git repository
   - Railway will automatically detect and deploy the Python app

3. **Configure Environment Variables:**
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

4. **Update Frontend URL:**
   After deployment, update the API URL in `index.html` to your Railway URL.

## Testing

You can test the API directly:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is your experience with Java?",
    "history": []
  }'
```

## Pre-Deployment Check

Run the deployment check script to verify everything is ready:

```bash
python deploy_check.py
```
