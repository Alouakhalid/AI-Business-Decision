import json
import re
import time
import requests
from typing import Dict, Any, Optional
from app.config import config

class GroqLLMClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Available working models pool to cycle through on rate limits
        self.model_pool = [
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
            "allam-2-7b"
        ]

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: str = None, json_mode: bool = False, temperature: float = 0.3) -> str:
        primary_model = model or config.GROQ_MODEL_PRIMARY
        
        # Build candidate models list starting with primary
        candidate_models = [primary_model] + [m for m in self.model_pool if m != primary_model]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None

        for current_model in candidate_models:
            payload = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            # Try up to 3 retries with backoff for rate limits per model
            for attempt in range(3):
                try:
                    res = requests.post(self.base_url, json=payload, headers=self.headers, timeout=60)
                    
                    if res.status_code == 200:
                        raw_text = res.json()["choices"][0]["message"]["content"]
                        clean_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
                        return clean_text
                    
                    elif res.status_code == 429:
                        print(f"Rate limit (429) hit on model {current_model} (attempt {attempt+1}). Sleeping 3s...")
                        time.sleep(3)
                        last_error = f"Groq API Rate Limit (429): {res.text[:150]}"
                        continue
                    else:
                        print(f"Model {current_model} returned status {res.status_code}: {res.text[:150]}")
                        last_error = f"Groq API Error ({res.status_code}): {res.text[:150]}"
                        break # try next model in pool

                except Exception as e:
                    print(f"Exception requesting model {current_model}: {e}")
                    last_error = str(e)
                    time.sleep(1)

        raise Exception(f"All models in pool failed. Last Error: {last_error}")

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, model: str = None) -> Dict[str, Any]:
        full_system = (system_prompt or "") + "\n\nCRITICAL: Respond ONLY with valid, strict JSON matching requested structure. No markdown wrapping unless inside JSON strings."
        response_text = self.generate(prompt=prompt, system_prompt=full_system, model=model, json_mode=True)
        
        cleaned = re.sub(r'^```json\s*', '', response_text)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            raise Exception(f"Failed to parse LLM response as JSON: {err}\nRaw text: {response_text[:300]}")

llm_client = GroqLLMClient()
