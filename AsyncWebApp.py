import asyncio
import html
from http import HTTPStatus
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from AppState import ChatHistoryStore, MetricsStore, SessionStore
from Services import AsyncAIService, StudentPortalService
from WebApp import SCRIPT, STYLE


app = FastAPI()
portal = StudentPortalService()
ai = AsyncAIService()
sessions = SessionStore()
admin_sessions = SessionStore()
chat_history = ChatHistoryStore()
metrics = MetricsStore()


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    started_at = metrics.request_started()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        metrics.request_finished(request.url.path, request.method, status_code, started_at)


async def read_form(request):
    body = (await request.body()).decode("utf-8")
    return parse_qs(body)


def current_username(request):
    return sessions.get(request.cookies.get("session"))


def current_admin(request):
    return admin_sessions.get(request.cookies.get("admin_session"))


def page(title, content):
    return f"""<!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{html.escape(title)} - UTS Enrollment</title>
        <style>{STYLE}</style>
    </head>
    <body>{content}<script>{SCRIPT}</script></body>
    </html>"""


def login_page(error=None):
    error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    return page(
        "Login",
        f"""
        <main class="login-shell">
            <section class="brand-panel">
                <div class="orb orb-one"></div>
                <div class="orb orb-two"></div>
                <p class="eyebrow">UTS Portal</p>
                <h1>Async Student Enrollment</h1>
                <p class="hero-copy">FastAPI async mode with streaming DeepSeek chat.</p>
                <div class="pattern">● ● ● &nbsp; ━━━━━━━ &nbsp; ● ● ●</div>
            </section>
            <section class="login-card">
                <h2>Welcome Back</h2>
                <p class="muted">Sign in with your university account.</p>
                {error_html}
                <form method="post" action="/login" autocomplete="off">
                    <label>Username</label>
                    <input name="username" placeholder="admin or firstname.lastname@university.com" autocomplete="off" required>
                    <label>Password</label>
                    <input name="password" type="password" placeholder="admin or your student password" autocomplete="new-password" required>
                    <button type="submit">Login</button>
                </form>
                <p class="hint">New student? <a href="/register">Create an account</a>.</p>
                <p class="hint">Super admin login: username <strong>admin</strong>, password <strong>admin</strong>.</p>
                <p class="hint">Demo student: <strong>zhuhang.li@university.com</strong> / <strong>Zhuhangli123</strong>.</p>
            </section>
        </main>
        """,
    )


def register_page(error=None, success=None):
    error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    success_html = f'<div class="success">{html.escape(success)}</div>' if success else ""
    return page(
        "Register",
        f"""
        <main class="login-shell register-shell">
            <section class="brand-panel">
                <div class="orb orb-one"></div>
                <div class="orb orb-two"></div>
                <p class="eyebrow">Create Account</p>
                <h1>Join the Enrollment Portal</h1>
                <p class="hero-copy">Use your university email format and a valid password.</p>
                <div class="pattern">firstname.lastname@university.com</div>
            </section>
            <section class="login-card">
                <h2>Register</h2>
                <p class="muted">Username format: firstname.lastname@university.com</p>
                {error_html}
                {success_html}
                <form method="post" action="/register">
                    <label>Username</label>
                    <input name="username" placeholder="firstname.lastname@university.com" required>
                    <label>Password</label>
                    <input name="password" type="password" placeholder="Example: Student123" required>
                    <label>Confirm Password</label>
                    <input name="confirm_password" type="password" required>
                    <button type="submit">Create Account</button>
                </form>
                <p class="hint">Already have an account? <a href="/login">Back to login</a>.</p>
            </section>
        </main>
        """,
    )


def subject_summary_html(subjects):
    if not subjects:
        return '<p class="empty">No enrolled subject yet.</p>'

    items = ""
    for subject in subjects:
        items += (
            f"<li><span>Subject {html.escape(subject.ID)}</span>"
            f"<strong>{subject.mark} / {html.escape(subject.grade)}</strong></li>"
        )
    return f'<ul class="subject-pills">{items}</ul>'


async def get_student_and_subjects(username):
    student = await asyncio.to_thread(portal.get_student, username)
    subjects = await asyncio.to_thread(portal.get_subjects, username)
    return student, subjects


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_get():
    return HTMLResponse(login_page())


