import os
from factcheck_engine import extract_text_from_pdf, extract_claims, search_web_ddg_fallback, verify_claim

def main():
    print("=" * 60)
    print("          TRUTHLAYER AI: PIPELINE VERIFICATION")
    print("=" * 60)
    
    # 1. Test PDF Text Extraction
    pdf_path = "Assessment_Product Management Trainee.pdf"
    print(f"\n[1] Extracting text from: {pdf_path}...")
    if not os.path.exists(pdf_path):
        print(f"[FAIL] PDF file not found at {pdf_path}")
        return
        
    text = extract_text_from_pdf(pdf_path)
    print(f"[OK] Extracted text length: {len(text)} characters")
    print(f"     Preview:\n{text[:300].strip()}\n...")
    
    # 2. Test Claim Extraction
    print("\n[2] Extracting factual claims using Gemini...")
    
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
        
    claims = extract_claims(text, api_key)
    
    print(f"[OK] Identified {len(claims)} verifiable claims:")
    for c in claims[:3]:
        print(f"     - ID {c['claim_id']}: [{c['category']}] \"{c['claim_text']}\"")
        print(f"       Context: \"{c['context']}\"")
        
    if not claims:
        print("[FAIL] No claims extracted. Stopping pipeline test.")
        return
        
    # 3. Test Search & Verification on the first claim
    test_claim = claims[0]
    claim_text = test_claim["claim_text"]
    context = test_claim["context"]
    
    print(f"\n[3] Running live web search for claim: \"{claim_text}\"...")
    search_results = search_web_ddg_fallback(claim_text, max_results=3)
    print(f"[OK] Retrieved {len(search_results)} search results:")
    for i, r in enumerate(search_results):
        print(f"     Source {i+1}: {r['title']}")
        print(f"              URL: {r['url']}")
        print(f"              Snippet: {r['snippet'][:100]}...")
        
    # 4. Test Verification
    print(f"\n[4] Running fact verification via Gemini...")
    verification = verify_claim(claim_text, context, search_results, api_key)
    print(f"[OK] Verification complete!")
    print(f"     Verdict: {verification.get('verdict')}")
    print(f"     Explanation: {verification.get('explanation')}")
    print(f"     Correct Facts: {verification.get('correct_facts')}")
    print(f"     Citations count: {len(verification.get('sources', []))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
