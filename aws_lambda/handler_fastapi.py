import httpx
import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from config import ALLOWED_ORIGINS, REGION_NAMES

app = FastAPI()
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "x-api-key"],
)

aws_region = os.getenv("AWS_REGION", "Local")
display_region = REGION_NAMES.get(aws_region, aws_region)


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
                # Some servers reject HEAD with 405 — fall back to GET
                if response.status_code in (403, 405):
                    response = await client.get(url, headers=stealth_headers, timeout=5, follow_redirects=True)

            except (httpx.ConnectError, httpx.RemoteProtocolError):
                response = await client.get(url, headers=stealth_headers, timeout=5, follow_redirects=True)

        end_time = time.time()
        latency = round((end_time - start_time) * 1000)

        status: dict = {
            "url": url,
            "region": "Europe (Frankfurt)",
        }

        if response.status_code < 400:
            # SUCCESS: 1xx-3xx Status Codes
            status.update({
                "is_up": True,
                "status_code": response.status_code,
                "latency_ms": latency,
                })

        elif response.status_code < 500:
            # UP WITH WARNING: 4xx Status Codes
            # Server is responding, but may be blocking automated requests
            # (e.g. Cloudflare 403) or returning client errors.
            status.update({
                "is_up": True,
                "status_code": response.status_code,
                "latency_ms": latency,
                "warning": f"Server responded with {response.status_code} ({response.reason_phrase}). Site is reachable but returned a client-side error.",
                })

        else:
            # FAILURE (Server error): 500-599 Status Codes
            status.update({
                "is_up": False,
                "status_code": response.status_code,
                "error": response.reason_phrase,
                })

    except httpx.TimeoutException:
        # FAILURE: Request timed out
        status.update({
            "is_up": False,
            "status_code": None,
            "error": "Connection timed out",
        })

    except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
        # FAILURE: Could not connect (invalid domain, server offline, etc.)
        status.update({
            "is_up": False,
            "status_code": None,
            "error": str(e),
        })

    except Exception as e:
        # FALLBACK: Catches any unexpected errors
        status.update({
            "is_up": False,
            "status_code": None,
            "error": str(e),
        })

    return status