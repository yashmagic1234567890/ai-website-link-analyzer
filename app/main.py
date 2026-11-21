
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from app.services.website_extractor import extract_website_content
from app.services.ai_analyzer import analyze_website


app = FastAPI(
    title="AI Website Link Analyzer",
    description="AI-powered website link analysis API",
    version="1.0.0"
)


# Allow requests from local development and Lovable preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://id-preview--fa93cbe7-40a0-44ba-905d-e69f9507e163.lovable.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LinkAnalysisRequest(BaseModel):
    url: HttpUrl


@app.get("/")
def home():
    return {
        "message": "AI Website Link Analyzer API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/link-analysis")
async def link_analysis(request: LinkAnalysisRequest):
    try:
        # Extract website content
        website_data = await extract_website_content(
            str(request.url)
        )

        # Analyze website using Gemini
        analysis_result = analyze_website(website_data)

        # Return structured analysis
        return {
            "success": True,
            "url": website_data["url"],
            "analysis": analysis_result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print("ACTUAL ANALYSIS ERROR:", repr(error))
        raise HTTPException(
            status_code=502,
            detail="Website analysis failed. Please check the server logs."
        )