@app.post("/login")
async def login_post(request: Request):
    form = await read_form(request)
    username = form.get("username", [""])[0].strip()
    password = form.get("password", [""])[0]
    if username == "admin" and password == "admin":
        token = admin_sessions.create("admin")
        response = RedirectResponse("/admin", status_code=HTTPStatus.SEE_OTHER)
        response.set_cookie("admin_session", token, httponly=True, samesite="lax")
        return response

    authenticated = await asyncio.to_thread(portal.authenticate, username, password)
    if not authenticated:
        return HTMLResponse(login_page(error="Invalid username or password."))

    token = sessions.create(username)
    response = RedirectResponse("/enrollment", status_code=HTTPStatus.SEE_OTHER)
    response.set_cookie("session", token, httponly=True, samesite="lax")
    return response


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if current_admin(request) != "admin":
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)

    students = await asyncio.to_thread(portal.database.get_students)
    metric_snapshot = metrics.snapshot()
    total_students = len(students)
    total_subjects = sum(1 for student in students for index in range(1, 5) if student.get(f"Subject_ID{index}"))
    grade_counts = {"HD": 0, "D": 0, "C": 0, "P": 0, "F": 0, "None": 0}
    for student in students:
        grade = student.get("Grade") or "None"
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    student_rows = ""
    for student in students:
        subjects = []
        for index in range(1, 5):
            subject_id = student.get(f"Subject_ID{index}")
            mark = student.get(f"Subject_Mark{index}")
            if subject_id:
                subjects.append(f"{html.escape(subject_id)} ({html.escape(str(mark))})")
        subject_text = ", ".join(subjects) if subjects else "No subjects"
        student_rows += f"""
        <tr>
            <td>{html.escape(student.get("Student_ID", ""))}</td>
            <td>{html.escape(student.get("Student_name", ""))}</td>
            <td>{html.escape(student.get("username", ""))}</td>
            <td>{html.escape(str(student.get("Mean_mark", "")))}</td>
            <td><span class="grade">{html.escape(str(student.get("Grade") or "-"))}</span></td>
            <td>{subject_text}</td>
        </tr>
        """

    grade_cards = "".join(
        f"<article><span>{count}</span><p>{html.escape(grade)} Students</p></article>"
        for grade, count in grade_counts.items()
    )

    chat_rows = ""
    history_snapshot = list(chat_history.history.items()) if hasattr(chat_history, "history") else []
    for username, messages in history_snapshot:
        chat_rows += f"""
        <tr>
            <td>{html.escape(username)}</td>
            <td>{len(messages)}</td>
            <td>{html.escape(messages[-1][1][:120]) if messages else ""}</td>
        </tr>
        """
    if not chat_rows:
        chat_rows = '<tr><td colspan="3" class="empty">No chat history yet</td></tr>'

    health_status, health_detail = site_health(metric_snapshot)
    estimated_capacity = estimate_capacity(metric_snapshot)
    path_rows = ""
    for path, count in metric_snapshot["path_counts"]:
        path_rows += f"<tr><td>{html.escape(path)}</td><td>{count}</td></tr>"
    if not path_rows:
        path_rows = '<tr><td colspan="2" class="empty">No request data yet</td></tr>'

    return HTMLResponse(
        page(
            "Admin Dashboard",
            f"""
            <main class="dashboard admin-dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">Super Admin</p>
                        <h1>System Overview</h1>
                    </div>
                    <a class="logout" href="/admin-logout">Logout</a>
                </nav>
                <section class="stats-grid">
                    <article><span>{total_students}</span><p>Total Students</p></article>
                    <article><span>{total_subjects}</span><p>Total Enrollments</p></article>
                    <article><span>{len(history_snapshot)}</span><p>Chat Users</p></article>
                </section>
                <section class="stats-grid admin-health-grid">
                    <article class="health-card">
                        <span>{html.escape(health_status)}</span>
                        <p>{html.escape(health_detail)}</p>
                    </article>
                    <article><span>{metric_snapshot["active_requests"]}</span><p>Active Requests</p></article>
                    <article><span>{metric_snapshot["rps"]:.1f}</span><p>Requests / Second</p></article>
                    <article><span>{metric_snapshot["p95_latency"]:.2f}s</span><p>P95 Latency</p></article>
                    <article><span>{metric_snapshot["server_error_rate"] * 100:.1f}%</span><p>Server Error Rate</p></article>
                    <article><span>{estimated_capacity}</span><p>Estimated Smooth Users</p></article>
                </section>
                <section class="panel admin-chat-panel">
                    <div class="panel-header">
                        <div>
                            <h2>Live Site Usage</h2>
                            <p class="muted">Metrics are in memory for this running server process. Rolling-window values use the last 5 minutes.</p>
                        </div>
                    </div>
                    <table>
                        <thead><tr><th>Metric</th><th>Value</th></tr></thead>
                        <tbody>
                            <tr><td>Total requests received since start</td><td>{metric_snapshot["total_started"]}</td></tr>
                            <tr><td>Completed requests since start</td><td>{metric_snapshot["total_requests"]}</td></tr>
                            <tr><td>Requests in current window</td><td>{metric_snapshot["window_requests"]}</td></tr>
                            <tr><td>Average latency</td><td>{metric_snapshot["avg_latency"]:.3f}s</td></tr>
                            <tr><td>Max latency</td><td>{metric_snapshot["max_latency"]:.3f}s</td></tr>
                            <tr><td>Client error rate</td><td>{metric_snapshot["client_error_rate"] * 100:.1f}%</td></tr>
                            <tr><td>AI concurrent limit</td><td>{ai.max_concurrent_requests}</td></tr>
                        </tbody>
                    </table>
                </section>
                <section class="panel admin-chat-panel">
                    <div class="panel-header">
                        <div>
                            <h2>Popular Paths</h2>
                            <p class="muted">Most requested paths in the current monitoring window.</p>
                        </div>
                    </div>
                    <table>
                        <thead><tr><th>Path</th><th>Requests</th></tr></thead>
                        <tbody>{path_rows}</tbody>
                    </table>
                </section>
                <section class="stats-grid admin-grade-grid">{grade_cards}</section>
                <section class="panel">
                    <div class="panel-header">
                        <div>
                            <h2>Student Records</h2>
                            <p class="muted">Read-only overview from the ORM database.</p>
                        </div>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Name</th><th>Email</th><th>Mean</th><th>Grade</th><th>Subjects</th></tr>
                        </thead>
                        <tbody>{student_rows or '<tr><td colspan="6" class="empty">No students</td></tr>'}</tbody>
                    </table>
                </section>
                <section class="panel admin-chat-panel">
                    <div class="panel-header">
                        <div>
                            <h2>Chat Activity</h2>
                            <p class="muted">In-memory chat history snapshot. It resets when the server restarts.</p>
                        </div>
                    </div>
                    <table>
                        <thead><tr><th>User</th><th>Messages</th><th>Last Message</th></tr></thead>
                        <tbody>{chat_rows}</tbody>
                    </table>
                </section>
            </main>
            """,
        )
    )


