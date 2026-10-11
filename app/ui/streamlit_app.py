import json, streamlit as st, httpx
st.set_page_config(page_title="Universal Product Crawler",layout="wide")
st.title("Universal AI Product Crawler")
st.caption("Cloudflare retrieves the page remotely; Gemini extracts structured fields; validation stays local.")
url=st.text_input("Public product-page URL")
mode=st.radio("Extraction",["Gemini structured extraction", "Metadata-only (lower coverage)"],horizontal=True)
fetch_mode=st.radio("Page retrieval",["Cloudflare remote browser (recommended)", "Direct local fetch (reveals your IP)"],horizontal=True)
if st.button("Extract Product",type="primary") and url:
    with st.spinner("Checking policy, fetching evidence, and validating output..."):
        try:
            r=httpx.post("http://127.0.0.1:8000/api/extract",json={"url":url,"use_llm":mode.startswith("Gemini"),"debug":True,"fetch_mode":"cloudflare" if fetch_mode.startswith("Cloudflare") else "local"},timeout=120)
            if r.is_error:
                try: raise RuntimeError(r.json().get("detail", r.text))
                except ValueError: raise RuntimeError(r.text)
            data=r.json()
            p=data["product"]; st.subheader(p["name"] or "Unnamed product"); st.write(f"**Brand:** {p['brand'] or '—'}  |  **Price:** {p['price'] or '—'} {p['currency'] or ''}  |  **Availability:** {p['availability'] or '—'}")
            if p["images"]: st.image(p["images"][:6],width=180)
            st.write(f"Rating: {p['rating'] or '—'} · Reviews: {p['review_count'] or '—'}"); st.write(p["description"] or "No supported description.")
            with st.expander("Specifications"): st.json(p["specs"])
            with st.expander("Confidence, evidence, and warnings"): st.json(data["report"])
            st.json(p); st.download_button("Download JSON",json.dumps(p,indent=2),"product.json","application/json")
        except Exception as e: st.error(str(e))
