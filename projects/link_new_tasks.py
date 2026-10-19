import pathlib, re

base = pathlib.Path.home()/"Hermes-vaults"/"clean-v2"/"01_AI_Агенты"/"Генерация_токенов"
if not base.exists():
    print("❌ Папка Генерация_токенов не найдена.")
    exit(1)

count = 0
for f in base.glob("task_*.md"):
    text = f.read_text(encoding="utf-8")
    
    # Берем первую строку как заголовок для тегов
    first_line = text.split('\n')[0].replace('# ', '').strip()
    
    # Проверяем, есть ли YAML шапка
    if not text.startswith("---"):
        header = f"---\ntitle: \"{first_line[:50]}...\"\ntags: [генерация, ai, контент]\ncategory: \"01_AI_Агенты\"\n---\n\n"
        text = header + text
        
    # Добавляем обратную ссылку на хаб
    if "[[HUB-01_AI_Агенты]]" not in text:
        text += "\n\n---\n**Навигация:** Вернуться в [[HUB-01_AI_Агенты]]\n"
        
    f.write_text(text, encoding="utf-8")
    count += 1

print(f"✓ Обработано и привязано новых файлов: {count}")

# Обновляем HUB, чтобы он знал о новых файлах
hub_file = pathlib.Path.home()/"Hermes-vaults"/"clean-v2"/"01_AI_Агенты"/"HUB-01_AI_Агенты.md"
if hub_file.exists():
    hub_text = hub_file.read_text(encoding="utf-8")
    if "[[task_01]]" not in hub_text:
        hub_text += "\n\n## Генерация токенов\n- [[task_01]]\n- [[task_02]]\n- [[task_03]]\n- [[task_04]]\n- [[task_05]]\n- [[task_06]]\n- [[task_07]]\n- [[task_08]]\n- [[task_09]]\n- [[task_10]]"
        hub_file.write_text(hub_text, encoding="utf-8")
        print("✓ HUB обновлен ссылками на новые файлы.")

