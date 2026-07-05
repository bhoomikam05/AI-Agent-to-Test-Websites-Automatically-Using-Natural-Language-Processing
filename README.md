# 🤖 AI Agent to Test Websites Automatically Using Natural Language Processing

An AI-powered web automation application that converts natural language instructions into Playwright automation scripts. Simply enter commands like **"Open YouTube and search songs"**, and the agent intelligently generates Playwright code, executes the automation, captures screenshots, and displays a detailed execution report.

---

# ✨ Features

- 🧠 Converts natural language into browser automation
- 🎭 Automatically generates Playwright automation code
- 🌐 Executes automation using Playwright and Chromium
- 📸 Captures screenshots after execution
- 📊 Displays parsed actions and execution status
- 🎤 Supports both text and voice input
- ⚡ Optimized browser reuse for faster execution
- 🔐 Secure API key management using environment variables
- ☁️ Deployable on Render using Docker

---

# 🛠️ Tech Stack

### Backend
- Python
- Flask
- Waitress

### Frontend
- HTML
- CSS
- JavaScript

### AI
- Groq API
- Llama Model

### Browser Automation
- Microsoft Playwright
- Chromium

### Deployment
- Docker
- Render

---

# 📂 Project Structure

```
AI-Agent/
│
├── agent.py
├── app.py
├── api_config.py
├── executor.py
├── parser.py
├── report.py
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

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/bhoomikam05/AI-Agent-to-Test-Websites-Automatically-Using-Natural-Language-Processing.git

cd AI-Agent-to-Test-Websites-Automatically-Using-Natural-Language-Processing
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Playwright Browser

```bash
playwright install chromium
```

---

# 🔑 Environment Variables

Create a file named `.env`

```env
GROQ_API_KEY=your_groq_api_key

CHROME_PROFILE_PATH=
```

You can generate your Groq API Key from:

https://console.groq.com/

---

# ▶️ Run the Application

```bash
python app.py
```

---

# 🌍 Open in Browser

Once the server starts, open:

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

**Default Port:** `5000`

> 💡 **Recommended:** For the best performance and full browser visualization, run the application locally. The browser window will be visible, and automation typically completes much faster than on free cloud deployments.

---

# 🧪 Sample Commands

### Google

```text
Open Google
```

```text
Open Google and search Artificial Intelligence
```

```text
Open Google and search Python Programming
```

```text
Open Google and search Machine Learning
```

---

### YouTube

```text
Open YouTube
```

```text
Open YouTube and search songs
```

```text
Open YouTube and search AI tutorials
```

```text
Open YouTube and search Python Flask
```

```text
Open YouTube and play the first video
```

---

# 💡 User Tips

- Use clear and simple natural language instructions.
- Wait for the current automation to complete before starting another one.
- Ensure you have a stable internet connection.
- For the best experience, use supported websites like Google and YouTube.
- If running locally, keep the browser window open while the automation is executing.

---

# 📸 Output

For every automation, the application displays:

- User Instruction
- Parsed Actions
- Generated Playwright Code
- Execution Status (PASS/FAIL)
- Captured Screenshot
- Detailed Execution Report

---

# 🚀 Deployment

The application is deployed using:

- Docker
- Render Web Service
- Environment Variables
- Waitress Production Server

Deployment Steps:

1. Push the project to GitHub.
2. Connect the repository to Render.
3. Deploy using Docker.
4. Configure environment variables.
5. Access the deployed application.

---

# 📝 Notes

- **Local execution is recommended** for the best experience. It provides faster browser automation, lower latency, and a visible browser window, making it ideal for development and demonstrations.
- The deployed version on **Render Free** runs Playwright in **headless mode** and may experience slightly slower execution because of shared CPU and memory resources.
- Some websites, particularly **Google Search**, may occasionally display CAPTCHA challenges when accessed from shared cloud server IP addresses. Running the project locally typically avoids these restrictions.
- The application is fully functional in both local and deployed environments, but local execution offers the best performance and user experience.

---

# 📷 Screenshots

Include screenshots of:

- 🏠 Home Page
- 📋 Parsed Actions
- 🎭 Generated Playwright Code
- ✅ PASS Status
- 📸 Screenshot Output
- 📊 Execution Report

---

# 🔮 Future Enhancements

- 🎥 Live Browser Streaming
- 🤖 Multi-Agent Workflow
- 🗣️ Voice Commands
- 📹 Automation Recording
- 🌍 Cross-Browser Support
- 📄 PDF Report Generation
- 📊 Automation Analytics Dashboard
- 🔄 Parallel Task Execution

---

# 👩‍💻 Author

**Bhoomika M**

Computer Science Engineering Student

GitHub:
https://github.com/bhoomikam05

## 🌐 Live Demo

https://ai-agent-to-test-websites-automatically.onrender.com

## 🔗 GitHub Repository

https://github.com/bhoomikam05/AI-Agent-to-Test-Websites-Automatically-Using-Natural-Language-Processing

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
