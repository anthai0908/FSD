from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
import html

from AppState import ChatHistoryStore, SessionStore
from Services import AIService, StudentPortalService


HOST = "127.0.0.1"
PORT = 8000
PORTAL_SERVICE = StudentPortalService()
AI_SERVICE = AIService()
SESSION_STORE = SessionStore()
CHAT_HISTORY_STORE = ChatHistoryStore()


class WebAppHandler(BaseHTTPRequestHandler):
    portal = PORTAL_SERVICE
    ai = AI_SERVICE
    sessions = SESSION_STORE
    chat_history = CHAT_HISTORY_STORE

    def do_GET(self):
        if self.path == "/":
            self.redirect("/login")
        elif self.path == "/login":
            self.send_html(self.login_page())
        elif self.path == "/register":
            self.send_html(self.register_page())
        elif self.path == "/enrollment":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            self.send_html(self.enrollment_page(username))
        elif self.path == "/ai-advice":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            self.send_html(self.ai_advice_page(username))
        elif self.path == "/chat":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            self.send_html(self.chat_page(username))
        elif self.path == "/logout":
            self.clear_session()
            self.redirect("/login")
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        body = self.read_form()
        if self.path == "/login":
            username = body.get("username", [""])[0].strip()
            password = body.get("password", [""])[0]
            if self.portal.authenticate(username, password):
                self.create_session(username)
                return
            else:
                self.send_html(self.login_page(error="Invalid username or password."))
        elif self.path == "/register":
            self.handle_register(body)
        elif self.path == "/enroll":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            self.portal.enroll_subject(username)
            self.redirect("/enrollment")
        elif self.path == "/remove":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            subject_id = body.get("subject_id", [""])[0]
            if subject_id:
                self.portal.remove_subject(username, subject_id)
            self.redirect("/enrollment")
        elif self.path == "/chat":
            username = self.current_username()
            if not username:
                self.redirect("/login")
                return
            message = body.get("message", [""])[0].strip()
            if message:
                student = self.portal.get_student(username)
                subjects = self.portal.get_subjects(username)
                reply = self.ai.chat(student, subjects, message)
                self.chat_history.append_pair(username, message, reply)
            self.send_html(self.chat_page(username))
        elif self.path == "/chat-stream":
            username = self.current_username()
            if not username:
                self.send_text_stream("Please log in again.")
                return
            message = body.get("message", [""])[0].strip()
            if not message:
                self.send_text_stream("Please enter a message.")
                return
            self.stream_chat_response(username, message)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def login_page(self, error=None):
        error_html = ""
        if error:
            error_html = f'<div class="error">{html.escape(error)}</div>'

        return self.page(
            title="Login",
            content=f"""
            <main class="login-shell">
                <section class="brand-panel">
                    <div class="orb orb-one"></div>
                    <div class="orb orb-two"></div>
                    <p class="eyebrow">UTS Portal</p>
                    <h1>Student Enrollment System</h1>
                    <p class="hero-copy">Manage subjects, review marks, and get AI-powered study advice from DeepSeek.</p>
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
                    <p class="hint">Super admin: <strong>admin</strong> / <strong>admin</strong>. Demo student: <strong>zhuhang.li@university.com</strong> / <strong>Zhuhangli123</strong>.</p>
                </section>
            </main>
            """,
        )

    def register_page(self, error=None, success=None):
        error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
        success_html = f'<div class="success">{html.escape(success)}</div>' if success else ""

        return self.page(
            title="Register",
            content=f"""
            <main class="login-shell register-shell">
                <section class="brand-panel">
                    <div class="orb orb-one"></div>
                    <div class="orb orb-two"></div>
                    <p class="eyebrow">Create Account</p>
                    <h1>Join the Enrollment Portal</h1>
                    <p class="hero-copy">Use your university email format and a valid password to register as a student.</p>
                    <div class="pattern">firstname.lastname@university.com</div>
                </section>
                <section class="login-card">
                    <h2>Register</h2>
                    <p class="muted">Username format: firstname.lastname@university.com</p>
                    {error_html}
                    {success_html}
                    <form method="post" action="/register">
                        <label>Username</label>
                        <input name="username" placeholder="firstname.lastname@university.com" autocomplete="username" required>
                        <label>Password</label>
                        <input name="password" type="password" placeholder="Example: Student123" autocomplete="new-password" required>
                        <label>Confirm Password</label>
                        <input name="confirm_password" type="password" autocomplete="new-password" required>
                        <button type="submit">Create Account</button>
                    </form>
                    <p class="hint">Already have an account? <a href="/login">Back to login</a>.</p>
                </section>
            </main>
            """,
        )

    def handle_register(self, body):
        username = body.get("username", [""])[0].strip()
        password = body.get("password", [""])[0]
        confirm_password = body.get("confirm_password", [""])[0]

        registered, message = self.portal.register(username, password, confirm_password)
        if registered:
            self.send_html(self.register_page(success=message))
        else:
            self.send_html(self.register_page(error=message))

    def enrollment_page(self, username):
        student = self.portal.get_student(username)
        subjects = self.portal.get_subjects(username)
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

        can_enroll = len(subjects) < 4
        enroll_button = (
            '<button type="submit">Enroll Random Subject</button>'
            if can_enroll
            else '<button type="button" disabled>Enrollment Limit Reached</button>'
        )

        return self.page(
            title="Enrollment",
            content=f"""
            <main class="dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">Student Dashboard</p>
                        <h1>Hello, {html.escape(student.name)}</h1>
                    </div>
                    <a class="logout" href="/logout">Logout</a>
                </nav>
                <section class="stats-grid">
                    <article>
                        <span>{len(subjects)}/4</span>
                        <p>Enrolled Subjects</p>
                    </article>
                    <article>
                        <span>{html.escape(student.ID or "-")}</span>
                        <p>Student ID</p>
                    </article>
                    <article>
                        <span>AI</span>
                        <p>DeepSeek Advice Ready</p>
                    </article>
                </section>
                <section class="panel">
                    <div class="panel-header">
                        <div>
                            <h2>Current Subjects</h2>
                            <p class="muted">Review marks, remove subjects, or request AI advice.</p>
                        </div>
                        <div class="actions">
                            <form method="post" action="/enroll">{enroll_button}</form>
                            <a class="button-link" href="/ai-advice">AI Study Advice</a>
                            <a class="button-link accent" href="/chat">Chat with DeepSeek</a>
                        </div>
                    </div>
                    <table>
                        <thead>
                            <tr><th>Subject ID</th><th>Mark</th><th>Grade</th><th>Action</th></tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </section>
            </main>
            """,
        )

    def chat_page(self, username):
        student = self.portal.get_student(username)
        subjects = self.portal.get_subjects(username)
        history = self.chat_history.get(username)
        conversation_html = """
            <div class="chat-empty">
                Ask DeepSeek about your study plan, subject marks, grades, or enrollment choices.
            </div>
        """

        if history:
            conversation_html = ""
            for role, text in history:
                if role == "user":
                    conversation_html += f"""
                        <div class="message user-message">
                            <strong>You</strong>
                            <p>{html.escape(text)}</p>
                        </div>
                    """
                else:
                    conversation_html += f"""
                        <div class="message ai-message">
                            <strong>DeepSeek</strong>
                            <pre>{html.escape(text)}</pre>
                        </div>
                    """

        return self.page(
            title="Chat",
            content=f"""
            <main class="dashboard chat-dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">DeepSeek Chat</p>
                        <h1>Ask About Your Study</h1>
                    </div>
                    <a class="logout" href="/enrollment">Back</a>
                </nav>
                <section class="chat-layout">
                    <aside class="chat-context">
                        <h2>{html.escape(student.name)}</h2>
                        <p class="muted">DeepSeek can see your current enrolled subjects and marks.</p>
                        {self.subject_summary_html(subjects)}
                    </aside>
                    <section class="panel chat-panel">
                        <div class="chat-window" id="chat-window">{conversation_html}</div>
                        <form class="chat-form" id="chat-form" method="post" action="/chat">
                            <textarea
                                id="chat-message"
                                name="message"
                                rows="4"
                                placeholder="Example: How can I improve my grades next week?"
                                required
                            ></textarea>
                            <button type="submit">Send to DeepSeek</button>
                        </form>
                    </section>
                </section>
            </main>
            """,
        )

    def stream_chat_response(self, username, user_message):
        student = self.portal.get_student(username)
        subjects = self.portal.get_subjects(username)
        full_reply = []

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        try:
            for delta in self.ai.stream_chat(student, subjects, user_message):
                full_reply.append(delta)
                if not self.write_stream_chunk(delta):
                    break
        except Exception as exc:
            error = f"\n\nDeepSeek stream failed: {exc}"
            full_reply.append(error)
            self.write_stream_chunk(error)

        self.chat_history.append_pair(username, user_message, "".join(full_reply))

    def write_stream_chunk(self, text):
        try:
            self.wfile.write(text.encode("utf-8"))
            self.wfile.flush()
            return True
        except BrokenPipeError:
            return False

    def send_text_stream(self, text):
        encoded = text.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def subject_summary_html(self, subjects):
        if not subjects:
            return '<p class="empty">No enrolled subject yet.</p>'

        items = ""
        for subject in subjects:
            items += (
                f"<li><span>Subject {html.escape(subject.ID)}</span>"
                f"<strong>{subject.mark} / {html.escape(subject.grade)}</strong></li>"
            )
        return f'<ul class="subject-pills">{items}</ul>'

    def ai_advice_page(self, username):
        student = self.portal.get_student(username)
        subjects = self.portal.get_subjects(username)
        advice = self.ai.get_study_advice(student, subjects)

        return self.page(
            title="AI Study Advice",
            content=f"""
            <main class="dashboard">
                <nav class="topbar">
                    <div>
                        <p class="eyebrow">DeepSeek Advisor</p>
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

    def page(self, title, content):
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

    def read_form(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        return parse_qs(data)

    def create_session(self, username):
        token = self.sessions.create(username)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Set-Cookie", f"session={token}; HttpOnly; SameSite=Lax")
        self.send_header("Location", "/enrollment")
        self.end_headers()

    def current_username(self):
        return self.sessions.get(self.current_session_token())

    def clear_session(self):
        self.sessions.delete(self.current_session_token())

    def current_session_token(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            key, _, value = part.strip().partition("=")
            if key == "session":
                return value
        return None

    def send_html(self, content):
        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, path):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", path)
        self.end_headers()

    def log_message(self, format, *args):
        return


STYLE = """
:root {
    --ink: #172033;
    --muted: #64748b;
    --navy: #0d2f4f;
    --blue: #176b87;
    --cyan: #26c6da;
    --paper: #fffaf0;
    --line: #d7e3ee;
    --danger: #b42318;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    color: var(--ink);
    font-family: Avenir, "Avenir Next", Helvetica, Arial, sans-serif;
    background:
        radial-gradient(circle at top left, rgba(38, 198, 218, .35), transparent 28rem),
        linear-gradient(135deg, #f9f0dc 0%, #ecf7fa 100%);
}
.login-shell {
    width: min(1000px, calc(100vw - 36px));
    min-height: 620px;
    margin: 5vh auto;
    display: grid;
    grid-template-columns: 1fr 1.15fr;
    border-radius: 34px;
    overflow: hidden;
    box-shadow: 0 28px 80px rgba(13, 47, 79, .22);
    background: white;
}
.brand-panel {
    position: relative;
    overflow: hidden;
    padding: 58px 44px;
    color: white;
    background: linear-gradient(155deg, var(--navy), var(--blue));
}
.orb {
    position: absolute;
    border-radius: 999px;
    opacity: .24;
    background: var(--cyan);
}
.orb-one { width: 190px; height: 190px; left: -70px; top: -54px; }
.orb-two { width: 260px; height: 260px; right: -120px; bottom: -90px; background: #facc15; }
.eyebrow {
    margin: 0 0 14px;
    color: #9ee8f2;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}
h1, h2 { margin: 0; line-height: 1.05; }
.brand-panel h1 { position: relative; max-width: 330px; font-size: 46px; }
.hero-copy { position: relative; margin-top: 28px; max-width: 310px; font-size: 17px; line-height: 1.55; color: #dff8fb; }
.pattern { position: relative; margin-top: 92px; color: #facc15; font-weight: 900; }
.login-card {
    padding: 76px 72px;
    background: rgba(255, 255, 255, .96);
}
.login-card h2 { font-size: 38px; }
.muted { color: var(--muted); }
form { margin-top: 30px; }
label {
    display: block;
    margin: 18px 0 8px;
    font-weight: 800;
}
input {
    width: 100%;
    padding: 16px 18px;
    border: 2px solid var(--line);
    border-radius: 16px;
    font-size: 16px;
    outline: none;
    background: #fbfdff;
}
input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 0 5px rgba(38, 198, 218, .15);
}
button, .button-link {
    border: 0;
    border-radius: 16px;
    padding: 14px 18px;
    color: white;
    background: var(--navy);
    font-size: 15px;
    font-weight: 900;
    text-decoration: none;
    cursor: pointer;
}
button:hover, .button-link:hover { background: var(--blue); }
.accent { background: #0f766e; }
.accent:hover { background: #115e59; }
button:disabled { opacity: .55; cursor: not-allowed; }
.hint { margin-top: 20px; color: var(--muted); font-size: 14px; }
.hint a { color: var(--blue); font-weight: 900; }
.error {
    margin-top: 22px;
    padding: 13px 15px;
    color: var(--danger);
    background: #fff1f1;
    border: 1px solid #ffc9c9;
    border-radius: 14px;
    font-weight: 800;
}
.success {
    margin-top: 22px;
    padding: 13px 15px;
    color: #166534;
    background: #ecfdf3;
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    font-weight: 800;
}
.dashboard {
    width: min(1120px, calc(100vw - 36px));
    margin: 36px auto;
}
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}
.topbar h1 { font-size: 42px; }
.logout {
    color: var(--navy);
    font-weight: 900;
    text-decoration: none;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 20px;
}
.stats-grid article, .panel {
    background: rgba(255, 255, 255, .92);
    border: 1px solid rgba(215, 227, 238, .9);
    border-radius: 26px;
    box-shadow: 0 18px 52px rgba(13, 47, 79, .12);
}
.stats-grid article { padding: 24px; }
.stats-grid span { font-size: 30px; font-weight: 900; color: var(--blue); }
.stats-grid p { margin: 8px 0 0; color: var(--muted); font-weight: 700; }
.panel { padding: 28px; }
.panel-header {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: flex-start;
    margin-bottom: 22px;
}
.actions { display: flex; gap: 10px; align-items: center; }
.actions form { margin: 0; }
table {
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 18px;
}
th, td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid var(--line);
}
th { background: #e9f5f8; }
.grade {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    color: var(--navy);
    background: #d9f8fc;
    font-weight: 900;
}
.secondary { padding: 10px 12px; background: #edf2f7; color: var(--ink); }
.danger { color: white; background: var(--danger); }
.empty { color: var(--muted); text-align: center; }
.advice pre {
    white-space: pre-wrap;
    font: inherit;
    line-height: 1.7;
    padding: 22px;
    border-radius: 18px;
    background: #f8fbfd;
}
.chat-layout {
    display: grid;
    grid-template-columns: 310px 1fr;
    gap: 18px;
}
.chat-context {
    padding: 24px;
    border-radius: 26px;
    color: white;
    background: linear-gradient(155deg, var(--navy), var(--blue));
    box-shadow: 0 18px 52px rgba(13, 47, 79, .16);
}
.chat-context .muted { color: #dff8fb; }
.subject-pills {
    list-style: none;
    margin: 24px 0 0;
    padding: 0;
    display: grid;
    gap: 12px;
}
.subject-pills li {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, .13);
}
.chat-panel {
    display: flex;
    flex-direction: column;
    min-height: 560px;
}
.chat-window {
    flex: 1;
    display: grid;
    align-content: start;
    gap: 14px;
    min-height: 330px;
    padding: 18px;
    border-radius: 20px;
    background: #f8fbfd;
}
.chat-empty {
    padding: 34px;
    color: var(--muted);
    text-align: center;
    border: 2px dashed var(--line);
    border-radius: 20px;
}
.message {
    max-width: 82%;
    padding: 16px 18px;
    border-radius: 20px;
}
.message p,
.message pre {
    margin: 8px 0 0;
    white-space: pre-wrap;
    font: inherit;
    line-height: 1.55;
}
.user-message {
    justify-self: end;
    color: white;
    background: var(--navy);
}
.ai-message {
    justify-self: start;
    background: white;
    border: 1px solid var(--line);
}
.chat-form {
    margin-top: 18px;
    display: grid;
    gap: 12px;
}
.admin-dashboard .topbar {
    padding: 24px;
    border-radius: 28px;
    color: white;
    background: linear-gradient(135deg, #111827, #7c2d12);
    box-shadow: 0 18px 52px rgba(17, 24, 39, .2);
}
.admin-dashboard .eyebrow,
.admin-dashboard .logout {
    color: #fed7aa;
}
.admin-dashboard .logout {
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, .12);
}
.admin-grade-grid {
    grid-template-columns: repeat(6, 1fr);
}
.admin-health-grid {
    grid-template-columns: repeat(6, 1fr);
}
.admin-health-grid article {
    min-height: 128px;
}
.admin-health-grid .health-card {
    background: linear-gradient(135deg, #ecfeff, #fff7ed);
    border-color: #fdba74;
}
.admin-chat-panel {
    margin-top: 20px;
}
textarea {
    width: 100%;
    resize: vertical;
    min-height: 118px;
    padding: 16px 18px;
    border: 2px solid var(--line);
    border-radius: 18px;
    font: inherit;
    outline: none;
}
textarea:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 0 5px rgba(38, 198, 218, .15);
}
@media (max-width: 760px) {
    .login-shell { grid-template-columns: 1fr; margin: 18px auto; }
    .brand-panel, .login-card { padding: 34px 26px; }
    .stats-grid { grid-template-columns: 1fr; }
    .admin-grade-grid,
    .admin-health-grid { grid-template-columns: 1fr; }
    .panel-header, .topbar, .actions { flex-direction: column; align-items: stretch; }
    .chat-layout { grid-template-columns: 1fr; }
    .message { max-width: 100%; }
}
"""

SCRIPT = """
function appendMessage(chatWindow, role, text) {
    const empty = chatWindow.querySelector(".chat-empty");
    if (empty) {
        empty.remove();
    }

    const message = document.createElement("div");
    message.className = role === "user" ? "message user-message" : "message ai-message";

    const label = document.createElement("strong");
    label.textContent = role === "user" ? "You" : "DeepSeek";
    message.appendChild(label);

    const body = document.createElement(role === "user" ? "p" : "pre");
    body.textContent = text || "";
    message.appendChild(body);

    chatWindow.appendChild(message);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return body;
}

async function streamChat(form) {
    const chatWindow = document.getElementById("chat-window");
    const textarea = document.getElementById("chat-message");
    const button = form.querySelector("button[type='submit']");
    const message = textarea.value.trim();

    if (!message || !chatWindow || !button) {
        return;
    }

    appendMessage(chatWindow, "user", message);
    const aiBody = appendMessage(chatWindow, "assistant", "");
    textarea.value = "";
    button.disabled = true;
    button.textContent = "Streaming...";

    try {
        const response = await fetch("/chat-stream", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: new URLSearchParams({message})
        });

        if (!response.body) {
            aiBody.textContent = await response.text();
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const result = await reader.read();
            if (result.done) {
                break;
            }
            aiBody.textContent += decoder.decode(result.value, {stream: true});
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    } catch (error) {
        aiBody.textContent += "\\n\\nChat request failed: " + error;
    } finally {
        button.disabled = false;
        button.textContent = "Send to DeepSeek";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        streamChat(form);
    });
});
"""


class AppServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    server = AppServer((HOST, PORT), WebAppHandler)
    print(f"Open http://{HOST}:{PORT}/login")
    server.serve_forever()
