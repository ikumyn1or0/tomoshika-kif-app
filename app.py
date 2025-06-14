import streamlit as st
import pandas as pd
import requests
import re


CSV_URL = "https://drive.google.com/uc?id=1Lg1xB79PYue1D5qSPy2IMo6zNMjOgEa4&export=download"

@st.cache_data(ttl=300)
def load_index_csv():
    df = pd.read_csv(CSV_URL)
    return df

def extract_file_id(drive_url: str) -> str | None:
    print(drive_url)
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
    if match:
        return match.group(1)
    return None

@st.cache_data(ttl=300)
def load_kif_text(kif_url):
    kif_if = extract_file_id(kif_url)
    response = requests.get(f"https://drive.google.com/uc?id={kif_if}&export=download")
    response.raise_for_status()
    return response.text

def get_match_text(df, i):
    date = df.loc[i, "日付"]
    no = df.loc[i, "試合番号"]
    sente = df.loc[i, "先手"]
    gote = df.loc[i, "後手"]
    result = df.loc[i, "結果"]
    return f"{date} {no}局目 {sente} 対 {gote} ({result})"



st.title("トモシカ対局棋譜データ")

df = load_index_csv()


col = st.columns([4, 1])

selected_index = st.selectbox(
    "対局を選択",
    df.index,
    format_func=lambda i: get_match_text(df, i)
)

row = df.loc[selected_index]

st.markdown(f"""
- 日付: {row["日付"]} - {row["試合番号"]}局目
- 先手: {row["先手"]}
- 後手: {row["後手"]}
- 結果: {row["結果"]}
- 動画: [こちらのリンク]({row["動画URL"]})
""")

try:
    kif_text = load_kif_text(row["棋譜データURL"])
    st.text_area("棋譜（KIF形式）", kif_text, height=300)
    st.download_button("棋譜をダウンロード", kif_text, file_name=get_match_text(df, selected_index)+".txt", mime="text/plain", type="primary")
except Exception as e:
    st.error(f"棋譜の読み込みに失敗しました: {e}")


st.markdown("---")
st.markdown("このサイトについての問い合わせは[@mega_ebi](https://x.com/mega_ebi)まで")