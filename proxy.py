from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import uvicorn
from typing import AsyncGenerator

app = FastAPI()

TARGET_API = "https://gpt-chatbotru-chat1.ru/api/openai/v1/chat/completions"
MODELS_LIST_API = "https://gpt-chatbotru-chat1.ru/api/openai/v1/models"

REQUIRED_HEADERS = {
    # Ваши 14 обязательных заголовков
    "accept": "text/event-stream",
    "accept-language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/json",
    "origin": "https://gpt-chatbotru-chat1.ru",
    "priority": "u=1, i",
    "referer": "https://gpt-chatbotru-chat1.ru/",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-fetch-storage-access": "active",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}

async def stream_generator(client: httpx.AsyncClient, request_data: dict) -> AsyncGenerator[bytes, None]:
    """Потоковый генератор, который не буферизирует данные"""
    async with client.stream(
        "POST",
        TARGET_API,
        json=request_data,
        headers=REQUIRED_HEADERS,
        timeout=None
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk

@app.post("/v1/chat/completions")
async def proxy_request(request: Request):
    request_data = await request.json()
    is_stream = request_data.get("stream", False)
    
    if not is_stream:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TARGET_API,
                json=request_data,
                headers=REQUIRED_HEADERS
            )
            return response.json()
    
    # Критически важные настройки для streaming
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(None),  # Бесконечный таймаут
        limits=httpx.Limits(max_connections=None)  # Без ограничений
    )
    
    return StreamingResponse(
        stream_generator(client, request_data),
        media_type="text/event-stream"
    )

@app.get("/v1/models")
async def models_list():  # Сделаем функцию асинхронной
    async with httpx.AsyncClient() as client:
        response = await client.get(
            MODELS_LIST_API,
            headers=REQUIRED_HEADERS
        )
        return response.json()

if __name__ == "__main__":
    # Запуск с оптимизацией для streaming
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        http="h11",
        loop="asyncio",
        timeout_keep_alive=300,
        log_level="info"
    )
