import re

import pandas as pd
import requests
import streamlit as st

CSV_URL = "https://drive.google.com/uc?id=1Lg1xB79PYue1D5qSPy2IMo6zNMjOgEa4&export=download"


@st.cache_data(ttl=300)
def load_index_csv() -> pd.DataFrame:
    """index.csvを読み込みキャッシュにためておく関数

    Returns:
        pd.DataFrame

    """
    return pd.read_csv(CSV_URL)


def extract_file_id(drive_url: str) -> str | None:
    """Google driveのurlからファイルidを取得する

    Args:
        drive_url: str
            google driveのurl

    Returns:
        str | None
            ファイルid

    """
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
    if match:
        return match.group(1)
    return None


@st.cache_data()
def load_kif_text(kif_url: str) -> str:
    """棋譜データのテキストをurlから取得する

    Args:
        kif_url: str
            棋譜データのurl

    Returns:
        str
            kif形式の棋譜データ

    """
    kif_if = extract_file_id(kif_url)
    response = requests.get(f"https://drive.google.com/uc?id={kif_if}&export=download", timeout=300)
    response.raise_for_status()
    return response.text


def get_match_text(df: pd.DataFrame, index: int) -> str:
    """指定されたindexの対局情報をテキストとして受け取る

    Args:
        df: pd.DataFrame
            対局情報を格納したテーブル
        index: int
            対局情報を返したいテーブルのindex

    Returns:
        str: _description_

    """
    date = df.loc[index, "日付"]
    no = df.loc[index, "試合番号"]
    sente = df.loc[index, "先手"]
    gote = df.loc[index, "後手"]
    teaiwari = df.loc[index, "手合割"]
    result = df.loc[index, "結果"]
    return f"{date} {no}局目 {sente} 対 {gote} ({teaiwari}, {result})"


st.set_page_config(page_title="トモシカ対局棋譜データ", page_icon="🦌")

st.title("☖トモシカ対局棋譜データ🦌")

df = load_index_csv()


col = st.columns([4, 1])

selected_index = st.selectbox(
    "対局を選択",
    sorted(df.index, reverse=True),
    format_func=lambda i: get_match_text(df, i),
)

row = df.loc[selected_index]

st.markdown(f"""
- 日付　: {row["日付"]} - {row["試合番号"]}局目
- 先手　: {row["先手"]}
- 後手　: {row["後手"]}
- 手合割: {row["手合割"]}
- 結果　: {row["結果"]}
- 動画　: [こちらのリンク]({row["動画URL"]})
""")

try:
    kif_text = load_kif_text(row["棋譜データURL"])
    st.text_area("棋譜（KIF形式）", kif_text, height=300)
    st.download_button(
        "棋譜をダウンロード",
        kif_text,
        file_name=get_match_text(df, selected_index) + ".txt",
        mime="text/plain",
        type="primary",
    )
except FileNotFoundError as e:
    st.error(f"棋譜の読み込みに失敗しました: {e}")


st.divider()
st.markdown(
    "[緋笠トモシカ](https://www.youtube.com/@tomoshikahikasa)さんやそのお友達の方が対局した棋譜データをまとめています。棋譜は手入力ですのでミスがあるかもしれませんが、ご了承ください。"
)

st.markdown("このサイトについての問い合わせや棋譜のミスについては[@mega_ebi](https://x.com/mega_ebi)まで")

with st.expander("このページに関するその他の注記"):
    st.markdown(
        "2024/08/12 - [【将棋】VOMS将棋部でぐちゃぐちゃ10秒将棋総当たり大会！！](https://www.youtube.com/live/Y7jC8mEBUbE?si=HIPig2pgMW3q4DeI)で実施した対局は、あまりにも対局数が多く手入力の手間がかかるため、少なくとも当面は対象外です。"
    )
    st.markdown("2025/08/12 - ５五将棋、短時間での切れ負け将棋は基本的に対象外です。")
