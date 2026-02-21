import json
from groq import Groq
import os
#Delete this key before you commit to GitHub!
# Pulls the key safely from the system environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def evaluate_job(title: str, description: str) -> dict:
    """Passes job details to Groq and returns a structured JSON evaluation."""
    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = """
    You are an expert technical recruiter evaluating jobs for a Data/AI Engineer. 
    The candidate's core skills are: n8n, RAG, LLM fine-tuning, Python, API integration, and chatbots.
    
    You MUST output ONLY a valid JSON object with exactly these keys:
    - "score": integer (1-10) on how well it matches the candidate's skills.
    - "summary": A very brief, one-sentence summary of the role.
    - "is_agency": boolean (true if it seems to be a recruiting agency, false if direct client).
    """
    
    user_prompt = f"Job Title: {title}\nJob Details: {description}"
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1, 
            response_format={"type": "json_object"} 
        )
        return json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        return {"score": 0, "summary": f"Evaluation failed: {e}", "is_agency": False}

# --- Testing Block ---
if __name__ == "__main__":
    sample_title = "AI Engineer - RAG & Python"
    sample_desc = "We need someone to build autonomous agents using Python, n8n, and fine-tuned LLMs."
    
    result = evaluate_job(sample_title, sample_desc)
    print(json.dumps(result, indent=2))