import streamlit as st

def get_styles():
    return """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stat-card {
        background: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
        margin-bottom: 10px;
    }
    .vs-card {
        background: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .comp-strip {
        display: flex;
        gap: 10px;
        overflow-x: auto;
        padding: 10px 0;
    }
    .miss-card {
        background: #1c1c1c;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    </style>
    """

def get_sidebar_toggle_js():
    return "<script>console.log('Sidebar toggle JS loaded');</script>"

def stat_card(icon, label, val, color):
    return f"""
    <div class="stat-card" style="border-top: 3px solid {color}">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div style="font-size: 0.8rem; color: #8b949e;">{label}</div>
        <div style="font-size: 1.2rem; font-weight: bold; color: {color};">{val}</div>
    </div>
    """

def vs_card(our_name, our_price, comp_name, comp_price, diff, comp_src, pid_str, image_url=""):
    color = "#00C853" if diff <= 0 else "#FF1744"
    img_html = ""
    if image_url and image_url not in ("", "None", "nan"):
        img_html = f'<img src="{image_url}" style="width:52px;height:52px;object-fit:cover;border-radius:8px;border:1px solid #30363d;margin-left:10px;flex-shrink:0;" onerror="this.style.display=\'none\'">'
    return f"""
    <div class="vs-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1; display: flex; align-items: center; gap: 10px;">
                {img_html}
                <div>
                    <div style="font-size: 0.9rem; color: #8b949e;">منتجنا ({pid_str})</div>
                    <div style="font-size: 1.1rem; font-weight: bold;">{our_name}</div>
                    <div style="font-size: 1.3rem; color: #58a6ff;">{our_price} ر.س</div>
                </div>
            </div>
            <div style="padding: 0 20px; font-size: 1.5rem; color: #8b949e;">VS</div>
            <div style="flex: 1; text-align: right;">
                <div style="font-size: 0.9rem; color: #8b949e;">{comp_src}</div>
                <div style="font-size: 1.1rem; font-weight: bold;">{comp_name}</div>
                <div style="font-size: 1.3rem; color: {color};">{comp_price} ر.س</div>
            </div>
        </div>
        <div style="margin-top: 10px; text-align: center; font-weight: bold; color: {color};">
            الفرق: {diff} ر.س
        </div>
    </div>
    """

def comp_strip(all_comps):
    html = '<div class="comp-strip">'
    for comp in all_comps:
        html += f'<div style="background: #21262d; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">{comp}</div>'
    html += '</div>'
    return html

def miss_card(name, price, brand, size, ptype, comp, suggested_price, note, variant_html, tester_badge, border_color, confidence_level, confidence_score, product_id):
    return f"""
    <div class="miss-card" style="border-left-color: {border_color}">
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div style="font-weight: bold; font-size: 1.1rem;">{tester_badge} {name} ({product_id})</div>
                <div style="color: #8b949e; font-size: 0.85rem;">{brand} | {size} | {ptype}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.2rem; font-weight: bold;">{price} ر.س</div>
                <div style="color: #00C853; font-size: 0.9rem;">المقترح: {suggested_price} ر.س</div>
            </div>
        </div>
        <div style="margin-top: 8px; font-size: 0.85rem; color: #8b949e;">
            المنافس: {comp} | الثقة: {confidence_level} ({confidence_score}%)
        </div>
        {variant_html}
        {f'<div style="margin-top: 5px; color: #ffd600; font-style: italic;">{note}</div>' if note else ''}
    </div>
    """
