import asyncio, pathlib, re, subprocess, yaml
from playwright.async_api import async_playwright

HH_SESSION = pathlib.Path.home() / "hh-bot" / "data" / "storage_state" / "hh_session.json"
CONFIG_PATH = pathlib.Path.home() / "hh-bot" / "data" / "config.yaml"
HH_BOT_DIR = pathlib.Path.home() / "hh-bot"

async def main():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    resumes = config.get("resumes", [])
    python_resume = next((r for r in resumes if r["id"] == "python"), None)
    if not python_resume:
        print("❌ Резюме python не найдено в конфиге")
        return

    m = re.search(r"/resume/([a-f0-9]+)", python_resume["resume_url"])
    if not m:
        print("❌ Не удалось извлечь ID резюме")
        return
    resume_id = m.group(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(HH_SESSION))
        page = await context.new_page()

        # 1. Открываем страницу редактирования
        url = f"https://hh.ru/resume/{resume_id}/edit"
        print(f"Открываю {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # 2. Прокручиваем до блока навыков
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # 3. Удаляем все навыки (ищем кнопки с иконкой крестика или data-qa)
        # Пробуем несколько селекторов, пока не найдём
        selectors = [
            "button[data-qa='skill-remove']",
            "button:has(svg[data-icon='cross'])",
            "button:has-text('Удалить')",
            "button[aria-label='Удалить']"
        ]
        total_deleted = 0
        for sel in selectors:
            buttons = await page.query_selector_all(sel)
            if buttons:
                print(f"Найдено кнопок по селектору '{sel}': {len(buttons)}")
                for btn in buttons:
                    try:
                        await btn.click()
                        await page.wait_for_timeout(300)
                        # Подтверждаем, если появилось окно
                        confirm = await page.query_selector("button:has-text('Удалить')")
                        if confirm:
                            await confirm.click()
                            await page.wait_for_timeout(300)
                        total_deleted += 1
                    except:
                        pass
                break  # если нашли по одному селектору, другие не пробуем

        print(f"Удалено навыков: {total_deleted}")

        # 4. Переименовываем резюме через hhru-bot
        print("Переименовываю резюме в 'Python Developer'...")
        subprocess.run(
            ["hhru-bot", "resume-position", "--resume", "python", "--position", "Python Developer"],
            cwd=HH_BOT_DIR,
            check=False
        )

        # 5. Заливаем новые навыки
        print("Заливаю новые навыки...")
        skills = [
            ("Python", "advanced"), ("FastAPI", "advanced"), ("LLM", "advanced"),
            ("RAG", "intermediate"), ("AI Agents", "advanced"), ("MCP", "advanced"),
            ("Prompt Engineering", "advanced"), ("Tool Calling", "advanced"),
            ("Ollama", "advanced"), ("OpenRouter", "advanced"),
            ("Docker", "intermediate"), ("Linux", "advanced"),
            ("Git", "advanced"), ("SQL", "intermediate"),
            ("PostgreSQL", "intermediate"), ("REST API", "advanced"),
            ("Bash", "advanced"), ("CI/CD", "intermediate"),
            ("Obsidian", "advanced")
        ]
        cmd = ["hhru-bot", "edit-skills", "--resume", "python", "--mode", "fresh", "--force"]
        for name, level in skills:
            cmd.extend(["--skill", f"{name}={level}"])
        subprocess.run(cmd, cwd=HH_BOT_DIR, check=False)

        await browser.close()

asyncio.run(main())
