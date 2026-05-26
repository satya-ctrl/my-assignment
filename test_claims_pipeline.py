import os
from factcheck_engine import extract_claims, search_web_ddg_fallback, verify_claim, generate_search_query

def main():
    print("=" * 60)
    print("      TRUTHLAYER AI: END-TO-END PIPELINE VALIDATION")
    print("=" * 60)
    
    # Custom test text with explicit claims
    sample_text = """
    We are auditing the performance of major tech companies.
    
    Claim 1: Apple Inc. was founded in Cupertino, California on April 1, 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne.
    
    Claim 2: Microsoft reached a market capitalization of $10 trillion in January 2024.
    
    Claim 3: The first iPhone was released by Apple in June 2007.
    
    Claim 4: In 2025, Nvidia became the most valuable company in the world, surpassing a market capitalization of $3 trillion.
    """
    
    print("\n[1] Sample Document Text:")
    print("-" * 50)
    print(sample_text.strip())
    print("-" * 50)
    
    # 2. Extract Claims
    print("\n[2] Extracting claims using Gemini...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == "GEMINI_API_KEY":
                            api_key = v.strip().strip("'\"")
                            break
                            
    if not api_key:
        print("[FAIL] Gemini API Key not found in environment variables or .env file.")
        return
        
    claims = extract_claims(sample_text, api_key)
    
    print(f"[OK] Identified {len(claims)} verifiable claims:")
    for c in claims:
        print(f"     - ID {c['claim_id']}: [{c['category']}] \"{c['claim_text']}\"")
        print(f"       Context: \"{c['context']}\"")
        
    if not claims:
        print("[FAIL] No claims extracted.")
        return
        
    # 3. Verify all claims
    print("\n[3] Running search and verification on all claims...")
    for c in claims:
        claim_text = c["claim_text"]
        context = c["context"]
        print(f"\n---> Verifying: \"{claim_text}\"")
        
        # Generate query
        search_query = generate_search_query(claim_text, api_key)
        print(f"     Generated query: \"{search_query}\"")
        search_results = search_web_ddg_fallback(search_query, max_results=3)
        print(f"     Retrieved {len(search_results)} search results.")
        
        verification = verify_claim(claim_text, context, search_results, api_key)
        print(f"     Verdict: {verification.get('verdict')}")
        print(f"     Correct Facts: {verification.get('correct_facts')}")
        print(f"     Explanation: {verification.get('explanation')[:200]}...")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
