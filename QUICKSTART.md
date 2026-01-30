# ⚡ Quick Start Guide

Get up and running in 5 minutes!

## 🎯 Prerequisites

- Python 3.8+
- OpenAI API key

## 🚀 3 Steps to Start

### 1️⃣ Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ Configure API Key

Create `backend/.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
```

### 3️⃣ Start the System

**Backend:**
```bash
cd backend
python app.py
```

**Frontend:**
Open `frontend/index.html` in your browser

## ✅ Verify It Works

1. Open `http://localhost:5000/api/health` - should show `"status": "healthy"`
2. Check frontend shows 38 transcripts in the sidebar
3. Click a transcript → Click "Анализировать с AI" → Wait ~30 seconds
4. View the analysis report!

## 📚 Next Steps

- Read `SETUP_GUIDE.md` for detailed setup
- Check `USAGE_EXAMPLES.md` for usage scenarios
- Run `python test_system.py` to test all components

## 🆘 Troubleshooting

**API not working?**
- Check `.env` file has correct API key
- Ensure backend is running on port 5000

**Can't analyze transcripts?**
- Verify OpenAI API key has billing enabled
- Check internet connection

**Need help?**
See `SETUP_GUIDE.md` for detailed troubleshooting.

---

**That's it!** Start analyzing your UX interview transcripts with AI! 🎉
