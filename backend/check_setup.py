"""
Quick Setup Check Script
Verifies all components are working before starting the server
"""
import os
import sys

def check_setup():
    """Check if everything is set up correctly"""
    print("=" * 60)
    print("Проверка настройки системы")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Check 1: Python version
    print("✓ Python версия:", sys.version.split()[0])
    
    # Check 2: Required modules
    print("\nПроверка библиотек...")
    required_modules = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'docx': 'python-docx',
        'openai': 'OpenAI',
        'dotenv': 'python-dotenv'
    }
    
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            errors.append(f"Библиотека {name} не установлена")
            print(f"  ✗ {name} - НЕ УСТАНОВЛЕНА")
    
    # Check 3: Project structure
    print("\nПроверка структуры проекта...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_dirs = {
        'Transcripts': os.path.join(base_dir, 'Transcripts'),
        'Insights': os.path.join(base_dir, 'Insights'),
        'frontend': os.path.join(base_dir, 'frontend')
    }
    
    for name, path in required_dirs.items():
        if os.path.exists(path):
            if name == 'Transcripts':
                docx_files = [f for f in os.listdir(path) if f.endswith('.docx')]
                print(f"  ✓ {name}/ ({len(docx_files)} .docx файлов)")
            else:
                print(f"  ✓ {name}/")
        else:
            errors.append(f"Папка {name}/ не найдена: {path}")
            print(f"  ✗ {name}/ - НЕ НАЙДЕНА")
    
    # Check 4: .env file
    print("\nПроверка конфигурации...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        print(f"  ✓ .env файл существует")
        
        # Check API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and len(api_key) > 20:
            print(f"  ✓ OPENAI_API_KEY настроен ({api_key[:10]}...)")
        else:
            warnings.append("OPENAI_API_KEY не настроен или слишком короткий")
            print(f"  ⚠ OPENAI_API_KEY не настроен")
    else:
        warnings.append(".env файл не найден")
        print(f"  ⚠ .env файл не найден")
    
    # Check 5: Backend modules
    print("\nПроверка модулей backend...")
    backend_modules = [
        'transcript_parser.py',
        'ai_analyzer.py',
        'insights_manager.py',
        'app.py'
    ]
    
    backend_dir = os.path.dirname(__file__)
    for module in backend_modules:
        module_path = os.path.join(backend_dir, module)
        if os.path.exists(module_path):
            print(f"  ✓ {module}")
        else:
            errors.append(f"Модуль {module} не найден")
            print(f"  ✗ {module} - НЕ НАЙДЕН")
    
    # Summary
    print()
    print("=" * 60)
    if errors:
        print("❌ ОШИБКИ:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    if warnings:
        print("⚠️  ПРЕДУПРЕЖДЕНИЯ:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ ВСЁ ГОТОВО! Можно запускать сервер.")
        print()
        print("Запустите: python app.py")
    elif not errors:
        print("✅ Основные компоненты готовы.")
        print("⚠️  Есть предупреждения, но можно попробовать запустить.")
        print()
        print("Запустите: python app.py")
    else:
        print("❌ Есть критические ошибки. Исправьте их перед запуском.")
        return False
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = check_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
