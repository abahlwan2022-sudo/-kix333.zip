import streamlit as st
import pandas as pd
import math
import html

def render_product_cards(df: pd.DataFrame, items_per_page: int = 15):
    if df.empty:
        st.warning("⚠️ لا توجد بيانات لعرضها.")
        return

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    st.markdown("### 🔍 أدوات التحكم والبحث")
    col_search, col_filter = st.columns([2, 1])
    
    with col_search:
        search_query = st.text_input("ابحث عن منتج (بالاسم أو SKU):", "").strip().lower()
    
    with col_filter:
        filter_options = ["الكل"]
        if 'action_required' in df.columns:
            filter_options.extend(df['action_required'].unique().tolist())
        selected_filter = st.selectbox("تصفية حسب الحالة:", filter_options)

    filtered_df = df.copy()
    
    if search_query:
        name_match = filtered_df.get('name', pd.Series(dtype=str)).str.lower().str.contains(search_query, na=False)
        sku_match = filtered_df.get('sku', pd.Series(dtype=str)).astype(str).str.lower().str.contains(search_query, na=False)
        filtered_df = filtered_df[name_match | sku_match]
        
    if selected_filter != "الكل" and 'action_required' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['action_required'] == selected_filter]

    total_items = len(filtered_df)
    if total_items == 0:
        st.info("لم يتم العثور على منتجات تطابق بحثك.")
        return

    total_pages = math.ceil(total_items / items_per_page)
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1
        
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_df = filtered_df.iloc[start_idx:end_idx]

    card_style = """
    <style>
    .product-card { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); padding: 15px; margin-bottom: 15px; text-align: center; transition: transform 0.2s; border: 1px solid #f0f0f0; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .product-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); border-color: #d1d5db; }
    .product-img { width: 100%; height: 180px; object-fit: contain; border-radius: 8px; margin-bottom: 10px; }
    .product-title { font-size: 15px; font-weight: 700; color: #1f2937; margin-bottom: 10px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .price-block { display: flex; justify-content: space-between; align-items: center; background-color: #f3f4f6; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .price-col { text-align: center; width: 50%; }
    .price-label { font-size: 11px; color: #6b7280; font-weight: 600; text-transform: uppercase;}
    .price-value { font-size: 16px; font-weight: 800; color: #374151; }
    .suggested-value { font-size: 16px; font-weight: 800; color: #059669; }
    .comp-block { padding-top: 10px; border-top: 1px dashed #e5e7eb; font-size: 14px; }
    .comp-higher { color: #dc2626; font-weight: bold; }
    .comp-lower { color: #059669; font-weight: bold; }
    .comp-neutral { color: #6b7280; font-weight: 500; }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: left; color: #6b7280; font-size: 14px;'>نعرض {len(page_df)} من أصل {total_items} منتج</p>", unsafe_allow_html=True)
    
    cols_per_row = 3
    for i in range(0, len(page_df), cols_per_row):
        cols = st.columns(cols_per_row)
        chunk = page_df.iloc[i:i+cols_per_row]
        
        for index, (_, row) in enumerate(chunk.iterrows()):
            with cols[index]:
                safe_name = html.escape(str(row.get('name', 'منتج غير معروف')))
                img_url = row.get('image_url') if pd.notna(row.get('image_url')) else "[https://via.placeholder.com/200?text=No+Image](https://via.placeholder.com/200?text=No+Image)"
                my_price = float(row.get('price', 0))
                sug_price = float(row.get('suggested_price', 0))
                comp_price = float(row.get('comp_price', 0))
                sku = html.escape(str(row.get('sku', index)))

                if comp_price == 0:
                    comp_status = "<span class='comp-neutral'>سعر المنافس: غير متوفر ➖</span>"
                elif comp_price > my_price:
                    comp_status = f"<span class='comp-higher'>سعر المنافس: {comp_price} ر.س 🔺 (أعلى من سعرك)</span>"
                elif comp_price < my_price:
                    comp_status = f"<span class='comp-lower'>سعر المنافس: {comp_price} ر.س 🔻 (أقل من سعرك)</span>"
                else:
                    comp_status = f"<span class='comp-neutral'>سعر المنافس: {comp_price} ر.س ➖ (مطابق)</span>"

                card_html = f'''
                <div class="product-card">
                    <div>
                        <img src="{img_url}" class="product-img" onerror="this.src='[https://via.placeholder.com/200?text=No+Image](https://via.placeholder.com/200?text=No+Image)'">
                        <div class="product-title" title="{safe_name}">{safe_name}</div>
                        <div style="font-size:11px; color:#9ca3af; margin-bottom:8px;">SKU: {sku}</div>
                    </div>
                    <div>
                        <div class="price-block">
                            <div class="price-col" style="border-left: 1px solid #e5e7eb;">
                                <div class="price-label">سعري الحالي</div><div class="price-value">{my_price}</div>
                            </div>
                            <div class="price-col">
                                <div class="price-label">المقترح</div><div class="suggested-value">{sug_price}</div>
                            </div>
                        </div>
                        <div class="comp-block">{comp_status}</div>
                    </div>
                </div>
                '''
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button(f"🚀 اعتماد السعر ({sug_price})", key=f"btn_sync_{sku}_{index}", use_container_width=True):
                    st.toast(f"تم إرسال أمر تحديث المنتج {sku} بنجاح!", icon="✅")

    st.markdown("---")
    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    with page_col1:
        if st.button("⬅️ الصفحة السابقة", disabled=(st.session_state.current_page == 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with page_col2:
        st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold;'>الصفحة {st.session_state.current_page} من {total_pages}</div>", unsafe_allow_html=True)
    with page_col3:
        if st.button("الصفحة التالية ➡️", disabled=(st.session_state.current_page == total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
