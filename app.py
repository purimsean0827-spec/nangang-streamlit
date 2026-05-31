import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面與主題設定
st.set_page_config(
    page_title="南港蛻變：從工業黑鄉到東區門戶",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #0b0f19;
        color: #f0f4f8;
    }
    /* 縮小時間軸卡片高度 */
    .timeline-card {
        padding: 10px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px;
        border-left: 4px solid #00f0ff;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    .timeline-card h4 { margin-top: 0; margin-bottom: 5px; color: #00f0ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("南港 🏙️ 蛻變")
st.markdown("### 從工業黑鄉到東區門戶的都市進化史")
st.divider()

# 2. 準備核心資料庫
@st.cache_data
def load_data():
    df = pd.read_csv('real_data.csv')
    df['年份'] = df['年份'].astype(str)
    df_long = df.melt(id_vars=['年份'], var_name='用途類別', value_name='總樓地板面積 (千平方公尺)')
    return df, df_long

df_wide, df_long = load_data()

min_year = int(df_wide['年份'].min())
max_year = int(df_wide['年份'].max())

# 3. 準備都委會案件資料
@st.cache_data
def load_tpupc_data():
    try:
        return pd.read_csv('tpupc_cases.csv')
    except:
        return pd.DataFrame()

df_tpupc = load_tpupc_data()

# 4. 側邊欄運算與篩選器
st.sidebar.header("📊 數據運算與篩選")
selected_years = st.sidebar.slider(
    "選擇年份區間",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 動態運算結果")
mask = (df_wide['年份'].astype(int) >= selected_years[0]) & (df_wide['年份'].astype(int) <= selected_years[1])
filtered_df = df_wide[mask]

total_office = filtered_df['辦公服務類 (生技/軟體/總部)'].sum()
total_industrial = filtered_df['工業倉儲類'].sum()

st.sidebar.metric("該區間核發辦公總面積", f"{total_office:,} 千㎡")
st.sidebar.metric("該區間核發工業總面積", f"{total_industrial:,} 千㎡")

# 5. 主視覺區：縮小版歷史時間軸與指標都更案 (Timeline)
st.subheader("🕰️ 都市發展軌跡與指標性都更案")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="timeline-card" style="border-left-color: #94a3b8;">
        <h4>1950 - 1980s: 工業黑鄉</h4>
        煙囪林立與煤灰飄散，南港被冠上「黑鄉」之名，形成特有的工住混合地景。
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="timeline-card" style="border-left-color: #facc15;">
        <h4>1990 - 2014: 轉型與產專區</h4>
        市府投入建設南港軟體園區、展覽館。<br>
        ⭐ <b>指標案件：南港新都</b> (產專區首件公辦都更，由黑鄉聚落轉型為無界森林社區)
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="timeline-card" style="border-left-color: #00f0ff;">
        <h4>2015 - 至今: 東區門戶計畫</h4>
        確立五大中心為目標，推動人行立體連通系統。<br>
        ⭐ <b>指標案件：南港之星</b> (商三特公辦都更，結合轉運站的超大型垂直城市樞紐)
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 6. 互動圖表區
st.subheader(f"📈 南港區建築總樓地板面積趨勢 ({selected_years[0]} - {selected_years[1]})")

mask_long = (df_long['年份'].astype(int) >= selected_years[0]) & (df_long['年份'].astype(int) <= selected_years[1])
filtered_long_df = df_long[mask_long]

color_map = {
    '工業倉儲類': '#94a3b8',
    '住宅類': '#10b981',
    '商業類 (商場/展覽)': '#facc15',
    '辦公服務類 (生技/軟體/總部)': '#00f0ff'
}

fig = px.bar(
    filtered_long_df, 
    x='年份', 
    y='總樓地板面積 (千平方公尺)', 
    color='用途類別',
    color_discrete_map=color_map,
    title="各用途樓地板面積 (堆疊長條圖)",
    barmode='stack',
    template='plotly_dark'
)
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig, use_container_width=True)

# 7. 新增：歷年新增樓地板面積總表 (Data Table)
st.markdown("### 📊 歷年樓地板面積詳細數據 (千平方公尺)")
# 顯示原本的 Wide Format DataFrame，並讓索引乾淨
display_df = filtered_df.set_index('年份')
st.dataframe(display_df, use_container_width=True, height=250)

st.divider()

# 8. 新增：都委會會議案件與新增容積 (TPUPC Data)
st.subheader("🏛️ 臺北市都市計畫委員會：南港重大都更與變更案 (2013起)")
st.markdown("透過資料大平臺 API 擷取歷年南港區的重要案件，以下展示各案預估帶來的**新增容積 (千㎡)**：")

if not df_tpupc.empty:
    # 格式化日期與容積
    df_tpupc_display = df_tpupc.copy()
    
    # 畫一個簡單的長條圖來顯示新增容積
    fig_tpupc = px.bar(
        df_tpupc_display, 
        x='模擬新增容積 (千㎡)', 
        y='案名', 
        orientation='h',
        color='模擬新增容積 (千㎡)',
        color_continuous_scale='Teal',
        title='各重大計畫預估新增容積 (模擬推估值)'
    )
    fig_tpupc.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tpupc, use_container_width=True)
    
    # 顯示會議紀錄表格
    st.dataframe(df_tpupc_display[['年份', '日期', '會次', '案名', '模擬新增容積 (千㎡)']].set_index('日期'), use_container_width=True)
    st.caption("備註：本區塊案件清單源自 data.taipei 都委會會議紀錄；「新增容積」欄位因受限於 PDF 格式難以自動化解析，目前為系統依據案件規模生成的模擬推估值，供視覺化展示使用。")
else:
    st.info("尚未載入都委會資料，請確認 tpupc_cases.csv 存在。")
