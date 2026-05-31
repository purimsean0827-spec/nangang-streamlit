import pandas as pd
import requests
import random
import os

# 臺北市資料大平臺：都市計畫委員會會議紀錄 API
API_URL = "https://data.taipei/api/v1/dataset/a9b89793-21c6-43b9-a5c9-94b2fcf089d8?scope=resourceAquire&limit=1000"

def fetch_and_process_tpupc_data():
    print("開始下載都委會會議紀錄...")
    
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        raw_data = response.json()['result']['results']
        df = pd.DataFrame(raw_data)
        
        # 1. 確保有日期與案名欄位，並轉型
        if '日期' not in df.columns or '案名' not in df.columns:
            raise ValueError("API 資料格式改變，缺少必要欄位")
            
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        df['年份'] = df['日期'].dt.year
        
        # 2. 過濾出 2013 年 (含) 以後，且案名包含「南港」的案件
        nangang_cases = df[(df['年份'] >= 2013) & (df['案名'].str.contains('南港', na=False))].copy()
        
        if nangang_cases.empty:
             raise ValueError("找不到南港區的案件資料")
        
        # 3. 簡化案名並配上模擬的「新增容積」
        # 真實的容積數字在 PDF 中，此處以常態分佈模擬各案帶來的容積增量 (單位：千平方公尺)
        random.seed(42) # 固定 seed 讓每次產生的資料一致
        
        def simulate_added_capacity(row):
             # 針對大型計畫給予較高容積
             if '變更' in str(row['案名']) and '主要計畫' in str(row['案名']):
                 return round(random.uniform(50.0, 150.0), 2)
             elif '通盤檢討' in str(row['案名']):
                 return round(random.uniform(100.0, 250.0), 2)
             else:
                 return round(random.uniform(5.0, 40.0), 2)
                 
        nangang_cases['模擬新增容積 (千㎡)'] = nangang_cases.apply(simulate_added_capacity, axis=1)
        
        # 整理最終輸出的欄位
        final_df = nangang_cases[['年份', '日期', '會次', '案名', '模擬新增容積 (千㎡)']]
        final_df = final_df.sort_values(by='日期', ascending=False)
        
        output_path = 'tpupc_cases.csv'
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 成功擷取並處理 {len(final_df)} 筆南港區都委會案件！已儲存至 {output_path}")

    except Exception as e:
        print(f"⚠️ 獲取真實 API 失敗: {e}")
        print("啟動備用方案：產生 2013 年至今具代表性的南港都委會模擬案件資料")
        
        # 建立幾個知名的南港都市計畫案來模擬 API 回傳結果
        mock_data = {
            '年份': [2023, 2021, 2019, 2018, 2016, 2015, 2013],
            '日期': ['2023-08-15', '2021-11-20', '2019-05-10', '2018-09-12', '2016-04-25', '2015-08-30', '2013-12-15'],
            '會次': ['第812次', '第780次', '第745次', '第721次', '第680次', '第665次', '第630次'],
            '案名': [
                '臺北市南港區經貿園區（商三特）公辦都更案 (南港之星)',
                '變更臺北市南港區鐵路地下化沿線土地特定專用區細部計畫案',
                '臺北市南港區都市計畫通盤檢討案',
                '臺北市南港區台電AR1公辦都更案',
                '臺北市南港區產業生活特定專用區都市更新計畫',
                '臺北市東區門戶計畫南港轉運站周邊土地變更案',
                '南港區鐵路地下化沿線老舊廠房都市更新計畫'
            ],
            '模擬新增容積 (千㎡)': [130.5, 85.2, 210.0, 95.8, 150.3, 110.0, 45.6]
        }
        
        final_df = pd.DataFrame(mock_data)
        output_path = 'tpupc_cases.csv'
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 備用資料產生完成！已儲存至 {output_path}")

if __name__ == "__main__":
    fetch_and_process_tpupc_data()
