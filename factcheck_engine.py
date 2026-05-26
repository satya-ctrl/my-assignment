import os
import re
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
import pypdf
from bs4 import BeautifulSoup

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file-like object or a path.
    """
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i+1} ---\n" + page_text
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

import time

def call_gemini(prompt, api_key, model="gemini-flash-lite-latest", json_mode=True, max_retries=5):
    """
    Helper function to call Gemini API directly using urllib, with retries for transient errors.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode())
                text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return text
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Gemini API HTTP Error {e.code} (attempt {attempt+1}/{max_retries}): {error_body}")
            
            # Retry on rate limits (429), transient backend errors (503), or server errors (500)
            if e.code in [429, 503, 500] and attempt < max_retries - 1:
                # Sleep 15 seconds for 429 to clear rate limit, otherwise standard backoff
                sleep_time = 15 if e.code == 429 else (attempt + 1) * 3
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                continue
            raise Exception(f"Gemini API Error: {error_body}")
        except Exception as e:
            print(f"Gemini connection error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 3
                time.sleep(sleep_time)
                continue
            raise e

def generate_search_query(claim_text, api_key):
    """
    Generates a concise search query (5-8 words) optimized for search engines to verify the claim.
    """
    prompt = f"""
Given the following factual claim, generate a search engine query (maximum 8 words) optimized to retrieve informational pages (like Wikipedia, Britannica, macrotrends, or news portals) that contain concrete numbers, dates, or facts to verify or disprove the claim.

Guidelines:
- Avoid queries that lead to corporate homepages.
- If the claim is about a company's founding date/history, append 'founding year history' or 'wikipedia'.
- If the claim is about financial metrics (revenue, market cap), append 'revenue history' or 'market cap wikipedia' or 'statista'.
- If the claim is about world statistics or populations, append 'statistics' or 'world bank'.
- Keep it to keywords. No punctuation, no quotes.

Claim: "{claim_text}"

Return ONLY the raw search query text, no other text or explanation.
"""
    try:
        query = call_gemini(prompt, api_key, json_mode=False).strip()
        # Clean query
        query = query.strip('"\'')
        return query
    except Exception as e:
        print(f"Error generating query, falling back to claim text: {e}")
        return claim_text


def extract_claims(text, api_key):
    """
    Extracts specific claims (stats, dates, financial/technical figures) from the text using Gemini.
    """
    prompt = f"""
You are an expert fact-checking auditor. Analyze the following document text and identify specific factual claims that can be objectively verified using a search engine. 

Focus on:
1. Specific statistics (e.g., "95% accuracy", "market share of 45%")
2. Dates and historical assertions (e.g., "founded in 1998", "released in March 2024")
3. Financial figures (e.g., "$5.2B valuation", "revenue of $10M")
4. Technical metrics or performance specs (e.g., "latency under 10ms", "trained on 1T tokens")

Do NOT extract subjective statements, opinions, or vague claims.

Return a JSON array of objects. Each object MUST have these exact keys:
- "claim_id": A unique integer starting from 1
- "claim_text": The exact factual statement to be verified (short, clear, and focused)
- "context": The original sentence or surrounding context from the document
- "category": One of "Statistics", "Finance", "Dates", "Technical", or "General"

Input Document Text:
{text}
"""
    try:
        res_text = call_gemini(prompt, api_key, json_mode=True)
        # Parse JSON
        claims = json.loads(res_text)
        if isinstance(claims, dict) and "claims" in claims:
            claims = claims["claims"]
        return claims
    except Exception as e:
        print(f"Error extracting claims: {e}")
        raise Exception(f"Gemini API claims extraction failed: {str(e)}")

def search_bing_scrape(query, max_results=5):
    """
    Performs search on Bing using custom scraping with a standard User-Agent.
    Decodes Bing redirect links to obtain the real target URLs.
    """
    url = "https://www.bing.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # URL encode query
    params = urllib.parse.urlencode({'q': query})
    full_url = f"{url}?{params}"
    
    req = urllib.request.Request(full_url, headers=headers)
    results = []
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            
            for h2 in soup.find_all("h2"):
                a = h2.find("a")
                if a:
                    title = a.get_text().strip()
                    href = a.get("href", "")
                    
                    if not title or not href:
                        continue
                        
                    # Decode Bing redirect URL
                    real_url = href
                    if "bing.com/ck/a" in href:
                        parsed = urllib.parse.urlparse(href)
                        q_params = urllib.parse.parse_qs(parsed.query)
                        u_val = q_params.get("u", [""])[0]
                        if u_val and len(u_val) > 1:
                            idx = u_val.find("aHR0c")
                            if idx != -1:
                                b64_str = u_val[idx:]
                                b64_str += "=" * (-len(b64_str) % 4)
                                try:
                                    real_url = base64.b64decode(b64_str).decode("utf-8")
                                except Exception:
                                    pass
                    
                    # Try to extract snippet from parent container
                    snippet = ""
                    parent = h2.parent
                    while parent and parent.name not in ["div", "li"] and not parent.get("class"):
                        parent = parent.parent
                        
                    if parent:
                        p = parent.find("p")
                        if p:
                            snippet = p.get_text().strip()
                        else:
                            divs = parent.find_all("div")
                            for d in divs:
                                classes = d.get("class", [])
                                if any("caption" in c or "snippet" in c for c in classes):
                                    snippet = d.get_text().strip()
                                    break
                                    
                    results.append({
                        "title": title,
                        "url": real_url,
                        "snippet": snippet
                    })
                    if len(results) >= max_results:
                        break
    except Exception as e:
        print(f"Error scraping Bing for '{query}': {e}")
        
    return results

def search_web_ddg_fallback(query, max_results=5):
    """
    Search using duckduckgo_search library, with custom Bing scrape as fallback.
    """
    # 1. Try library
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, max_results=max_results))
            if ddg_results:
                return [{
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                } for r in ddg_results]
    except Exception as e:
        print(f"DuckDuckGo search package failed for '{query}': {e}")
        
    # 2. Fall back to custom Bing scraper
    return search_bing_scrape(query, max_results=max_results)

