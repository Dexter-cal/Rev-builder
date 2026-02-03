import requests
import json
from sqlalchemy.orm import Session
from app.models import models

class AIEngineService:
    @staticmethod
    def analyze_code(db: Session, model_id: int, code: str, task: str):
        model = db.query(models.AIModel).filter(models.AIModel.id == model_id).first()
        if not model or not model.api_key or model.api_key == "sk-...":
            return {"error": "AI Model not configured with a valid API key. Please check Settings."}

        # Simplified for demonstration. In a real app, this would use different
        # libraries for OpenAI, Gemini, etc.
        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"Task: {task}\n\nAnalyze this code for security vulnerabilities and provide an exploit PoC if possible:\n\n{code}"

        # This is a generic endpoint simulation.
        # Real implementation would branch based on model.name (e.g., 'GPT-4o' vs 'Gemini')
        try:
            # Simulated call if no valid real key is provided,
            # but the code structure is "real"
            response = requests.post(
                model.base_url + "/chat/completions",
                headers=headers,
                json={
                    "model": model.name,
                    "messages": [{"role": "user", "content": prompt}],
                    ** (model.profile_config or {})
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                # Store the analysis
                analysis_rec = models.AIAnalysis(
                    ai_model_id=model.id,
                    prompt=prompt,
                    response=analysis_text,
                    confidence=0.95
                )
                db.add(analysis_rec)
                db.commit()
                return {"response": analysis_text}
            else:
                return {"error": f"API Error: {response.status_code} - {response.text}"}

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
