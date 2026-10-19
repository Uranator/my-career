import os, time, requests, pathlib, json

# Загружаем ключи
env_path = pathlib.Path.home() / ".hermes" / ".env"
env = {}
for line in env_path.read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

OR_KEY = env.get("OPENROUTER_API_KEY")
GROQ_KEY = env.get("GROQ_API_KEY")

out_dir = pathlib.Path.home() / "Hermes-vaults" / "clean-v2" / "01_AI_Агенты" / "Генерация_токенов"
out_dir.mkdir(parents=True, exist_ok=True)

# Список задач для сжигания токенов
tasks = [
    "Напиши 5 сценариев для Reels про бутик L-Jeans (стиль, логотипы, качество).",
    "Составь пошаговый гайд для отца: как настроить Zapret на роутере за 5 минут.",
    "Придумай 3 варианта заголовков для YouTube-видео про Python-автоматизацию.",
    "Напиши пост в Telegram про то, как ИИ (Hermes) помогает экономить время.",
    "Составь чек-лист для собеседования на DevOps Junior.",
    "Придумай идею для приложения на Python, которое можно сделать за выходные.",
    "Напиши письмо-сопровождение (Cover Letter) для позиции AI Engineer.",
    "Составь список 10 бесплатных API для разработчиков (кроме OpenRouter).",
    "Придумай 5 мемов про программистов и нейросети.",
    "Напиши инструкцию, как восстановить роутер Cudy WR3000S через TFTP."
]

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"}
    payload = {"model": "nvidia/nemotron-3-super-120b-a12b:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 429: return None
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None

def call_groq(prompt):
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 429: return None
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None

print("🔥 Начинаем сжигание токенов...")
for i, task in enumerate(tasks):
    print(f"[{i+1}/{len(tasks)}] Генерация: {task[:40]}...")
    
    # Пытаемся сначала OpenRouter, если 429 - переключаемся на Groq
    res = call_openrouter(task)
    if not res:
        print("  ⚠️ OpenRouter лимит, переключаюсь на Groq...")
        res = call_groq(task)
        
    if res:
        filename = f"task_{i+1:02d}.md"
        (out_dir / filename).write_text(f"# {task}\n\n{res}\n", encoding="utf-8")
        print(f"  ✓ Сохранено в {filename}")
    else:
        print(f"  ❌ Оба лимита исчерпаны. Останавливаюсь.")
        break
        
    time.sleep(3) # Пауза, чтобы не поймать бан

print("✅ Готово. Смотри папку 01_AI_Агенты/Генерация_токенов")
