import os
import groq
import json
from typing import Dict, Any, List, Optional
from config import GROQ_API_KEY, MODEL_NAME, logger

class LLMUtils:
    def __init__(self):
        if not GROQ_API_KEY:
            self.client = None
            logger.error("Groq Client initialized without API Key.")
        else:
            self.client = groq.Groq(api_key=GROQ_API_KEY)

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        if not self.client:
            return "Error: LLM client not configured. Please add GROQ_API_KEY to .env"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=MODEL_NAME,
                temperature=temperature,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            return f"Error communicating with LLM: {str(e)}"

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Attempt to extract and parse JSON from LLM response."""
        try:
            # Simple extractor if LLM surrounds with ```json
            if "```json" in response:
                content = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                content = response.split("```")[1].split("```")[0].strip()
            else:
                content = response.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to parse JSON from LLM: {str(e)}")
            return {"error": "Invalid JSON format", "raw": response}

llm = LLMUtils()
