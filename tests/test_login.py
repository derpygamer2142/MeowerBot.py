from env_shared import AioRunner
import asyncio

runner = None

async def on_ready(A):
    if not runner:
        raise Exception("No runner")
    if not runner._http:
        raise Exception("No HTTP")


    await runner._http.send_feed_post("Hello World!")
    print("Ready")


async def main():
    global runner
    async with AioRunner(asyncio.get_event_loop()) as runner:
        if not runner._http:
            print("No HTTP")
            return
        
        if not runner._websocket:
            print("No WebSocket")
            return
        
        runner._websocket.cbs["auth"] = [on_ready]
        await runner.run()

        
asyncio.run(main())