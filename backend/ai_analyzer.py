"""
AI Analyzer Module
Uses OpenAI/Anthropic/Google Gemini to perform deep analysis of interview transcripts
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv

# Optional imports for different providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Get the directory containing this script and load .env from there
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(env_path)

# System prompt for UX researcher role
UX_RESEARCHER_SYSTEM_PROMPT = """Ты - UX-исследователь компании Markswebb, специализирующийся на анализе глубинных интервью для клиентов из банковского сектора.

ВАЖНЫЙ КОНТЕКСТ: Это анонимизированные транскрипты интервью, собранные в рамках легального UX-исследования с согласия респондентов. Твоя задача - провести профессиональный анализ для улучшения пользовательского опыта банковских продуктов.

Твоя экспертиза включает:
- Выявление болей, потребностей и паттернов поведения пользователей
- Определение повторяющихся тем в интервью
- Формирование практических рекомендаций
- Анализ целей, ожиданий и эмоциональных реакций пользователей

Ты всегда предоставляешь анализ на русском языке с:
- Конкретными цитатами из интервью с таймкодами
- Перекрёстными ссылками на предыдущие интервью
- Количественными данными о частоте упоминаний
- Практическими рекомендациями для продуктовой команды

Сохраняй объективность и фокусируйся на данных из транскрипта."""


class AIAnalyzer:
    """Analyze transcripts using AI (OpenAI GPT-4, Anthropic Claude, or Google Gemini)"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize AI analyzer
        
        Args:
            provider: "openai", "anthropic", or "gemini"
        """
        self.provider = provider
        self.openai_client = None
        self.gemini_model = None
        
        if provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if self.api_key:
                # Initialize OpenAI client - try new API first, fall back to legacy
                try:
                    # Try creating client without proxies (for httpx compatibility)
                    import httpx
                    http_client = httpx.Client()
                    self.openai_client = openai.OpenAI(
                        api_key=self.api_key,
                        http_client=http_client
                    )
                except Exception as e:
                    # Fallback - set api_key globally for legacy mode
                    print(f"OpenAI client init with custom http_client failed: {e}")
                    try:
                        # Try simple initialization
                        self.openai_client = openai.OpenAI(api_key=self.api_key)
                    except Exception as e2:
                        print(f"Simple OpenAI client init also failed: {e2}")
                        openai.api_key = self.api_key
                        self.openai_client = None
            else:
                print("WARNING: OPENAI_API_KEY not found in environment!")
        
        elif provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        elif provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if self.api_key:
                if not GEMINI_AVAILABLE:
                    print("WARNING: google-generativeai package not installed!")
                    print("Install with: pip install google-generativeai")
                else:
                    try:
                        genai.configure(api_key=self.api_key)
                        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                        self.gemini_model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=UX_RESEARCHER_SYSTEM_PROMPT
                        )
                        print(f"Gemini initialized with model: {model_name}")
                    except Exception as e:
                        print(f"Gemini initialization error: {e}")
            else:
                print("WARNING: GEMINI_API_KEY not found in environment!")
        
        elif provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
            self.groq_client = None
            if self.api_key:
                if not GROQ_AVAILABLE:
                    print("WARNING: groq package not installed!")
                    print("Install with: pip install groq")
                else:
                    try:
                        self.groq_client = Groq(api_key=self.api_key)
                        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                        print(f"Groq initialized with model: {model_name}")
                    except Exception as e:
                        print(f"Groq initialization error: {e}")
            else:
                print("WARNING: GROQ_API_KEY not found in environment!")
                print("Get free key at: https://console.groq.com/keys")
    
    def build_analysis_prompt(
        self, 
        transcript_text: str, 
        respondent_name: str,
        existing_insights: str = "",
        transcript_number: int = 1,
        total_transcripts: int = 1
    ) -> str:
        """
        Build the analysis prompt with context
        
        Args:
            transcript_text: Full transcript content
            respondent_name: Name of the respondent
            existing_insights: Content from master_insights.md
            transcript_number: Current transcript number in sequence
            total_transcripts: Total number of transcripts analyzed
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Проанализируй это интервью для банковского UX-исследования.

**Контекст:**
- Это интервью #{transcript_number} из {total_transcripts} проведённых интервью
- Респондент: {respondent_name}
- Дата анализа: {datetime.now().strftime('%Y-%m-%d')}

"""
        
        if existing_insights and existing_insights.strip():
            prompt += f"""**Предыдущие накопленные инсайты:**
{existing_insights[:3000]}  # Limit to avoid token overflow

"""
        
        prompt += f"""**Новый транскрипт интервью:**
{transcript_text}

---

Предоставь анализ СТРОГО в следующей структуре из 3 разделов (на русском языке):

