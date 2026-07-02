import asyncio
from services.llm_agent import chat_stream

async def main():
    out = []
    async for token in chat_stream([{'role': 'user', 'content': '只回复hello'}], max_tokens=20):
        out.append(token)
    print(''.join(out))

asyncio.run(main())
