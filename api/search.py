from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="AI向け 検証済み検索API",
    description="構造化検索API のサンプル実装",
    version="0.1.0"
)

# Pydanticモデル定義
class Source(BaseModel):
    name: str
    url : str

class SearchResult(BaseModel):
    id: str
    title: str
    summary: str
    source: Source
    published_at: str
    confidence_score: float
    fact_checked: bool

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    max_results: Optional[int] = 5

class Contributor(BaseModel):
    name: str
    verified: bool

class DocumentResponse(BaseModel):
    id: str
    title: str
    full_text: str
    source: Source
    published_at: str
    confidence_score: float
    fact_checked: bool
    contributors: List[Contributor]
    tags: List[str]

documents = {
    "kg-20240530-001": DocumentResponse(
        id="kg-20240530-001",
        title="2024年 金価格の見通し：インフレとドル安が要因",
        full_text=(
            "2024年の金価格はインフレ圧力とドル安を背景に上昇傾向にある。"
            "米連邦準備制度の政策変更、地政学的リスク、中央銀行の買い増しが主な要因とされる。"
        ),
        source=Source(
            name="Bloomberg",
            url="https://www.bloomberg.co.jp/news/articles/2024-gold-forecast"
        ),
        published_at="2024-05-01",
        confidence_score=0.92,
        fact_checked=True,
        contributors=[
            Contributor(name="Bloomberg Economics Team", verified=True)
        ],
        tags=["金価格", "インフレ", "ドル安", "2024年"]
    ),
}


# search エンドポイント
@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    matched_results: List[SearchResult] = []
    count = 0

    keywords = request.query.split()

    for doc_id, doc in documents.items():
        if count >= request.max_results:
            break

        if any(keyword in doc.title for keyword in keywords):
            summary_text = doc.full_text[:100]
            matched_results.append(SearchResult(
                id=doc.id,
                title=doc.title,
                summary=summary_text,
                source=doc.source,
                published_at=doc.published_at,
                confidence_score=doc.confidence_score,
                fact_checked=doc.fact_checked
            ))
            count += 1
    
    return SearchResponse(
        query=request.query,
        results=matched_results
    )

# document/{id}エンドポイント
@app.get("/document/{id}", response_model=DocumentResponse)
def get_document(id: str):
    doc = documents.get(id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc