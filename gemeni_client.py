# gemini_client.py

import os
import google.generativeai as genai


class GeminiClientError(Exception):
    pass


class GeminiClient:
    """
    Wrapper to make Gemini behave like GroqClient so the rest of the
    codebase does NOT need to change.

    Returned format always matches:
        response["choices"][0]["message"]["content"]
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiClientError("Missing GEMINI_API_KEY environment variable")

        genai.configure(api_key=api_key)

        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise GeminiClientError(f"Failed to initialize Gemini model: {e}")

    def chat(self, messages, temperature=0.1):
        """
        Accepts Groq-style messages:
            [{"role": "system", "content": ""}, {"role": "user", "content": ""}]
        Converts to a single Gemini prompt.
        """

        try:
            # Convert ChatML messages → single Gemini prompt
            prompt = ""
            for m in messages:
                prompt += f"{m['role'].upper()}: {m['content']}\n"

            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": temperature},
            )

            text = response.text

            # Return in Groq-style for compatibility
            return {
                "choices": [
                    {
                        "message": {"content": text}
                    }
                ]
            }

        except Exception as e:
            raise GeminiClientError(f"Gemini API error: {str(e)}")
