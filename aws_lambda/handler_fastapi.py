import httpx
import time
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)


@app.get("/check")
async def check_url(url: str = None):
    # 1. Validate the URL from the user's request
    if not url:
        return {"error": "No target URL provided. Please add ?url=example.com to your request."}

    # Add https:// if the user forgot it
    if not url.startswith("http"):
        url = "https://" + url

    try:
        # 2. The "Knock" (HEAD request with the Browser Disguise, GET fallback)
        start_time = time.time()

        stealth_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(verify=False) as client:
            # Try HEAD first, fall back to GET if it fails
            # (many servers/CDNs reject HEAD requests)
            try:
                response = await client.head(url, headers=stealth_headers, timeout=5, follow_redirects=True)
            except (httpx.ConnectError, httpx.RemoteProtocolError):
                response = await client.get(url, headers=stealth_headers, timeout=5, follow_redirects=True)

        end_time = time.time()
        latency = round((end_time - start_time) * 1000)  # milliseconds

        if response.status_code < 400:
            # SUCCESS: 200-399 Status Codes
            return {
                "url": url,
                "is_up": True,
                "status_code": response.status_code,
                "latency_ms": latency,
                "region": "Europe (Frankfurt)",
            }
        else:
            # FAILURE (Server responded): 400-599 Status Codes
            return {
                "url": url,
                "is_up": False,
                "status_code": response.status_code,
                "error": response.reason_phrase,
                "region": "Europe (Frankfurt)",
            }

    except httpx.TimeoutException:
        # FAILURE: Request timed out
        return {
            "url": url,
            "is_up": False,
            "status_code": None,
            "error": "Connection timed out",
            "region": "Europe (Frankfurt)",
        }

    except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
        # FAILURE: Could not connect (invalid domain, server offline, etc.)
        return {
            "url": url,
            "is_up": False,
            "status_code": None,
            "error": str(e),
            "region": "Europe (Frankfurt)",
        }

    except Exception as e:
        # FALLBACK: Catches any unexpected errors
        return {
            "url": url,
            "is_up": False,
            "status_code": None,
            "error": str(e),
            "region": "Europe (Frankfurt)",
        }
