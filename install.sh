#!/bin/bash

echo "========================================"
echo "Video MCP Server - Installation"
echo "========================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "❌ FFmpeg is not installed!"
    echo ""
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: https://ffmpeg.org/download.html"
    exit 1
fi

echo "✓ FFmpeg found: $(ffmpeg -version | head -n1)"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install --break-system-packages -e .

echo ""
echo "========================================"
echo "Installation Complete!"
echo ""
echo "Features:"
echo "  ✓ FFmpeg-only tools (no API key needed)"
echo "    - Video info extraction"
echo "    - Frame extraction"
echo "    - Audio extraction"
echo "    - Video splitting"
echo ""
echo "  ✓ YouTube tools (no API key needed)"
echo "    - Get YouTube video info"
echo "    - Download YouTube videos"
echo "    - Videos saved to: ~/video-downloads/"
echo ""
echo "  ✓ AI-powered tools (with Groq API key)"
echo "    - AI video analysis"
echo "    - Video summarization"
echo "    - Audio transcription"
echo "    - Complete visual+audio analysis"
echo ""
echo "Optional: Get free Groq API key for AI features"
echo "  https://console.groq.com/keys"
echo ""
echo "To clean up downloaded videos:"
echo "  rm -rf ~/video-downloads/*"
echo ""
echo "Add to OpenCode config:"
echo '{'
echo '  "mcp": {'
echo '    "video-mcp-server": {'
echo '      "type": "local",'
echo '      "command": ["python", "-m", "video_mcp_server.server"]'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "Or with API key:"
echo '{'
echo '  "mcp": {'
echo '    "video-mcp-server": {'
echo '      "type": "local",'
echo '      "command": ["python", "-m", "video_mcp_server.server"],'
echo '      "environment": {'
echo '        "GROQ_API_KEY": "gsk_your_key"'
echo '      }'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "Run tests: python3 test_server.py"
