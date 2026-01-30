# 📖 Usage Examples - UX Transcript Analysis System

Real-world usage scenarios and examples for the system.

## 🎯 Scenario 1: Analyzing Your First Transcript

**Goal**: Analyze a single interview to understand user pain points

### Steps:

1. **Start the System**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python app.py
   
   # Open frontend in browser
   open frontend/index.html  # or double-click file
   ```

2. **Select a Transcript**
   - In the left sidebar, scroll through the list
   - Click on a respondent's name (e.g., "Абатурова Елена")
   - The transcript details appear in the center panel

3. **Run Analysis**
   - Click the blue "🤖 Анализировать с AI" button
   - Wait 30-60 seconds for AI processing
   - View the structured analysis report

4. **Review Results**
   The analysis includes:
   - Summary of key findings
   - User goals and motivations
   - Pain points (with direct quotes)
   - Behavioral patterns
   - Emotional responses
   - Actionable recommendations
   - Tags for categorization

### Expected Output:

```markdown
# Анализ интервью: Абатурова Елена

## Краткое резюме
Пользователь активно использует мобильный банк, но испытывает 
трудности с процессом авторизации и поиском нужных функций.

## Цели пользователя
- Быстро проверять баланс счета
  > "Мне нужно просто посмотреть, сколько денег осталось"
- Делать переводы без сложностей
  > "Хочу отправить деньги и не думать о технических деталях"

## Боли и препятствия
- Долгая авторизация при каждом входе
  > "Каждый раз ввожу этот длинный пароль, хотя телефон мой"
  > Частота: новая тема, требует проверки в других интервью
  
...
```

---

## 🔄 Scenario 2: Comparing Across Multiple Interviews

**Goal**: Find recurring patterns mentioned by multiple users

### Steps:

1. **Analyze Multiple Transcripts**
   - Analyze 5-10 transcripts individually
   - Or use batch analysis for all at once

2. **View Accumulated Insights**
   - Click the "Инсайты" tab at the top
   - Scroll through the master insights document
   - Look for frequency indicators like "упоминается в 15/38 интервью"

3. **Search for Specific Topics**
   - Use browser's Find function (Ctrl+F / Cmd+F)
   - Search for keywords like "авторизация", "безопасность", "удобство"

### Expected Patterns:

```markdown
## Ключевые темы

### Тема: Проблемы с авторизацией
**Частота упоминаний**: 23 из 38 интервью (60%)
**Инсайт**: Большинство пользователей испытывают трудности 
с частыми запросами повторной авторизации, даже при 
использовании биометрии.

**Цитаты**:
- "Постоянно выкидывает, приходится снова вводить пароль" - Иванов
- "Биометрия работает через раз" - Петрова
- "Не могу войти с первого раза, это раздражает" - Сидоров

**Рекомендации**: 
1. Увеличить время сессии с 5 до 30 минут
2. Улучшить стабильность биометрической авторизации
3. Добавить опцию "Запомнить устройство"
```

---

## 📊 Scenario 3: Batch Analysis of All Transcripts

**Goal**: Build comprehensive insights database from all interviews

### Steps:

1. **Prepare for Batch Analysis**
   - Ensure you have API credits (~$5-8 needed)
   - Verify all transcripts are in `Transcripts/` folder
   - Check you have time (20-30 minutes)

2. **Option A: Via Command Line**
   ```bash
   cd backend
   python initial_indexing.py
   ```
   
   You'll see:
   ```
   Found 38 transcripts
   Estimated time: 19 minutes
   Estimated cost: $3.80
   Proceed with initial indexing? (yes/no): yes
   ```

3. **Option B: Via Web Interface**
   - Click "📊 Массовый анализ всех транскриптов"
   - Confirm the operation
   - Watch progress in the loading screen

4. **Monitor Progress**
   ```
   [1/38] Analyzing: Абатурова Елена
     Words: 2,450
     ✓ Analysis completed (3,200 tokens)
     ✓ Report saved
     ✓ Master insights updated
   [2/38] Analyzing: Астахов Дмитрий
   ...
   ```

5. **Review Results**
   - Check `Insights/master_insights.md` for accumulated insights
   - Browse individual reports in `Insights/reports/`
   - View statistics in the web interface header

---

## 🏷️ Scenario 4: Working with Tags

**Goal**: Filter and categorize insights by topic

### Common Tag Categories:

**Products & Features:**
- `#mobile_app` - Mobile banking app issues
- `#web_platform` - Web interface feedback
- `#atm` - ATM usage and problems
- `#cards` - Card-related feedback

**User Journeys:**
- `#onboarding` - First-time user experience
- `#authentication` - Login and security
- `#transactions` - Payment and transfer flows
- `#support` - Customer service interactions

**Emotions:**
- `#frustration` - User frustrations
- `#satisfaction` - Positive experiences
- `#anxiety` - Security concerns
- `#confusion` - Unclear interfaces

**Topics:**
- `#security` - Security and privacy
- `#usability` - Ease of use
- `#performance` - Speed and reliability
- `#design` - Visual design feedback

### How to Use Tags:

1. **In Analysis Reports**: AI automatically adds relevant tags
2. **In Search**: Use tags to filter insights
3. **In Web UI**: View top tags in the info panel
4. **For Reporting**: Group insights by tag for presentations