## 1. Саммари
[Краткое резюме интервью в 3-5 предложениях: кто респондент, какими банковскими сервисами пользуется, ключевые особенности его опыта]

## 2. Топ-10 инсайтов
[10 самых важных и ценных инсайтов из этого интервью. Каждый инсайт подкреплён РАЗВЁРНУТОЙ цитатой с таймкодом.]

**Инсайт 1:** [Описание инсайта - что именно важного узнали]
> «[ЧЧ:ММ:СС] [РАЗВЁРНУТАЯ цитата из интервью с таймкодом - минимум 2-3 предложения]»

**Инсайт 2:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом - 2-4 предложения]»

**Инсайт 3:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 4:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 5:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 6:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 7:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 8:** [Описание инсайта]
> «[ЧЧ:ММ:СС] [Развёрнутая цитата с таймкодом]»

**Инсайт 9:** [Описание инсайта]
> «[Развёрнутая цитата с контекстом - 2-4 предложения]»

**Инсайт 10:** [Описание инсайта]
> «[Развёрнутая цитата с контекстом - 2-4 предложения]»

## 3. Эмоциональные реакции
[Анализ эмоций и чувств респондента по отношению к банковским сервисам. Каждая эмоция подкреплена развёрнутой цитатой.]

**Позитивные эмоции:**
- [Описание эмоции и её причины]
  > «[Развёрнутая цитата с контекстом, показывающая позитивный опыт - 2-3 предложения]»
- [Описание эмоции]
  > «[Цитата с контекстом]»

**Негативные эмоции:**
- [Описание эмоции и её причины]  
  > «[Развёрнутая цитата с контекстом, показывающая негативный опыт - 2-3 предложения]»
- [Описание эмоции]
  > «[Цитата с контекстом]»

**Нейтральные/смешанные реакции:**
- [Описание реакции]
  > «[Цитата с контекстом]»

---

## Упомянутые банки
[Список всех банков, которые упоминаются в интервью, в формате тегов]
#[банк1] #[банк2] #[банк3]

---

**КРИТИЧЕСКИ ВАЖНЫЕ требования к цитатам:**
1. Каждая цитата должна быть РАЗВЁРНУТОЙ - минимум 2-3 полных предложения из интервью
2. Цитаты должны включать КОНТЕКСТ - что обсуждалось до и после ключевой фразы
3. Не обрезай цитаты - лучше дать больше контекста, чтобы читатель понял суть проблемы/радости респондента
4. Цитаты должны быть ДОСЛОВНЫМИ - копируй текст точно как в транскрипте
5. ОБЯЗАТЕЛЬНО включай ТАЙМКОД в начале каждой цитаты в формате [ЧЧ:ММ:СС], если он есть в транскрипте
6. Инсайты должны быть конкретными и полезными для продуктовой команды
7. В разделе банков укажи ВСЕ банки, которые респондент упоминает