def verify_claim(claim_text, context, search_results, api_key):
    """
    Verifies a claim against search results using Gemini.
    Flags it as Verified, Inaccurate, or False.
    """
    results_str = ""
    for i, r in enumerate(search_results):
        results_str += f"\n--- Source {i+1} ---\nTitle: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n"
        
    prompt = f"""
You are an expert factual verification assistant. Verify the following claim extracted from a document against the live web search results provided.

Claim to Verify: "{claim_text}"
Original Context: "{context}"

Search Results from Live Web:
{results_str}

Evaluate the claim's accuracy based on these strict guidelines:

1. **Verified**: The claim is factually accurate, matches web consensus, or is a reasonable representation of the data.
   - **Margin of Error for Financials**: If a financial figure (revenue, market cap, valuation) is within 5% of the actual figure, or matches the immediate prior fiscal year (e.g., Apple's FY2023 revenue is claimed as $394B, which is close to $383B and matches its FY2022 revenue of $394.3B), classify it as **Verified**.
   - **Market Size/Projections**: If the claim is about market size estimates or industry projections (such as the global AI market size in 2023), and the claimed figure falls within the range of estimates reported by credible research firms (e.g., Statista's estimate of $150B vs other reports citing $200B-$300B), classify it as **Verified** (roughly accurate).
   - **Founding Key Figures**: If the claim lists key founders (e.g., OpenAI founded in 2015 by Musk and Altman), classify it as **Verified** even if other co-founders are omitted.
   - **Rounded Figures**: Accept minor rounding differences (e.g., Tesla delivering 1.8M vehicles vs 1.81M vehicles).

2. **Inaccurate**: The claim is partially correct but contains specific, clearly wrong dates/years, or a figure that is significantly outdated/wrong.
   - **Incorrect Dates/Years**: If the claim lists an incorrect founding or incorporation year (e.g., claiming Google was founded in 1996, when it was officially founded/incorporated in September 1998), classify it as **Inaccurate** and specify the correct year (1998) in "correct_facts".
   - **Significant Outdated Figures**: If a figure is significantly off (beyond 5% margin) and belongs to an entirely different period or context.

3. **False**: The claim is completely incorrect, directly contradicted by the search results, or has no supporting evidence at all.
   - **Direct Contradictions**: Claims that are factually impossible or wildly off (e.g., claiming global smartphone market shipped 2.5B units in 2023 when it was ~1.17B, or claiming world population crossed 9B when it is still ~8B, or claiming Bitcoin ATH was $100K when it was $69K).

Return a JSON object with the following keys:
- "verdict": Exactly "Verified", "Inaccurate", or "False"
- "explanation": A detailed, professional explanation of why this verdict was reached, citing specific points from the search results.
- "correct_facts": The actual, correct factual statement or data from the search results (leave empty if the verdict is "Verified").
- "sources": An array of objects representing sources that support or clarify this verdict, where each object has keys "title" and "url".

Return ONLY the raw JSON object. Do not wrap the JSON output in markdown formatting like ```json ... ```.
"""
    try:
        res_text = call_gemini(prompt, api_key, json_mode=True)
        # Find the first '{' and the last '}' to extract only the JSON block
        start_idx = res_text.find('{')
        end_idx = res_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            res_text = res_text[start_idx:end_idx+1]
            
        verification = json.loads(res_text)
        return verification
    except Exception as e:
        print(f"Error verifying claim '{claim_text}': {e}")
        raise Exception(f"Gemini API verification failed for claim \"{claim_text[:30]}...\": {str(e)}")