---

## 📝 Scenario 5: Generating Recommendations

**Goal**: Extract actionable recommendations for product team

### Steps:

1. **Analyze Representative Sample**
   - Select 10-15 transcripts covering different user profiles
   - Include both satisfied and frustrated users

2. **Extract Recommendations Section**
   - Go to "Инсайты" tab
   - Find "## Рекомендации для продуктовой команды" sections
   - Compile top recommendations

3. **Prioritize by Frequency**
   - Count how many users mentioned each issue
   - Focus on problems mentioned by >30% of users
   - Quick wins: high impact, easy to fix

### Example Recommendations Output:

```markdown
# Топ-10 Рекомендаций для Продуктовой Команды

## Высокий приоритет (упомянуто >50% пользователей)

1. **Улучшить процесс авторизации** (60% пользователей)
   - Проблема: Частые запросы повторной авторизации
   - Решение: Увеличить время сессии до 30 минут
   - Ожидаемый эффект: Снижение негативных отзывов на 40%
   
2. **Упростить навигацию в мобильном приложении** (55%)
   - Проблема: Пользователи не могут найти нужные функции
   - Решение: Редизайн главного экрана с частыми действиями
   - Ожидаемый эффект: Рост использования на 25%

## Средний приоритет (30-50% пользователей)

3. **Добавить поиск по транзакциям** (45%)
   - Проблема: Трудно найти старые операции
   - Решение: Поисковая строка с фильтрами
   
...
```

---

## 🔍 Scenario 6: Searching for Specific Topics

**Goal**: Find all mentions of a specific feature or problem

### Using the API:

```bash
# Search via curl
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "биометрия"}'
```

### Using the Web Interface:

1. Go to "Инсайты" tab
2. Use browser search (Ctrl+F)
3. Search for keywords like:
   - "биометрия" → biometric authentication issues
   - "перевод" → transfer/payment flows
   - "карта" → card-related feedback
   - "безопасность" → security concerns

### Example Search Results:

```
Found 12 mentions of "биометрия":

1. Insights/reports/Ivanov-Ivan.md
   "Биометрия работает через раз, приходится использовать пароль"
   
2. Insights/reports/Petrova-Anna.md
   "Удобно, что есть биометрия, но она часто не срабатывает"
   
3. master_insights.md (line 234)
   "Проблемы с биометрией упоминаются в 18 из 38 интервью"
```

---

## 📤 Scenario 7: Exporting Results

**Goal**: Create a presentation or report for stakeholders

### Steps:

1. **Collect Key Insights**
   - Open `Insights/master_insights.md`
   - Copy relevant sections

2. **Format for Presentation**
   - Use the structured format from master insights
   - Include direct quotes
   - Add frequency statistics
   - List actionable recommendations

3. **Create Visualizations** (manual)
   - Count frequency of each theme
   - Create charts in Excel/Google Sheets
   - Show top pain points as bar chart
   - Show tag distribution as pie chart

### Example Export Format:

```markdown
# UX Research Insights - Banking App
Date: 2026-01-29
Interviews Analyzed: 38
Research Period: Q4 2025

## Executive Summary
- Analyzed 38 deep interviews with banking app users
- Identified 15 major pain points
- Generated 23 actionable recommendations
- 60% of users struggle with authentication

## Top 5 User Pain Points
1. Frequent re-authentication required (60%)
2. Difficulty finding features in app (55%)
3. Slow transaction history loading (48%)
4. Unclear error messages (42%)
5. Limited offline functionality (38%)

## Key Recommendations
[See detailed recommendations above]

## Next Steps
1. Prioritize top 3 recommendations
2. Create design mockups for authentication flow
3. Conduct A/B testing with proposed changes
```

---

## 🎓 Tips for Best Results

### Analyzing Transcripts:
- **Start Small**: Analyze 3-5 transcripts first to understand output
- **Check Quality**: Review AI analysis for accuracy
- **Iterate**: Adjust prompts in `ai_analyzer.py` if needed

### Building Insights:
- **Look for Patterns**: Focus on themes mentioned by multiple users
- **Quantify**: Always include frequency (e.g., "15 out of 38")
- **Use Quotes**: Direct quotes make insights more compelling

### Using Tags:
- **Be Consistent**: Use the same tags across analyses
- **Don't Over-tag**: 5-8 tags per transcript is enough
- **Create Tag Taxonomy**: Maintain a list of standard tags

### Presenting Results:
- **Tell a Story**: Group insights into narratives
- **Show Impact**: Quantify the effect of each problem
- **Prioritize**: Focus on high-frequency, high-impact issues

---

## ❓ Common Questions

**Q: How long does one analysis take?**
A: 30-60 seconds per transcript, depending on length

**Q: Can I re-analyze a transcript?**
A: Yes, just click analyze again. New report will be created.

**Q: How much does it cost?**
A: ~$0.10-0.20 per transcript on average

**Q: Can I edit the master insights manually?**
A: Yes, edit `Insights/master_insights.md` directly

**Q: What if AI misses something important?**
A: Adjust the prompt in `ai_analyzer.py` or add notes manually

---

**Need more help?** Check `SETUP_GUIDE.md` or `README.md`
