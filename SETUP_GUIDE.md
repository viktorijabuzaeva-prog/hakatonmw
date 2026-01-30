# 🚀 Setup Guide - UX Transcript Analysis System

Complete step-by-step guide for setting up and running the system.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation on Windows, check "Add Python to PATH"

2. **OpenAI API Key** (or Anthropic API Key)
   - Get from: https://platform.openai.com/api-keys
   - You'll need billing enabled on your OpenAI account

3. **Modern Web Browser**
   - Chrome, Firefox, Safari, or Edge (latest version)

4. **Interview Transcripts**
   - .docx format
   - UTF-8 encoding recommended
   - Already have 38 transcripts in the `Transcripts/` folder

## 🔧 Installation Steps

### Step 1: Verify Python Installation

Open terminal/command prompt and run:

```bash
python --version
# or
python3 --version
```

You should see: `Python 3.8.x` or higher

### Step 2: Install Python Dependencies

Navigate to the backend folder and install dependencies:

**Windows:**
```bash
cd backend
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd backend
pip3 install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin requests)
- python-docx (Word document parsing)
- openai (AI analysis)
- anthropic (alternative AI provider)
- python-dotenv (environment variables)

### Step 3: Configure API Keys

1. In the `backend/` folder, copy `.env.example` to `.env`:

**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

2. Edit `.env` file and add your API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
AI_PROVIDER=openai
```

**Alternative**: Use Anthropic Claude instead:
```env
ANTHROPIC_API_KEY=your-anthropic-key-here
AI_PROVIDER=anthropic
```

### Step 4: Test the System

Run the test script to verify everything works:

```bash
cd backend
python test_system.py
```

You should see:
```
✓ PASS Transcript Parser
✓ PASS Insights Manager
✓ PASS AI Analyzer
⚠️  SKIP Integration (optional)

Results: 3/4 tests passed
🎉 All tests passed! System is ready to use.
```

## 🎯 Running the System

### Option 1: Using Start Scripts (Recommended)

**Windows:**
Double-click `start_backend.bat`

**Mac/Linux:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

### Option 2: Manual Start

1. **Start the Backend:**

```bash
cd backend
python app.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║   UX Transcript Analysis System - Backend API            ║
╚═══════════════════════════════════════════════════════════╝

Server: http://0.0.0.0:5000
AI Provider: openai
...
```

2. **Open the Frontend:**

Open `frontend/index.html` in your web browser, or serve it with a local server:

```bash
cd frontend
python -m http.server 8000
```

Then navigate to: `http://localhost:8000`

## 📊 Initial Indexing (Optional)

To analyze all existing transcripts and build the initial insights database:

```bash
cd backend
python initial_indexing.py
```

This will:
- Analyze all 38 transcripts
- Generate individual reports
- Build `master_insights.md`
- Takes approximately 20-30 minutes
- Costs approximately $3-5 in API credits

**Note**: You can also do this later through the web interface by clicking "Массовый анализ всех транскриптов"

## 🌐 Using the Web Interface

Once both backend and frontend are running:

1. **View Transcripts**: Left sidebar shows all available transcripts
2. **Analyze Single Transcript**: Click a transcript, then click "Анализировать с AI"
3. **View Insights**: Click the "Инсайты" tab to see accumulated insights
4. **Upload New Transcript**: Click "Загрузить новый транскрипт" button

## 🔍 Verifying the Setup

### Check 1: Backend API
Navigate to: `http://localhost:5000/`

You should see JSON response:
```json
{
  "app": "UX Transcript Analysis System",
  "version": "1.0.0",
  ...
}
```

### Check 2: Health Endpoint
Navigate to: `http://localhost:5000/api/health`

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T..."
}
```

### Check 3: Transcripts Endpoint
Navigate to: `http://localhost:5000/api/transcripts`

You should see list of 38 transcripts

## 🐛 Troubleshooting

### Problem: "Python not found"
**Solution**: 
- Install Python from python.org
- On Windows, reinstall and check "Add Python to PATH"
- Restart terminal after installation

### Problem: "pip: command not found"
**Solution**:
- Try `python -m pip` instead of `pip`
- Or `python3 -m pip` on Mac/Linux

### Problem: "Module 'flask' not found"
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Problem: "API key invalid" or "401 Unauthorized"
**Solution**:
- Check `.env` file has correct API key
- Verify no spaces around the `=` sign
- Ensure API key starts with `sk-` for OpenAI
- Check your OpenAI account has billing enabled

### Problem: "CORS error" in browser console
**Solution**:
- Ensure backend is running
- Check frontend is accessing `http://localhost:5000/api`
- Try opening frontend via local server instead of direct file

### Problem: "Connection refused" error
**Solution**:
- Ensure backend is running on port 5000
- Check no other application is using port 5000
- Try accessing `http://127.0.0.1:5000` instead

### Problem: Can't parse .docx files
**Solution**:
- Ensure files are valid .docx format (not .doc)
- Check file isn't password protected
- Try opening file in Word to verify it's not corrupted

## 📞 Getting Help

If you encounter issues not covered here:

1. Check the logs in the terminal where backend is running
2. Check browser console (F12) for JavaScript errors
3. Review the `README.md` for additional documentation
4. Check the error message details - they often contain the solution

## 🎓 Next Steps

After successful setup:

1. **Explore the Interface**: Click around and familiarize yourself with the UI
2. **Analyze a Test Transcript**: Pick one transcript and run analysis
3. **Review the Results**: Check the generated report and insights
4. **Batch Analysis**: When comfortable, run batch analysis on all transcripts
5. **Customize**: Edit prompts in `ai_analyzer.py` to adjust analysis style

## 🔐 Security Notes

- Keep your `.env` file private (it contains API keys)
- Don't commit `.env` to version control
- API keys grant access to paid services
- Monitor your API usage on OpenAI dashboard
- The system doesn't send transcripts anywhere except OpenAI/Anthropic

## 💰 Cost Estimates

Per transcript analysis (approximate):
- Small transcript (1000 words): $0.05 - $0.10
- Medium transcript (3000 words): $0.10 - $0.20
- Large transcript (5000+ words): $0.20 - $0.40

For 38 transcripts: **$3 - $8 total** (one-time cost for initial indexing)

Additional analyses are cheaper as the system reuses existing insights.

---

**Ready to start?** Run `python test_system.py` to verify everything works!
