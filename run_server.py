import sys
import asyncio

# Monkey-patch asyncio on Windows before importing Uvicorn!
# Uvicorn explicitly sets WindowsSelectorEventLoopPolicy which breaks Playwright subprocesses.
# By overwriting it here, Uvicorn is tricked into using ProactorEventLoopPolicy.
if sys.platform.startswith('win'):
    asyncio.WindowsSelectorEventLoopPolicy = asyncio.WindowsProactorEventLoopPolicy
    asyncio.DefaultEventLoopPolicy = asyncio.WindowsProactorEventLoopPolicy
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8002, reload=False)
