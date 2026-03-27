import streamlit as st
import json
import os

from utils.sitemap_resolve import resolve_store_to_sitemap_url

COMPETITORS_FILE = 'data/competitors_list.json'


def load_competitors():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(COMPETITORS_FILE):
        with open(COMPETITORS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    try:
        with open(COMPETITORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_competitors(competitors_list):
    if not os.path.exists('data'):
        os.makedirs('data')
    with open(COMPETITORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(competitors_list, f, ensure_ascii=False, indent=4)


def render_competitor_management_ui():
    st.markdown("## 🏢 إدارة روابط المنافسين (Sitemaps)")
    st.info(
        "أدخل **رابط المتجر** (مثل `https://mahwous.com/`) أو **رابط Sitemap مباشر**. "
        "التطبيق يستنتج تلقائياً ملف الـ sitemap الصحيح من `robots.txt` أو المسارات الشائعة."
    )

    competitors = load_competitors()

    with st.form("add_competitor_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_url = st.text_input(
                "رابط المتجر أو Sitemap:",
                placeholder="https://example.com/",
            )
        with col2:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("➕ إضافة", use_container_width=True)

        if submitted:
            if not (new_url and new_url.strip()):
                st.error("الرجاء إدخال رابط.")
            else:
                resolved, msg = resolve_store_to_sitemap_url(new_url.strip())
                if not resolved:
                    st.error(msg)
                elif resolved in competitors:
                    st.warning("هذا الرابط (مُسنّداً) مضاف مسبقاً.")
                else:
                    competitors.append(resolved)
                    save_competitors(competitors)
                    st.success(f"تمت الإضافة بنجاح! {msg}")
                    st.rerun()

    st.markdown(f"### 📋 قائمة المنافسين الحاليين ({len(competitors)})")
    if not competitors:
        st.warning("لم تقم بإضافة أي منافسين بعد. ابدأ بإضافة 7 منافسين كاختبار.")
    else:
        for idx, url in enumerate(competitors):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.code(url)
            with c2:
                if st.button("🗑️ حذف", key=f"del_{idx}", use_container_width=True):
                    competitors.pop(idx)
                    save_competitors(competitors)
                    st.rerun()