def site_health(snapshot):
    if snapshot["server_error_rate"] >= 0.05:
        return "Degraded", "Server errors are above 5%."
    if snapshot["p95_latency"] >= 5:
        return "Lagging", "Users may feel the website is slow."
    if snapshot["p95_latency"] >= 2:
        return "Busy", "Usable, but response time is rising."
    return "Smooth", "Website is responding quickly."


def estimate_capacity(snapshot):
    p95 = snapshot["p95_latency"]
    active = snapshot["active_requests"]
    if p95 == 0:
        return "50+"
    if p95 < 0.5:
        return "100+"
    if p95 < 2:
        return "50-100"
    if p95 < 5:
        return "25-50"
    if active > 0:
        return "<25"
    return "25-50"


@app.get("/register", response_class=HTMLResponse)
async def register_get():
    return HTMLResponse(register_page())


@app.post("/register", response_class=HTMLResponse)
async def register_post(request: Request):
    form = await read_form(request)
    username = form.get("username", [""])[0].strip()
    password = form.get("password", [""])[0]
    confirm_password = form.get("confirm_password", [""])[0]
    registered, message = await asyncio.to_thread(portal.register, username, password, confirm_password)
    if registered:
        return HTMLResponse(register_page(success=message))
    return HTMLResponse(register_page(error=message))


@app.get("/enrollment", response_class=HTMLResponse)
async def enrollment(request: Request):
    username = current_username(request)
    if not username:
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)

    student, subjects = await get_student_and_subjects(username)
    rows = ""
    if subjects:
        for subject in subjects:
            rows += f"""
            <tr>
                <td>{html.escape(subject.ID)}</td>
                <td>{subject.mark}</td>
                <td><span class="grade">{html.escape(subject.grade)}</span></td>
                <td>
                    <form method="post" action="/remove">
                        <input type="hidden" name="subject_id" value="{html.escape(subject.ID)}">
                        <button class="secondary danger" type="submit">Remove</button>
                    </form>
                </td>
            </tr>
            """
    else:
        rows = '<tr><td colspan="4" class="empty">No enrolled subject</td></tr>'

    enroll_button = (
        '<button type="submit">Enroll Random Subject</button>'
        if len(subjects) < 4
        else '<button type="button" disabled>Enrollment Limit Reached</button>'
    )

    return HTMLResponse(
        page(
            "Enrollment",
            f"""
            <main class="dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">Async Student Dashboard</p>
                        <h1>Hello, {html.escape(student.name)}</h1>
                    </div>
                    <a class="logout" href="/logout">Logout</a>
                </nav>
                <section class="stats-grid">
                    <article><span>{len(subjects)}/4</span><p>Enrolled Subjects</p></article>
                    <article><span>{html.escape(student.ID or "-")}</span><p>Student ID</p></article>
                    <article><span>ASGI</span><p>Async Streaming Ready</p></article>
                </section>
                <section class="panel">
                    <div class="panel-header">
                        <div>
                            <h2>Current Subjects</h2>
                            <p class="muted">Review marks, remove subjects, or chat with DeepSeek.</p>
                        </div>
                        <div class="actions">
                            <form method="post" action="/enroll">{enroll_button}</form>
                            <a class="button-link" href="/ai-advice">AI Study Advice</a>
                            <a class="button-link accent" href="/chat">Chat with DeepSeek</a>
                        </div>
                    </div>
                    <table>
                        <thead><tr><th>Subject ID</th><th>Mark</th><th>Grade</th><th>Action</th></tr></thead>
                        <tbody>{rows}</tbody>
                    </table>
                </section>
            </main>
            """,
        )
    )


