
import json

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL


client = genai.Client(api_key=GEMINI_API_KEY)

FALLBACK_MODEL = "gemini-3.1-flash-lite"

REQUIRED_SECTIONS = [
    "brand_and_competitor_analysis",
    "top_five_target_search_queries",
    "seo_recommendations",
    "top_five_services",
    "target_audience"
]


def analyze_website(website_data: dict) -> dict:
    """
    Analyze website content using Gemini.

    Uses a fallback model if the primary model fails.
    Normalizes JSON keys and validates required sections.
    """

    prompt = f"""
You are an expert website, brand, competitor, SEO and marketing analyst.

Analyze the supplied website information carefully.

WEBSITE INFORMATION

URL: {website_data.get("url", "")}
Title: {website_data.get("title", "")}
Meta description: {website_data.get("description", "")}

Website content:
{website_data.get("content", "")}


IMPORTANT ANALYSIS RULES:

1. Use the supplied website content as the primary source of facts.

2. Never invent company information, products, services, statistics,
   customer numbers, revenue or business achievements.

3. COMPETITOR ANALYSIS:
   - Identify up to three plausible competitors using your general
     knowledge when the brand and industry are recognizable.
   - Return competitors only when you have reasonable confidence
     that they operate in the same or a closely related market.
   - Clearly label every such competitor as
     "AI-identified, not verified from supplied website content."
   - Do not claim that the website itself names these competitors.
   - Include a short explanation of why each competitor is relevant.
   - If reliable identification is not possible, return an empty list.
   - Do not invent competitor strengths, weaknesses, market share
     or performance statistics.

4. Clearly distinguish verified facts from assumptions and inferences.

5. Never present inferred services as confirmed services.

6. Do not invent search volumes, keyword rankings or traffic figures.

7. Do not invent company headquarters, market share, revenue,
   geographic presence or customer demographics.

8. If the website is a placeholder, empty page or non-commercial
   website:
   - Explain that fact clearly.
   - Return an empty competitor list.
   - Return an empty services list if no actual services exist.
   - Do not invent commercial opportunities.

9. Do not use the word "None" as a service name.
   Use an empty list when no actual or reasonable inferred services
   exist.

10. Provide exactly five relevant search queries whenever the
    available information supports five useful queries.
    Do not invent business facts to fill the list.

11. Return exactly five main sections using the JSON keys below.

12. Return valid JSON only. Do not use Markdown code fences.


REQUIRED JSON STRUCTURE:

{{
  "brand_and_competitor_analysis": {{
    "brand_name": "",
    "brand_overview_and_category": "",
    "products_and_services": "",
    "competitors": [
      {{
        "competitor_name": "",
        "reason_for_competition": "",
        "evidence_type": "AI-identified, not verified"
      }}
    ],
    "competitor_strengths_weaknesses_and_market_gaps": "",
    "brand_advantages_and_opportunities": ""
  }},

  "top_five_target_search_queries": [
    {{
      "query": "",
      "platform": "",
      "search_intent": "",
      "business_relevance": "",
      "target_audience": ""
    }}
  ],

  "seo_recommendations": {{
    "primary_keywords": [],
    "secondary_keywords": [],
    "long_tail_keywords": [],
    "business_keywords": [],
    "suggested_seo_title": "",
    "suggested_meta_description": "",
    "content_ideas": []
  }},

  "top_five_services": [
    {{
      "service_name": "",
      "description": "",
      "target_industry_or_customer": "",
      "benefits": "",
      "evidence_type": "Explicit or Inferred"
    }}
  ],

  "target_audience": {{
    "primary_and_secondary_audiences": "",
    "industries_and_business_types": "",
    "customer_profiles": "",
    "geography": "",
    "customer_needs_and_challenges": "",
    "interests_and_marketing_segments": ""
  }}
}}


SECTION REQUIREMENTS:

1. Brand and competitor analysis:
   Identify the brand, category, products and services.

   Identify up to three plausible competitors when possible.
   Clearly distinguish AI-identified competitors from information
   verified on the supplied website.

   Do not claim that competitor strengths, weaknesses or market
   gaps are verified unless the supplied information supports them.
   Label market observations based on general knowledge as
   assumptions or AI-generated assessments.

2. Search queries:
   Provide up to five relevant queries.
   Use Google, Facebook, Instagram, LinkedIn or X as platforms.
   Include intent, relevance and target audience.
   Do not claim actual search volume or ranking data.

3. SEO recommendations:
   Suggest relevant primary, secondary, long-tail and business
   keywords, an SEO title, meta description and content ideas.
   Base suggestions on the actual website and its business category.

4. Services:
   Provide up to five actual or clearly labelled inferred services.
   Use "Explicit" only when supported by website content.
   Use "Inferred" for reasonable business inferences.
   Return an empty list if no services can reasonably be identified.

5. Target audience:
   Identify primary and secondary audiences, industries,
   customer profiles, geography, needs and interests.
   Clearly label assumptions when the website does not provide
   enough evidence.


FINAL QUALITY CHECK:

Before returning JSON:
- Check that all five required top-level keys exist.
- Check that competitors are clearly labelled as AI-identified
  and unverified when they come from general knowledge.
- Check that no unsupported business facts are presented as certain.
- Check that non-commercial websites do not receive invented
  commercial services.
- Check that all JSON values use the required data types.
- Return valid JSON only.
"""


    models_to_try = list(dict.fromkeys([
        GEMINI_MODEL,
        FALLBACK_MODEL
    ]))

    last_error = None

    for model_name in models_to_try:

        try:
            print("Trying Gemini model:", model_name)

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            result = json.loads(response.text)

            if not isinstance(result, dict):
                raise ValueError(
                    "Gemini response must be a JSON object."
                )

            # Normalize JSON keys
            normalized_result = {}

            for key, value in result.items():

                normalized_key = (
                    key.strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )

                normalized_result[normalized_key] = value

            result = normalized_result

            # Validate required sections
            missing_sections = [
                section
                for section in REQUIRED_SECTIONS
                if section not in result
            ]

            if missing_sections:
                raise ValueError(
                    f"Missing required analysis sections: "
                    f"{missing_sections}"
                )

            # Validate section data types
            if not isinstance(
                result["brand_and_competitor_analysis"], dict
            ):
                raise ValueError(
                    "Invalid brand_and_competitor_analysis format."
                )

            if not isinstance(
                result["top_five_target_search_queries"], list
            ):
                raise ValueError(
                    "Invalid target search queries format."
                )

            if not isinstance(
                result["seo_recommendations"], dict
            ):
                raise ValueError(
                    "Invalid SEO recommendations format."
                )

            if not isinstance(
                result["top_five_services"], list
            ):
                raise ValueError(
                    "Invalid top five services format."
                )

            if not isinstance(
                result["target_audience"], dict
            ):
                raise ValueError(
                    "Invalid target audience format."
                )

            # Validate competitor list
            competitors = result[
                "brand_and_competitor_analysis"
            ].get("competitors")

            if not isinstance(competitors, list):
                raise ValueError(
                    "Competitors must be returned as a list."
                )

            # Validate service list
            services = result["top_five_services"]

            if any(
                not isinstance(service, dict)
                for service in services
            ):
                raise ValueError(
                    "Each service must be a JSON object."
                )

            print(
                "Gemini analysis successful using:",
                model_name
            )

            return result

        except Exception as error:

            last_error = error

            print(
                "Gemini model failed:",
                model_name,
                repr(error)
            )

    raise RuntimeError(
        "All Gemini models failed or returned invalid analysis. "
        "Please try again later."
    ) from last_error
