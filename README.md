# 🤖 AI Agent to Test Websites Automatically Using Natural Language Processing

An AI-powered web automation agent that converts natural language instructions into browser automation using Large Language Models (LLMs) and Playwright. Users can describe a task in plain English, and the system automatically generates and executes the required browser actions without writing any code.

---

## 📌 Project Overview

This project simplifies browser automation by allowing users to interact with websites using natural language commands. Instead of manually writing Playwright scripts, users simply enter instructions such as:

> "Open YouTube and search for AI Tools"

The system intelligently parses the instruction, generates Playwright automation code using AI, executes the automation, captures screenshots, and provides a detailed execution report.

---

## 🚀 Features

- 🧠 Natural Language Understanding using Groq LLM
- ⚡ Automatic Playwright Script Generation
- 🌐 Browser Automation
- 📸 Automatic Screenshot Capture
- 📊 Detailed Execution Report
- 🔄 Rule-Based Parsing Fallback
- ☁️ Cloud Deployment on Render
- 🔐 Secure API Key Management using Environment Variables
- 🐳 Dockerized Application
- 📱 Responsive Web Interface

---

# 🛠️ Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Python
- Flask
- Waitress

## AI

- Groq API
- LLaMA Model

## Browser Automation

- Microsoft Playwright
- Chromium

## Deployment

- Docker
- Render

---

# 📂 Project Structure

```
AI-Agent/
│
├── agent.py
├── app.py
├── executor.py
├── parser.py
├── report.py
├── api_config.py
├── requirements.txt
├── Dockerfile
├── render.yaml
├── .env.example
│
├── static/
│   ├── screenshots/
│   ├── css/
│   └── js/
│
├── templates/
│   └── index.html
│
└── README.md
```

---

# ⚙️ How It Works

### Step 1

User enters a natural language instruction.

Example:

```
Open YouTube and search AI Agents
```

↓

### Step 2

The instruction is parsed using:

- Groq LLM
- Rule-Based Parser (Fallback)

↓

### Step 3

Structured browser actions are generated.

↓

### Step 4

Playwright automation code is generated automatically.

↓

### Step 5

Chromium browser executes the automation.

↓

### Step 6

Screenshot is captured.

↓

### Step 7

Execution Report is displayed.

---

# 📷 Example Workflow

**Input**

```
Open YouTube and search AI Tools
```

↓

**Generated Actions**

```
Open Website
Type Search Query
Press Enter
Wait for Results
Capture Screenshot
```

↓

**Generated Playwright Code**

```python
page.goto("https://youtube.com")
page.fill("input", "AI Tools")
page.keyboard.press("Enter")
page.screenshot(path="result.png")
```

↓

**Output**

- Screenshot
- Execution Report
- Generated Code
- Automation Status

---

# 📸 Screenshots

Add screenshots of:

- Home Page
- Generated Actions
- Generated Playwright Code
- Execution Report
- Screenshot Output

Example:

```
screenshots/
├── home.png
├── automation.png
├── result.png
```

---

# 🔐 Environment Variables

Create a `.env` file.

```
GROQ_API_KEY=your_groq_api_key
HEADLESS=false
```

---

# ▶️ Running Locally

Clone repository

```bash
git clone https://github.com/bhoomikam05/AI-Agent-to-Test-Websites-Automatically-Using-Natural-Language-Processing.git
```

Move inside project

```bash
cd AI-Agent-to-Test-Websites-Automatically-Using-Natural-Language-Processing
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run application

```bash
python app.py
```

Open

```
http://localhost:5000
```

---

# 🐳 Docker Deployment

Build Docker image

```bash
docker build -t ai-agent .
```

Run container

```bash
docker run -p 5000:5000 ai-agent
```

---

# ☁️ Render Deployment

The application is deployed using:

- Docker
- Render Web Service
- Environment Variables
- Waitress Server

---

# 🧪 Sample Commands

```
Open YouTube and search AI Tools

Open GitHub

Search Python on Wikipedia

Open Amazon and search headphones

Open Netflix

Open Stack Overflow
```

---

# 🔒 Security

- API Keys stored securely using `.env`
- `.env` excluded using `.gitignore`
- `.env.example` provided for setup
- Sensitive credentials never committed

---

# 📈 Future Enhancements

- 🎥 Live Browser Streaming
- 🗣️ Voice Commands
- 📹 Automation Video Recording
- 🤖 Multi-Agent Workflow
- 📄 PDF Report Generation
- 🌍 Multi-Browser Support
- 📊 Automation Analytics Dashboard
- 🔄 Parallel Task Execution

---

# 👩‍💻 Author

**Bhoomika M**

Computer Science Engineering Student

Community Manager @ OSCode

AI & Automation Enthusiast

GitHub:
https://github.com/bhoomikam05

LinkedIn:
(Add your LinkedIn URL)

---

# ⭐ If you found this project useful, don't forget to star the repository!
Bhoomika M
