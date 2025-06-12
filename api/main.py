import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from src.recommendation import recommend, build_market_basket_rules, build_similarity_matrix
from src.data_preprocessing import load_data, items_data

df=None
rules = None
similarity_df = None
tedf = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, rules, similarity_df, tedf
    # Startup logic
    df = load_data('data/raw/train.csv')
    items_df = items_data(df)
    rules = build_market_basket_rules(items_df)
    similarity_df, tedf = build_similarity_matrix(items_df)
    yield
    
app = FastAPI(title="Retail Recommendation API", lifespan=lifespan)

class RecommendationRequest(BaseModel):
    customer_name: str
    cart: list[str] | None = None
    category: str | None = None

@app.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    recommendations = recommend(
        name=request.customer_name,
        rules=rules,
        similarity_df=similarity_df,
        tedf=tedf,
        cart=request.cart,
        category=request.category,
        df=df
    )
    return {"recommendations": recommendations}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)