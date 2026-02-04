#!/usr/bin/env python3
"""Test script for video-mcp-server (complete version)"""

import os
import sys

sys.path.insert(0, "/home/debian/video-mcp-server")


def test_imports():
    """Test that all imports work"""
    print("\nTesting imports...")
    try:
        from video_mcp_server.server import (
            AIAnalyzer,
            VideoProcessor,
            YouTubeDownloader,
            check_api_key,
        )

        print("✓ VideoProcessor imported successfully")
        print("✓ YouTubeDownloader imported successfully")
        print("✓ AIAnalyzer imported successfully")
        print("✓ check_api_key imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ffmpeg():
    """Test FFmpeg availability"""
    print("\nTesting FFmpeg...")
    import subprocess

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            print(f"✓ FFmpeg found: {version}")
            return True
        else:
            print("✗ FFmpeg not found or not working")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not installed")
        return False


async def test_list_tools():
    """Test that tools are listed correctly"""
    print("\nTesting list_tools()...")
    try:
        from video_mcp_server.server import list_tools

        tools = await list_tools()
        print(f"✓ Successfully listed {len(tools)} tools:")

        ffmpeg_tools = []
        youtube_tools = []
        ai_tools = []

        for tool in tools:
            if "requires GROQ_API_KEY" in tool.description:
                ai_tools.append(tool.name)
                print(f"  - {tool.name}: [AI] {tool.description[:50]}...")
            elif "YouTube" in tool.description or "youtube" in tool.name:
                youtube_tools.append(tool.name)
                print(f"  - {tool.name}: [YouTube] {tool.description[:50]}...")
            else:
                ffmpeg_tools.append(tool.name)
                print(f"  - {tool.name}: [FFmpeg] {tool.description[:50]}...")

        print(f"\n  FFmpeg-only tools: {len(ffmpeg_tools)}")
        print(f"  YouTube tools: {len(youtube_tools)}")
        print(f"  AI-powered tools: {len(ai_tools)}")
        print(f"  Total: {len(tools)} tools")
        return True
    except Exception as e:
        print(f"✗ Error listing tools: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_key_check():
    """Test API key detection"""
    print("\nTesting API key detection...")
    try:
        from video_mcp_server.server import check_api_key

        has_key = check_api_key()
        if has_key:
            print("✓ GROQ_API_KEY is set")
            print("  Server will run with AI capabilities")
        else:
            print("⚠ GROQ_API_KEY not set")
            print("  Server will run in FFmpeg-only mode")
            print("  AI features will be unavailable")
        return True
    except Exception as e:
        print(f"✗ Error checking API key: {e}")
        return False


async def main():
    print("=" * 60)
    print("Video MCP Server - Complete Test Suite")
    print("=" * 60)

    # Test 1: Imports
    imports_ok = test_imports()

    # Test 2: FFmpeg
    ffmpeg_ok = test_ffmpeg()

    # Test 3: List tools
    tools_ok = await test_list_tools()

    # Test 4: API key
    api_key_ok = test_api_key_check()

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"  Imports:     {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"  FFmpeg:      {'✓ PASS' if ffmpeg_ok else '✗ FAIL'}")
    print(f"  Tools:       {'✓ PASS' if tools_ok else '✗ FAIL'}")
    print(f"  API Check:   {'✓ PASS' if api_key_ok else '✗ FAIL'}")

    if all([imports_ok, ffmpeg_ok, tools_ok, api_key_ok]):
        print("\n✓ Video MCP Server is ready!")
        print("\nFeatures:")
        print("  - FFmpeg-only mode: Always available")
        print("  - AI-powered mode: Available with GROQ_API_KEY")
        print("\nTo use AI features, get free API key:")
        print("  https://console.groq.com/keys")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    import asyncio

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
