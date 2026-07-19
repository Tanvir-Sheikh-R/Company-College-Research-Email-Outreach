import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from agents.search_agent import SearchAgent
from agents.extract_agent import ExtractAgent
from agents.verify_agent import VerifyAgent
from agents.llm_agent import LLMAgent
from agents.email_sender import EmailSender

load_dotenv()

st.set_page_config(page_title="Company Research & Outreach", page_icon="🔍", layout="wide")

st.title("🔍 Company & College Research + Email Outreach")
st.markdown("Search, extract contacts, verify emails, and send proposals — all from one dashboard.")

tab1, tab2, tab3 = st.tabs(["🔎 Research", "🤖 AI Outreach Drafts", "📧 Send Emails"])

with st.sidebar:
    st.header("🔑 API Key")
    env_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key = st.text_input("OpenRouter API Key", type="password",
                            value=env_key if env_key and env_key != "sk-or-v1-your-key-here" else "",
                            help="Set via .env file or paste here. Get free at openrouter.ai/keys")
    if not api_key:
        api_key = env_key if env_key and env_key != "sk-or-v1-your-key-here" else ""

    if api_key:
        llm = LLMAgent(api_key)
        st.success("LLM connected!")
    else:
        llm = None
        st.info("Add OpenRouter key to enable AI features")
        st.page_link("https://openrouter.ai/keys", label="Get free key →")

    st.divider()
    st.header("📋 Search Criteria")
    search_type = st.radio("Search for:", ["Companies", "Colleges/Universities"])
    country = st.text_input("Country", placeholder="e.g. Germany")
    city = st.text_input("City", placeholder="e.g. Berlin")
    category = st.text_input("Category", placeholder="e.g. AI, Software, Engineering, Medical")
    company_size = st.text_input("Size (optional)", placeholder="e.g. 50-200 employees, Startup")
    max_results = st.slider("Max sites to scan", 5, 100, 25)

    run_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)

if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame()
if "verified_count" not in st.session_state:
    st.session_state.verified_count = 0
if "all_data" not in st.session_state:
    st.session_state.all_data = []
if "searched_keywords" not in st.session_state:
    st.session_state.searched_keywords = []

