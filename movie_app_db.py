import streamlit as st
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Google Sheets 数据库连接 (核心修改: 使用 gspread) ---

def get_sheet():
    # 定义权限范围
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    # 从 secrets.toml 读取配置
    # 注意：我们将 secrets 转换成字典，可以直接喂给 Google 的验证模块
    secrets_dict = dict(st.secrets["connections"]["gsheets"])

    # 建立认证
    creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
    client = gspread.authorize(creds)

    # 打开表格 (通过 secrets 里的 spreadsheet 链接)
    spreadsheet_url = secrets_dict["spreadsheet"]
    sheet = client.open_by_url(spreadsheet_url).sheet1
    return sheet

# 读取所有数据
def view_all_movies():
    try:
        sheet = get_sheet()
        # 获取所有记录并转为 DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # 如果是空表，初始化列名
        if df.empty or "title" not in df.columns:
            return pd.DataFrame(columns=["title", "poster_url", "rating", "tags", "review", "created_at"])
        return df
    except Exception as e:
        # st.error(f"连接出错: {e}") # 调试用
        return pd.DataFrame(columns=["title", "poster_url", "rating", "tags", "review", "created_at"])

# 添加电影
def add_movie_to_db(title, poster, rating, tags, review):
    sheet = get_sheet()
    date = pd.Timestamp.now().strftime("%Y-%m-%d")
    # gspread 添加一行非常简单，直接 append
    sheet.append_row([title, poster, rating, tags, review, date])

# 更新电影 (根据行号 index)
def update_movie_in_db(index, new_review, new_rating):
    sheet = get_sheet()
    # Google Sheets 的行号是从 1 开始的，而且第一行是标题
    # 所以 Pandas 的 index 0 对应的是 Sheets 的 row 2
    row_number = index + 2

    # 更新特定单元格 (review在第5列，rating在第3列)
    # 注意：这里假设列顺序是 title, poster, rating, tags, review, date
    # 如果你的列顺序不一样，需要调整这里的 col 数字
    sheet.update_cell(row_number, 5, new_review) # 第5列是 review
    sheet.update_cell(row_number, 3, new_rating) # 第3列是 rating

# 删除电影
def delete_movie_from_db(index):
    sheet = get_sheet()
    row_number = index + 2
    sheet.delete_rows(row_number)

# --- 2. 页面配置 (保持不变) ---
st.set_page_config(page_title="iMovie Cloud", page_icon="☁️", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 3. macOS 登录界面 (保持不变) ---
def login_page():
    st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        .stApp {
            background-image: url("https://4kwallpapers.com/images/wallpapers/macos-big-sur-apple-layers-fluidic-colorful-wwdc-2020-5120x2880-1455.jpg");
            background-size: cover;
            background-position: center;
        }
        .login-container {
            background-color: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(15px);
            padding: 40px; border-radius: 20px;
            text-align: center; width: 350px; margin: 100px auto;
        }
        .stTextInput input {text-align: center; border-radius: 12px;}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; justify-content: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/2965/2965303.png" style="width:100px; border-radius:50%;">
        </div>
        <h3 style="text-align: center; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">Admin Cloud</h3>
        """, unsafe_allow_html=True)

        password = st.text_input("", type="password", placeholder="Password (欢迎回来，请输入密码)", label_visibility="collapsed")

        if st.button("Enter") or password == "li147521":
            if password == "li147521":
                st.session_state['logged_in'] = True
                st.rerun()
            elif password:
                st.error("Wrong Password")

# --- 4. 主程序 (稍微调整) ---
def main_app():
    st.markdown("""
    <style>
        .stApp {background-image: none; background-color: #1e1e2e;}
        [data-testid="stSidebar"] {display: block; background-color: #262626;}
        .movie-card {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 15px; padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write("☁️ 数据已连接 Google Drive (Gspread)")
        if st.button("🔴 退出"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.divider()
        st.header("🎟️ 添加电影")
        with st.form("add_form", clear_on_submit=True):
            title = st.text_input("电影名")
            poster = st.text_input("海报URL")
            rating = st.slider("评分", 1, 5, 4)
            tags = st.multiselect("标签", ["科幻", "剧情", "动作", "动画"], default=["剧情"])
            review = st.text_area("短评")
            if st.form_submit_button("归档"):
                poster_f = poster if poster else "https://via.placeholder.com/300?text=No+Img"
                add_movie_to_db(title, poster_f, rating, ",".join(tags), review)
                st.success("已同步至云端")
                time.sleep(1)
                st.rerun()

    st.title("🎬 极光云影库")

    with st.spinner('正在从 Google Sheets 同步数据...'):
        df = view_all_movies()

    if df.empty:
        st.info("云端表格是空的，或者列名不对。请去Google Sheets手动添加第一行标题：title, poster_url, rating, tags, review, created_at")
    else:
        for index, row in df.iterrows():
            c1, c2 = st.columns([1, 4])
            with c1:
                try:
                    st.image(row['poster_url'])
                except:
                    st.write("无图")
            with c2:
                st.markdown(f"""
                <div class="movie-card">
                    <h3>{row['title']}</h3>
                    <p>⭐ {row['rating']} | 📅 {row['created_at']}</p>
                    <p><i>“{row['review']}”</i></p>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"编辑 / 删除"):
                    new_rev = st.text_input("改评", row['review'], key=f"r_{index}")
                    try:
                        current_rating = int(row['rating'])
                    except:
                        current_rating = 3
                    new_rat = st.slider("改分", 1, 5, current_rating, key=f"s_{index}")

                    col_a, col_b = st.columns(2)
                    if col_a.button("更新", key=f"u_{index}"):
                        update_movie_in_db(index, new_rev, new_rat)
                        st.success("云端已更新")
                        time.sleep(1)
                        st.rerun()
                    if col_b.button("删除", key=f"d_{index}"):
                        delete_movie_from_db(index)
                        st.warning("云端已删除")
                        time.sleep(1)
                        st.rerun()
            st.divider()

# --- 5. 入口 ---
if not st.session_state['logged_in']:
    login_page()
else:
    main_app()
