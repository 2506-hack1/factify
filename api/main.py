from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()

# テキストの正規化を行う
def clean_text(raw_text: str) -> str:
    # 全角スペースやタブを半角スペースに変換
    text = raw_text.replace("\u3000", " ").replace("\t", " ")
    # 改行もスペースに置換
    text = text.replace("\r", " ").replace("\n", " ")
    # 複数スペースを1つにする
    text = re.sub(r" +", " ", text)
    return text.strip()

@app.get("/")
async def read_root():
  return HTMLResponse("<h1>Hello from FastAPI on Fargate!</h1>")
