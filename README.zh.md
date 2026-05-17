# FSD 学生选课系统

一个同时支持 Tkinter 桌面端和 Web 端的学生选课系统。
系统支持学生注册、登录、选课、退课、成绩展示，以及基于 DeepSeek 的学习建议与聊天功能。

## 功能

- 学生登录与注册
- 课程选修与移除
- 平均分与等级计算
- 使用 DeepSeek 提供学习建议和聊天
- 桌面端 GUI
- 同步 Web 版本与异步 Web 版本
- 异步 Web 版本提供管理员仪表板

## 项目结构

- `GUI.py` - Tkinter 桌面端入口
- `WebApp.py` - 同步 HTTP 服务入口
- `AsyncWebApp.py` - FastAPI 异步 Web 入口
- `Services.py` - 业务逻辑与 AI 服务
- `Database.py` - 数据库访问封装
- `models.py` - SQLAlchemy 模型和 SQLite 初始化
- `migrate_csv_to_orm.py` - 将 CSV 数据迁移到 SQLite
- `students_data.csv` - 示例数据
- `run_gui.sh` - 启动桌面端
- `run_web.sh` - 启动同步 Web 端
- `run_async_web.sh` - 启动异步 Web 端

## 环境要求

- Python 3.10+
- `pip`
- macOS 推荐使用仓库中的 `.sh` 启动脚本，因为脚本使用了 `open`
- AI 功能需要有效的 `DEEPSEEK_API_KEY`

## 安装

创建并激活虚拟环境，然后安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果你要使用 Tkinter 启动脚本，仓库默认使用 `.venv-tk`：

```bash
python -m venv .venv-tk
source .venv-tk/bin/activate
pip install -r requirements.txt
```

## DeepSeek API Key

AI 功能会从以下位置读取 `DEEPSEEK_API_KEY`：

- 当前 shell 环境变量
- 项目根目录下的 `.env` 文件

示例：

```env
DEEPSEEK_API_KEY=your_api_key_here
```

## 运行

### 桌面端 GUI

```bash
./run_gui.sh
```

### 同步 Web 版本

```bash
./run_web.sh
```

访问：

```text
http://127.0.0.1:8000/login
```

### 异步 Web 版本

```bash
./run_async_web.sh
```

访问：

```text
http://127.0.0.1:8000/login
```

## 默认账号

- 管理员：`admin` / `admin`
- 示例学生：`zhuhang.li@university.com` / `Zhuhangli123`

## 数据库

项目使用 SQLite，并会自动创建 `students.db`。

如果你想把 CSV 示例数据导入数据库，可以运行：

```bash
python migrate_csv_to_orm.py
```

## 说明

- 桌面端界面使用按钮来显示文字，这是为了适配当前环境的 Tk 渲染限制。
- Web 端会在内存中保存会话，因此重启进程后登录状态会失效。
- 如果你在 Linux 或 Windows 上运行，请直接执行 Python 入口文件，不要使用 `.sh` 脚本。
