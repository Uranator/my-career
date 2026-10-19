import sys
import time
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
timeline = proj.GetCurrentTimeline()

print("1. Включаем звук...")
# Размьютить аудиодорожку A1
timeline.SetTrackMute("audio", 1, False)
print("   Звук включен.")

print("2. Применяем цветокор (если API позволит)...")
try:
    proj.SetSetting("colorScienceMode", "davinciYRGBColorManaged")
    proj.SetSetting("colorSpaceInput", "Rec.2100 HLG")
    proj.SetSetting("colorSpaceTimeline", "Rec.709")
    print("   Цветокор применен.")
except Exception as e:
    print(f"   API не дал изменить цвет: {e}. Попробуй вручную в Настройках.")

print("3. Ставим зум на первые 3 клипа...")
items = timeline.GetItemListInTrack("video", 1)
if items:
    for i in range(min(3, len(items))):
        item = items[i]
        item.SetProperty("ZoomX", 1.15)
        item.SetProperty("ZoomY", 1.15)
        print(f"   Зум 1.15x на клип {i+1}.")

print("4. Сохраняем проект...")
pm.SaveProject()
print("✅ Готово.")
