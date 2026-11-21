
import pytest

from app.services.website_extractor import extract_website_content


@pytest.mark.asyncio
async def test_extract_example_website():
    result = await extract_website_content("https://example.com")

    assert isinstance(result, dict)
    assert result["url"].startswith("https://example.com")
    assert result["title"] != ""
    assert isinstance(result["description"], str)
    assert isinstance(result["content"], str)
    assert "Example Domain" in result["content"]


@pytest.mark.asyncio
async def test_reject_non_html_website():
    with pytest.raises(
        ValueError,
        match="The URL does not return an HTML webpage"
    ):
        await extract_website_content(
            "https://www.rfc-editor.org/rfc/rfc9110.txt"
        )


@pytest.mark.asyncio
async def test_reject_localhost_website():
    with pytest.raises(
        ValueError,
        match="Localhost URLs are not allowed"
    ):
        await extract_website_content("http://localhost")
