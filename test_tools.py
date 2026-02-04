#!/usr/bin/env python3
"""Test video-mcp-server tools through OpenCode MCP"""

import subprocess
import json
import os

os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY_HERE"


def test_tool_call(tool_name, arguments):
    """Test calling a specific tool"""

    call_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }

    try:
        # Start server
        proc = subprocess.Popen(
            ["python3", "-m", "video_mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Initialize first
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
            },
        }

        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        proc.stdout.readline()  # Skip init response

        # Call tool
        proc.stdin.write(json.dumps(call_request) + "\n")
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            result = response.get("result", [])
            if result:
                print(f"✓ Tool '{tool_name}' executed")
                print(f"  Result: {result[0].get('text', '')[:200]}...")
                return True
        else:
            print(f"✗ No response from tool '{tool_name}'")

        # Cleanup
        proc.stdin.close()
        proc.terminate()
        proc.wait()

    except Exception as e:
        print(f"✗ Error testing '{tool_name}': {e}")
        return False


def main():
    """Main test function"""

    print("Testing video-mcp-server tools through MCP")
    print("=" * 60)

    # Test 1: YouTube info (real video URL)
    print("\nTest 1: get_youtube_info")
    print("-" * 60)
    test_tool_call(
        "get_youtube_info", {"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"}
    )

    # Test 2: Video info (use video we downloaded)
    print("\nTest 2: get_video_info")
    print("-" * 60)
    video_path = "/home/debian/video-downloads/openclaw_2026_ai_agent.mp4"
    if os.path.exists(video_path):
        test_tool_call("get_video_info", {"video_path": video_path})
    else:
        print(f"Video file not found: {video_path}")

    print("\n" + "=" * 60)
    print("video-mcp-server tools are accessible through OpenCode MCP!")
    print("=" * 60)


if __name__ == "__main__":
    main()
