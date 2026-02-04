#!/usr/bin/env python3
"""Quick test of YouTube functionality"""

import sys

sys.path.insert(0, "/home/debian/video-mcp-server")


def test_youtube_info():
    """Test getting YouTube video info"""
    print("\nTesting YouTube info retrieval...")
    print("Using URL: https://www.youtube.com/watch?v=jNQXAC9IVRw")

    try:
        from video_mcp_server.server import YouTubeDownloader

        downloader = YouTubeDownloader()
        result = downloader.get_video_info_url(
            "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        )

        if result.get("success"):
            print(f"✓ Successfully got video info:")
            print(f"  Title: {result.get('title', 'unknown')}")
            print(f"  Duration: {result.get('duration', 0)} seconds")
            print(f"  Uploader: {result.get('uploader', 'unknown')}")
            return True
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_youtube_info()
    sys.exit(0 if success else 1)
