import json
import os
import threading

import pandas as pd
import streamlit as st

from utils.sitemap_resolve import resolve_store_to_sitemap_url

_SCRAPER_PROGRESS = os.path.join("data", "scraper_progress.json")

COMPETITORS_FILE = "data/competitors_list.json"
# مرجع متجرنا (للعرض — لا يُكشط كمنافس من هذه القائمة)
PRIMARY_STORE_SITEMAP = "https://mahwous.com/sitemap.xml"
PRIMARY_STORE_LABEL = "مهووس — متجرنا"


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


def render_competitor_scrape_page():  # noqa: C901
    """صفحة كاملة: إدارة روابط المنافسين + كشط مع حفظ وعرض تدريجي."""
    st.header("🏢 كشط المنافسين")
    st.caption(
        f"**{PRIMARY_STORE_LABEL}** = مرجع ملف منتجاتك (رفع من «📂 رفع الملفات») — "
        f"Sitemap المرجعي: `{PRIMARY_STORE_SITEMAP}`. أدناه **روابط كشط المنافسين فقط**."
    )
    st.success(
        "المنافسون المقترحون: **عالم جيفنشي** · **خبير العطور** · **سارا ميك أب** — "
        "يُكشطون إلى `competitors_latest.csv` لاستخدامها في المقارنة و**بطاقات VS** في الأقسام."
    )

    render_competitor_management_ui()

    st.markdown("---")
    st.subheader("🤖 تشغيل محرك الكشط وعرض النتائج")
    st.info(
        "يُجلب أحدث أسعار المنافسين من روابط الـ Sitemap أعلاه. **الكشط يعمل في الخلفية**؛ "
        "سترى تقدّم الطلبات وعدد الصفوف المحفوظة أثناء العمل، ثم الملخص عند الانتهاء."
    )

    prog_running = False
    prog: dict = {}
    if os.path.exists(_SCRAPER_PROGRESS):
        try:
            with open(_SCRAPER_PROGRESS, "r", encoding="utf-8") as _pf:
                prog = json.load(_pf)
            prog_running = bool(prog.get("running"))
        except Exception:
            pass

    if prog_running:
        try:
            from streamlit_autorefresh import st_autorefresh

            st_autorefresh(interval=4000, key="competitor_scrape_autorefresh")
        except ImportError:
            pass
        st.warning("⏳ جاري سحب البيانات… يُحدَّث العرض كل بضع ثوانٍ حتى يكتمل.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "تقدّم الطلبات",
                f"{prog.get('urls_processed', 0):,} / {max(prog.get('urls_total', 0), 1):,}",
            )
        with c2:
            st.metric("صفوف محفوظة في CSV", f"{prog.get('rows_in_csv', 0):,}")
        with c3:
            st.caption(f"Sitemap: `{prog.get('current_sitemap', '—')}`")

    def _run_scraper_bg() -> None:
        import asyncio

        from utils.async_scraper import run_scraper_engine

        asyncio.run(run_scraper_engine())

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        start_disabled = prog_running
        if st.button(
            "🚀 بدء جلب بيانات المنافسين الآن",
            use_container_width=True,
            disabled=start_disabled,
            key="btn_start_scrape_page",
        ):
            threading.Thread(target=_run_scraper_bg, daemon=True).start()
            st.rerun()

    meta_path = os.path.join(os.getcwd(), "data", "scraper_last_run.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as _mf:
                sm = json.load(_mf)
            st.markdown("### 📈 ملخص أداء آخر كشط")
            st.caption(
                f"آخر تحديث (UTC): `{sm.get('finished_at', '—')}` · الحالة: **{sm.get('status', '—')}**"
            )
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("روابط في الطابور", f"{sm.get('urls_queued', 0):,}")
            with c2:
                st.metric("صفوف في CSV", f"{sm.get('rows_written_csv', 0):,}")
            with c3:
                st.metric("نسبة النجاح", f"{sm.get('success_rate_pct', 0.0):.1f}%")
            with c4:
                st.metric("المدة (ث)", f"{sm.get('duration_seconds', 0):.1f}")
            c5, c6, c7 = st.columns(3)
            with c5:
                st.metric("قبل إزالة التكرار", f"{sm.get('rows_extracted_before_dedupe', 0):,}")
            with c6:
                st.metric("طلبات فاشلة (استثناء)", f"{sm.get('fetch_exceptions', 0):,}")
            with c7:
                st.metric("بدون استخراج (فراغ)", f"{sm.get('parse_null', 0):,}")
            diag = sm.get("sitemap_diagnostics") or []
            if diag:
                with st.expander("🔎 تشخيص روابط الـ Sitemap (حالة HTTP وأخطاء الجلب)", expanded=False):
                    st.dataframe(pd.DataFrame(diag), use_container_width=True, hide_index=True)
                    st.caption(
                        "إذا ظهرت حالة **410 Gone** أو **404** فالرابط لم يعد متاحاً على الخادم — "
                        "استبدله برابط sitemap حديث من المتجر (أو من لوحة تحكم سلة/زد)."
                    )
        except Exception:
            pass

    st.markdown("### 📊 البيانات المسحوبة من المنافسين")
    data_path = os.path.join(os.getcwd(), "data", "competitors_latest.csv")
    if os.path.exists(data_path):
        try:
            df_comp = pd.read_csv(data_path)
            if df_comp.empty:
                st.warning(
                    "⚠️ الملف موجود لكنه فارغ. تحقق من الـ Sitemap أو انتظر أول دفعة بعد بدء الكشط."
                )
            else:
                st.success(
                    f"✅ **{len(df_comp)}** صف محفوظ — يُحدَّث أثناء الكشط إن كان يعملاً."
                )
                st.dataframe(df_comp, use_container_width=True, height=400)
                st.download_button(
                    "📥 تنزيل CSV",
                    data=df_comp.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                    file_name="competitors_latest.csv",
                    mime="text/csv",
                    key="dl_competitors_csv_page",
                )
        except Exception as e:
            st.error(f"❌ حدث خطأ في قراءة ملف البيانات: {str(e)}")
    else:
        st.info(
            "لا يوجد ملف بعد. اضغط **بدء جلب** أعلاه — سيُنشأ `competitors_latest.csv` ويُملأ تدريجياً."
        )
