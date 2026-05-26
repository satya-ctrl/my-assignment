import os
import json
from factcheck_engine import generate_search_query, search_web_ddg_fallback, verify_claim

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Load from .env
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == "GEMINI_API_KEY":
                            api_key = v.strip().strip("'\"")
                            break
                            
    if not api_key:
        print("API Key not found.")
        return
        
    claims = [
        "The global smartphone market shipped 2.5 billion units in 2023.",
        "Apple's revenue in fiscal year 2023 was $394 billion.",
        "ChatGPT reached 1 million users in just 5 days after launch.",
        "The world population crossed 9 billion in 2023.",
        "Tesla delivered 1.8 million vehicles in 2023.",
        "OpenAI was founded in 2015 by Elon Musk and Sam Altman.",
        "India surpassed China as the world's most populous country in 2023.",
        "Google was founded in 1996 by Larry Page and Sergey Brin.",
        "Bitcoin reached an all-time high of $100,000 in November 2021.",
        "The global AI market is valued at $150 billion as of 2023."
    ]
    
    print("Starting Claim Audit Debugging...")
    
    for i, claim in enumerate(claims):
        print(f"\n=========================================")
        print(f"CLAIM {i+1}: {claim}")
        print(f"=========================================")
        
        # 1. Generate Query
        query = generate_search_query(claim, api_key)
        print(f"-> Generated Query: {query}")
        
        # 2. Search Web
        results = search_web_ddg_fallback(query, max_results=3)
        print(f"-> Search Results count: {len(results)}")
        for j, r in enumerate(results):
            print(f"   Source {j+1}: {r['title']}")
            print(f"            URL: {r['url']}")
            print(f"            Snippet: {r['snippet']}")
            
        # 3. Verify
        context = f"This is statement {i+1} in the marketing deck."
        verification = verify_claim(claim, context, results, api_key)
        print(f"-> Verdict: {verification.get('verdict')}")
        print(f"-> Correct Facts: {verification.get('correct_facts')}")
        print(f"-> Explanation: {verification.get('explanation')}")

if __name__ == "__main__":
    main()
