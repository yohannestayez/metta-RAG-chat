import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiModel():
    def __init__(self, api_key: str, model_provider,model_name="gemini-2.0-flash"): 
        genai.configure(api_key=os.getenv('GEMINI_API'))
        self.model = genai.GenerativeModel(model_name or "gemini-2.0-flash")
        self.model_name = model_name
        self.model_provider = model_provider
        self.api_key = api_key

    def generate(self, prompt: str,system_prompt=None, temperature=0.0, top_k=1) :
        response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    top_k=top_k
                )
            )

        content = response.text

        json_content = self._extract_json_from_codeblock(content)
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            return json_content

    def _extract_json_from_codeblock(self, content: str) -> str:
        start = content.find("```json")
        end = content.rfind("```")
        if start != -1 and end != -1:
            json_content = content[start + 7:end].strip()
            return json_content
        else:
            return content