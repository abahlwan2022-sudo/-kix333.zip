import streamlit as st
import json
import os

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
    st.info("قم بإضافة رابط خريطة المنتجات للمنافس. مثال: [https://store.com/sitemap_products.xml](https://store.com/sitemap_products.xml)")

    competitors = load_competitors()

    with st.form("add_competitor_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_url = st.text_input("رابط Sitemap:", placeholder="https://...")
        with col2:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("➕ إضافة", use_container_width=True)

        if submitted:
            if new_url and new_url.startswith("http") and "xml" in new_url:
                if new_url not in competitors:
                    competitors.append(new_url.strip())
                    save_competitors(competitors)
                    st.success("تمت الإضافة بنجاح!")
                    st.rerun()
                else:
                    st.warning("هذا الرابط مضاف مسبقاً.")
            else:
                st.error("الرجاء إدخال رابط Sitemap صحيح يبدأ بـ http وينتهي بـ xml")

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
