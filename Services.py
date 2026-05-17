import hashlib
import asyncio
import threading

from AppState import RequestLimiter, TTLCache
from DeepSeekClient import DeepSeekClient
from Student import Student
from System import System


class StudentPortalService:
    def __init__(self):
        self.system = System()
        self.database = self.system.database
        self.lock = threading.RLock()

    def authenticate(self, username, password):
        with self.lock:
            return self.system.student_authenticate(username, password)

    def register(self, username, password, confirm_password):
        with self.lock:
            if not self.system.username_format_validation(username):
                return False, "Username must be firstname.lastname@university.com."
            if not self.system.password_format_validation(password):
                return (
                    False,
                    "Password must start with uppercase, contain at least 6 letters, and end with at least 3 digits.",
                )
            if password != confirm_password:
                return False, "Password and confirm password do not match."
            if not self.system.check_username(username):
                return False, "This username is already registered."

            name = self.system.getname(username)
            student_id = self.system.ID_generate()
            self.database.register_write(name, student_id, username, password)
            return True, "Registration successful. You can now return to login."

    def get_student(self, username):
        with self.lock:
            return Student(username, self.database)

    def get_subjects(self, username):
        with self.lock:
            return self.database.get_subjects(username)

    def enroll_subject(self, username):
        with self.lock:
            Student(username, self.database).subject_enrol()

    def remove_subject(self, username, subject_id):
        with self.lock:
            self.database.remove_subject(username, subject_id)


class AIService:
    def __init__(self, deepseek_client=None, max_concurrent_requests=4):
        self.deepseek_client = deepseek_client or DeepSeekClient()
        self.max_concurrent_requests = max_concurrent_requests
        self.limiter = RequestLimiter(max_concurrent=max_concurrent_requests)
        self.study_advice_cache = TTLCache(ttl_seconds=120, max_entries=128)

    def get_study_advice(self, student, subjects):
        cache_key = self._cache_key(student, subjects)
        cached = self.study_advice_cache.get(cache_key)
        if cached:
            return cached

        if not self.limiter.acquire(timeout=2):
            return "AI service is busy. Please try again in a moment."

        try:
            advice = self.deepseek_client.get_study_advice(student.name, subjects)
            self.study_advice_cache.set(cache_key, advice)
            return advice
        except Exception as exc:
            return f"AI advice failed: {exc}"
        finally:
            self.limiter.release()

    def chat(self, student, subjects, user_message):
        if not self.limiter.acquire(timeout=2):
            return "AI service is busy. Please try again in a moment."

        try:
            return self.deepseek_client.chat(self.build_chat_messages(student, subjects, user_message))
        except Exception as exc:
            return f"DeepSeek chat failed: {exc}"
        finally:
            self.limiter.release()

    def stream_chat(self, student, subjects, user_message):
        if not self.limiter.acquire(timeout=2):
            yield "AI service is busy. Please try again in a moment."
            return

        try:
            messages = self.build_chat_messages(student, subjects, user_message)
            yield from self.deepseek_client.stream_chat(messages)
        except Exception as exc:
            yield f"\n\nDeepSeek stream failed: {exc}"
        finally:
            self.limiter.release()

    def build_chat_messages(self, student, subjects, user_message):
        subject_lines = []
        if subjects:
            for subject in subjects:
                subject_lines.append(f"Subject {subject.ID}: mark {subject.mark}, grade {subject.grade}")
        else:
            subject_lines.append("No enrolled subjects.")

        return [
            {
                "role": "system",
                "content": (
                    "You are a friendly university study assistant. Use the student's "
                    "current subjects and marks as context. Be practical, concise, and "
                    "avoid making up university policy."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Student name: {student.name}\n"
                    f"Student ID: {student.ID}\n"
                    f"Subjects:\n" + "\n".join(subject_lines) + "\n\n"
                    f"Student question: {user_message}"
                ),
            },
        ]

    def _cache_key(self, student, subjects):
        subject_snapshot = "|".join(f"{subject.ID}:{subject.mark}:{subject.grade}" for subject in subjects)
        raw_key = f"{student.username}:{subject_snapshot}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class AsyncAIService:
    def __init__(self, deepseek_client=None, max_concurrent_requests=4):
        self.deepseek_client = deepseek_client or DeepSeekClient()
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.study_advice_cache = TTLCache(ttl_seconds=120, max_entries=128)

    async def get_study_advice(self, student, subjects):
        cache_key = self._cache_key(student, subjects)
        cached = self.study_advice_cache.get(cache_key)
        if cached:
            return cached

        try:
            async with self.semaphore:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful university study advisor.",
                    },
                    {
                        "role": "user",
                        "content": self._study_advice_prompt(student, subjects),
                    },
                ]
                advice = await self.deepseek_client.async_chat(messages)
                self.study_advice_cache.set(cache_key, advice)
                return advice
        except Exception as exc:
            return f"AI advice failed: {exc}"

    async def chat(self, student, subjects, user_message):
        try:
            async with self.semaphore:
                messages = AIService.build_chat_messages(self, student, subjects, user_message)
                return await self.deepseek_client.async_chat(messages)
        except Exception as exc:
            return f"DeepSeek chat failed: {exc}"

    async def stream_chat(self, student, subjects, user_message):
        try:
            async with self.semaphore:
                messages = AIService.build_chat_messages(self, student, subjects, user_message)
                async for delta in self.deepseek_client.async_stream_chat(messages):
                    yield delta
        except Exception as exc:
            yield f"\n\nDeepSeek stream failed: {exc}"

    def _study_advice_prompt(self, student, subjects):
        subject_lines = []
        if subjects:
            for subject in subjects:
                subject_lines.append(f"Subject {subject.ID}: mark {subject.mark}, grade {subject.grade}")
        else:
            subject_lines.append("No enrolled subjects.")

        return (
            f"Student name: {student.name}\n"
            f"Subjects:\n" + "\n".join(subject_lines) + "\n\n"
            "Give concise study advice for this student. Include strengths, risks, "
            "and 3 practical next steps. Keep it under 160 words."
        )

    def _cache_key(self, student, subjects):
        subject_snapshot = "|".join(f"{subject.ID}:{subject.mark}:{subject.grade}" for subject in subjects)
        raw_key = f"{student.username}:{subject_snapshot}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
