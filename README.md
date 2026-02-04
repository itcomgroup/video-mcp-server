# Video MCP Server - Complete Solution

**The most comprehensive video processing MCP server** - combines FFmpeg video processing, YouTube downloading, and optional Groq AI analysis.

## Features Overview

### Video Storage

**By default, downloaded videos are saved to:**
```
~/video-downloads/
```

You can specify a custom directory with the `output_dir` parameter.

To clean up old downloads:
```bash
rm -rf ~/video-downloads/*
```

### Three Categories of Tools:

1. **FFmpeg-only mode** (no API key needed)
   - Video metadata extraction
   - Frame/screenshot extraction
   - Audio extraction to MP3
   - Video splitting into segments

2. **YouTube tools** (no API key needed)
   - Get YouTube video information
   - Download YouTube videos (360p-1080p, best quality)

3. **AI-powered mode** (with Groq API key)
   - AI video analysis with Llama 4 Vision
   - Automatic video summarization
   - Audio transcription with Whisper
   - Complete video analysis (visual + audio)

**Total: 10 powerful tools!**

## Prerequisites

- Python 3.10+
- FFmpeg (required)
- Optional: Groq API key (free) for AI features

### Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: https://ffmpeg.org/download.html
```

### Get Groq API Key (Free & Optional)

For AI features, get a free API key:
1. Visit https://console.groq.com/keys
2. Sign up (free)
3. Create API key

## Installation

```bash
cd video-mcp-server
pip3 install --break-system-packages -e .
```

Or use the install script:
```bash
./install.sh
```

## Configuration

### OpenCode Configuration

**Without API key (FFmpeg-only):**
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

**With API key (Full AI features):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "video-mcp-server": {
      "type": "local",
      "command": ["python", "-m", "video_mcp_server.server"],
      "environment": {
        "GROQ_API_KEY": "gsk_your_key_here"
      }
    }
  }
}
```

### Claude Desktop (Claude Code)

**Configuration file location:**
- Linux/macOS: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Example configuration:**
```json
{
  "mcpServers": {
    "video-mcp-server": {
      "command": "python3",
      "args": ["-m", "video_mcp_server.server"],
      "env": {
        "GROQ_API_KEY": "YOUR_GROQ_API_KEY_HERE"
      }
    },
    "vision-mcp-server": {
      "command": "python3",
      "args": ["-m", "vision_mcp_server.server"]
    }
  }
}
```

**See [claude-desktop-config-example.json](claude-desktop-config-example.json) for a complete example.**

**For detailed setup:** See [CLAUDE_SETUP.md](CLAUDE_SETUP.md)

**Note:** For Linux/macOS, use `python3`. For Windows, use `python`.

### 📋 Check OpenCode Connection Status

**To verify the server is connected:**
```bash
opencode mcp list
```

**Expected output:**
```
●  ✓ video-mcp-server  connected
     python3 -m video_mcp_server.server
```

### 📖 For Detailed OpenCode Setup

See [OPENCODE_SETUP.md](OPENCODE_SETUP.md) for:
- Complete installation guide
- All available tools (10 tools)
- Usage examples
- Troubleshooting
- Test scripts

### Quick Start

1. **Install:**
```bash
cd video-mcp-server
pip3 install --break-system-packages -e .
```

2. **Configure OpenCode:** Copy the configuration above to `~/.config/opencode/config.json`

3. **Test connection:**
```bash
opencode mcp list
```

4. **Use tools in OpenCode chat:**
```
Get information about this video: /path/to/video.mp4
Download this video: https://youtube.com/watch?v=...
Analyze this video: /path/to/video.mp4
```

## Available Tools

### FFmpeg-Only Tools (No API Key Required)

#### 1. `get_video_info`
Get metadata about a video file.

**Usage:**
```
Get information about this video: tutorial.mp4
```

**Returns:**
- Duration (seconds and minutes)
- Resolution (width x height)
- Video codec
- File name

#### 2. `extract_video_frames`
Extract frames/screenshots at equal intervals.

**Usage:**
```
Extract 5 frames from this video: demo.mp4
```

**Parameters:**
- `video_path`: Path to video
- `num_frames`: Number of frames (default: 5, max: 20)
- `output_dir`: Where to save frames (optional)

**Returns:** Paths to extracted frame images

#### 3. `extract_video_audio`
Extract audio track to MP3 file.

**Usage:**
```
Extract audio from this video: lecture.mp4
```

**Returns:** Path to extracted MP3 file

#### 4. `split_video`
Split video into smaller segments.

**Usage:**
```
Split this video into 60-second segments: long-video.mp4
```

**Parameters:**
- `video_path`: Path to video
- `segment_duration`: Seconds per segment (default: 60, max: 300)
- `output_dir`: Where to save segments (optional)

**Returns:** List of segment file paths

### YouTube Tools (No API Key Required)

#### 5. `get_youtube_info`
Get information about a YouTube video without downloading.

**Usage:**
```
Get info about this YouTube video: https://youtube.com/watch?v=...
```

**Returns:**
- Video title
- Duration
- Uploader name
- View count
- Like count
- Upload date
- Short description

#### 6. `download_youtube_video`
Download a YouTube video to local storage.

**Usage:**
```
Download this YouTube video in 720p: https://youtube.com/watch?v=...
```

**Parameters:**
- `url`: YouTube video URL
- `quality`: Video quality (360p, 480p, 720p, 1080p, best)
- `output_dir`: Where to save video (optional)

