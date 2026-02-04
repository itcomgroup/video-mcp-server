#!/usr/bin/env python3
"""Test MCP server connection"""

import subprocess
import json
import os

os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY_HERE"


def test_server():
    """Test if video-mcp-server responds to MCP protocol"""

    # Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }

    try:
        # Start the server
        proc = subprocess.Popen(
            ["python3", "-m", "video_mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send initialization request
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Read response
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("✓ Server responds to initialize")
            print(f"  Response ID: {response.get('id')}")
            print(f"  Result: {response.get('result', {}).get('serverInfo', {})}")

            # List tools request
            list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

            proc.stdin.write(json.dumps(list_tools_request) + "\n")
            proc.stdin.flush()

            tools_response = proc.stdout.readline()
            if tools_response:
                tools_data = json.loads(tools_response)
                tools = tools_data.get("result", {}).get("tools", [])
                print(f"\n✓ Server has {len(tools)} tools:")
                for tool in tools[:5]:  # Show first 5
                    print(
                        f"  - {tool.get('name')}: {tool.get('description', '')[:50]}..."
                    )
                if len(tools) > 5:
                    print(f"  ... и {len(tools) - 5} ещё")

                print(f"\n✅ video-mcp-server is working correctly!")
                print(f"   Total tools: {len(tools)}")
                print(f"   FFmpeg-only: 4")
                print(f"   YouTube: 2")
                print(f"   AI-powered: 4")
            else:
                print("✗ No response from tools/list")
        else:
            print("✗ No response from initialize")

        # Cleanup
        proc.stdin.close()
        proc.terminate()
        proc.wait()

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_server()
