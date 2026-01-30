# Деплой на Railway

## Шаг 1: Регистрация

1. Перейдите на https://railway.app
2. Нажмите **Login** → **Login with GitHub**
3. Авторизуйтесь через GitHub

## Шаг 2: Создание проекта

1. На главной странице нажмите **New Project**
2. Выберите **Deploy from GitHub repo**
3. Найдите репозиторий `hakatonmw` и выберите его
4. Railway автоматически начнёт деплой

## Шаг 3: Получение бесплатного API ключа Groq

1. Перейдите на **https://console.groq.com/keys**
2. Зарегистрируйтесь (можно через Google)
3. Нажмите **Create API Key**
4. Скопируйте ключ (начинается с `gsk_...`)

## Шаг 4: Настройка переменных окружения

1. В проекте Railway нажмите на сервис (карточка с названием)
2. Перейдите во вкладку **Variables**
3. Добавьте переменные:

```
GROQ_API_KEY=gsk_ваш-ключ-от-groq
AI_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
SECRET_KEY=любая-случайная-строка
```

### Альтернативные провайдеры:

**Google Gemini (бесплатно, но не работает в России):**
```
GEMINI_API_KEY=ваш-ключ
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-1.5-flash
```

**OpenAI (платно):**
```
OPENAI_API_KEY=sk-ваш-ключ-от-openai
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o
```

**Anthropic (платно):**
```
ANTHROPIC_API_KEY=sk-ant-ваш-ключ
AI_PROVIDER=anthropic
```

## Шаг 5: Получение ссылки

1. Перейдите во вкладку **Settings**
2. В разделе **Domains** нажмите **Generate Domain**
3. Railway создаст публичную ссылку вида: `https://hakatonmw-production.up.railway.app`

## Готово!

Сайт будет доступен по сгенерированной ссылке.

---

## Полезные команды Railway CLI (опционально)

```bash
# Установка CLI
npm install -g @railway/cli

# Логин
railway login

# Деплой из локальной папки
railway up
```

---

## Устранение проблем

### Ошибка "No start command"
Убедитесь, что файл `railway.json` загружен в репозиторий.

### Ошибка "Module not found"
Проверьте, что `requirements.txt` находится в папке `backend/`.

### Сайт не открывается
1. Проверьте логи: в Railway нажмите на сервис → **Deployments** → выберите деплой → **View Logs**
2. Убедитесь, что домен сгенерирован в **Settings** → **Domains**

### AI-анализ не работает
Проверьте, что переменная `OPENAI_API_KEY` добавлена в **Variables**.
