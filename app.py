import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面與主題設定 (Page Configuration)
st.set_page_config(
    page_title="南港蛻變：從工業黑鄉到東區門戶",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隱藏預設選單與增加自訂 CSS 來微調深色樣式
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #0b0f19;
        color: #f0f4f8;
    }
    .highlight {
        color: #00f0ff;
        font-weight: bold;
    }
    .highlight-gold {
        color: #facc15;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 標題與簡介 (Header & Intro)
st.title("南港 🏙️ 蛻變")
st.markdown("### 從工業黑鄉到東區門戶的都市進化史")
st.markdown("透過建築規模與產業板塊的變化，見證南港的轉型。")
st.divider()

# 3. 準備資料庫 (Data Preparation using Pandas)
@st.cache_data
def load_data():
    # 讀取 ETL 腳本產生的真實/模擬清理後資料
    df = pd.read_csv('real_data.csv')
    df['年份'] = df['年份'].astype(str)
    
    # 轉換為 Long Format 供 Plotly 使用
    df_long = df.melt(id_vars=['年份'], var_name='用途類別', value_name='總樓地板面積 (千平方公尺)')
    return df, df_long

df_wide, df_long = load_data()

# 動態獲取年份範圍以設定 Slider
min_year = int(df_wide['年份'].min())
max_year = int(df_wide['年份'].max())

# 4. 側邊欄運算與篩選器 (Sidebar Filters for Interactivity)
st.sidebar.header("📊 數據運算與篩選")
selected_years = st.sidebar.slider(
    "選擇年份區間",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 動態運算結果")
# 根據篩選運算總量
mask = (df_wide['年份'].astype(int) >= selected_years[0]) & (df_wide['年份'].astype(int) <= selected_years[1])
filtered_df = df_wide[mask]

total_office = filtered_df['辦公服務類 (生技/軟體/總部)'].sum()
total_industrial = filtered_df['工業倉儲類'].sum()

st.sidebar.metric("該區間核發辦公總面積", f"{total_office:,} 千㎡")
st.sidebar.metric("該區間核發工業總面積", f"{total_industrial:,} 千㎡")

if total_office > total_industrial:
    st.sidebar.success("✅ 辦公商業已全面取代工業")

# 5. 主視覺區：歷史時間軸 (History Timeline)
st.subheader("🕰️ 都市發展軌跡")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**1950 - 1980s: 工業黑鄉**\n\n由於煙囪林立與煤灰飄散，南港被冠上「黑鄉」之名，形成特有的工住混合地景。")
with col2:
    st.info("**1990 - 2014: 轉型期**\n\n鐵路地下化騰出大量都市空間，市府投入建設南港軟體園區、南港展覽館。")
with col3:
    st.warning("**2015 - 至今: 東區門戶計畫 (轉捩點)**\n\n確立五大中心為目標，推動人行立體連通系統，南港加速蛻變為現代化智慧生態城市。")

st.divider()

# 6. 互動圖表區 (Interactive Chart)
st.subheader(f"📈 南港區建築總樓地板面積趨勢 ({selected_years[0]} - {selected_years[1]})")

# 篩選繪圖用的資料
mask_long = (df_long['年份'].astype(int) >= selected_years[0]) & (df_long['年份'].astype(int) <= selected_years[1])
filtered_long_df = df_long[mask_long]

# 設定各類別對應的顏色 (還原先前的設計)
color_map = {
    '工業倉儲類': '#94a3b8',        # Gray
    '住宅類': '#10b981',            # Green
    '商業類 (商場/展覽)': '#facc15', # Gold
    '辦公服務類 (生技/軟體/總部)': '#00f0ff' # Neon Blue
}

fig = px.bar(
    filtered_long_df, 
    x='年份', 
    y='總樓地板面積 (千平方公尺)', 
    color='用途類別',
    color_discrete_map=color_map,
    title="各用途樓地板面積 (堆疊長條圖)",
    barmode='stack',
    template='plotly_dark' # 套用深色主題
)

# 微調圖表外觀
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# 7. 重點數據卡片 (Stat Cards)
st.markdown("### 💡 關鍵發展指標")
stat1, stat2, stat3 = st.columns(3)
with stat1:
    st.metric(label="2015年後最強推力", value="辦公服務類", delta="指數級攀升")
with stat2:
    st.metric(label="產業板塊轉移", value="商業與住宅 取代 工廠", delta="- 工業倉儲萎縮", delta_color="inverse")
with stat3:
    st.metric(label="近期開發高峰", value="2021 年", delta="公辦都更與商辦案")

st.caption("資料來源參考：臺北市資料大平臺 (data.taipei) - 臺北市現有營造建築物總面積。 (本展示數據基於歷史趨勢模擬)")
