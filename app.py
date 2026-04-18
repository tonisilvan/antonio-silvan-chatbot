from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import json

load_dotenv()

app = FastAPI(title="Antonio Silván Chatbot API")

# Configure CORS
# Get allowed origins from environment variable or default to localhost for development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000").split(",")

# In production, you should set ALLOWED_ORIGINS to your frontend domain
# For Railway deployment, you might want to set it to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize OpenAI clients with error handling
openai_api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key configured: {bool(openai_api_key)}")

try:
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        OPENAI_AVAILABLE = True
        print("OpenAI client initialized successfully")
    else:
        print("Warning: OPENAI_API_KEY not found in environment variables")
        openai_client = None
        OPENAI_AVAILABLE = False
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    openai_client = None
    OPENAI_AVAILABLE = False

try:
    gemini_client = OpenAI(
        api_key=os.getenv("GOOGLE_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Warning: Gemini client initialization failed: {e}")
    gemini_client = None
    GEMINI_AVAILABLE = False

# Load Antonio Silván's data
def load_curriculum_data():
    """Load PDF and summary data for Antonio Silván"""
    resume_text = ""
    linkedin_text = ""
    summary_text = ""
    
    # Try to load Resume PDF
    try:
        resume_path = "data/antonio_silvan_resume_en.pdf"
        if os.path.exists(resume_path):
            reader = PdfReader(resume_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    resume_text += text
            print(f"Resume PDF loaded successfully: {len(resume_text)} characters")
    except Exception as e:
        print(f"Error loading Resume PDF: {e}")
    
    # Try to load LinkedIn Profile PDF
    try:
        linkedin_path = "data/Profile.pdf"
        if os.path.exists(linkedin_path):
            reader = PdfReader(linkedin_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    linkedin_text += text
            print(f"LinkedIn Profile PDF loaded successfully: {len(linkedin_text)} characters")
    except Exception as e:
        print(f"Error loading LinkedIn Profile PDF: {e}")
    
    # Try to load summary text
    try:
        summary_path = "data/summary.txt"
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()
            print(f"Summary text loaded successfully: {len(summary_text)} characters")
    except Exception as e:
        print(f"Error loading summary: {e}")
    
    # Fallback data if files don't exist
    if not resume_text and not linkedin_text and not summary_text:
        summary_text = """
        Antonio Silván is a Full-Stack Engineer & Technical Lead with extensive experience 
        building backend systems, APIs, and modern web applications. He specializes in 
        React, TypeScript, Java, Spring, and Kubernetes. He has worked on various projects 
        including GraphQL services, Spring Boot APIs, API gateways, and full-stack applications 
        deployed on Kubernetes. He is interested in scalable architectures, distributed systems, 
        and modern web technologies.
        """
    
    return resume_text, linkedin_text, summary_text

# Load data at startup
resume_data, linkedin_data, summary_data = load_curriculum_data()
name = "Antonio Silván"

# Create system prompt
system_prompt = f"""You are acting as {name}. You are answering questions on {name}'s website, 
and you MUST ONLY respond to questions related to {name}'s career, background, skills, experience, projects, education, or professional expertise.

CRITICAL RULES:
1. ONLY answer questions about {name}'s professional career, skills, experience, projects, education, or work history
2. If a question is NOT related to {name}'s professional background, you MUST respond with: "This topic is not related to my professional experience. I can only answer questions about my career, skills, projects, and work background."
3. Do NOT engage in conversations about personal topics, hobbies, opinions on unrelated subjects, current events, or anything not directly connected to {name}'s professional life
4. Do NOT provide advice on topics unrelated to {name}'s expertise
5. Be polite but firm in maintaining these boundaries
6. Always stay in character as {name} but within these strict professional boundaries

Your responsibility is to represent {name} for professional interactions on this website, as if talking to a potential client, recruiter, or employer. You are professional and focused on career-related discussions only."""

system_prompt += f"\n\n## Resume:\n{resume_data}\n\n## LinkedIn Profile:\n{linkedin_data}\n\n## Summary:\n{summary_data}\n\n"
system_prompt += f"With this context, answer ONLY professional questions about {name}. For any non-professional questions, use the exact rejection message specified above."

# Evaluation system prompt
evaluator_system_prompt = f"""You are an evaluator that decides whether a response to a question is acceptable. 
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. 
The Agent is playing the role of {name} and is representing {name} on their website. 
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. 
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details."""

evaluator_system_prompt += f"\n\n## Resume:\n{resume_data}\n\n## LinkedIn Profile:\n{linkedin_data}\n\n## Summary:\n{summary_data}\n\n"
evaluator_system_prompt += "With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str
    evaluation_passed: bool
    feedback: Optional[str] = None

def evaluator_user_prompt(reply: str, message: str, history: List[ChatMessage]) -> str:
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{[f'{h.role}: {h.content}' for h in history]}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt

def evaluate_reply(reply: str, message: str, history: List[ChatMessage]) -> Evaluation:
    """Evaluate the agent's reply using Gemini"""
    if not GEMINI_AVAILABLE:
        # Fallback: accept the reply if Gemini is not available
        return Evaluation(is_acceptable=True, feedback="Evaluation service unavailable")
    
    try:
        messages = [
            {"role": "system", "content": evaluator_system_prompt}, 
            {"role": "user", "content": evaluator_user_prompt(reply, message, history)}
        ]
        response = gemini_client.beta.chat.completions.parse(
            model="gemini-2.5-flash", 
            messages=messages, 
            response_format=Evaluation
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Evaluation error: {e}")
        # Fallback: accept the reply if evaluation fails
        return Evaluation(is_acceptable=True, feedback="Evaluation service unavailable")

def rerun_reply(reply: str, message: str, history: List[ChatMessage], feedback: str) -> str:
    """Rerun the chat with feedback"""
    try:
        import requests
        updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        
        messages = [{"role": "system", "content": updated_system_prompt}] + [{"role": h.role, "content": h.content} for h in history] + [{"role": "user", "content": message}]
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return "I apologize, but I encountered an error while processing your request. Please try again."
            
    except Exception as e:
        print(f"Rerun error: {e}")
        return "I apologize, but I encountered an error while processing your request. Please try again."

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with evaluation system"""
    try:
        
        # Check for special conditions (like the patent example in the notebook)
        system = system_prompt
        if "patent" in request.message.lower():
            system += "\n\nEverything in your reply needs to be in pig latin - it is mandatory that you respond only and entirely in pig latin"
        
        # Convert history to proper format
        history_dict = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        messages = [{"role": "system", "content": system}] + history_dict + [{"role": "user", "content": request.message}]
        
        # Get initial response using direct API call
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                # Fallback response
                fallback_response = f"""Hello! I'm Antonio Silván's AI assistant. I can answer questions about my background, skills, and experience based on the following information:

{summary_data[:500]}...

To get full AI-powered responses, please configure the OpenAI API key in the backend. For now, I can provide basic information about my profile.

What would you like to know about my experience or skills?"""
                reply = fallback_response
                
        except Exception as e:
            print(f"Chat API error: {e}")
            # Fallback response
            fallback_response = f"""Hello! I'm Antonio Silván's AI assistant. I can answer questions about my background, skills, and experience based on the following information:

{summary_data[:500]}...

To get full AI-powered responses, please configure the OpenAI API key in the backend. For now, I can provide basic information about my profile.

What would you like to know about my experience or skills?"""
            reply = fallback_response
        
        # Evaluate the response
        evaluation = evaluate_reply(reply, request.message, request.history)
        
        if evaluation.is_acceptable:
            return ChatResponse(
                reply=reply,
                evaluation_passed=True,
                feedback=None
            )
        else:
            # Rerun with feedback
            print(f"Failed evaluation - retrying. Feedback: {evaluation.feedback}")
            new_reply = rerun_reply(reply, request.message, request.history, evaluation.feedback)
            return ChatResponse(
                reply=new_reply,
                evaluation_passed=False,
                feedback=evaluation.feedback
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Antonio Silván Chatbot API is running", "name": name}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "data_loaded": bool(linkedin_data or summary_data),
        "name": name
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check configuration"""
    return {
        "openai_available": OPENAI_AVAILABLE,
        "gemini_available": GEMINI_AVAILABLE,
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "google_api_key_set": bool(os.getenv("GOOGLE_API_KEY")),
        "allowed_origins": allowed_origins,
        "data_loaded": {
            "summary": bool(summary_data),
            "linkedin": bool(linkedin_data)
        }
    }

@app.get("/test-openai")
async def test_openai():
    """Test OpenAI connection directly"""
    try:
        import requests
        api_key = os.getenv("OPENAI_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else "No response",
            "api_key_length": len(api_key) if api_key else 0,
            "api_key_starts_with_sk": api_key.startswith("sk-") if api_key else False
        }
    except Exception as e:
        return {
            "error": str(e),
            "api_key_length": len(api_key) if api_key else 0,
            "api_key_starts_with_sk": api_key.startswith("sk-") if api_key else False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
