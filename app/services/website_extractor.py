
import httpx
from bs4 import BeautifulSoup

from app.utils.url_validator import validate_url


async def extract_website_content(url: str) -> dict:
    """
    Fetch a website and extract its title, description and readable text.
    """

    # Validate the URL before making a request
    safe_url = validate_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebsiteAnalyzer/1.0)"
    }

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=False
    ) as client:

        response = await client.get(
            safe_url,
            headers=headers
        )

        response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type.lower():
            raise ValueError("The URL does not return an HTML webpage.")

        if len(response.content) > 2_000_000:
            raise ValueError("Website content is too large to analyze.")

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary HTML elements
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript"
        ]):
            element.decompose()

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else ""
        )

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        description = (
            description_tag.get("content", "")
            if description_tag
            else ""
        )

        text = soup.get_text(separator=" ", strip=True)

        # Limit extracted text
        text = " ".join(text.split())[:15000]

        return {
            "url": str(response.url),
            "title": title,
            "description": description,
            "content": text
        }
