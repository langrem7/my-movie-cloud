import os
import streamlit as st
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials

# --- 2. 核心配置 ---
# 这里直接用你的表格 ID，比用 URL 更稳
SPREADSHEET_ID = "1wLR_VyaIIRf438hYOjSk5pOJAcAEPNBlwTgSdgCz6Hw"

# --- 3. 连接 Google Sheets ---
def get_sheet():
    # 这里的 scopes 是固定写法
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # 读取 secrets
    if "connections" not in st.secrets:
        st.error("❌ 未找到 secrets.toml 配置！")
        st.stop()

    secrets_dict = dict(st.secrets["connections"]["gsheets"])

    # 登录
    creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
    client = gspread.authorize(creds)

    # ★关键修改：使用 ID 直连，且不隐藏错误★
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

# --- 4. 数据库操作 (去掉了 try...except，让错误直接爆出来) ---
def view_all_movies():
    # 这里我们故意删除了 try 模块，如果有网络问题，屏幕会直接报错
    # 这样我们才能知道到底发生了什么
    sheet = get_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 如果是空表，手动构建 DataFrame 避免报错
    if df.empty:
        return pd.DataFrame(columns=["title", "poster_url", "rating", "tags", "review", "created_at"])
    return df

def add_movie_to_db(title, poster, rating, tags, review):
    sheet = get_sheet()
    date = pd.Timestamp.now().strftime("%Y-%m-%d")
    sheet.append_row([title, poster, rating, tags, review, date])

def update_movie_in_db(index, new_review, new_rating):
    sheet = get_sheet()
    row = index + 2
    sheet.update_cell(row, 5, new_review)
    sheet.update_cell(row, 3, new_rating)

def delete_movie_from_db(index):
    sheet = get_sheet()
    row = index + 2
    sheet.delete_rows(row)

# --- 5. 页面 UI 配置 ---
st.set_page_config(page_title="iMovie Cloud", page_icon="☁️", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 6. 登录界面 ---
def login_page():
    st.markdown("""
    <style>
        header, footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        .stApp {
            background-image: url("https://4kwallpapers.com/images/wallpapers/macos-big-sur-apple-layers-fluidic-colorful-wwdc-2020-5120x2880-1455.jpg");
            background-size: cover;
            background-position: center;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(20px);
            padding: 40px; border-radius: 20px;
            text-align: center; width: 350px; margin: 100px auto;
        }
        .stTextInput input {text-align: center; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; justify-content:center;">
            <img src="https://cdn-icons-png.flaticon.com/512/2965/2965303.png" style="width:80px;border-radius:50%;">
        </div>
        <h3 style="text-align:center; color:white;">Admin Cloud</h3>
        """, unsafe_allow_html=True)

        pwd = st.text_input("", type="password", placeholder="Password (一直在等你)", label_visibility="collapsed")
        if st.button("Login") or pwd == "li147521":
            if pwd == "li147521":
                st.session_state['logged_in'] = True
                st.rerun()

# --- 7. 主程序 ---
def main_app():
    # 恢复侧边栏
    st.markdown("""
    <style>
        .stApp {background-image: none; background-color: #1e1e2e;}
        [data-testid="stSidebar"] {display: block; background-color: #262626;}
        .movie-card {
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            padding: 20px; border-radius: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write("✅ 已连接 Google Drive")
        if st.button("退出登录"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()
        with st.form("add"):
            t = st.text_input("电影名")
            p = st.text_input("海报URL")
            r = st.slider("评分", 1, 5, 4)
            tag = st.multiselect("标签", ["剧情", "科幻"], default=["剧情"])
            rev = st.text_area("短评")
            if st.form_submit_button("添加"):
                # 如果 URL 为空，给个默认图
                final_p = p if p else "https://via.placeholder.com/300?text=No+Img"
                add_movie_to_db(t, final_p, r, ",".join(tag), rev)
                st.success("已保存")
                time.sleep(1)
                st.rerun()

    st.title("☁️ 极光云影库")

    # 直接加载数据，不隐藏错误
    df = view_all_movies()

    if df.empty:
        st.info("表格目前是空的（但这说明连接成功了！）快去左侧添加第一部电影吧！")
    else:
        for idx, row in df.iterrows():
            c1, c2 = st.columns([1,4])
            with c1:
                try: st.image(row['poster_url'])
                except: st.write("无图")
            with c2:
                st.markdown(f"""
                <div class="movie-card">
                    <h3>{row['title']}</h3>
                    <p>⭐ {row['rating']} | {row['created_at']}</p>
                    <p>“{row['review']}”</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("编辑"):
                    nr = st.text_input("改评", row['review'], key=f"r{idx}")
                    save_col, del_col = st.columns(2)
                    if save_col.button("保存", key=f"s{idx}"):
                        update_movie_in_db(idx, nr, row['rating'])
                        st.rerun()
                    if del_col.button("删除", key=f"d{idx}"):
                        delete_movie_from_db(idx)
                        st.rerun()
            st.divider()

if not st.session_state['logged_in']:
    login_page()
else:
    main_app()
