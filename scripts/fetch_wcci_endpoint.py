#!/usr/bin/env python3
"""Fetch WCCI endpoint data to understand the JSON structure."""

import json
import re
import sys
import urllib.request
from pathlib import Path


def fetch_wcci_data(base_url: str = "http://servicewelt.localiot") -> dict:
    """Fetch WCCI configuration data from the endpoint."""
    
    # First, get the session token from the WCCI page
    page_url = f"{base_url}/?s=4,25"
    print(f"Fetching page: {page_url}")
    
    try:
        req = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            # Use latin-1 encoding since UTF-8 fails
            html = response.read().decode('latin-1', errors='replace')
    except Exception as e:
        print(f"Error fetching page: {e}")
        return {}
    
    # Extract session token
    token_match = re.search(r'<div class="sessionToken"[^>]*id="sessionToken"[^>]*>([^<]+)<', html)
    if not token_match:
        print("Could not extract session token from page")
        return {}
    
    session_token = token_match.group(1)
    print(f"Session token: {session_token}")
    
    # Fetch WCCI endpoint data
    endpoint_url = f"{base_url}/external_connections/wcci/wcci_endpoint.php?sessionToken={session_token}"
    print(f"Fetching endpoint: {endpoint_url}")
    
    try:
        req = urllib.request.Request(
            endpoint_url, 
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            response_text = response.read().decode('utf-8')
            print(f"Response: {response_text[:200]}...")
            data = json.loads(response_text)
            return data
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response was: {response_text[:500]}")
        return {}
    except Exception as e:
        print(f"Error fetching endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    """Main function."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://servicewelt.localiot"
    
    print(f"Fetching WCCI data from {base_url}...")
    data = fetch_wcci_data(base_url)
    
    if data:
        # Save to file
        output_file = Path(__file__).parent / "testdata" / "wcci_endpoint_response.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved to: {output_file}")
        print(f"\nWCCI Data Structure:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Analyze the structure
        print(f"\n\nField Analysis:")
        print(f"{'Field Name':<30} {'Type':<15} {'Value'}")
        print("-" * 80)
        for key, value in sorted(data.items()):
            value_type = type(value).__name__
            value_str = str(value)[:50]
            print(f"{key:<30} {value_type:<15} {value_str}")
    else:
        print("Failed to fetch WCCI data")
        sys.exit(1)


if __name__ == "__main__":
    main()
