from fastapi import Request


async def block_mutations_when_read_only(request: Request, call_next):
    return await call_next(request)
