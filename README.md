# QA Engine - UAT Test Case Generator

An AI-powered and Rule-based UAT test case generation platform designed for professional software testing. It transforms BRD/PRD documents into 50-100+ comprehensive UAT test cases with built-in coverage analysis across 6 business domains.

---

## 🚀 Local Deployment Guide

### Prerequisites
- **Python 3.10+**
- **Node.js** (for serving the frontend, or use any static file server)
- **Git**

### 1. Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize/Patch the database:
   ```bash
   python patch_db.py
   ```
5. Run the FastAPI server:
   ```bash
   python main.py
   ```
   *The backend will run on `http://localhost:8000`.*

### 2. Frontend Setup
The frontend consists of static HTML/JS files. You can serve them using any local server.
- **Using Python (Recommended):**
  In the root project directory, run:
  ```bash
  python -m http.server 5500
  ```
- **Access the App:** Open `http://localhost:5500/index.html` in your browser.

---

## 🔑 User Registration & Authentication

1. **Default Account:**
   - **Email:** `admin.com`
   - **Password:** `admin123`
2. **Register a New User:**
   - Navigate to the Login page (`index.html`).
   - Click "Need an account? Register here".
   - Fill in your Username, Email, and Password.
   - Once registered, you will be automatically logged in.

---

## ⚙️ Configuration (Jira & LLM)

Once logged in, navigate to the **Configuration** page from the sidebar to set up your integrations.

### 🔌 Jira Integration
- **Jira Base URL:** Your organization's Jira URL (e.g., `https://your-domain.atlassian.net`).
- **Jira Email:** The email associated with your Jira account.
- **Jira API Token:** Generate this from your Atlassian Account settings.
- *Tip: Once configured, use the **Jira Story** page to fetch stories directly and generate test cases.*

### 🤖 LLM Configuration (AI Generation)
- **LLM API Key:** Enter your API key for the chosen provider (Gemini, Groq, or OpenAI).
- **Fallbacks:** The system is built with "Smart Fallback". If the LLM call fails or the API key is missing, it will automatically switch to the high-performance **Rules Engine** to ensure your work isn't interrupted.

---

## 🧪 Generating UAT Test Cases

1. Navigate to the **UAT Generator**.
2. **Input:** Either upload a document (`.pdf`, `.docx`, `.txt`, `.md`) or paste the BRD/PRD text manually.
3. **Configure:**
   - **Target Count:** Use the slider to specify how many cases you want (up to 100).
   - **Domain:** Select your industry (Banking, E-Commerce, etc.) for more specialized patterns.
   - **Method:** Choose "Rules Engine" (super fast) or "AI / LLM" (more creative).
4. **Analyze:** After generation, review the **Coverage Dashboard** to see how much of your requirements are covered.
5. **Export:** Download your test cases as **Excel** or **CSV** for easy distribution.

---

## 📁 Project Structure
- **/backend**: FastAPI application, services, and database.
- **/css**: UI styling (vibrant glassmorphism and modern themes).
- **/js**: Frontend logic and API integration.
- **uat.html**: The flagship UAT generation interface.
- **story.html**: User story-focused test generation.
