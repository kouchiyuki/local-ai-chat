from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# OllamaのURL
OLLAMA_URL = "http://localhost:11434/api/generate"

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "あなたは親切なアシスタントです。" # もし空っぽならこれを使う

@app.post("/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": "gemma3:4b",
        "prompt": request.message,
        "stream": True,  # ストリーミングを有効化
        "system": request.system_prompt #性格

    }

    def event_generator():
        # stream=True でリクエストを送り、接続を維持する
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                # Ollamaから届く1行ずつのJSONを解析して文字だけを取り出す
                data = json.loads(line.decode("utf-8"))
                token = data.get("response", "")
                yield token  # 1文字（1トークン）ずつブラウザに送信
                
                if data.get("done"):
                    break

    # StreamingResponseとして返す
    return StreamingResponse(event_generator(), media_type="text/plain")

# 最後にフロントエンドを表示するための設定
app.mount("/", StaticFiles(directory=".", html=True), name="static")