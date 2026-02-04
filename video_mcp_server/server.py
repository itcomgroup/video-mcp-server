"""Video MCP Server - Complete video processing with FFmpeg + Optional Groq AI

This server provides:
1. FFmpeg-only features (no API key needed): video info, frame extraction, audio extraction, video splitting
2. Groq AI features (requires GROQ_API_KEY): AI analysis of frames, video summarization, audio transcription

Usage:
- Without API key: Basic video processing and frame extraction
- With API key: Full AI-powered video analysis and transcription
"""

import asyncio
import base64
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from groq import AsyncGroq
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

SERVER_NAME = "video-mcp-server"
SERVER_VERSION = "0.1.0"

server = Server(SERVER_NAME)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
AUDIO_MODEL = "whisper-large-v3-turbo"


class VideoProcessor:
    """Video processing using FFmpeg"""

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            # Get duration
            duration_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ]
            duration_result = subprocess.run(
                duration_cmd, capture_output=True, text=True
            )
            duration = (
                float(duration_result.stdout.strip())
                if duration_result.returncode == 0
                else 0
            )

            # Get width/height
            size_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=s=x:p=0",
                video_path,
            ]
            size_result = subprocess.run(size_cmd, capture_output=True, text=True)
            width, height = 0, 0
            if size_result.returncode == 0 and "x" in size_result.stdout:
                width, height = map(int, size_result.stdout.strip().split("x"))

            # Get codec info
            codec_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ]
            codec_result = subprocess.run(codec_cmd, capture_output=True, text=True)
            codec = (
                codec_result.stdout.strip()
                if codec_result.returncode == 0
                else "unknown"
            )

            return {
                "duration": duration,
                "width": width,
                "height": height,
                "codec": codec,
                "path": video_path,
                "filename": Path(video_path).name,
            }
        except Exception as e:
            return {"error": str(e), "path": video_path}

    @staticmethod
    def extract_frames(
        video_path: str, num_frames: int = 5, output_dir: Optional[str] = None
    ) -> List[str]:
        """Extract frames from video at equal intervals"""
        if output_dir is None:
            output_dir = os.path.dirname(video_path) or "."

        os.makedirs(output_dir, exist_ok=True)

        info = VideoProcessor.get_video_info(video_path)
        if "error" in info:
            return []

        duration = info.get("duration", 0)
        if duration <= 0:
            return []

        interval = duration / (num_frames + 1)
        extracted_frames = []

        for i in range(1, num_frames + 1):
            timestamp = i * interval
            frame_filename = f"{Path(video_path).stem}_frame_{i:03d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-ss",
                str(timestamp),
                "-vframes",
                "1",
                "-q:v",
                "2",
                frame_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(frame_path):
                extracted_frames.append(frame_path)

        return extracted_frames

    @staticmethod
    def extract_audio(video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from video to MP3"""
        if output_path is None:
            output_dir = os.path.dirname(video_path) or "."
            output_path = os.path.join(output_dir, f"{Path(video_path).stem}_audio.mp3")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "libmp3lame",
            "-q:a",
            "2",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        return ""

    @staticmethod
    def split_video(
        video_path: str, segment_duration: int = 60, output_dir: Optional[str] = None
    ) -> List[str]:
        """Split video into segments"""
        if output_dir is None:
            output_dir = os.path.dirname(video_path) or "."

        os.makedirs(output_dir, exist_ok=True)

        info = VideoProcessor.get_video_info(video_path)
        if "error" in info:
            return []

        duration = info.get("duration", 0)
        if duration <= 0:
            return []

        output_pattern = os.path.join(
            output_dir, f"{Path(video_path).stem}_segment_%03d.mp4"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-c",
            "copy",
            "-map",
            "0",
            "-segment_time",
            str(segment_duration),
            "-f",
            "segment",
            "-reset_timestamps",
            "1",
            output_pattern,
        ]

        subprocess.run(cmd, capture_output=True, text=True)

        base_name = Path(video_path).stem
        segments = []
        for f in os.listdir(output_dir):
            if f.startswith(f"{base_name}_segment_") and f.endswith(".mp4"):
                segments.append(os.path.join(output_dir, f))

        return sorted(segments)


class YouTubeDownloader:
    """Download videos from YouTube using yt-dlp"""

    @staticmethod
    def download_video(
        url: str, output_dir: Optional[str] = None, quality: str = "720p"
    ) -> Dict[str, Any]:
        """Download YouTube video"""
        import yt_dlp

        if output_dir is None:
            # Use a dedicated downloads directory
            home_dir = os.path.expanduser("~")
            output_dir = os.path.join(home_dir, "video-downloads")

        os.makedirs(output_dir, exist_ok=True)

        # Quality options
        quality_formats = {
            "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
            "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]",
        }

        format_spec = quality_formats.get(quality, quality_formats["720p"])

        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            "format": format_spec,
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "unknown")
                duration = info.get("duration", 0)
                uploader = info.get("uploader", "unknown")
                description = info.get("description", "")[:200]

                # Download video
                ydl.download([url])

                # Find downloaded file
                filename = ydl.prepare_filename(info)
                # Change extension to mp4
                video_path = str(Path(filename).with_suffix(".mp4"))

                # Verify file exists
                if os.path.exists(video_path):
                    return {
                        "success": True,
                        "video_path": video_path,
                        "title": title,
                        "duration": duration,
                        "uploader": uploader,
                        "description": description,
                        "output_dir": output_dir,
                    }
                else:
                    # Try to find the file with any extension
                    base_name = Path(filename).stem
                    for f in os.listdir(output_dir):
                        if f.startswith(base_name) and not f.endswith(".part"):
                            return {
                                "success": True,
                                "video_path": os.path.join(output_dir, f),
                                "title": title,
                                "duration": duration,
                                "uploader": uploader,
                                "description": description,
                                "output_dir": output_dir,
                            }

                    return {
                        "success": False,
                        "error": "Download completed but file not found",
                    }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_video_info_url(url: str) -> Dict[str, Any]:
        """Get info about YouTube video without downloading"""
        import yt_dlp

        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "success": True,
                    "title": info.get("title", "unknown"),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", "unknown"),
                    "description": info.get("description", "")[:500],
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "upload_date": info.get("upload_date", "unknown"),
                    "url": url,
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


class AIAnalyzer:
    """AI analysis using Groq API (optional)"""

    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)

    async def analyze_frames(
        self, frame_paths: List[str], prompt: str, model: str = VISION_MODEL
    ) -> str:
        """Analyze multiple frames using vision model"""
        content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

        for frame_path in frame_paths:
            with open(frame_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                }
            )

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            temperature=0.7,
            max_tokens=4096,
        )

        return response.choices[0].message.content or ""

    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Whisper"""
        with open(audio_path, "rb") as audio_file:
            transcription = await self.client.audio.transcriptions.create(
                file=("audio.mp3", audio_file.read()),
                model=AUDIO_MODEL,
                response_format="text",
            )
            return str(transcription) if transcription else ""

    async def analyze_video(
        self,
        video_path: str,
        prompt: str,
        num_frames: int = 5,
        include_audio: bool = False,
    ) -> Dict[str, str]:
        """Complete video analysis with optional audio"""
        processor = VideoProcessor()

        # Extract frames
        frames = processor.extract_frames(video_path, num_frames)
        if not frames:
            return {"error": "Failed to extract frames from video"}

        # Analyze frames
        visual_result = await self.analyze_frames(frames, prompt)
        result = {"visual_analysis": visual_result, "frames": frames}

        # Optional audio analysis
        if include_audio:
            audio_path = processor.extract_audio(video_path)
            if audio_path:
                try:
                    transcript = await self.transcribe_audio(audio_path)
                    result["transcript"] = transcript
                except Exception as e:
                    result["audio_error"] = str(e)

        return result


# Global instances
ai_analyzer: Optional[AIAnalyzer] = None
video_processor = VideoProcessor()
youtube_downloader = YouTubeDownloader()


def check_api_key() -> bool:
    """Check if Groq API key is available"""
    return bool(os.environ.get("GROQ_API_KEY"))


async def init_analyzer() -> bool:
    """Initialize AI analyzer if API key available"""
    global ai_analyzer
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            ai_analyzer = AIAnalyzer(api_key)
            return True
        except Exception:
            return False
    return False


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        # FFmpeg-only tools (always available)
        Tool(
            name="get_video_info",
            description="Get metadata about a video file (duration, resolution, codec, etc.). No API key required.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    }
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="extract_video_frames",
            description="Extract frames/screenshots from video at equal intervals. No API key required. Returns paths to extracted images.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "num_frames": {
                        "type": "integer",
                        "description": "Number of frames to extract (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save frames (optional)",
                    },
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="extract_video_audio",
            description="Extract audio track from video to MP3 file. No API key required.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output MP3 (optional)",
                    },
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="split_video",
            description="Split video into smaller segments. No API key required.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "segment_duration": {
                        "type": "integer",
                        "description": "Segment duration in seconds (default: 60, max: 300)",
                        "default": 60,
                        "minimum": 10,
                        "maximum": 300,
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for segments (optional)",
                    },
                },
                "required": ["video_path"],
            },
        ),
        # YouTube tools (no API key required)
        Tool(
            name="get_youtube_info",
            description="Get information about a YouTube video (title, duration, uploader, description) without downloading. No API key required.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL (e.g., https://www.youtube.com/watch?v=...)",
                    }
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="download_youtube_video",
            description="Download a YouTube video to local storage. No API key required. Supports quality selection (360p-1080p). Returns path to downloaded video file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL",
                    },
                    "quality": {
                        "type": "string",
                        "description": "Video quality: 360p, 480p, 720p, 1080p, or best (default: 720p)",
                        "default": "720p",
                        "enum": ["360p", "480p", "720p", "1080p", "best"],
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save the video (optional, defaults to current directory)",
                    },
                },
                "required": ["url"],
            },
        ),
        # AI-powered tools (require API key)
        Tool(
            name="analyze_video",
            description="AI-powered video analysis using Groq API (requires GROQ_API_KEY). Extracts frames and analyzes them with Llama 4 Vision model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Analysis prompt (default: 'Describe this video in detail')",
                        "default": "Describe this video in detail, including scenes, actions, objects, people, and context",
                    },
                    "num_frames": {
                        "type": "integer",
                        "description": "Number of frames to analyze (default: 5, max: 10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="summarize_video",
            description="AI-powered video summarization (requires GROQ_API_KEY). Provides comprehensive summary with narrative flow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "num_frames": {
                        "type": "integer",
                        "description": "Number of frames to analyze (default: 8, max: 10)",
                        "default": 8,
                        "minimum": 3,
                        "maximum": 10,
                    },
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="transcribe_video",
            description="AI-powered audio transcription using Groq Whisper API (requires GROQ_API_KEY). Converts speech to text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    }
                },
                "required": ["video_path"],
            },
        ),
        Tool(
            name="analyze_video_complete",
            description="Complete video analysis with visual AND audio content using Groq API (requires GROQ_API_KEY). Most comprehensive analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the video file",
                    },
                    "num_frames": {
                        "type": "integer",
                        "description": "Number of frames to analyze (default: 5, max: 10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["video_path"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    global ai_analyzer

    try:
        # Initialize analyzer if needed for AI tools
        if name in [
            "analyze_video",
            "summarize_video",
            "transcribe_video",
            "analyze_video_complete",
        ]:
            if not ai_analyzer and not await init_analyzer():
                return [
                    TextContent(
                        type="text",
                        text="Error: GROQ_API_KEY environment variable is required for AI features.\n"
                        "Set it with: export GROQ_API_KEY=your-key\n"
                        "Or use FFmpeg-only tools: get_video_info, extract_video_frames, extract_video_audio, split_video",
                    )
                ]

        # Get video path (common for most tools)
        video_path = arguments.get("video_path", "")
        if video_path and not os.path.exists(video_path):
            return [
                TextContent(
                    type="text", text=f"Error: Video file not found: {video_path}"
                )
            ]

        # === FFmpeg-only tools ===
        if name == "get_video_info":
            info = video_processor.get_video_info(video_path)
            if "error" in info:
                result = f"Error: {info['error']}"
            else:
                result = f"""Video Information:
- File: {info["filename"]}
- Duration: {info["duration"]:.2f} seconds ({info["duration"] / 60:.1f} minutes)
- Resolution: {info["width"]}x{info["height"]}
- Video Codec: {info["codec"]}"""

        elif name == "extract_video_frames":
            num_frames = min(arguments.get("num_frames", 5), 20)
            output_dir = arguments.get("output_dir")
            frames = video_processor.extract_frames(video_path, num_frames, output_dir)

            if frames:
                frame_list = "\n".join(
                    [f"  {i + 1}. {frame}" for i, frame in enumerate(frames)]
                )
                result = f"Successfully extracted {len(frames)} frames:\n{frame_list}"
                if not check_api_key():
                    result += (
                        "\n\nYou can analyze these images with your AI model (Kimi)."
                    )
            else:
                result = "Error: Failed to extract frames from video."

        elif name == "extract_video_audio":
            output_path = arguments.get("output_path")
            audio_file = video_processor.extract_audio(video_path, output_path)

            if audio_file:
                result = f"Successfully extracted audio to:\n  {audio_file}"
                if check_api_key():
                    result += "\n\nYou can transcribe this with: transcribe_video"
            else:
                result = "Error: Failed to extract audio from video."

        elif name == "split_video":
            segment_duration = arguments.get("segment_duration", 60)
            output_dir = arguments.get("output_dir")
            segments = video_processor.split_video(
                video_path, segment_duration, output_dir
            )

            if segments:
                segment_list = "\n".join(
                    [f"  {i + 1}. {seg}" for i, seg in enumerate(segments)]
                )
                result = f"Successfully split into {len(segments)} segments ({segment_duration}s each):\n{segment_list}"
            else:
                result = "Error: Failed to split video into segments."

        # === YouTube tools (no API key required) ===
        elif name == "get_youtube_info":
            url = arguments.get("url", "")
            if not url:
                return [TextContent(type="text", text="Error: YouTube URL is required")]

            info = youtube_downloader.get_video_info_url(url)
            if info.get("success"):
                duration_min = info.get("duration", 0) / 60
                result = f"""YouTube Video Information:
- Title: {info.get("title", "unknown")}
- Duration: {info.get("duration", 0)} seconds ({duration_min:.1f} minutes)
- Uploader: {info.get("uploader", "unknown")}
- Views: {info.get("view_count", 0):,}
- Likes: {info.get("like_count", 0):,}
- Upload Date: {info.get("upload_date", "unknown")}
- Description: {info.get("description", "")[:200]}...

To download this video, use: download_youtube_video"""
            else:
                result = f"Error: {info.get('error', 'Failed to get video info')}"

        elif name == "download_youtube_video":
            url = arguments.get("url", "")
            if not url:
                return [TextContent(type="text", text="Error: YouTube URL is required")]

            quality = arguments.get("quality", "720p")
            output_dir = arguments.get("output_dir")

            result = f"Downloading YouTube video...\nURL: {url}\nQuality: {quality}\nThis may take a few minutes..."

            # Perform download
            download_result = youtube_downloader.download_video(
                url, output_dir, quality
            )

            if download_result.get("success"):
                video_path = download_result.get("video_path", "")
                title = download_result.get("title", "unknown")
                duration = download_result.get("duration", 0)
                duration_min = duration / 60 if duration else 0

                result = f"""Successfully downloaded YouTube video!

Title: {title}
Duration: {duration} seconds ({duration_min:.1f} minutes)
Uploader: {download_result.get("uploader", "unknown")}
Saved to: {video_path}

You can now analyze this video:
- Extract frames: extract_video_frames
- Extract audio: extract_video_audio
- Get info: get_video_info
- AI analysis: analyze_video (requires API key)"""
            else:
                result = f"Error downloading video: {download_result.get('error', 'Unknown error')}"

        # === AI-powered tools (require API key) ===
        elif name == "analyze_video":
            prompt = arguments.get(
                "prompt",
                "Describe this video in detail, including scenes, actions, objects, people, and context",
            )
            num_frames = min(arguments.get("num_frames", 5), 10)

            if ai_analyzer:
                analysis = await ai_analyzer.analyze_video(
                    video_path, prompt, num_frames
                )
                if "error" in analysis:
                    result = f"Error: {analysis['error']}"
                else:
                    result = f"=== AI Video Analysis ===\n\n{analysis['visual_analysis']}\n\nAnalyzed {len(analysis['frames'])} frames."
            else:
                result = "Error: AI analyzer not available"

        elif name == "summarize_video":
            num_frames = min(arguments.get("num_frames", 8), 10)

            if ai_analyzer:
                prompt = """Analyze this video and provide a comprehensive summary:
1. Main topic or subject
2. Key events or actions in chronological order
3. Setting and context
4. Visual elements (objects, people, text visible)
5. Overall narrative or message
6. Important details worth noting"""

                analysis = await ai_analyzer.analyze_video(
                    video_path, prompt, num_frames
                )
                if "error" in analysis:
                    result = f"Error: {analysis['error']}"
                else:
                    result = f"=== Video Summary ===\n\n{analysis['visual_analysis']}"
            else:
                result = "Error: AI analyzer not available"

        elif name == "transcribe_video":
            if ai_analyzer:
                # Extract audio first
                audio_path = video_processor.extract_audio(video_path)
                if not audio_path:
                    result = "Error: Failed to extract audio from video"
                else:
                    try:
                        transcript = await ai_analyzer.transcribe_audio(audio_path)
                        result = f"=== Audio Transcription ===\n\n{transcript}"
                    except Exception as e:
                        result = f"Error transcribing audio: {str(e)}"
            else:
                result = "Error: AI analyzer not available"

        elif name == "analyze_video_complete":
            num_frames = min(arguments.get("num_frames", 5), 10)

            if ai_analyzer:
                prompt = """Analyze this video thoroughly. Describe:
1. Visual scenes, settings, and environments
2. Actions, movements, and events
3. Objects, people, and visual elements
4. Visual context and atmosphere"""

                analysis = await ai_analyzer.analyze_video(
                    video_path, prompt, num_frames, include_audio=True
                )

                if "error" in analysis:
                    result = f"Error: {analysis['error']}"
                else:
                    result = f"=== VISUAL ANALYSIS ===\n{analysis['visual_analysis']}"

                    if "transcript" in analysis:
                        result += (
                            f"\n\n=== AUDIO TRANSCRIPTION ===\n{analysis['transcript']}"
                        )
                    elif "audio_error" in analysis:
                        result += f"\n\nNote: Audio analysis unavailable ({analysis['audio_error']})"
            else:
                result = "Error: AI analyzer not available"

        else:
            result = f"Unknown tool: {name}"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point"""
    # Initialize AI analyzer if key is available
    if check_api_key():
        await init_analyzer()
        print("Video MCP Server started with AI capabilities (Groq API)")
    else:
        print("Video MCP Server started (FFmpeg-only mode)")
        print("Set GROQ_API_KEY for AI features")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
