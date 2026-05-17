import os
import json


class DeepSeekClient:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY") or self._load_api_key_from_env_file()

    def _load_api_key_from_env_file(self):
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if not os.path.exists(env_path):
            return None

        with open(env_path) as file:
            for line in file:
                key, separator, value = line.strip().partition("=")
                if separator and key == "DEEPSEEK_API_KEY":
                    return value.strip().strip('"').strip("'")

        return None

    def get_study_advice(self, student_name, subjects):
        subject_lines = []
        if subjects:
            for subject in subjects:
                subject_lines.append(
                    f"Subject {subject.ID}: mark {subject.mark}, grade {subject.grade}"
                )
        else:
            subject_lines.append("No enrolled subjects.")

        prompt = (
            f"Student name: {student_name}\n"
            f"Subjects:\n" + "\n".join(subject_lines) + "\n\n"
            "Give concise study advice for this student. Include strengths, risks, "
            "and 3 practical next steps. Keep it under 160 words."
        )

        return self.chat(
            [
                {
                    "role": "system",
                    "content": "You are a helpful university study advisor.",
                },
                {"role": "user", "content": prompt},
            ]
        )

    def chat(self, messages):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("The openai package is not installed. Run: pip install openai") from exc

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
        )

        return response.choices[0].message.content.strip()

    def stream_chat(self, messages):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("The openai package is not installed. Run: pip install openai") from exc

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

        stream = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def async_chat(self, messages):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        import httpx

        payload = {
            "model": "deepseek-v4-flash",
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def async_stream_chat(self, messages):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        import httpx

        payload = {
            "model": "deepseek-v4-flash",
            "messages": messages,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    payload_line = line.removeprefix("data: ").strip()
                    if payload_line == "[DONE]":
                        break

                    data = json.loads(payload_line)
                    delta = data["choices"][0].get("delta", {}).get("content")
                    if delta:
                        yield delta
