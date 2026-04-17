# Railway Deployment Guide

## Overview
This guide explains how to deploy the Antonio Silván Chatbot API to Railway.

## Prerequisites
- Railway account (Pro account recommended)
- Git repository with the project
- OpenAI API key (optional but recommended)
- Google API key (optional but recommended for evaluation)

## Step 1: Prepare Your Repository

1. **Push your code to a Git repository** (GitHub, GitLab, etc.)
2. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

## Step 2: Deploy to Railway

1. **Login to Railway** at https://railway.com
2. **Click "New Project"**
3. **Connect your Git repository**
4. **Select the AntonioSilvanBack directory**
5. **Railway will automatically detect the Python application**

## Step 3: Configure Environment Variables

In your Railway project settings, add these environment variables:

### Required for Full Functionality
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Configuration
```
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
PORT=8000
HOST=0.0.0.0
```

## Step 4: Update Frontend URL

After deployment, Railway will give you a URL like:
`https://your-app-name.up.railway.app`

Update this line in `index.html`:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'  // Development
    : 'https://your-actual-railway-url.up.railway.app';  // Production
```

## Step 5: Deploy Frontend

For the frontend, you have several options:

### Option A: Railway Static Site
1. Create a new Railway project for the frontend
2. Point it to your repository
3. Configure it as a static site
4. Set the build command to `echo "No build needed"`
5. Set the publish directory to the root

### Option B: Vercel/Netlify
Deploy your `index.html` to Vercel or Netlify for better static hosting.

### Option C: GitHub Pages
1. Enable GitHub Pages on your repository
2. Deploy `index.html` as a GitHub Page

## Step 6: Test the Deployment

1. **Check the API health:**
   ```
   GET https://your-app-name.up.railway.app/health
   ```

2. **Test the chat endpoint:**
   ```bash
   curl -X POST "https://your-app-name.up.railway.app/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, what can you tell me about Antonio?",
       "history": []
     }'
   ```

3. **Test the frontend chat interface**

## Railway Configuration Files

### `railway.json`
Configures build and deployment settings:
- Uses NIXPACKS builder
- Sets health check path
- Configures restart policy

### `nixpacks.toml`
Defines how to build the Python application:
- Sets up Python 3.11
- Installs dependencies
- Configures startup command

### `Procfile`
Alternative deployment configuration (Railway will use this if available)

## Troubleshooting

### Common Issues

1. **Build fails:**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **CORS errors:**
   - Set `ALLOWED_ORIGINS` to your frontend domain
   - Include both HTTP and HTTPS versions

3. **API key errors:**
   - Ensure environment variables are set correctly
   - Check that API keys have proper permissions

4. **Timeout issues:**
   - Railway has a 30-second timeout for free accounts
   - Pro accounts have longer timeouts

### Logs and Monitoring

- Check Railway logs for deployment issues
- Monitor the health endpoint
- Use Railway's built-in monitoring

## Production Optimizations

1. **Enable caching** for API responses
2. **Set up monitoring** for error tracking
3. **Configure rate limiting** if needed
4. **Use Railway's Pro features** for better performance

## Cost Considerations

- **Free tier:** Limited hours, good for testing
- **Pro tier:** Better performance, no sleep time
- **API costs:** OpenAI and Google API usage

## Security Notes

1. **Never commit API keys** to your repository
2. **Use Railway's environment variables** for secrets
3. **Enable HTTPS** (Railway does this automatically)
4. **Consider rate limiting** for production use

## Support

- Railway documentation: https://docs.railway.app/
- FastAPI documentation: https://fastapi.tiangolo.com/
- OpenAI API documentation: https://platform.openai.com/docs
