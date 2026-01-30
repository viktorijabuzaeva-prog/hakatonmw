# 🔍 UX Transcript Analysis System

AI-powered system for analyzing interview transcripts in UX research for banking sector. Built for Markswebb.

## 📋 Overview

This system helps UX researchers analyze deep interview transcripts, extract insights, identify patterns, and generate actionable recommendations. It uses AI (OpenAI GPT-4 or Anthropic Claude) to perform semantic analysis of user interviews.

## ✨ Features

- **📄 Transcript Management**: Upload and manage .docx interview transcripts
- **🤖 AI-Powered Analysis**: Deep semantic analysis using GPT-4/Claude
- **💡 Insights Accumulation**: Build a knowledge base of user insights over time
- **🔄 Pattern Recognition**: Identify recurring themes across multiple interviews
- **📊 Batch Processing**: Analyze multiple transcripts at once
- **🏷️ Auto-tagging**: Automatic categorization with tags
- **🔍 Search**: Full-text search through insights and reports
- **📈 Statistics**: Track analysis progress and metrics

## 🏗️ Architecture

```
Hakaton/
├── backend/                 # Python Flask API
│   ├── app.py              # Main Flask application
│   ├── transcript_parser.py # .docx file parser
│   ├── ai_analyzer.py      # AI analysis engine
│   ├── insights_manager.py # Insights management
│   └── requirements.txt    # Python dependencies
├── frontend/               # Web interface
│   ├── index.html         # Main UI
│   ├── styles.css         # Styling
│   └── app.js             # Frontend logic
├── Transcripts/           # Interview transcripts (.docx)
├── Insights/              # Analysis results
│   ├── master_insights.md # Accumulated insights
│   └── reports/           # Individual reports
└── .cursor/
    └── rules/
        └── ux_researcher.md # Cursor AI role configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key or Anthropic API key
- Modern web browser

### Installation

1. **Clone or navigate to the project directory**

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure API keys**

Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your-openai-api-key-here
# or
ANTHROPIC_API_KEY=your-anthropic-api-key-here

AI_PROVIDER=openai
FLASK_ENV=development
FLASK_DEBUG=True
```

4. **Start the backend server**
```bash
cd backend
python app.py
```

The API will start at `http://localhost:5000`

5. **Open the frontend**

Open `frontend/index.html` in your web browser, or serve it with a local server:
```bash
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

## 📖 Usage

### Uploading Transcripts

1. Click "Загрузить новый транскрипт" in the sidebar
2. Select a .docx file containing the interview transcript
3. The transcript will appear in the list

### Analyzing a Single Transcript

1. Select a transcript from the list
2. Click "Анализировать с AI"
3. Wait for AI analysis (30-60 seconds)
4. View the detailed analysis report

### Batch Analysis

1. Click "Массовый анализ всех транскриптов"
2. Confirm the operation
3. Wait for all transcripts to be analyzed
4. View accumulated insights in the "Инсайты" tab

### Viewing Insights

1. Switch to the "Инсайты" tab
2. Browse the accumulated insights from all analyzed interviews
3. Use the search function to find specific topics

## 🔧 API Endpoints

### Transcripts
- `GET /api/transcripts` - List all transcripts
- `POST /api/transcripts` - Upload a new transcript
- `GET /api/transcripts/<name>` - Get specific transcript

### Analysis
- `POST /api/analyze` - Analyze a transcript
- `POST /api/analyze/batch` - Batch analyze transcripts
- `POST /api/compare` - Compare transcript with existing insights

### Insights
- `GET /api/insights` - Get master insights
- `POST /api/insights` - Update master insights
- `GET /api/insights/reports` - List all reports

### Utilities
- `GET /api/statistics` - Get system statistics
- `POST /api/search` - Search through insights
- `GET /api/health` - Health check

## 📊 Analysis Framework

The AI analyzer uses a structured framework:

1. **User Goals**: What users want to achieve
2. **Pain Points**: Obstacles and frustrations
3. **Behavioral Patterns**: How users interact with services
4. **Expectations vs Reality**: Service delivery gaps
5. **Emotional Responses**: Sentiment and feelings

Each analysis includes:
- Direct quotes from interviews
- Cross-references with previous interviews
- Quantified patterns (e.g., "mentioned by 15/38 respondents")
- Actionable recommendations
- Automatic tagging

## 🏷️ Tagging System

Consistent tags for categorization:
- **Products**: `#mobile_app`, `#web_platform`, `#atm`, `#cards`
- **Journeys**: `#onboarding`, `#authentication`, `#transactions`
- **Emotions**: `#frustration`, `#satisfaction`, `#anxiety`, `#trust`
- **Topics**: `#security`, `#usability`, `#performance`, `#design`

## 🔐 Data Privacy

- All data is stored locally
- No data is sent to external services except AI APIs
- Respondent anonymity is maintained in reports
- Follow GDPR and data protection guidelines

## 🛠️ Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.0.0
- python-docx 1.1.0
- OpenAI API / Anthropic API
- Flask-CORS

**Frontend:**
- HTML5
- CSS3 (Modern design with CSS Grid/Flexbox)
- Vanilla JavaScript (ES6+)
- No framework dependencies

## 📝 Development

### Adding Custom Analysis Prompts

Edit `backend/ai_analyzer.py` and modify the `UX_RESEARCHER_SYSTEM_PROMPT` or `build_analysis_prompt()` method.

### Customizing the UI

Edit `frontend/styles.css` to change colors, layout, or styling. The design uses CSS variables for easy customization.

### Extending the API

Add new endpoints in `backend/app.py`. Follow the existing patterns for consistency.

## 🐛 Troubleshooting

**API not connecting:**
- Check that the backend is running on port 5000
- Verify CORS is enabled
- Check browser console for errors

**AI analysis failing:**
- Verify API keys are set correctly in `.env`
- Check API key has sufficient credits
- Review error messages in backend console

**Transcripts not loading:**
- Ensure .docx files are valid and not corrupted
- Check file permissions
- Verify python-docx is installed

## 📄 License

This project is proprietary software developed for Markswebb UX research.

## 👥 Contributors

Developed for UX research team at Markswebb.

## 📮 Support

For issues or questions, contact the UX research team lead.

---

**Note**: This system requires an active OpenAI or Anthropic API key. Analysis costs depend on the number and length of transcripts analyzed.
