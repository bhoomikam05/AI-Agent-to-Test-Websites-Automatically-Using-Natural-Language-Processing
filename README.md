# AI Agent for Website Test Automation

This project is an AI-based web testing tool that automates website testing using natural language instructions.

## Features
- Automates website testing
- Accepts natural language commands
- Executes test actions using an AI agent
- Simple web interface

## Project Structure
app.py – Main Flask application  
agent.py – AI agent logic  
templates/index.html – Web interface  

## Installation

1. Clone the repository
2. Install required packages

pip install -r requirements.txt

3. Run the application

python app.py

## Usage
Open your browser and navigate to the server URL (e.g., `http://localhost:5000` locally, or your deployed Render app URL).

Enter a test instruction and run the automation.

## Deployment on Render
This project is configured for deployment to **Render**.

1. Connect your GitHub repository to Render.
2. Select **New** > **Blueprint**. Render will automatically detect the `render.yaml` file.
3. Configure the following environment variable in the Render dashboard:
   - `GROQ_API_KEY`: Your Groq API key for NLP parsing capabilities.
4. Click **Apply** to deploy.

Alternatively, if creating a manual Web Service on Render:
- **Runtime**: `Docker`
- Render will automatically find the `Dockerfile` to build the app and download all necessary Chromium browser dependencies.

## Author
Bhoomika M