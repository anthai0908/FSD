import argparse
import asyncio
from dataclasses import dataclass

import httpx

from models import SessionLocal, StudentRecord


@dataclass
class LoginResult:
    username: str
    ok: bool
    detail: str


def load_students():
    with SessionLocal() as session:
        rows = (
            session.query(StudentRecord.username, StudentRecord.password)
            .filter(StudentRecord.username != "admin")
            .order_by(StudentRecord.username)
            .all()
        )
    return [(username, password) for username, password in rows]


async def login_one(base_url, username, password):
    async with httpx.AsyncClient(base_url=base_url, follow_redirects=False, timeout=30.0) as client:
        try:
            response = await client.post(
                "/login",
                data={"username": username, "password": password},
            )
            if response.status_code not in (302, 303):
                return LoginResult(username, False, f"login status {response.status_code}")

            enrollment = await client.get("/enrollment")
            if enrollment.status_code != 200:
                return LoginResult(username, False, f"enrollment status {enrollment.status_code}")
            if "Current Subjects" not in enrollment.text:
                return LoginResult(username, False, "dashboard content missing")

            return LoginResult(username, True, "logged in")
        except Exception as exc:
            return LoginResult(username, False, f"{type(exc).__name__}: {exc}")


async def run(base_url, concurrency):
    students = load_students()
    semaphore = asyncio.Semaphore(concurrency)

    async def guarded_login(username, password):
        async with semaphore:
            return await login_one(base_url, username, password)

    tasks = [guarded_login(username, password) for username, password in students]
    return await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Batch login all student accounts.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8001", help="Web app base URL")
    parser.add_argument("--concurrency", type=int, default=8, help="Parallel login attempts")
    args = parser.parse_args()

    results = asyncio.run(run(args.base_url, args.concurrency))
    success = [result for result in results if result.ok]
    failure = [result for result in results if not result.ok]

    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"{status} {result.username} - {result.detail}")

    print(
        f"summary success={len(success)} failed={len(failure)} "
        f"total={len(results)} base_url={args.base_url}"
    )

    if failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
