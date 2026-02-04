# Video MCP Server - Резюме проекта

## Что создано:

### Проект: video-mcp-server
**Расположение:** `/home/debian/video-mcp-server/`

### Функционал:
✅ **10 инструментов** для обработки видео:

#### 1. FFmpeg-only (4 инструмента) - без API ключа:
- `get_video_info` — метаданные видео (длительность, разрешение)
- `extract_video_frames` — извлечение кадров (до 20)
- `extract_video_audio` — извлечение аудио в MP3
- `split_video` — разбиение видео на сегменты

#### 2. YouTube (2 инструмента) - без API ключа:
- `get_youtube_info` — информация о YouTube видео
- `download_youtube_video` — скачивание видео (360p-1080p, best)
  - Скачивает в: `~/video-downloads/`
  - Папка создаётся автоматически

#### 3. AI-powered (4 инструмента) - требует Groq API ключ:
- `analyze_video` — AI анализ видео (Llama 4 Vision)
- `summarize_video` — AI саммари видео
- `transcribe_video` — AI транскрибация аудио (Whisper)
- `analyze_video_complete` — полный анализ (видео + аудио)

### Зависимости:
- Python 3.10+
- FFmpeg (установлен)
- yt-dlp (установлен)
- mcp>=1.0.0
- groq>=0.9.0 (для AI функций)
- pillow>=10.0.0

### Структура проекта:
```
video-mcp-server/
├── video_mcp_server/
│   ├── __init__.py
│   └── server.py          # 905 строк, 33KB
├── install.sh             # Скрипт установки
├── test_server.py         # Тесты (10 инструментов)
├── test_youtube.py        # Тест YouTube
├── pyproject.toml         # Зависимости Python
├── README.md              # Полная документация
└── opencode-config-example.json  # Пример конфигурации
```

### Тестирование:
```
✓ All imports working
✓ FFmpeg installed
✓ 10 tools registered (4 FFmpeg, 2 YouTube, 4 AI)
✓ YouTube info retrieval works
✓ Download path: ~/video-downloads/
```

### Конфигурация OpenCode:

**Без API ключа (FFmpeg + YouTube):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "video-mcp-server": {
      "type": "local",
      "command": ["python", "-m", "video_mcp_server.server"]
    }
  }
}
```

**С API ключом (полный функционал):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "video-mcp-server": {
      "type": "local",
      "command": ["python", "-m", "video_mcp_server.server"],
      "environment": {
        "GROQ_API_KEY": "gsk_your_api_key_here"
      }
    }
  }
}
```

### Где скачиваются видео:
```
~/video-downloads/
```

Очистка:
```bash
rm -rf ~/video-downloads/*
```

### Следующие шаги:
1. ✅ Проект создан
2. ✅ Тесты пройдены
3. ✅ Git репозиторий инициализан
4. ⏸️ Авторизация на GitHub в процессе...
   - GitHub CLI установлен (v2.86.0)
   - Код авторизации: 7165-3B72
   - Нужно открыть: https://github.com/login/device

5. 📋 После авторизации:
   ```bash
   cd /home/debian/video-mcp-server
   gh repo create video-mcp-server --public --source=. --remote=origin --push
   ```

### Предыдущий проект:
- **vision-mcp-server** — для работы с изображениями
- URL: https://github.com/itcomgroup/vision-mcp-server.git
- Использовать как пример для создания репозитория

### Ключевые команды:
```bash
# Установка
cd /home/debian/video-mcp-server
pip3 install --break-system-packages -e .

# Тестирование
python3 test_server.py

# Git статус
git status
git log --oneline

# GitHub (после авторизации)
gh auth status
gh repo list
```

---
**Дата создания:** 2026-02-04
**Версия:** 0.1.0
**Статус:** Готово к деплою на GitHub после авторизации
