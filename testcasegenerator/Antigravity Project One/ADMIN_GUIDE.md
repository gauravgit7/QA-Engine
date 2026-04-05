# 📘 FirstFintech QA Engine: Admin Deployment Guide

This guide provides step-by-step instructions for deploying the **FirstFintech QA Engine** on a local Windows machine with support for local AI generation via **Ollama**.

---

## 📋 Prerequisites

Before starting, ensure your system meets these requirements:
- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: Minimum 16GB RAM (32GB recommended for Llama 3)
- **Disk Space**: ~10GB for Python environments and AI models
- **Software**: 
    - [Python 3.12+](https://www.python.org/downloads/) (Stable)
    - [Ollama](https://ollama.com/download) (For local AI)

---

## 🚀 Step 1: Local AI Setup (Ollama)

1. **Install Ollama**: Download and run the Ollama installer.
2. **Pull the Model**: Open a terminal (PowerShell or CMD) and run:
   ```powershell
   ollama pull llama3:latest
   ```
3. **Verify API**: Ensure the Ollama tray app is running. You can check the health at: [http://127.0.0.1:11434/api/tags](http://127.0.0.1:11434/api/tags)

---

## 🛠️ Step 2: Backend Environment Setup

1. **Navigate to the Backend Folder**:
   ```powershell
   cd "backend"
   ```
2. **Create a Virtual Environment**:
   ```powershell
   python -m venv venv
   ```
3. **Activate the Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```
4. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🔌 Step 3: Launching the Application

You need two separate terminal windows to run the full stack:

### **Terminal A: Backend API**
```powershell
cd "backend"
.\venv\Scripts\python.exe main.py
```
*The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)*

### **Terminal B: Frontend Interface**
```powershell
# In the root project folder
python -m http.server 5500 --bind 127.0.0.1
```
*The Web UI will be available at: [http://127.0.0.1:5500](http://127.0.0.1:5500)*

---

## ⚙️ Step 4: Final Configuration

1. **Log In**: Use the default administrator credentials:
   - **Email**: `admin@firstfintech.com`
   - **Password**: `admin123`
2. **Configure AI Engine**:
   - Go to the **Configuration** panel in the dashboard.
   - Set **LLM API Key** to exactly: `ollama`
   - Save the configuration.

---

## 🛡️ Troubleshooting

> [!IMPORTANT]
> **Issue: Stuck at "Generating..."**
> - Ensure **no other terminal** is running `ollama run llama3`. This locks the model.
> - Check your **Task Manager**. If `ollama_llama_server.exe` is not using ~4GB RAM, the model hasn't finished loading. Wait up to 60 seconds on the first run.

> [!WARNING]
> **Issue: "Connection Refused"**
> - Verify both servers are running.
> - Ensure you are accessing the app via `127.0.0.1` and NOT `localhost` to avoid DNS mismatches.

---

## 📜 Maintenance

- **Database**: All data is stored in `backend/firstfintech_qa.db`. Back this file up frequently.
- **Logs**: Backend execution logs are printed to **Terminal A** for debugging.
