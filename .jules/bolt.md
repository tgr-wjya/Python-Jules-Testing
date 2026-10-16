## 2024-05-24 - Event Loop Starvation with time.sleep
**Learning:** Using `time.sleep` in a synchronous or asynchronous endpoint blocks the entire main thread, causing event loop starvation in FastAPI/Uvicorn.
**Action:** Always use `await asyncio.sleep` in asynchronous context to unblock the main thread, or run synchronous sleep/blocking logic inside a threadpool using `run_in_threadpool`.
