# web.py (ФИНАЛ: ЛОГОТИП УМЕНЬШЕН, РАЗДЕЛЬНЫЙ ВЫВОД ЦС)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import math

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
FILE_RESULT = os.path.join(OUTPUT_DIR, "result.parquet")
FILE_MOV = os.path.join(OUTPUT_DIR, "movements.parquet")
FILE_DEFICIT = os.path.join(OUTPUT_DIR, "deficit.parquet")
FILE_PURCHASE = os.path.join(OUTPUT_DIR, "purchase_plan.parquet")

# Логотип из папки input
LOGO_PATH = os.path.join(INPUT_DIR, "img.png")
if not os.path.exists(LOGO_PATH): LOGO_PATH = os.path.join(BASE_DIR, "src", "img.png")

if not os.path.exists(FILE_RESULT):
    st.error(f"Файл данных не найден: {FILE_RESULT}. Сначала запусти run.py")
    st.stop()

@st.cache_data(show_spinner="Загрузка данных...")
def load_data():
    df = pd.read_parquet(FILE_RESULT)
    df_mov = pd.read_parquet(FILE_MOV) if os.path.exists(FILE_MOV) else pd.DataFrame()
    df_def = pd.read_parquet(FILE_DEFICIT) if os.path.exists(FILE_DEFICIT) else pd.DataFrame()
    df_purch = pd.read_parquet(FILE_PURCHASE) if os.path.exists(FILE_PURCHASE) else pd.DataFrame()
    return df, df_mov, df_def, df_purch

df, df_mov, df_def, df_purch = load_data()

df['Код'] = df['Код'].apply(lambda x: str(x).split('.')[0].zfill(8))
df['Наименование'] = df['Наименование'].astype(str)
df['SKN'] = df['SKN'].astype(str).str.strip()
df['Артикул'] = df['Артикул'].astype(str).str.strip()
df['СТО'] = df['СТО'].astype(str)

cols_money = ['Остаток, ₽', 'Свободный остаток, ₽', 'Излишек, ₽', 'Неликвид, ₽', 'Нужно привезти, ₽']
for col in cols_money:
    if col not in df.columns: df[col] = 0.0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

if not df_mov.empty:
    df_mov['Код'] = df_mov['Код'].apply(lambda x: str(x).split('.')[0].zfill(8))
    df_mov['SKN'] = df_mov['SKN'].astype(str).str.strip()
    if 'Артикул' not in df_mov.columns: df_mov['Артикул'] = ""
    if 'Артикул на ЦС' not in df_mov.columns: df_mov['Артикул на ЦС'] = ""

if not df_purch.empty:
    df_purch['Код'] = df_purch['Код'].apply(lambda x: str(x).split('.')[0].zfill(8))

df['Тип'] = df['SKN'].apply(lambda x: 'Расходник' if str(x).upper().startswith(('Р', 'P')) else 'Запчасть')

with st.sidebar:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=200) # УМЕНЬШЕН ЛОГОТИП
    else: st.markdown("<h1 style='text-align: center; color: #FFFFFF; margin-bottom: 30px;'>ЛОГОТИП</h1>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #A0AEC0; margin-bottom: 10px;'>КАТЕГОРИЯ</div>", unsafe_allow_html=True)
    category_filter = st.radio("", ["Запасные части", "Расходные материалы"], label_visibility="collapsed")
    
    st.markdown("<hr style='border-color: #2D3748; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #A0AEC0; margin-bottom: 10px;'>МОДУЛЬ</div>", unsafe_allow_html=True)
    menu = st.radio("", [
        "📊 Аналитика запасов", 
        "🚚 Перемещения из ЦС", 
        "🔄 Перемещения между СТО", 
        "📦 Внеплановое поступление",
        "🛒 Планирование закупок", 
        "📋 Итоговая таблица"
    ], label_visibility="collapsed")

    if menu == "🔄 Перемещения между СТО":
        sub_menu = st.radio("", ["Неликвиды (6+ мес)", "Излишки", "Возврат на ЦС"], label_visibility="collapsed")
    
    st.markdown("<hr style='border-color: #2D3748; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #A0AEC0; margin-bottom: 10px;'>ФИЛЬТР СТО</div>", unsafe_allow_html=True)
    all_stos = sorted([s for s in df['СТО'].unique() if s != 'ЦС'])
    selected_stos = st.multiselect("", options=all_stos, default=all_stos, label_visibility="collapsed")

