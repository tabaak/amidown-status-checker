import urllib.request
import urllib.error
import json
import time

def lambda_handler(event, context):
    # 1. Safely get the URL from the user's request
    query_params = event.get('queryStringParameters') or {}
    target_url = query_params.get('url')

    if not target_url:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "No target URL provided. Please add ?url=example.com to your request."})
        }

    # Add https:// if the user forgot it
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    try:
        # 2. The "Knock" (HEAD request with the Browser Disguise)
        start_time = time.time()
        
        stealth_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        req = urllib.request.Request(target_url, headers=stealth_headers, method='HEAD')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            end_time = time.time()
            latency = round((end_time - start_time) * 1000) # milliseconds
            
            # SUCCESS: 200-399 Status Codes
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "url": target_url,
                    "is_up": True,
                    "status_code": response.getcode(),
                    "latency_ms": latency,
                    "region": "Europe (Frankfurt)"
                })
            }

    except urllib.error.HTTPError as e:
        # FAILURE (Server responded): 400-599 Status Codes (e.g., 404 Not Found, 500 Server Error)
        return {
            "statusCode": 200, 
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "url": target_url,
                "is_up": False,
                "status_code": e.code, # Grabs the exact error number
                "error": str(e.reason),
                "region": "Europe (Frankfurt)"
            })
        }
        
    except urllib.error.URLError as e:
        # FAILURE (No response): Timeout, invalid domain, or server completely offline
        return {
            "statusCode": 200, 
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "url": target_url,
                "is_up": False,
                "status_code": None, # No server to give us a code
                "error": str(e.reason),
                "region": "Europe (Frankfurt)"
            })
        }
        
    except Exception as e:
        # FALLBACK: Catches any weird Python execution errors just in case
        return {
            "statusCode": 200, 
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "url": target_url,
                "is_up": False,
                "status_code": None,
                "error": str(e),
                "region": "Europe (Frankfurt)"
            })
        }