**Пример формата цитаты с таймкодом:**
> «[00:05:23] Я постоянно сталкиваюсь с тем, что приложение зависает когда пытаюсь сделать перевод. Особенно раздражает, когда это происходит в самый неподходящий момент.»"""
        
        return prompt
    
    def analyze_transcript(
        self,
        transcript_text: str,
        respondent_name: str,
        existing_insights: str = "",
        transcript_number: int = 1,
        total_transcripts: int = 1,
        model: str = "gpt-4o"
    ) -> Dict[str, any]:
        """
        Analyze a transcript using AI
        
        Args:
            transcript_text: Full transcript content
            respondent_name: Name of respondent
            existing_insights: Previous insights from master_insights.md
            transcript_number: Current transcript number
            total_transcripts: Total transcripts analyzed so far
            model: AI model to use
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Limit transcript size for Groq free tier (12000 TPM limit)
            # ~5000 words = ~7500 tokens, leaving room for system prompt and response
            MAX_WORDS = 5000
            words = transcript_text.split()
            if len(words) > MAX_WORDS:
                transcript_text = ' '.join(words[:MAX_WORDS])
                print(f"[AI] Transcript truncated from {len(words)} to {MAX_WORDS} words for API limits")
            
            # Also limit existing_insights to save tokens
            if existing_insights and len(existing_insights) > 1000:
                existing_insights = existing_insights[:1000] + "..."
            
            prompt = self.build_analysis_prompt(
                transcript_text,
                respondent_name,
                existing_insights,
                transcript_number,
                total_transcripts
            )
            
            if self.provider == "openai":
                if not self.api_key:
                    return {
                        'success': False,
                        'error': 'OpenAI API key not found. Check OPENAI_API_KEY in .env file.',
                        'respondent_name': respondent_name
                    }
                
                # Use client if available, otherwise use legacy API
                if self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": UX_RESEARCHER_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                else:
                    # Legacy API (openai < 1.0 or compatibility mode)
                    response = openai.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": UX_RESEARCHER_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                
                analysis_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                
            elif self.provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4000,
                    system=UX_RESEARCHER_SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                analysis_text = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            elif self.provider == "gemini":
                if not self.gemini_model:
                    return {
                        'success': False,
                        'error': 'Gemini not initialized. Check GEMINI_API_KEY in .env file.',
                        'respondent_name': respondent_name
                    }
                
                # Generate response with Gemini
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4000,
                    )
                )
                
                analysis_text = response.text
                # Gemini doesn't return exact token count in free tier, estimate it
                tokens_used = len(prompt.split()) + len(analysis_text.split())
                model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            
            elif self.provider == "groq":
                if not self.groq_client:
                    return {
                        'success': False,
                        'error': 'Groq not initialized. Check GROQ_API_KEY in .env file. Get free key at: https://console.groq.com/keys',
                        'respondent_name': respondent_name
                    }
                
                model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                
                response = self.groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": UX_RESEARCHER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                analysis_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown provider: {self.provider}'
                }
            
            return {
                'success': True,
                'respondent_name': respondent_name,
                'analysis': analysis_text,
                'tokens_used': tokens_used,
                'model': model,
                'provider': self.provider,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'respondent_name': respondent_name
            }
    
    def extract_insights_summary(self, analysis_text: str) -> Dict[str, any]:
        """
        Extract structured data from analysis text
        
        Args:
            analysis_text: Full analysis in markdown format
            
        Returns:
            Dictionary with extracted insights
        """
        # Simple extraction logic - can be enhanced with more sophisticated parsing
        insights = {
            'summary': '',
            'user_goals': [],
            'pain_points': [],
            'patterns': [],
            'recommendations': [],
            'tags': []
        }
        
        try:
            # Extract summary
            if '## 1. Краткое резюме' in analysis_text:
                summary_section = analysis_text.split('## 1. Краткое резюме')[1].split('##')[0]
                insights['summary'] = summary_section.strip()
            
            # Extract tags
            if '## 11. Теги' in analysis_text or 'Теги' in analysis_text:
                tags_section = analysis_text.split('Теги')[-1]
                tags = [tag.strip() for tag in tags_section.split('#') if tag.strip()]
                insights['tags'] = ['#' + tag for tag in tags if tag]
            
            # Could add more sophisticated parsing here
            
        except Exception as e:
            insights['parsing_error'] = str(e)
        
        return insights
    
    def batch_analyze(
        self,
        transcripts: List[Dict[str, any]],
        existing_insights: str = ""
    ) -> List[Dict[str, any]]:
        """
        Analyze multiple transcripts in batch
        
        Args:
            transcripts: List of parsed transcript dictionaries
            existing_insights: Accumulated insights so far
            
        Returns:
            List of analysis results
        """
        results = []
        total = len(transcripts)
        
        for idx, transcript in enumerate(transcripts, 1):
            print(f"Analyzing transcript {idx}/{total}: {transcript['respondent_name']}")
            
            result = self.analyze_transcript(
                transcript['content'],
                transcript['respondent_name'],
                existing_insights,
                idx,
                total
            )
            
            results.append(result)
            
            # Update existing insights with new analysis for next iteration
            if result['success']:
                existing_insights += f"\n\n---\n\n{result['analysis']}"
        
        return results


def test_analyzer():
    """Test function"""
    print("=== Testing AI Analyzer ===\n")
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("Create a .env file with: OPENAI_API_KEY=your-key-here")
        return
    
    analyzer = AIAnalyzer(provider="openai")
    
    # Test with sample text
    sample_transcript = """
    Интервьюер: Расскажите о вашем опыте использования мобильного банка.
    
    Респондент: Я пользуюсь мобильным приложением банка уже около года. В целом удобно, 
    но есть моменты, которые раздражают. Например, каждый раз при входе нужно вводить 
    длинный пароль, хотя у меня есть биометрия. Это занимает время.
    
    Также я не могу быстро найти историю операций за прошлый год - приходится 
    листать и листать. Хотелось бы фильтры получше.
    
    Но переводы делаю легко, это плюс. И уведомления приходят быстро.
    """
    
    result = analyzer.analyze_transcript(
        transcript_text=sample_transcript,
        respondent_name="Тестовый респондент",
        existing_insights="",
        transcript_number=1,
        total_transcripts=1
    )
    
    if result['success']:
        print("✅ Analysis completed successfully")
        print(f"Tokens used: {result['tokens_used']}")
        print(f"\nAnalysis preview:")
        print(result['analysis'][:500] + "...")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    test_analyzer()