if category_filter == "Запасные части":
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
        .stApp { background: linear-gradient(135deg, #07131E 0%, #0C2335 100%); color: #E0F2FE; }
        h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -0.5px; }
        
        section[data-testid="stSidebar"] { background-color: #05101A !important; border-right: 1px solid #17465A; width: 320px !important; }
        section[data-testid="stSidebar"] * { color: #38B2AC !important; }
        div[role="radiogroup"] > label { font-size: 15px; font-weight: 500; padding: 10px 15px; border-radius: 8px; transition: all 0.2s ease; color: #A0AEC0; }
        div[role="radiogroup"] > label:hover { background-color: #143445; color: #FFFFFF !important; }
        div[data-testid="stSidebarNav"] { display: none; }
        
        div[data-testid="stMetric"] { 
            background: linear-gradient(145deg, #0D2638, #081C2A); border: 1px solid #17465A; 
            border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.7);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        div[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: #38B2AC; }
        div[data-testid="stMetric"] label { color: #38B2AC !important; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 32px !important; font-weight: 800; }
        div[data-testid="stMetricDelta"] { font-size: 14px; font-weight: 500; color: #48BB78 !important; }
        
        .stMultiSelect div[data-baseweb="select"] { background-color: #0D2638; border: 1px solid #17465A; border-radius: 8px; color: white; }
        .section-header { font-size: 18px; font-weight: 700; color: #FFFFFF; margin-top: 40px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        .section-header::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, #38B2AC 0%, transparent 100%); }
        
        .stDataFrame { background-color: #0D2638; border-radius: 12px; overflow: hidden; border: 1px solid #17465A; }
        div[data-testid="stExpander"] { 
            background-color: #081C2A; border: 1px solid #17465A; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        }
        div[data-testid="stExpander"] summary { color: #38B2AC; font-weight: 600; }
    </style>
    """
else:
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
        .stApp { background: linear-gradient(135deg, #0F051E 0%, #1A0C2E 100%); color: #E0F2FE; }
        h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -0.5px; }
        
        section[data-testid="stSidebar"] { background-color: #0A0314 !important; border-right: 1px solid #3B1E5A; width: 320px !important; }
        section[data-testid="stSidebar"] * { color: #9F7AEA !important; }
        div[role="radiogroup"] > label { font-size: 15px; font-weight: 500; padding: 10px 15px; border-radius: 8px; transition: all 0.2s ease; color: #A0AEC0; }
        div[role="radiogroup"] > label:hover { background-color: #2D1445; color: #FFFFFF !important; }
        div[data-testid="stSidebarNav"] { display: none; }
        
        div[data-testid="stMetric"] { 
            background: linear-gradient(145deg, #1A0C2E, #12061F); border: 1px solid #3B1E5A; 
            border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.7);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        div[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: #9F7AEA; }
        div[data-testid="stMetric"] label { color: #9F7AEA !important; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 32px !important; font-weight: 800; }
        div[data-testid="stMetricDelta"] { font-size: 14px; font-weight: 500; color: #48BB78 !important; }
        
        .stMultiSelect div[data-baseweb="select"] { background-color: #1A0C2E; border: 1px solid #3B1E5A; border-radius: 8px; color: white; }
        .section-header { font-size: 18px; font-weight: 700; color: #FFFFFF; margin-top: 40px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        .section-header::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, #9F7AEA 0%, transparent 100%); }
        
        .stDataFrame { background-color: #1A0C2E; border-radius: 12px; overflow: hidden; border: 1px solid #3B1E5A; }
        div[data-testid="stExpander"] { 
            background-color: #12061F; border: 1px solid #3B1E5A; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        }
        div[data-testid="stExpander"] summary { color: #9F7AEA; font-weight: 600; }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

col_title, col_empty = st.columns([8, 2])
with col_title:
    st.markdown("<h1 style='font-size: 36px; margin-bottom: 5px; color: #FFFFFF;'>Панель управления запасами</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {('#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA')}; font-size: 16px;'>Мониторинг логистики и распределения товаров по сети СТО</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

df_sto = df[(df['СТО'] != 'ЦС') & (df['СТО'].isin(selected_stos))]
df_cs = df[df['СТО'] == 'ЦС']
is_r = df_sto['SKN'].str.upper().str.startswith(('Р', 'P'))
if category_filter == "Расходные материалы":
    df_sto = df_sto[is_r]; df_cs = df_cs[df_cs['SKN'].str.upper().str.startswith(('Р', 'P'))]
else:
    df_sto = df_sto[~is_r]; df_cs = df_cs[~df_cs['SKN'].str.upper().str.startswith(('Р', 'P'))]

df_sto_clean = df_sto[~df_sto['Признак'].isin(("отм", "гсм", "расходный материал"))]
df_cs_clean = df_cs[~df_cs['Признак'].isin(("отм", "гсм", "расходный материал"))]

has_mov = not df_mov.empty and 'Тип' in df_mov.columns
mov_filtered = df_mov.copy() if has_mov else pd.DataFrame()
if not mov_filtered.empty:
    mov_filtered = mov_filtered[
        (mov_filtered['Куда'].isin(selected_stos)) | (mov_filtered['Откуда'].isin(selected_stos))
    ]
    if category_filter == "Расходные материалы":
        mov_filtered = mov_filtered[mov_filtered['SKN'].str.upper().str.startswith(('Р', 'P'))]
    else:
        mov_filtered = mov_filtered[~mov_filtered['SKN'].str.upper().str.startswith(('Р', 'P'))]

purch_filtered = df_purch.copy() if not df_purch.empty else pd.DataFrame()
if not purch_filtered.empty:
    if category_filter == "Расходные материалы":
        purch_filtered = purch_filtered[purch_filtered['SKN'].str.upper().str.startswith(('Р', 'P'))]
    else:
        purch_filtered = purch_filtered[~purch_filtered['SKN'].str.upper().str.startswith(('Р', 'P'))]

if menu == "📊 Аналитика запасов":
    st.markdown("<div class='section-header'>Финансовая сводка</div>", unsafe_allow_html=True)
    
    if category_filter == "Запасные части":
        qty_ost_sto = int(df_sto['Остаток'].sum()); rub_ost_sto = df_sto['Остаток, ₽'].sum(); sku_ost_sto = df_sto['Код'].nunique()
        qty_cs = int(df_cs['Остаток'].sum()); rub_cs = df_cs['Остаток, ₽'].sum(); sku_cs = df_cs[df_cs['Остаток'] > 0]['Код'].nunique()
        qty_nag = int(df[df['СТО'] == 'ЦС_Нагатинская']['Остаток'].sum()); rub_nag = df[df['СТО'] == 'ЦС_Нагатинская']['Остаток, ₽'].sum(); sku_nag = df[df['СТО'] == 'ЦС_Нагатинская']['Код'].nunique()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Товар на СТО", f"{qty_ost_sto:,} шт", f"{rub_ost_sto:,.2f} ₽ ({sku_ost_sto} АРТИКУЛОВ)")
        with c2: st.metric("ЦС Сокол (Свободный)", f"{qty_cs:,} шт", f"{rub_cs:,.2f} ₽ ({sku_cs} АРТИКУЛОВ)")
        with c3: st.metric("ЦС Нагатинская", f"{qty_nag:,} шт", f"{rub_nag:,.2f} ₽ ({sku_nag} АРТИКУЛОВ)")
        with c4: st.metric("Потребность СТО", f"{int(df_sto['Нужно привезти'].sum()):,} шт", f"{df_sto['Нужно привезти, ₽'].sum():,.2f} ₽")
    else:
        qty_ost_sto = int(df_sto['Остаток'].sum()); rub_ost_sto = df_sto['Остаток, ₽'].sum(); sku_ost_sto = df_sto['Код'].nunique()
        qty_cs = int(df_cs['Остаток'].sum()); rub_cs = df_cs['Остаток, ₽'].sum(); sku_cs = df_cs[df_cs['Остаток'] > 0]['Код'].nunique()
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Товар на СТО", f"{qty_ost_sto:,} шт", f"{rub_ost_sto:,.2f} ₽ ({sku_ost_sto} АРТИКУЛОВ)")
        with c2: st.metric("ЦС Расходных материалов", f"{qty_cs:,} шт", f"{rub_cs:,.2f} ₽ ({sku_cs} АРТИКУЛОВ)")
        with c3: st.metric("Потребность СТО", f"{int(df_sto['Нужно привезти'].sum()):,} шт", f"{df_sto['Нужно привезти, ₽'].sum():,.2f} ₽")

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.metric("Излишки на СТО", f"{int(df_sto['Излишек'].sum()):,} шт", f"{df_sto['Излишек, ₽'].sum():,.2f} ₽")
    with c5: st.metric("Неликвид на СТО", f"{int(df_sto['Неликвид'].sum()):,} шт", f"{df_sto['Неликвид, ₽'].sum():,.2f} ₽")

    st.markdown("<div class='section-header'>Покрытие потребности за счет ЦС (по SKU)</div>", unsafe_allow_html=True)
    def make_groupkey(row):
        skn = str(row["SKN"]).strip()
        return f"KOD_{row['Код']}" if skn in ("", "0", "nan") else f"SKN_{skn}"

    need_df = df_sto_clean[df_sto_clean['Нужно привезти'] > 0][['SKN', 'Код', 'Нужно привезти']].copy()
    need_df['GroupKey'] = need_df.apply(make_groupkey, axis=1)
    need_grouped = need_df.groupby('GroupKey')['Нужно привезти'].sum().reset_index()
    need_grouped = need_grouped[need_grouped['Нужно привезти'] > 0]

    cs_df = df_cs_clean[df_cs_clean['Остаток'] > 0][['SKN', 'Код', 'Остаток']].copy()
    cs_df['GroupKey'] = cs_df.apply(make_groupkey, axis=1)
    cs_grouped = cs_df.groupby('GroupKey')['Остаток'].sum().reset_index()

    cover_df = pd.merge(need_grouped, cs_grouped, on='GroupKey', how='left').fillna(0)
    cover_df['Покрыто_ЦС'] = cover_df[['Нужно привезти', 'Остаток']].min(axis=1)
    
    total_need_sku = len(need_grouped)
    covered_sku = len(cover_df[cover_df['Покрыто_ЦС'] > 0])
    uncovered_sku = total_need_sku - covered_sku
    pct_covered = (covered_sku / total_need_sku * 100) if total_need_sku > 0 else 0

    col_pie, col_info = st.columns([1, 1])
    with col_pie:
        fig = go.Figure(data=[go.Pie(
            labels=['Можно взять с ЦС', 'Нужно докупить'], 
            values=[covered_sku, uncovered_sku], 
            hole=.7, 
            marker=dict(colors=['#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA', '#FC8181'], line=dict(color='#0D2638', width=2)),
            textinfo='none'
        )])
        fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
        fig.add_annotation(text=f"{pct_covered:.1f}%", x=0.5, y=0.5, font=dict(size=32, color='#FFFFFF'), showarrow=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_info:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin-bottom: 5px; color: #FFFFFF;'>Всего нужно: <span style='color: {('#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA')};'>{total_need_sku} SKU</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 16px; color: #38B2AC;'>Закрывает ЦС: <b>{covered_sku} SKU</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 16px; color: #FC8181;'>Дефицит (Нет на ЦС): <b>{uncovered_sku} SKU</b></p>", unsafe_allow_html=True)

    with st.expander("📈 1. Ходовые товары (XY)", expanded=True):
        if not df_sto_clean.empty:
            c1, c2, c3 = st.columns(3)
            xy_total = len(df_sto_clean[df_sto_clean['XYZ'].isin(['X', 'Y'])]['Код'].unique())
            crit_df = df_sto_clean[(df_sto_clean['XYZ'].isin(['X', 'Y'])) & (df_sto_clean['Хватит дней'] < 20)]
            crit_count = len(crit_df['Код'].unique())
            
            with c1: st.metric("Всего ходовых SKU", f"{xy_total:,}")
            with c2: st.metric("Критический запас (<20 дн)", f"{crit_count:,}", delta_color="inverse")
            
            crit_codes = crit_df['Код'].unique()
            covered_cs = len(mov_filtered[(mov_filtered['Тип'] == 'Из ЦС') & (mov_filtered['Код'].isin(crit_codes))]['Код'].unique())
            covered_sto = len(mov_filtered[(mov_filtered['Тип'] == 'Из СТО') & (mov_filtered['Код'].isin(crit_codes))]['Код'].unique())
            uncovered = max(0, crit_count - covered_cs - covered_sto)

            pct_cs = (covered_cs / crit_count * 100) if crit_count > 0 else 0
            pct_sto = (covered_sto / crit_count * 100) if crit_count > 0 else 0
            pct_def = (uncovered / crit_count * 100) if crit_count > 0 else 0

            col_pie, col_info = st.columns([1, 1])
            with col_pie:
                fig_bar = go.Figure(data=[go.Pie(
                    labels=['Из ЦС', 'Из СТО', 'Дефицит'],
                    values=[covered_cs, covered_sto, uncovered],
                    hole=.7,
                    marker=dict(colors=['#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA', '#F6E05E', '#FC8181'], line=dict(color='#0D2638', width=2)),
                    textinfo='none'
                )])
                fig_bar.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
                fig_bar.add_annotation(text=f"{crit_count} SKU", x=0.5, y=0.5, font=dict(size=24, color='#FFFFFF'), showarrow=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_info:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='margin-bottom: 5px; color: #FFFFFF;'>Критический запас: <span style='color: #FC8181;'>{crit_count} SKU</span></h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px; color: {('#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA')};'>Из ЦС: <b>{covered_cs} SKU</b> ({pct_cs:.0f}%)</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px; color: #F6E05E;'>Из СТО: <b>{covered_sto} SKU</b> ({pct_sto:.0f}%)</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px; color: #FC8181;'>Дефицит: <b>{uncovered} SKU</b> ({pct_def:.0f}%)</p>", unsafe_allow_html=True)

    with st.expander("📉 2. Неликвид (Z) - От 6 до 12 мес и Свыше года", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            rub_6_12 = df_sto_clean['Неликвид_6_12'].sum() * df_sto_clean['Цена'].mean() if 'Неликвид_6_12' in df_sto_clean.columns else 0
            st.metric("Неликвид 6–12 мес", f"{rub_6_12:,.0f} ₽", delta_color="inverse")
        with c2:
            rub_12_plus = df_sto_clean['Неликвид_12_plus'].sum() * df_sto_clean['Цена'].mean() if 'Неликвид_12_plus' in df_sto_clean.columns else 0
            st.metric("Неликвид 12+ мес", f"{rub_12_plus:,.0f} ₽", delta_color="inverse")

    with st.expander("📦 3. Излишки (XY)", expanded=False):
        if not df_sto_clean.empty:
            df_surplus = df_sto_clean[df_sto_clean['Излишек'] > 0].groupby('СТО')['Излишек'].sum().reset_index().sort_values('Излишек', ascending=False).head(10)
            colors = px.colors.sequential.Teal if category_filter == 'Запасные части' else px.colors.sequential.Purples
            fig_sur = px.bar(df_surplus, x='Излишек', y='СТО', orientation='h', title="Топ-10 СТО по излишкам (шт)", template='plotly_dark', color='Излишек', color_continuous_scale=colors)
            fig_sur.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=40, b=0), font=dict(color='#FFFFFF'), coloraxis_showscale=False)
            st.plotly_chart(fig_sur, use_container_width=True)

    with st.expander("💰 4. Деньги и оборачиваемость", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Сумма запасов", f"{df_sto['Остаток, ₽'].sum():,.0f} ₽")
        with c2: st.metric("Сумма излишков", f"{df_sto['Излишек, ₽'].sum():,.0f} ₽", delta_color="inverse")
        with c3: st.metric("Сумма неликвидов", f"{df_sto['Неликвид, ₽'].sum():,.0f} ₽", delta_color="inverse")
        
        total_year_sales = df_sto['Сумма за год'].sum()
        total_stock = df_sto['Остаток'].sum()
        turnover = total_year_sales / total_stock if total_stock > 0 else 0
        st.markdown(f"<p style='color: {('#38B2AC' if category_filter == 'Запасные части' else '#9F7AEA')}; font-size: 18px;'>Общая оборачиваемость склада: <b>{turnover:.2f}</b> раз в год</p>", unsafe_allow_html=True)

    with st.expander("🚚 5. Логистика (Штуки к перемещению)", expanded=False):
        move_cs_val = mov_filtered[mov_filtered['Тип'] == 'Из ЦС']['Количество'].sum() if not mov_filtered.empty else 0
        move_nag_val = mov_filtered[mov_filtered['Тип'] == 'Из ЦС Нагатинская']['Количество'].sum() if not mov_filtered.empty else 0
        move_sto_val = mov_filtered[mov_filtered['Тип'] == 'Из СТО']['Количество'].sum() if not mov_filtered.empty else 0
        return_val = mov_filtered[mov_filtered['Тип'] == 'Возврат на ЦС']['Количество'].sum() if not mov_filtered.empty else 0

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Из ЦС Сокол", f"{move_cs_val:,.0f} шт")
        with c2: st.metric("Из ЦС Нагат", f"{move_nag_val:,.0f} шт")
        with c3: st.metric("Между СТО", f"{move_sto_val:,.0f} шт")
        with st.expander("Возврат на ЦС"):
            st.metric("Возврат на ЦС", f"{return_val:,.0f} шт", delta_color="inverse")

elif menu == "📦 Внеплановое поступление":
    st.markdown("<div class='section-header'>Распределение нового поступления</div>", unsafe_allow_html=True)
    col_search, col_qty = st.columns([3, 1])
    with col_search: search_query = st.text_input("Поиск по Наименованию, Артикулу или Коду", "")
    with col_qty: qty_incoming = st.number_input("Количество пришедшего товара", min_value=1, value=200, step=1)
        
    if search_query:
        mask = (df_sto['Наименование'].str.contains(search_query, case=False, na=False)) | \
               (df_sto['Артикул'].str.contains(search_query, case=False, na=False)) | \
               (df_sto['Код'].str.contains(search_query, case=False, na=False))
        df_found = df_sto[mask].copy()
        
        if df_found.empty: st.warning("Товар не найден на СТО.")
        else:
            df_found['Расход_3мес'] = df_found['Суточный расход'] * 90
            df_calc = df_found.groupby('СТО').agg(
                Расход_3мес=('Расход_3мес', 'sum'), Остаток_P=('Остаток', 'sum'),
                Норма_упак=('Норма упак', 'first'), Код=('Код', 'first'), Артикул=('Артикул', 'first'), Наименование=('Наименование', 'first')
            ).reset_index()
            total_3m_rashod = df_calc['Расход_3мес'].sum()

            if total_3m_rashod == 0: st.warning("За последние 3 месяца не было расхода. Распределите вручную.")
            else:
                df_calc['Доля'] = df_calc['Расход_3мес'] / total_3m_rashod
                df_calc['Причитается_по_доле'] = df_calc['Доля'] * qty_incoming
                df_calc['Норма_упак'] = df_calc['Норма_упак'].apply(lambda x: x if x > 0 else 1)
                df_calc['К_отгрузке_сырое'] = (df_calc['Причитается_по_доле'] - df_calc['Остаток_P']).clip(lower=0)
                
                def round_up(row):
                    val = row['К_отгрузке_сырое']
                    if val <= 0: return 0
                    norma = row['Норма_упак']
                    return math.ceil(val / norma) * norma

                df_calc['К_отгрузке'] = df_calc.apply(round_up, axis=1)
                total_alloc = df_calc['К_отгрузке'].sum()
                if total_alloc > qty_incoming:
                    df_calc['К_отгрузке'] = df_calc['К_отгрузке'].apply(lambda x: min(x, qty_incoming))
                    total_alloc = df_calc['К_отгрузке'].sum()
                df_final = df_calc[df_calc['К_отгрузке'] > 0].copy()
                
                if not df_final.empty:
                    st.markdown(f"### Рекомендация по распределению ({total_alloc} шт)")
                    st.dataframe(df_final[['СТО', 'Код', 'Артикул', 'Наименование', 'Расход_3мес', 'Остаток_P', 'Норма_упак', 'К_отгрузке']], use_container_width=True, hide_index=True)
                    rem_qty = qty_incoming - total_alloc
                    if rem_qty > 0: st.info(f"Остаток {rem_qty} шт. можно оставить на складе.")
                else: st.success("Отлично! У всех СТО достаточно текущего остатка.")

elif menu == "🛒 Планирование закупок":
    st.markdown("<div class='section-header'>Планирование закупок</div>", unsafe_allow_html=True)
    
    if purch_filtered.empty:
        st.success("Отлично! Закупки не требуются, запасов хватает до приезда АЗК.")
    else:
        total_purch_sku = len(purch_filtered)
        total_purch_sum = purch_filtered['Сумма'].sum()
        urgent_sku = len(purch_filtered[purch_filtered['Хватит_дней'] < 20])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Всего SKU к закупке", f"{total_purch_sku:,}")
        with c2: st.metric("Общая сумма закупки", f"{total_purch_sum:,.0f} ₽")
        with c3: st.metric("Срочные (меньше 20 дней)", f"{urgent_sku:,}", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)
        
        def highlight_row(row):
            if row['Хватит_дней'] < 20:
                return ['background-color: rgba(252, 129, 129, 0.2)'] * len(row)
            elif row['Хватит_дней'] < 60:
                return ['background-color: rgba(246, 224, 94, 0.2)'] * len(row)
            else:
                return ['background-color: rgba(56, 178, 172, 0.1)' if category_filter == 'Запасные части' else 'background-color: rgba(159, 122, 234, 0.1)'] * len(row)
        
        styled_df = purch_filtered[['Код', 'SKN', 'Артикул', 'Наименование', 'Кому_нужно', 'Общий_запас', 'Хватит_дней', 'Срок_АЗК', 'Суточный_расход', 'Нужно_купить', 'Сумма']].style.apply(highlight_row, axis=1).format({
            "Общий_запас": "{:.0f}", "Хватит_дней": "{:.0f}", "Срок_АЗК": "{:.0f}", 
            "Суточный_расход": "{:.2f}", "Нужно_купить": "{:.0f}", "Сумма": "{:,.2f}"
        })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
        
        st.info("💡 Красный — срочно (меньше 20 дней). Желтый — планово (20-60 дней). Зеленый — запас есть, но меньше срока АЗК.")

elif menu == "🚚 Перемещения из ЦС":
    st.markdown("<div class='section-header'>Перемещения из Центрального склада</div>", unsafe_allow_html=True)
    mov_cs = mov_filtered[mov_filtered['Тип'].isin(['Из ЦС', 'Из ЦС Нагатинская'])].copy() if has_mov else pd.DataFrame()
    if not mov_cs.empty:
        mov_cs_table = mov_cs.rename(columns={'Куда': 'Название СТО', 'SKN': 'Номенклатура (SKN)', 'Количество': 'Кол-во переместить'})
        st.dataframe(mov_cs_table[['Откуда', 'Название СТО', 'Код', 'Номенклатура (SKN)', 'Артикул', 'Артикул на ЦС', 'Наименование', 'Кол-во переместить']], use_container_width=True, hide_index=True)
    else: st.info("Нет необходимости перемещать из ЦС.")

elif menu == "🔄 Перемещения между СТО":
    st.markdown("<div class='section-header'>Перемещения между СТО</div>", unsafe_allow_html=True)
    mov_sto = mov_filtered[mov_filtered['Тип'].isin(['Из СТО', 'Возврат на ЦС'])].copy() if has_mov else pd.DataFrame()
    def render_mov(df_):
        if df_.empty: st.info("Нет данных."); return
        tbl = df_.rename(columns={'Откуда': 'Откуда (донор)', 'Куда': 'Куда', 'SKN': 'Номенклатура (SKN)', 'Количество': 'Кол-во переместить'})
        st.dataframe(tbl[['Куда', 'Код', 'Номенклатура (SKN)', 'Артикул', 'Артикул на ЦС', 'Наименование', 'Кол-во переместить', 'Откуда (донор)']], use_container_width=True, hide_index=True)
    
    if sub_menu == "Неликвиды (6+ мес)":
        render_mov(mov_sto[(mov_sto['Метка_донора'] == 4) | (mov_sto['Тип'] == 'Возврат на ЦС')] if not mov_sto.empty else pd.DataFrame())
    elif sub_menu == "Излишки":
        render_mov(mov_sto[(mov_sto['Метка_донора'] == 1) & (mov_sto['Тип'] == 'Из СТО')] if not mov_sto.empty else pd.DataFrame())
    elif sub_menu == "Возврат на ЦС":
        render_mov(mov_sto[mov_sto['Тип'] == 'Возврат на ЦС'] if not mov_sto.empty else pd.DataFrame())

elif menu == "📋 Итоговая таблица":
    st.markdown("<div class='section-header'>Полная аналитика по выбранным СТО</div>", unsafe_allow_html=True)
    
    search_q = st.text_input("🔍 Умный поиск по Итоговой таблице (Код, SKN, Артикул или Наименование)", "")
    
    if not df_sto.empty:
        if category_filter == "Запасные части":
            df_cs_ost = df[df['СТО'] == 'ЦС'].pivot_table(index='Код', columns='СТО', values='Остаток', aggfunc='sum').reset_index().rename(columns={'ЦС': 'Остаток ЦС Сокол'})
            df_nag_ost = df[df['СТО'] == 'ЦС_Нагатинская'].pivot_table(index='Код', columns='СТО', values='Остаток', aggfunc='sum').reset_index().rename(columns={'ЦС_Нагатинская': 'Остаток ЦС Нагат'})
            
            cols_to_show = ['СТО', 'Тип', 'Код', 'SKN', 'Артикул', 'Наименование', 'Суточный расход', 'XYZ', 'Хватит дней', 'Остаток', 'Остаток, ₽', 'Излишек', 'Излишек, ₽', 'Неликвид', 'Неликвид, ₽', 'Нужно привезти', 'Нужно привезти, ₽', 'Доля (потребн.)', 'Норма упак']
            df_final = df_sto[cols_to_show].copy()
            df_final = df_final.merge(df_cs_ost, on='Код', how='left').fillna({'Остаток ЦС Сокол': 0})
            df_final = df_final.merge(df_nag_ost, on='Код', how='left').fillna({'Остаток ЦС Нагат': 0})
            cols_out = ['СТО', 'Тип', 'Код', 'SKN', 'Артикул', 'Наименование', 'Суточный расход', 'XYZ', 'Хватит дней', 'Остаток', 'Остаток, ₽', 'Остаток ЦС Сокол', 'Остаток ЦС Нагат', 'Излишек', 'Излишек, ₽', 'Неликвид', 'Неликвид, ₽', 'Нужно привезти', 'Нужно привезти, ₽', 'Доля (потребн.)', 'Норма упак']
        else:
            df_cs_ost = df[df['СТО'] == 'ЦС'].pivot_table(index='Код', columns='СТО', values='Остаток', aggfunc='sum').reset_index().rename(columns={'ЦС': 'Остаток ЦС РМ'})
            
            cols_to_show = ['СТО', 'Тип', 'Код', 'SKN', 'Артикул', 'Наименование', 'Суточный расход', 'XYZ', 'Хватит дней', 'Остаток', 'Остаток, ₽', 'Излишек', 'Излишек, ₽', 'Неликвид', 'Неликвид, ₽', 'Нужно привезти', 'Нужно привезти, ₽', 'Доля (потребн.)', 'Норма упак']
            df_final = df_sto[cols_to_show].copy()
            df_final = df_final.merge(df_cs_ost, on='Код', how='left').fillna({'Остаток ЦС РМ': 0})
            cols_out = ['СТО', 'Тип', 'Код', 'SKN', 'Артикул', 'Наименование', 'Суточный расход', 'XYZ', 'Хватит дней', 'Остаток', 'Остаток, ₽', 'Остаток ЦС РМ', 'Излишек', 'Излишек, ₽', 'Неликвид', 'Неликвид, ₽', 'Нужно привезти', 'Нужно привезти, ₽', 'Доля (потребн.)', 'Норма упак']

        df_final['Готово'] = False
        
        if search_q:
            mask = df_final['Код'].str.contains(search_q, case=False, na=False) | \
                   df_final['SKN'].str.contains(search_q, case=False, na=False) | \
                   df_final['Артикул'].str.contains(search_q, case=False, na=False) | \
                   df_final['Наименование'].str.contains(search_q, case=False, na=False)
            df_final = df_final[mask]

        st.data_editor(df_final[cols_out + ['Готово']],
            use_container_width=True, hide_index=True,
            column_config={"Готово": st.column_config.CheckboxColumn("Готово?", default=False), "Суточный расход": st.column_config.NumberColumn(format="%.3f"), "Хватит дней": st.column_config.NumberColumn(format="%d"), "Остаток": st.column_config.NumberColumn(format="%d"), "Остаток, ₽": st.column_config.NumberColumn(format="%.2f"), "Остаток ЦС Сокол": st.column_config.NumberColumn(format="%d"), "Остаток ЦС Нагат": st.column_config.NumberColumn(format="%d"), "Остаток ЦС РМ": st.column_config.NumberColumn(format="%d"), "Излишек": st.column_config.NumberColumn(format="%d"), "Излишек, ₽": st.column_config.NumberColumn(format="%.2f"), "Неликвид": st.column_config.NumberColumn(format="%d"), "Неликвид, ₽": st.column_config.NumberColumn(format="%.2f"), "Нужно привезти": st.column_config.NumberColumn(format="%d"), "Нужно привезти, ₽": st.column_config.NumberColumn(format="%.2f"), "Доля (потребн.)": st.column_config.NumberColumn(format="%d"), "Норма упак": st.column_config.NumberColumn(format="%d")},
            disabled=[c for c in cols_out])
    else: st.info("Нет данных по выбранным СТО.")