import streamlit as st
import os
import json
import pandas as pd
from factcheck_engine import extract_text_from_pdf, extract_claims, search_web_ddg_fallback, verify_claim, generate_search_query

# Page Configuration
st.set_page_config(
    page_title="TruthLayer AI - Document Fact-Checker",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injected Custom CSS for premium light-mode SaaS/Luxury design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Main font styling */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Base Light Mode Colors & Styling */
.stApp {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Hide Streamlit Sidebar completely */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Clean Header styling */
header[data-testid="stHeader"] {
    background-color: #ffffff !important;
    border-bottom: 1px solid #f1f5f9 !important;
}

header[data-testid="stHeader"] * {
    color: #0f172a !important;
}

/* Navigation bar mockup */
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 32px;
}

.nav-links {
    display: flex;
    gap: 32px;
}

.nav-link {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #475569 !important;
    text-decoration: none !important;
}

.nav-link:hover {
    color: #0f172a !important;
}

/* Modern Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    letter-spacing: -0.5px !important;
}

/* Header style overrides */
.main-title {
    font-size: 48px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #1ba0fc 0%, #a855f7 40%, #e53f7b 70%, #fd7443 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-top: 16px !important;
    margin-bottom: 8px !important;
    letter-spacing: -1.5px !important;
    text-align: center !important;
}

.subtitle {
    font-size: 14px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    margin-bottom: 32px !important;
    line-height: 1.6 !important;
    text-align: center !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
}

/* Full-screen Loading Overlay matching Sidewave loader */
.loader-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: #09090b !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    color: #ffffff !important;
}

.loader-spinner {
    width: 70px;
    height: 70px;
    border: 2px solid rgba(255, 255, 255, 0.05);
    border-radius: 50%;
    border-top-color: #a855f7;
    border-bottom-color: #1ba0fc;
    animation: rotate 1.5s cubic-bezier(0.53, 0.21, 0.29, 0.87) infinite;
    margin-bottom: 24px;
}

.loader-text {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-bottom: 12px;
    animation: pulse 2s infinite;
    background: linear-gradient(135deg, #1ba0fc 0%, #a855f7 40%, #e53f7b 70%, #fd7443 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.loader-subtext {
    font-size: 11px;
    color: #a1a1aa;
    letter-spacing: 1px;
    font-family: 'Space Grotesk', sans-serif;
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

/* Custom cards / lines for claim results (Sidewave Stats Inspired) */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid #cbd5e1;
    border-bottom: 1px solid #cbd5e1;
    margin: 40px 0;
    padding: 32px 0;
    background-color: #ffffff;
    animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.stats-item {
    text-align: center;
    border-right: 1px solid #e2e8f0;
}

.stats-item:last-child {
    border-right: none;
}

.stats-number {
    font-size: 64px !important;
    font-weight: 800 !important;
    font-family: 'Outfit', sans-serif !important;
    line-height: 1 !important;
    letter-spacing: -2px !important;
    margin-bottom: 8px !important;
}

.stats-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #64748b !important;
}

/* Custom badges */
.custom-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 0px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-right: 12px;
}

.badge-verified {
    background-color: #ecfdf5;
    color: #047857;
    border: 1px solid #d1fae5;
}

.badge-inaccurate {
    background-color: #fffbeb;
    color: #b45309;
    border: 1px solid #fef3c7;
}

.badge-false {
    background-color: #fff1f2;
    color: #be123c;
    border: 1px solid #ffe4e6;
}

/* Truth Score Bar */
.truth-score-container {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    padding: 32px;
    margin-top: 24px;
    animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
    animation-delay: 0.1s;
}

.truth-score-bg {
    background-color: #f1f5f9;
    height: 8px;
    width: 100%;
    margin-top: 12px;
    overflow: hidden;
}