**Returns:** Path to downloaded video file with title and metadata

### AI-Powered Tools (Groq API Key Required)

#### 7. `analyze_video`
AI analysis of video content using Llama 4 Vision.

**Usage:**
```
Analyze this video and describe what's happening: tutorial.mp4
```

**Parameters:**
- `video_path`: Path to video
- `prompt`: Custom analysis prompt (optional)
- `num_frames`: Frames to analyze (default: 5, max: 10)

**Returns:** Detailed AI analysis of video content

#### 6. `summarize_video`
AI-powered video summarization with narrative flow.

**Usage:**
```
Give me a summary of this video: lecture.mp4
```

**Returns:**
- Main topic/subject
- Key events in chronological order
- Setting and context
- Visual elements
- Overall narrative

#### 7. `transcribe_video`
AI audio transcription using Whisper API.

**Usage:**
```
Transcribe the audio from this video: meeting.mp4
```

**Returns:** Full text transcription of video audio

#### 8. `analyze_video_complete`
Most comprehensive analysis - combines visual and audio.

**Usage:**
```
Do a complete analysis of this video with visuals and audio: demo.mp4
```

**Returns:**
- Visual scene analysis
- Audio transcription
- Combined insights

## Usage Examples

### Basic Usage (No API Key)

```
# Get video info
Get information about tutorial.mp4

# Extract frames for manual analysis
Extract 10 frames from presentation.mp4

# Extract audio
Get audio from meeting.mp4

# Split long video
Split lecture.mp4 into 5-minute segments

# Get YouTube info
Get info about this YouTube video: https://youtube.com/watch?v=...

# Download from YouTube
Download this YouTube video: https://youtube.com/watch?v=...
```

### YouTube Workflow

```
# Step 1: Get info about YouTube video
Get info: https://youtube.com/watch?v=abc123

# Step 2: Download video
Download in 720p: https://youtube.com/watch?v=abc123

# Step 3: Process downloaded video
Extract frames from downloaded_video.mp4
```
# Get video info
Get information about tutorial.mp4

# Extract frames for manual analysis
Extract 10 frames from presentation.mp4

# Extract audio
Get the audio from meeting.mp4

# Split long video
Split lecture.mp4 into 5-minute segments
```

### AI-Powered Usage (With API Key)

```
# AI video analysis
Analyze this tutorial video and explain the steps

# Get summary
Summarize this lecture video

# Transcribe
Transcribe the audio from this presentation

# Complete analysis
Do a full analysis of this demo video with both visuals and audio
```

### Combined Workflow

```
# Step 1: Extract frames
Extract frames from tutorial.mp4

# Step 2: AI analyzes them (if API key set)
Analyze these images for me

# Or: Direct AI video analysis
Analyze tutorial.mp4
```

## Models Used

- **Meta Llama 4 Scout 17B** (vision) - For video frame analysis
- **Whisper Large V3 Turbo** - For audio transcription
- Both available for free via Groq API

## Testing

Run the test suite:

```bash
python3 test_server.py
```

This will check:
- ✓ FFmpeg installation
- ✓ All imports (VideoProcessor, YouTubeDownloader, AIAnalyzer)
- ✓ Tool registration (10 tools: 4 FFmpeg, 2 YouTube, 4 AI)
- ✓ API key detection

## Architecture

```
┌─────────────────────────────────────────────┐
│           Video MCP Server                  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │     VideoProcessor (FFmpeg)          │  │
│  │  • get_video_info                    │  │
│  │  • extract_frames                    │  │
│  │  • extract_audio                     │  │
│  │  • split_video                       │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │     YouTubeDownloader (yt-dlp)      │  │
│  │  • get_youtube_info                  │  │
│  │  • download_youtube_video            │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │      AIAnalyzer (Groq API)           │  │
│  │  • analyze_video                     │  │
│  │  • summarize_video                   │  │
│  │  • transcribe_video                  │  │
│  │  • analyze_video_complete            │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

## Supported Formats

Any format supported by FFmpeg:
- MP4, AVI, MOV, MKV, WebM, FLV, WMV, etc.

## Troubleshooting

### FFmpeg not found
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

### YouTube download issues
```bash
# Install/upgrade yt-dlp
pip3 install --upgrade yt-dlp

# Check yt-dlp version
yt-dlp --version

# Test directly
yt-dlp --help
```

### AI features not working
- Check that `GROQ_API_KEY` is set
- Verify key is valid at https://console.groq.com/keys
- Server starts in FFmpeg-only mode without key

### Permission errors
```bash
chmod +x /path/to/video/file
```

## License

MIT

## Complete Feature List

✅ **4 FFmpeg-only tools** (no API key)
✅ **2 YouTube tools** (no API key)
✅ **4 AI-powered tools** (with Groq API)
✅ **10 total tools**
✅ Video metadata extraction
✅ Frame extraction (up to 20 frames)
✅ Audio extraction to MP3
✅ Video splitting
✅ YouTube video info retrieval
✅ YouTube video downloading (360p-1080p, best)
✅ AI video analysis (Llama 4 Vision)
✅ AI video summarization
✅ AI audio transcription (Whisper)
✅ Complete visual + audio analysis
✅ Works with any FFmpeg-supported format
✅ Works with YouTube videos
✅ Optional API key - graceful degradation
