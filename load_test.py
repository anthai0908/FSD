import argparse
import asyncio
import statistics
import time

import httpx

from models import SessionLocal, StudentRecord

DEFAULT_BASE_URL = "http://127.0.0.1:8001"


def build_client_kwargs(base_url, timeout, transport):
    if transport == "asgi":
        from AsyncWebApp import app

        return {
            "base_url": "http://testserver",
            "timeout": timeout,
            "transport": httpx.ASGITransport(app=app),
        }
    return {"base_url": base_url, "timeout": timeout}


def load_credentials(limit):
    with SessionLocal() as session:
        rows = (
            session.query(StudentRecord.username, StudentRecord.password)
            .order_by(StudentRecord.username)
            .limit(limit)
            .all()
        )
    return [(username, password) for username, password in rows]


async def run_user(base_url, credential, index, timeout, transport):
    start = time.perf_counter()
    username, password = credential
    try:
        async with httpx.AsyncClient(**build_client_kwargs(base_url, timeout, transport)) as client:
            login_response = await client.post(
                "/login",
                data={"username": username, "password": password},
                follow_redirects=False,
            )
            if login_response.status_code not in (302, 303):
                return False, time.perf_counter() - start, f"login {login_response.status_code}"

            enrollment_response = await client.get("/enrollment")
            if enrollment_response.status_code != 200:
                return False, time.perf_counter() - start, f"enrollment {enrollment_response.status_code}"
            if "Current Subjects" not in enrollment_response.text:
                return False, time.perf_counter() - start, "missing dashboard content"

        return True, time.perf_counter() - start, ""
    except Exception as exc:
        return False, time.perf_counter() - start, f"{type(exc).__name__}: {exc}"


async def run_chat_user(base_url, credential, index, timeout, transport):
    start = time.perf_counter()
    username, password = credential
    try:
        async with httpx.AsyncClient(**build_client_kwargs(base_url, timeout, transport)) as client:
            login_response = await client.post(
                "/login",
                data={"username": username, "password": password},
                follow_redirects=False,
            )
            if login_response.status_code not in (302, 303):
                return False, time.perf_counter() - start, f"login {login_response.status_code}"

            async with client.stream(
                "POST",
                "/chat-stream",
                data={"message": f"Give one short tip for test user {index}."},
            ) as response:
                if response.status_code != 200:
                    return False, time.perf_counter() - start, f"chat {response.status_code}"
                chunks = []
                async for chunk in response.aiter_text():
                    chunks.append(chunk)
                    if sum(len(item) for item in chunks) >= 80:
                        break
            if not "".join(chunks).strip():
                return False, time.perf_counter() - start, "empty stream"

        return True, time.perf_counter() - start, ""
    except Exception as exc:
        return False, time.perf_counter() - start, f"{type(exc).__name__}: {exc}"


async def run_batch(base_url, concurrency, mode, transport):
    credentials = load_credentials(concurrency)
    if not credentials:
        raise RuntimeError("No student credentials found in the database.")

    timeout = httpx.Timeout(60.0)
    task_fn = run_chat_user if mode == "chat" else run_user
    tasks = [
        task_fn(base_url, credentials[index % len(credentials)], index, timeout, transport)
        for index in range(concurrency)
    ]
    start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    total = time.perf_counter() - start

    successes = [duration for ok, duration, _ in results if ok]
    failures = [error for ok, _, error in results if not ok]
    p50 = statistics.median(successes) if successes else 0
    p95 = sorted(successes)[int(len(successes) * 0.95) - 1] if successes else 0

    return {
        "concurrency": concurrency,
        "mode": mode,
        "success": len(successes),
        "failed": len(failures),
        "total_seconds": total,
        "rps": len(successes) / total if total else 0,
        "p50_seconds": p50,
        "p95_seconds": p95,
        "sample_errors": failures[:3],
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--mode", choices=["page", "chat"], default="page")
    parser.add_argument("--transport", choices=["network", "asgi"], default="network")
    parser.add_argument("--concurrency", type=int, nargs="+", default=[10, 25, 50, 100])
    args = parser.parse_args()

    for concurrency in args.concurrency:
        result = await run_batch(args.base_url, concurrency, args.mode, args.transport)
        print(
            f"mode={result['mode']} concurrency={result['concurrency']} "
            f"success={result['success']} failed={result['failed']} "
            f"total={result['total_seconds']:.2f}s rps={result['rps']:.1f} "
            f"p50={result['p50_seconds']:.3f}s p95={result['p95_seconds']:.3f}s"
        )
        if result["sample_errors"]:
            print("sample_errors=" + " | ".join(result["sample_errors"]))


if __name__ == "__main__":
    asyncio.run(main())