.truth-score-fill {
    height: 100%;
    background: linear-gradient(90deg, #1ba0fc, #a855f7);
    transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

/* File Uploader styling */
[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 1px solid #0f172a !important;
    border-radius: 0px !important;
    padding: 32px !important;
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

[data-testid="stFileUploader"] > section {
    background-color: #ffffff !important;
    border: 1px dashed #cbd5e1 !important;
    border-radius: 0px !important;
    padding: 40px 24px !important;
}

[data-testid="stFileUploader"] * {
    color: #0f172a !important;
    background-color: transparent !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: #ffffff !important;
    border: none !important;
}

[data-testid="stFileUploader"] button[data-testid="baseButton-secondary"] {
    background-color: #0f172a !important;
    border: 1px solid #0f172a !important;
    color: #ffffff !important;
    border-radius: 0px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 11px !important;
    padding: 8px 24px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"] button[data-testid="baseButton-secondary"]:hover {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Premium Primary/Secondary Buttons (Cartier Style) */
.stButton>button, .stDownloadButton>button {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border-radius: 0px !important;
    padding: 12px 32px !important;
    border: 1px solid #0f172a !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: none !important;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #0f172a !important;
}

/* Custom HTML Alerts */
.custom-alert {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0px;
    padding: 20px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.custom-alert-success {
    border-left: 4px solid #10b981;
    background-color: #f0fdf4;
}

.custom-alert-warning {
    border-left: 4px solid #f59e0b;
    background-color: #fffbeb;
}

.custom-alert-info {
    border-left: 4px solid #3b82f6;
    background-color: #eff6ff;
}

.custom-alert-error {
    border-left: 4px solid #ef4444;
    background-color: #fef2f2;
}

.custom-alert-text {
    font-size: 13px;
    color: #1e293b;
    font-weight: 500;
}

/* Settings Expander styling */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: none !important;
    border-bottom: 1px solid #e2e8f0 !important;
    border-radius: 0px !important;
    box-shadow: none !important;
    margin-bottom: 24px !important;
}

div[data-testid="stExpander"] > details > summary {
    padding: 16px 0 !important;
    background-color: #ffffff !important;
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    border: none !important;
    outline: none !important;
}

div[data-testid="stExpander"] > details > summary:hover {
    color: #0f172a !important;
}

div[data-testid="stExpander"] > details > summary ~ div {
    padding: 24px 0 !important;
    border-top: none !important;
    background-color: #ffffff !important;
}

/* Settings input custom layouts */
div[data-testid="stTextInput"] input {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 0px !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #0f172a !important;
}

/* Style Sliders */
div[data-testid="stSlider"] [data-testid="stSliderTrack"] {
    background-color: #e2e8f0 !important;
}

div[data-testid="stSlider"] [data-testid="stSliderTrack"] > div {
    background-color: #0f172a !important;
}

div[data-testid="stSlider"] [role="slider"] {
    background-color: #ffffff !important;
    border: 2px solid #0f172a !important;
    box-shadow: none !important;
}

/* Hide standard Streamlit alerts */
[data-testid="stNotification"] {
    display: none !important;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
""", unsafe_allow_html=True)

# Navigation Bar Mockup
st.markdown("""
<div class="nav-bar">
    <div class="nav-links">
        <a class="nav-link" href="#audit">Audit Document</a>
        <a class="nav-link" href="#engine">Verification Engine</a>
    </div>
    <div class="nav-links">
        <span class="nav-link" style="color: #94a3b8 !important; cursor: default;">Developed by Satya</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Title & Subtitle
st.markdown("<div class='main-title'>TruthLayer AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>A digital layer transforming document verification through human-centered accuracy and live web predictions</div>", unsafe_allow_html=True)

# Try to load API key from environment variable or .env file
env_key = os.environ.get("GEMINI_API_KEY")
if not env_key and os.path.exists(".env"):
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "GEMINI_API_KEY":
                        env_key = v.strip().strip("'\"")
                        break
    except Exception:
        pass

# Force update session state if the loaded key has changed
if "api_key_loaded" not in st.session_state or st.session_state.get("env_key_hash") != env_key:
    st.session_state["api_key_loaded"] = env_key if env_key else ""
    st.session_state["env_key_hash"] = env_key

# Collapsible Settings Expander at the top
with st.expander("Settings & Configuration", expanded=False):
    col_api, col_search, col_density = st.columns([2, 1, 1])
    
    with col_api:
        if env_key:
            api_key = env_key
            st.markdown("<div style='font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;'>Gemini API Key</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 11px; color: #047857; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #d1fae5; background-color: #ecfdf5; padding: 8px 16px; display: inline-block;'>Secure Connection Active</div>", unsafe_allow_html=True)
        else:
            api_key = st.text_input(
                "Gemini API Key", 
                value="", 
                type="password",
                help="Provide your own Gemini API Key from Google AI Studio to run the audit."
            )
            st.markdown("<div style='font-size: 11px; color: #64748b; font-weight: 500; letter-spacing: 0.5px;'>No system key detected. Please input your key.</div>", unsafe_allow_html=True)
            
    with col_search:
        max_search_results = st.slider("Web Search Sources", min_value=1, max_value=10, value=4)
        
    with col_density:
        claim_density = st.select_slider("Extraction Density", options=["Low", "Medium", "High"], value="Medium")

# Main File Uploader
uploaded_file = st.file_uploader("Drop your PDF document here", type=["pdf"])

# Session State Initialization
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "processing" not in st.session_state:
    st.session_state.processing = False

if uploaded_file is not None:
    st.markdown(f"""
    <div class='custom-alert custom-alert-info'>
        <div class='custom-alert-text'>Loaded file: <b>{uploaded_file.name}</b> ({len(uploaded_file.getvalue()) / 1024:.1f} KB)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Audit Trigger Button
    if not st.session_state.processing:
        run_audit = st.button("Start Auditing Document", type="primary")
    else:
        st.button("Auditing...", disabled=True)
        run_audit = False

    if run_audit:
        if not api_key:
            st.markdown("""
            <div class='custom-alert custom-alert-error'>
                <div class='custom-alert-text'>Please configure a valid Gemini API Key in the settings panel to proceed.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state.processing = True
            
            # Full-screen loader placeholder
            loader_placeholder = st.empty()
            
            def update_loader(status_msg):
                loader_placeholder.markdown(f"""
                <div class="loader-overlay">
                    <div class="loader-spinner"></div>
                    <div class="loader-text">VERIFYING TRUTH LAYER</div>
                    <div class="loader-subtext">{status_msg}</div>
                </div>
                """, unsafe_allow_html=True)
                
            try:
                # Step 1: Text extraction
                update_loader("1/4: Extracting text from PDF...")
                pdf_text = extract_text_from_pdf(uploaded_file)
                
                if not pdf_text:
                    loader_placeholder.empty()
                    st.markdown("""
                    <div class='custom-alert custom-alert-error'>
                        <div class='custom-alert-text'>Failed to extract text from the PDF file.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.processing = False
                else:
                    # Step 2: Claim extraction
                    update_loader("2/4: Extracting specific factual claims...")
                    claims = extract_claims(pdf_text, api_key)
                    
                    if not claims:
                        loader_placeholder.empty()
                        st.markdown("""
                        <div class='custom-alert custom-alert-warning'>
                            <div class='custom-alert-text'>No verifiable claims found in the document.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.audit_results = []
                        st.session_state.processing = False
                    else:
                        # Step 3: Verify each claim
                        verified_claims = []
                        total_claims = len(claims)
                        
                        for idx, claim in enumerate(claims):
                            claim_text = claim["claim_text"]
                            context = claim["context"]
                            category = claim["category"]
                            
                            update_loader(f"3/4: Verifying claim {idx+1}/{total_claims}: \"{claim_text[:40]}...\"")
                            
                            # Generate optimized search query
                            search_query = generate_search_query(claim_text, api_key)
                            
                            # Live search
                            search_results = search_web_ddg_fallback(search_query, max_results=max_search_results)
                            
                            # Gemini verification
                            verification = verify_claim(claim_text, context, search_results, api_key)
                            
                            verified_claims.append({
                                "claim_id": claim["claim_id"],
                                "claim_text": claim_text,
                                "context": context,
                                "category": category,
                                "verdict": verification.get("verdict", "False"),
                                "explanation": verification.get("explanation", ""),
                                "correct_facts": verification.get("correct_facts", ""),
                                "sources": verification.get("sources", [])
                            })
                            
                        # Step 4: Finalize
                        update_loader("4/4: Finalizing audit report...")
                        
                        st.session_state.audit_results = verified_claims
                        st.session_state.processing = False
                
                # Clear progress loader and refresh page to show dashboard
                loader_placeholder.empty()
                st.rerun()
            except Exception as e:
                loader_placeholder.empty()
                st.session_state.processing = False
                st.markdown("""
                <div class='custom-alert custom-alert-error'>
                    <div class='custom-alert-text'><b>Automated Audit Failed</b></div>
                </div>
                """, unsafe_allow_html=True)
                err_msg = str(e)
                if "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower() or "429" in err_msg:
                    st.markdown("""
                    <div class='custom-alert custom-alert-warning'>
                        <div class='custom-alert-text'>
                            <b>Gemini API Rate Limit or Quota Exceeded (429)</b>: The active API key has reached its requests-per-minute rate limit (20 RPM) or daily request limit.<br/><br/>
                            <b>How to fix:</b><br/>
                            - Wait 10-15 seconds and try clicking <b>Start Auditing Document</b> again.<br/>
                            - Make sure your key is active in Google AI Studio.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif "API_KEY_INVALID" in err_msg or "invalid" in err_msg.lower():
                    st.markdown("""
                    <div class='custom-alert custom-alert-warning'>
                        <div class='custom-alert-text'><b>Invalid API Key</b>: The configured Gemini API Key is invalid. Please verify the key in your settings panel.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='custom-alert custom-alert-error'>
                        <div class='custom-alert-text'>Error Details: {err_msg}</div>
                    </div>
                    """, unsafe_allow_html=True)

# Display Results if Audit is complete
if st.session_state.audit_results is not None:
    results = st.session_state.audit_results
    total_claims = len(results)
    
    if total_claims == 0:
        st.markdown("""
        <div class='custom-alert custom-alert-info'>
            <div class='custom-alert-text'>No verifiable claims found in the document. Try uploading a different document with stats, financial figures, or dates.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Calculate counts
        verified_count = sum(1 for c in results if c["verdict"] == "Verified")
        inaccurate_count = sum(1 for c in results if c["verdict"] == "Inaccurate")
        false_count = sum(1 for c in results if c["verdict"] == "False")
        
        truth_score = int((verified_count / total_claims) * 100) if total_claims > 0 else 0
        
        # Display Dashboard Header
        st.markdown("<h2 style='font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 48px; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 1px;'>Document Audit Dashboard</h2>", unsafe_allow_html=True)
        
        # Metric Cards Layout (Sidewave Stats Grid style)
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stats-item">
                <div class="stats-number color-total">{total_claims}</div>
                <div class="stats-label">Claims Audited</div>
            </div>
            <div class="stats-item">
                <div class="stats-number color-verified">{verified_count}</div>
                <div class="stats-label">Verified Claims</div>
            </div>
            <div class="stats-item">
                <div class="stats-number color-inaccurate">{inaccurate_count}</div>
                <div class="stats-label">Inaccurate Stats</div>
            </div>
            <div class="stats-item">
                <div class="stats-number color-false">{false_count}</div>
                <div class="stats-label">False Assertions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Truth Score Section
        st.markdown(f"""
        <div class="truth-score-container">
            <div style="display: flex; justify-content: space-between; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; font-size: 13px;">
                <span>Document Truth Score</span>
                <span class="color-verified">{truth_score}%</span>
            </div>
            <div class="truth-score-bg">
                <div class="truth-score-fill" style="width: {truth_score}%;"></div>
            </div>
            <p style="font-size: 13px; color: #64748b; margin-top: 12px; margin-bottom: 0; font-weight: 500;">
                The Truth Score represents the percentage of verified statements relative to all audited factual assertions in the PDF.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive filters
        st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 24px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px;'>Audited Claims</h3>", unsafe_allow_html=True)
        
        filter_col_verdict, filter_col_cat = st.columns(2)
        
        with filter_col_verdict:
            verdict_filter = st.multiselect(
                "Filter by Verdict",
                options=["Verified", "Inaccurate", "False"],
                default=["Verified", "Inaccurate", "False"]
            )
            
        with filter_col_cat:
            all_cats = list(set(c["category"] for c in results))
            cat_filter = st.multiselect(
                "Filter by Category",
                options=all_cats,
                default=all_cats
            )
            
        # Render Filtered List
        filtered_results = [
            c for c in results 
            if c["verdict"] in verdict_filter and c["category"] in cat_filter
        ]
        
        if not filtered_results:
            st.markdown("""
            <div class='custom-alert custom-alert-warning'>
                <div class='custom-alert-text'>No claims match your selected filters.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for c in filtered_results:
                # Custom expander headers based on verdict
                verdict = c["verdict"]
                claim_text = c["claim_text"]
                category = c["category"]
                
                badge_class = "badge-verified" if verdict == "Verified" else "badge-inaccurate" if verdict == "Inaccurate" else "badge-false"
                
                header_html = f"<span class='custom-badge {badge_class}'>{verdict}</span> <b>[{category}]</b> {claim_text}"
                
                with st.expander(f"{verdict} | [{category}] {claim_text}", expanded=(verdict != "Verified")):
                    st.markdown(f"**Original Statement in Document:**")
                    st.markdown(f"> *\"{c['context']}\"*")
                    st.markdown("---")
                    
                    if verdict != "Verified" and c["correct_facts"]:
                        st.markdown("### Corrected Facts")
                        st.markdown(f"""
                        <div class='custom-alert custom-alert-success' style='margin-bottom: 12px;'>
                            <div class='custom-alert-text'>{c['correct_facts']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("---")
                        
                    st.markdown("### Audit Verdict Explanation")
                    st.write(c["explanation"])
                    st.markdown("---")
                    
                    # Sources
                    st.markdown("### Citations and Web Sources")
                    if not c["sources"]:
                        st.write("No direct source links referenced.")
                    else:
                        for s in c["sources"]:
                            st.markdown(f"- [{s['title']}]({s['url']})")
                            
        # Export options
        st.write("---")
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 40px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px;'>Export Audit Report</h3>", unsafe_allow_html=True)
        
        # Format results as pandas DataFrame
        df_export = pd.DataFrame([{
            "Claim ID": c["claim_id"],
            "Category": c["category"],
            "Claimed Statement": c["claim_text"],
            "Verdict": c["verdict"],
            "Corrected Facts": c["correct_facts"],
            "Explanation": c["explanation"],
            "Sources": ", ".join(s["url"] for s in c["sources"])
        } for c in results])
        
        export_csv = df_export.to_csv(index=False).encode('utf-8')
        export_json = json.dumps(results, indent=2)
        
        btn_col_csv, btn_col_json, _ = st.columns([1, 1, 4])
        with btn_col_csv:
            st.download_button(
                label="Download CSV Report",
                data=export_csv,
                file_name="truthlayer_audit_report.csv",
                mime="text/csv"
            )
        with btn_col_json:
            st.download_button(
                label="Download JSON Report",
                data=export_json,
                file_name="truthlayer_audit_report.json",
                mime="application/json"
            )
            
        # Add Reset button
        st.write("")
        if st.button("Clear Audit and Start Over"):
            st.session_state.audit_results = None
            st.rerun()