# ===================== TAB 1: RESEARCH =====================
with tab1:
    if run_btn:
        if not country and not city and not category:
            st.error("Please fill in at least Country, City, or Category.")
            st.stop()

        search_agent = SearchAgent()
        extract_agent = ExtractAgent()
        verify_agent = VerifyAgent()

        status_box = st.empty()
        progress_bar = st.progress(0)

        if llm:
            status_box.info("🧠 AI expanding keywords for smarter search...")
            expanded_keywords = llm.expand_search_keywords(category, search_type)
            st.session_state.searched_keywords = [category] + expanded_keywords
            status_box.info(f"🔎 Searching with {len(expanded_keywords) + 1} related keywords...")
        else:
            expanded_keywords = None
            st.session_state.searched_keywords = [category]

        queries = search_agent.build_queries(country, city, category, company_size, search_type, expanded_keywords)

        discovered_urls = []
        for i, query in enumerate(queries):
            results = search_agent.search_companies(query, max_results=max(3, max_results // len(queries)))
            for r in results:
                url = r["url"]
                if url and url not in [du["url"] for du in discovered_urls]:
                    url_lower = url.lower()
                    if any(ext in url_lower for ext in [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip"]):
                        continue
                    discovered_urls.append(r)
            progress_bar.progress((i + 1) / len(queries))

        status_box.info(f"✅ Found {len(discovered_urls)} sites. Extracting contact info from ALL...")

        all_results = []
        for i, entry in enumerate(discovered_urls):
            status_box.info(f"📄 ({i+1}/{len(discovered_urls)}) {entry['title'][:50]}...")
            info = extract_agent.extract_company_info(entry["url"], country, city)

            name = info["name"] or entry["title"]
            description = info.get("description", "")

            if info["emails"] and llm:
                llm_info = llm.extract_company_details(info.get("page_text", ""), entry["url"])
                if llm_info.get("name") and llm_info["name"] != "unknown":
                    name = llm_info["name"]
                if llm_info.get("description") and not description:
                    description = llm_info["description"]

            all_results.append({
                "name": name,
                "url": info["url"],
                "emails": info["emails"],
                "phone": info["phone"],
                "phone_with_code": info["phone_with_code"],
                "socials": "; ".join(info["socials"]) if info["socials"] else "",
                "description": description[:200] if description else "",
                "snippet": entry.get("snippet", ""),
                "has_contact_page": info.get("has_contact_page", False),
            })
            progress_bar.progress((i + 1) / len(discovered_urls))

        status_box.info(f"📧 Verifying {sum(len(r['emails']) for r in all_results)} emails...")
        all_emails = list(set(e for res in all_results for e in res["emails"]))
        verification_results = verify_agent.verify_batch(all_emails)

        final_rows = []
        verified_count = 0
        for res in all_results:
            email_statuses = {}
            for e in res["emails"]:
                is_valid, reason = verification_results.get(e, (False, "not_checked"))
                email_statuses[e] = "Verified" if is_valid else "Invalid"

            verified_emails = [e for e, s in email_statuses.items() if s == "Verified"]
            invalid_emails = [e for e, s in email_statuses.items() if s == "Invalid"]

            if verified_emails:
                verified_count += 1

            final_rows.append({
                "Name": res["name"],
                "Website": res["url"],
                "Verified Emails": ", ".join(verified_emails) if verified_emails else "",
                "Invalid Emails": ", ".join(invalid_emails) if invalid_emails else "",
                "Email Status": "Verified" if verified_emails else ("Invalid" if invalid_emails else "No Email Found"),
                "Phone": res["phone"],
                "Phone (Country Code)": res["phone_with_code"],
                "Description": res.get("description", "")[:150],
                "Has Contact Page": "Yes" if res.get("has_contact_page") else "No",
            })

        df = pd.DataFrame(final_rows)
        st.session_state.results = df
        st.session_state.verified_count = verified_count
        st.session_state.all_data = final_rows

        status_box.success(
            f"✅ Done! {len(discovered_urls)} sites scanned, "
            f"{sum(1 for r in all_results if r['emails'])} with emails, "
            f"{verified_count} with verified emails."
        )
        progress_bar.empty()

    if not st.session_state.results.empty:
        df = st.session_state.results

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sites Scanned", len(df))
        col2.metric("With Verified Emails", st.session_state.verified_count)
        col3.metric("Keywords Used", len(st.session_state.get("searched_keywords", [category])))

        if st.session_state.get("searched_keywords"):
            with st.expander("🔑 Keywords searched"):
                st.write(", ".join(st.session_state.searched_keywords))

        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full CSV",
            data=csv,
            file_name=f"company_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        verified_only = df[df["Email Status"] == "Verified"]
        if not verified_only.empty:
            verified_csv = verified_only.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Verified Only CSV",
                data=verified_csv,
                file_name=f"verified_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

    elif run_btn:
        st.warning("No results found. Try broader search terms.")
    else:
        st.info("Enter criteria in the sidebar and click 'Start Research'.")

# ===================== TAB 2: AI OUTREACH DRAFTS =====================
with tab2:
    if not llm:
        st.warning("Enter your OpenRouter API key in the sidebar (or set in .env) to use AI drafting.")
    elif st.session_state.results.empty:
        st.info("Run a research first — results will appear here for drafting.")
    else:
        st.subheader("✍️ AI-Powered Outreach Drafts")

        df = st.session_state.results

        col1, col2 = st.columns(2)
        with col1:
            sender_name = st.text_input("Your Name", placeholder="John Doe",
                                        key="draft_sender_name")
            sender_company = st.text_input("Your Agency Name", placeholder="Naimur Consulting",
                                           key="draft_sender_company")
        with col2:
            sender_email = st.text_input("Your Email", placeholder="john@agency.com",
                                         key="draft_sender_email")

        custom_message = st.text_area("Custom Instructions (optional)",
                                      placeholder="e.g. Mention that we specialize in student visas for Germany")

        verified_df = df[df["Email Status"] == "Verified"]
        selected_indices = st.multiselect(
            "Select targets to generate emails for (verified only)",
            options=verified_df.index.tolist(),
            format_func=lambda i: f"{verified_df.iloc[i]['Name']} — {verified_df.iloc[i]['Verified Emails']}"
        )

        if st.button("🤖 Generate Email Drafts", use_container_width=True):
            if not sender_name or not sender_company:
                st.error("Please fill in your name and agency name.")
            elif not selected_indices:
                st.error("Select at least one target.")
            else:
                drafts = []
                gen_progress = st.progress(0)
                for idx, i in enumerate(selected_indices):
                    row = verified_df.iloc[i]
                    company_name = row["Name"]
                    first_email = row["Verified Emails"].split(", ")[0] if row["Verified Emails"] else ""
                    company_desc = row.get("Description", "")
                    draft = llm.generate_outreach_email(
                        company_name=company_name,
                        email=first_email,
                        category=category,
                        country=country,
                        city=city,
                        sender_name=sender_name,
                        sender_company=sender_company,
                        custom_message=custom_message,
                        company_description=company_desc,
                    )
                    drafts.append({"company": company_name, "email": first_email, "draft": draft})
                    gen_progress.progress((idx + 1) / len(selected_indices))

                st.session_state.drafts = drafts
                gen_progress.empty()
                st.success(f"Generated {len(drafts)} personalized email drafts!")

        if "drafts" in st.session_state and st.session_state.drafts:
            st.divider()
            for d in st.session_state.drafts:
                with st.expander(f"📧 {d['company']} → {d['email']}"):
                    st.text_area("Draft", d["draft"], height=250, key=f"draft_{d['email']}")

            all_drafts_text = "\n\n---\n\n".join(
                f"TO: {d['email']}\nCOMPANY: {d['company']}\n\n{d['draft']}"
                for d in st.session_state.drafts
            )
            st.download_button(
                "📥 Download All Drafts",
                data=all_drafts_text.encode("utf-8"),
                file_name=f"outreach_drafts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )

# ===================== TAB 3: SEND EMAILS =====================
with tab3:
    st.subheader("📧 Send Emails")

    with st.expander("⚙️ SMTP Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
        with col2:
            sender_email_smtp = st.text_input("Your Email (SMTP)", placeholder="you@gmail.com")
            sender_password = st.text_input("App Password", type="password",
                                            help="Use an App Password, not your regular password")

    if "drafts" in st.session_state and st.session_state.drafts:
        st.subheader("Select emails to send")
        send_selection = []
        for d in st.session_state.drafts:
            checked = st.checkbox(f"{d['company']} → {d['email']}", value=False, key=f"send_{d['email']}")
            if checked:
                send_selection.append(d)

        subject_input = st.text_input("Email Subject", value="Partnership Opportunity")

        if st.button("📤 Send Selected Emails", type="primary", use_container_width=True):
            if not sender_email_smtp or not sender_password:
                st.error("Enter SMTP credentials above.")
            elif not send_selection:
                st.error("Select at least one email to send.")
            else:
                sender = EmailSender(smtp_server, smtp_port, sender_email_smtp, sender_password)
                results = []
                send_progress = st.progress(0)
                status_text = st.empty()

                for idx, item in enumerate(send_selection):
                    status_text.info(f"Sending to {item['company']} ({item['email']})...")
                    success, msg = sender.send_email(item["email"], subject_input, item["draft"])
                    results.append({
                        "company": item["company"],
                        "email": item["email"],
                        "success": success,
                        "status": msg,
                    })
                    send_progress.progress((idx + 1) / len(send_selection))

                send_progress.empty()
                status_text.empty()

                st.subheader("📬 Delivery Results")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

                success_count = sum(1 for r in results if r["success"])
                st.success(f"Sent {success_count}/{len(results)} emails successfully!")
    else:
        st.info("Generate email drafts in the 'AI Outreach Drafts' tab first.")

st.divider()
st.caption("Powered by DuckDuckGo, DeepSeek V4 via OpenRouter, SMTP verification — 100% free tier")