@app.post("/enroll")
async def enroll(request: Request):
    username = current_username(request)
    if not username:
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    await asyncio.to_thread(portal.enroll_subject, username)
    return RedirectResponse("/enrollment", status_code=HTTPStatus.SEE_OTHER)


@app.post("/remove")
async def remove(request: Request):
    username = current_username(request)
    if not username:
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    form = await read_form(request)
    subject_id = form.get("subject_id", [""])[0]
    if subject_id:
        await asyncio.to_thread(portal.remove_subject, username, subject_id)
    return RedirectResponse("/enrollment", status_code=HTTPStatus.SEE_OTHER)


@app.get("/ai-advice", response_class=HTMLResponse)
async def ai_advice(request: Request):
    username = current_username(request)
    if not username:
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    student, subjects = await get_student_and_subjects(username)
    advice = await ai.get_study_advice(student, subjects)
    return HTMLResponse(
        page(
            "AI Study Advice",
            f"""
            <main class="dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">Async DeepSeek Advisor</p>
                        <h1>AI Study Advice</h1>
                    </div>
                    <a class="logout" href="/enrollment">Back</a>
                </nav>
                <section class="panel advice">
                    <h2>{html.escape(student.name)}</h2>
                    <pre>{html.escape(advice)}</pre>
                </section>
            </main>
            """,
        )
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    username = current_username(request)
    if not username:
        return RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    student, subjects = await get_student_and_subjects(username)
    history = chat_history.get(username)

    conversation_html = """
        <div class="chat-empty">
            Ask DeepSeek about your study plan, subject marks, grades, or enrollment choices.
        </div>
    """
    if history:
        conversation_html = ""
        for role, text in history:
            if role == "user":
                conversation_html += f'<div class="message user-message"><strong>You</strong><p>{html.escape(text)}</p></div>'
            else:
                conversation_html += f'<div class="message ai-message"><strong>DeepSeek</strong><pre>{html.escape(text)}</pre></div>'

    return HTMLResponse(
        page(
            "Chat",
            f"""
            <main class="dashboard chat-dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">Async DeepSeek Chat</p>
                        <h1>Ask About Your Study</h1>
                    </div>
                    <a class="logout" href="/enrollment">Back</a>
                </nav>
                <section class="chat-layout">
                    <aside class="chat-context">
                        <h2>{html.escape(student.name)}</h2>
                        <p class="muted">Async stream uses FastAPI + httpx.</p>
                        {subject_summary_html(subjects)}
                    </aside>
                    <section class="panel chat-panel">
                        <div class="chat-window" id="chat-window">{conversation_html}</div>
                        <form class="chat-form" id="chat-form" method="post" action="/chat">
                            <textarea id="chat-message" name="message" rows="4" placeholder="Example: How can I improve my grades next week?" required></textarea>
                            <button type="submit">Send to DeepSeek</button>
                        </form>
                    </section>
                </section>
            </main>
            """,
        )
    )


@app.post("/chat-stream")
async def chat_stream(request: Request):
    username = current_username(request)
    if not username:
        return StreamingResponse(iter(["Please log in again."]), media_type="text/plain")

    form = await read_form(request)
    message = form.get("message", [""])[0].strip()
    if not message:
        return StreamingResponse(iter(["Please enter a message."]), media_type="text/plain")

    student, subjects = await get_student_and_subjects(username)

    async def stream():
        full_reply = []
        async for delta in ai.stream_chat(student, subjects, message):
            full_reply.append(delta)
            yield delta
        chat_history.append_pair(username, message, "".join(full_reply))

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@app.get("/logout")
async def logout(request: Request):
    sessions.delete(request.cookies.get("session"))
    response = RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    response.delete_cookie("session")
    return response


@app.get("/admin-logout")
async def admin_logout(request: Request):
    admin_sessions.delete(request.cookies.get("admin_session"))
    response = RedirectResponse("/login", status_code=HTTPStatus.SEE_OTHER)
    response.delete_cookie("admin_session")
    return response
