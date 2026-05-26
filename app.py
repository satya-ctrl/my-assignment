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
    initial_sidebar_state="expanded"
)

# Injected Custom CSS for premium light-mode SaaS design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Main font styling */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Base Light Mode Colors & Styling */
.stApp {
    background-color: #f8fafc !important;
    color: #334155 !important;
}

/* Header styling override to fix dark black bar at top */
header[data-testid="stHeader"] {
    background-color: #f8fafc !important;
    border-bottom: 1px solid #e2e8f0 !important;
}

header[data-testid="stHeader"] * {
    color: #475569 !important;
}

/* Sidebar styling override */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.02) !important;
}

/* Aggressive Sidebar text color overrides for visibility */
[data-testid="stSidebar"] * {
    color: #475569 !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4, 
[data-testid="stSidebar"] h5, 
[data-testid="stSidebar"] h6 {
    color: #0f172a !important;
}

/* Title colors in sidebar */
.sidebar-title {
    font-size: 24px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #1ba0fc 0%, #a855f7 40%, #e53f7b 70%, #fd7443 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center !important;
    margin-bottom: 2px !important;
    letter-spacing: -0.5px !important;
}

.sidebar-subtitle {
    color: #64748b !important;
}

/* Alert text overrides in sidebar */
[data-testid="stSidebar"] .custom-alert-success * {
    color: #047857 !important;
}
[data-testid="stSidebar"] .custom-alert-warning * {
    color: #b45309 !important;
}
[data-testid="stSidebar"] .custom-alert-error * {
    color: #be123c !important;
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
    font-size: 42px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #1ba0fc 0%, #a855f7 40%, #e53f7b 70%, #fd7443 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 8px !important;
    letter-spacing: -1.5px !important;
}

.subtitle {
    font-size: 16px !important;
    color: #64748b !important;
    font-weight: 400 !important;
    margin-bottom: 24px !important;
    line-height: 1.6 !important;
}


/* Custom fade-in & slide-up entrance animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Stagger animations for list items */
.animated-item {
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Custom cards for claim results */
.metric-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 24px -4px rgba(0, 0, 0, 0.06), 0 8px 12px -3px rgba(0, 0, 0, 0.03);
    border-color: #cbd5e1;
}

/* Stagger metric cards animations */
.metric-card-1 { animation-delay: 0.05s; }
.metric-card-2 { animation-delay: 0.1s; }
.metric-card-3 { animation-delay: 0.15s; }
.metric-card-4 { animation-delay: 0.2s; }

.metric-value {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 6px;
    letter-spacing: -1.5px;
    font-family: 'Outfit', sans-serif !important;
}

.metric-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Color codes */
.color-verified { color: #10b981; }
.color-inaccurate { color: #f59e0b; }
.color-false { color: #ef4444; }
.color-total { color: #4f46e5; }

/* Custom badges */
.custom-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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

/* Truth Score Card */
.truth-score-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    margin-top: 24px;
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    animation-delay: 0.25s;
}

.truth-score-bg {
    background-color: #f1f5f9;
    border-radius: 100px;
    height: 10px;
    width: 100%;
    margin-top: 10px;
    overflow: hidden;
}

.truth-score-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #4f46e5, #10b981);
    transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Aggressive custom style overrides to fix the dark file uploader dropzone */
[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

/* Target the inner dropzone section directly */
[data-testid="stFileUploader"] > section {
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 32px 24px !important;
}

/* Force all text inside uploader to be dark slate */
[data-testid="stFileUploader"] * {
    color: #475569 !important;
}

/* Override dark background set on inner drag-and-drop elements */
[data-testid="stFileUploaderDropzone"] {
    background-color: #f8fafc !important;
    border: none !important;
}

/* Style the file uploader browse button */
[data-testid="stFileUploader"] button[data-testid="baseButton-secondary"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
}

/* Premium Primary Buttons */
.stButton>button {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.15) !important;
}

.stButton>button:hover {
    background-color: #4338ca !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.25) !important;
    border: none !important;
}

/* Custom Premium Alerts (Replacements for st.info / st.success) */
.custom-alert {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    display: flex;
    align-items: center;
    gap: 12px;
    animation: fadeInUp 0.4s ease;
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
    font-size: 14px;
    color: #334155;
    font-weight: 500;
    line-height: 1.5;
}

/* Sidebar Inputs and Sliders Customization */
div[data-testid="stTextInput"] input {
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1) !important;
}

/* Style Streamlit Sliders to match the theme */
div[data-testid="stSlider"] [data-testid="stSliderTrack"] {
    background-color: #e2e8f0 !important;
}

div[data-testid="stSlider"] [data-testid="stSliderTrack"] > div {
    background-color: #4f46e5 !important;
}

div[data-testid="stSlider"] [role="slider"] {
    background-color: #4f46e5 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* Style select slider text */
div[class*="stSelectSlider"] {
    color: #4f46e5 !important;
}

/* Expander Overrides for accordion feel */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.01) !important;
    margin-bottom: 12px !important;
    overflow: hidden !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stExpander"]:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.03) !important;
}

div[data-testid="stExpander"] > details > summary {
    padding: 16px 20px !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    border: none !important;
    outline: none !important;
}

div[data-testid="stExpander"] > details > summary ~ div {
    padding: 24px !important;
    border-top: 1px solid #e2e8f0 !important;
    background-color: #fafafa !important;
}

/* Hide standard Streamlit alerts default icons for clean custom notifications */
[data-testid="stNotification"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar UI
st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-title'>TruthLayer AI</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-subtitle'>Factual Document Verification Engine</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center; font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; margin-bottom: 16px;'>Developed by Satya</div>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin: 0 0 24px 0; border-color: #e2e8f0;'/>", unsafe_allow_html=True)

# API Configuration
st.sidebar.markdown("### Configuration")

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

api_key = st.sidebar.text_input(
    "Gemini API Key", 
    value=st.session_state["api_key_loaded"], 
    type="password",
    help="Pre-configured with a default key, loaded from .env, or paste your own key."
)

if env_key:
    st.sidebar.markdown("""
    <div class='custom-alert custom-alert-success' style='padding: 10px 14px; margin-top: 10px; margin-bottom: 16px; border-radius: 8px;'>
        <div class='custom-alert-text' style='font-size: 12px;'>API Key loaded from environment file.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class='custom-alert custom-alert-warning' style='padding: 10px 14px; margin-top: 10px; margin-bottom: 16px; border-radius: 8px;'>
        <div class='custom-alert-text' style='font-size: 12px;'>Using shared default API key. Daily limits apply.</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# Settings
st.sidebar.markdown("### Analysis Settings")
max_search_results = st.sidebar.slider("Web Search Sources", min_value=1, max_value=10, value=4, help="Number of search results analyzed per claim")
claim_density = st.sidebar.select_slider("Extraction Density", options=["Low", "Medium", "High"], value="Medium", help="How many claims the model extracts from the text")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### How it works
1. **Upload**: Provide any PDF document.
2. **Extract**: TruthLayer AI scans the document and extracts factual claims, figures, and dates.
3. **Verify**: The engine performs live web queries via Bing Search.
4. **Report**: Claims are evaluated and flagged with source citations.
""")

# Main Layout
col_header, col_logo = st.columns([5, 1])
with col_header:
    st.markdown("<div class='main-title'>TruthLayer AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Upload and fact-check marketing collateral, pitches, or technical articles against the live web in real time.</div>", unsafe_allow_html=True)

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
                <div class='custom-alert-text'>Please configure a valid Gemini API Key in the sidebar to proceed.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state.processing = True
            
            # Progress Container
            progress_placeholder = st.empty()
            
            try:
                with progress_placeholder.container():
                    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 12px;'>Audit Pipeline Status</h3>", unsafe_allow_html=True)
                    p_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Step 1: Text extraction
                    status_text.text("1/4: Extracting text from PDF...")
                    p_bar.progress(10)
                    pdf_text = extract_text_from_pdf(uploaded_file)
                    
                    if not pdf_text:
                        st.markdown("""
                        <div class='custom-alert custom-alert-error'>
                            <div class='custom-alert-text'>Failed to extract text from the PDF file.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.processing = False
                    else:
                        # Step 2: Claim extraction
                        status_text.text("2/4: Extracting specific factual claims...")
                        p_bar.progress(30)
                        claims = extract_claims(pdf_text, api_key)
                        
                        if not claims:
                            st.markdown("""
                            <div class='custom-alert custom-alert-warning'>
                                <div class='custom-alert-text'>No verifiable claims found in the document.</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.audit_results = []
                            st.session_state.processing = False
                        else:
                            st.markdown(f"""
                            <div class='custom-alert custom-alert-info'>
                                <div class='custom-alert-text'>Identified <b>{len(claims)}</b> verifiable claims in the document.</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Step 3: Verify each claim
                            verified_claims = []
                            total_claims = len(claims)
                            
                            for idx, claim in enumerate(claims):
                                claim_text = claim["claim_text"]
                                context = claim["context"]
                                category = claim["category"]
                                
                                status_text.text(f"3/4: Verifying claim {idx+1}/{total_claims}: \"{claim_text[:50]}...\"")
                                # Progress from 30% to 90%
                                progress_val = int(30 + (idx / total_claims) * 60)
                                p_bar.progress(progress_val)
                                
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
                            status_text.text("4/4: Finalizing audit report...")
                            p_bar.progress(100)
                            
                            st.session_state.audit_results = verified_claims
                            st.session_state.processing = False
                
                # Clear progress box and reload UI
                progress_placeholder.empty()
                st.rerun()
            except Exception as e:
                progress_placeholder.empty()
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
                            - Wait 10-15 seconds and try clicking <b>Start Auditing Document</b> again (free keys have a 20 requests-per-minute limit).<br/>
                            - Make sure your key is active in Google AI Studio.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif "API_KEY_INVALID" in err_msg or "invalid" in err_msg.lower():
                    st.markdown("""
                    <div class='custom-alert custom-alert-warning'>
                        <div class='custom-alert-text'><b>Invalid API Key</b>: The configured Gemini API Key is invalid. Please verify the key in your .env file or sidebar.</div>
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
        st.markdown("<h2 style='font-size: 26px; font-weight: 800; color: #0f172a; margin-top: 32px; margin-bottom: 20px;'>Document Audit Dashboard</h2>", unsafe_allow_html=True)
        
        # Metric Cards Layout
        col_total, col_verified, col_inaccurate, col_false = st.columns(4)
        
        with col_total:
            st.markdown(f"""
            <div class="metric-card metric-card-1">
                <div class="metric-value color-total">{total_claims}</div>
                <div class="metric-label">Claims Audited</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_verified:
            st.markdown(f"""
            <div class="metric-card metric-card-2">
                <div class="metric-value color-verified">{verified_count}</div>
                <div class="metric-label">Verified Claims</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_inaccurate:
            st.markdown(f"""
            <div class="metric-card metric-card-3">
                <div class="metric-value color-inaccurate">{inaccurate_count}</div>
                <div class="metric-label">Inaccurate Stats</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_false:
            st.markdown(f"""
            <div class="metric-card metric-card-4">
                <div class="metric-value color-false">{false_count}</div>
                <div class="metric-label">False Assertions</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Truth Score Section
        st.markdown(f"""
        <div class="truth-score-container">
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <span>Document Truth Score</span>
                <span class="color-verified" style="font-weight: 700;">{truth_score}%</span>
            </div>
            <div class="truth-score-bg">
                <div class="truth-score-fill" style="width: {truth_score}%;"></div>
            </div>
            <p style="font-size: 13px; color: #64748b; margin-top: 8px; margin-bottom: 0; font-weight: 400;">
                The Truth Score represents the percentage of verified statements relative to all audited factual assertions in the PDF.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive filters
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 24px; margin-bottom: 12px;'>Audited Claims</h3>", unsafe_allow_html=True)
        
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
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 24px; margin-bottom: 12px;'>Export Audit Report</h3>", unsafe_allow_html=True)
        
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
