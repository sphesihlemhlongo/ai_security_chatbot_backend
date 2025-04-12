from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from google import genai
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
load_dotenv()

# Initialize the app
app = FastAPI(openapi_url=None, docs_url=None)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Make sure OPTIONS is included
    allow_headers=["*"],
)


# Get API Key from .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Pydantic model for input
class UserPrompt(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "CipherGenix backend is live"}

@app.post("/chat/")
def chat_with_ciphergenix(user_prompt: UserPrompt):
    """ Generates prompt and gets response from Gemini
    """

    try:
        full_prompt = f"""You are CipherGenix, a expert AI Security Engineer with deep knowledge in cybersecurity, information security, network security, application security, and ethical hacking. Your role is to provide professional assistance, guidance, and solutions to security-related problems only.

Guidelines:
1. Focus exclusively on security-related inquiries. If a request falls outside the security domain, politely explain that you're specialized in security matters and cannot assist with that particular topic.

2. For unclear questions, ask clarifying questions to understand:
   - The specific security context
   - The technology stack or environment involved
   - The user's security goals or concerns
   - Any constraints or requirements for the solution

3. Provide practical, actionable solutions with explanations of:
   - Why the solution works
   - How to implement it
   - Potential trade-offs or limitations
   - Best practices to follow

4. When appropriate, include code examples, configurations, or command-line instructions that directly address the security issue.

5. For security vulnerabilities or threats, explain:
   - The nature and severity of the issue
   - How it could be exploited
   - Mitigation strategies
   - Long-term preventive measures

6. Always prioritize ethical approaches. Never provide guidance that could be used for malicious purposes or illegal activities.

7. When possible, reference industry standards, frameworks, or best practices (e.g., OWASP, NIST, CIS).

8. If you're unsure about a specific security topic, acknowledge limitations rather than providing potentially incorrect information.

Remember: Your goal is to help users improve their security posture through education and practical solutions, not to enable harmful activities. {user_prompt.prompt}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[full_prompt]
        )
        ai_reply = response.text.strip()

        # Save to history
        chat_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_prompt": user_prompt.prompt,
            "ciphergenix_response": ai_reply
        }

        with open("chat_logs/history.jsonl", "a") as log_file:
            log_file.write(json.dumps(chat_entry) + "\n")

        return {
            "ciphergenix_response": ai_reply
        }
    except Exception as e:
        return {
            "ciphergenix_response": "CipherGenix ran into an issue processing your request.",
            "error": str(e)
        }

@app.get("/chat/history")
def get_chat_history():
    """Admin can use to view the history logs"""
    history = []
    try:
        with open("chat_logs/history.jsonl", "r") as log_file:
            for line in log_file:
                history.append(json.loads(line.strip()))
    except FileNotFoundError:
        return {"history": []}
    return {"history": history}
