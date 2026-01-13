import streamlit as st
import pandas as pd
from img2table.document import Image as TableImage
from img2table.ocr import PaddleOCR
import io
from PIL import Image

st.set_page_config(page_title="成績單掃描器", layout="centered")
st.title("🍎 智能成績單計算系統")

@st.cache_resource
def load_ocr():
    # 這是免費的辨識引擎
    return PaddleOCR(lang="ch", show_log=False)

ocr = load_ocr()

file = st.file_uploader("點擊上傳或拍照 (成績單照片)", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, caption="成功讀取照片", width=300)
    
    with st.spinner("AI 正在解析數據中..."):
        doc = TableImage(io.BytesIO(file.getvalue()))
        tables = doc.extract_tables(ocr=ocr, implicit_rows=True)
        
    if tables:
        df = tables[0].df
        # 根據你的圖片，自動修正標題
        df.columns = ["姓名", "國文", "英文", "平均"]
        df = df[1:].reset_index(drop=True)
        
        # 轉換數字
        df["國文"] = pd.to_numeric(df["國文"], errors='coerce').fillna(0)
        df["英文"] = pd.to_numeric(df["英文"], errors='coerce').fillna(0)
        
        st.subheader("📊 辨識結果與自定義計算")
        
        # 權重設定
        w = st.slider("調整加權 (國文佔比 %)", 0, 100, 50)
        df["自定義總分"] = (df["國文"] * w / 100) + (df["英文"] * (100 - w) / 100)
        
        # 標色 (低於60變紅色)
        def color_rule(val):
            return 'color: red' if isinstance(val, (int, float)) and val < 60 else 'color: black'
        
        st.dataframe(df.style.applymap(color_rule, subset=['自定義總分']))
        st.success("計算完畢！")
    else:
        st.error("找不到表格，請再拍清楚一點。")
