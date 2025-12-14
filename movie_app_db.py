
import os
import streamlit as st
import pandas as pd
import time
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 🧠 智能网络配置 ---
if st.secrets.get("is_local"):
    PROXY_PORT = "7890"  # 请确认你的端口
    os.environ["http_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"
    os.environ["https_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"

# --- 2. 🎨 CSS & HTML 注入 (让页面动起来的核心) ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* 1. 定义霓虹灯闪烁动画 (针对电影标题) */
        @keyframes neon-flicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
                text-shadow:
                    0 0 4px #fff,
                    0 0 11px #fff,
                    0 0 19px #fff,
                    0 0 40px #0fa,
                    0 0 80px #0fa,
                    0 0 90px #0fa,
                    0 0 100px #0fa,
                    0 0 150px #0fa;
                color: #fff;
            }
            20%, 24%, 55% {
                text-shadow: none;
                color: rgba(255,255,255,0.2);
            }
        }

        /* 2. 定义星星闪烁动画 */
        @keyframes star-twinkle {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }

        /* 应用类名 */
        .neon-title {
            font-family: 'Courier New', Courier, monospace;
            animation: neon-flicker 2.5s infinite alternate;
            font-size: 1.5em;
            font-weight: bold;
        }

        .twinkle-star {
            display: inline-block;
            animation: star-twinkle 1.5s infinite ease-in-out;
            color: #FFD700; /* 金色 */
            font-size: 1.2em;
            letter-spacing: 5px;
        }

        /* 卡片玻璃拟态增强 */
        .movie-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s;
        }
        .movie-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets 连接逻辑 ---
SPREADSHEET_ID = "1wLR_VyaIIRf438hYOjSk5pOJAcAEPNBlwTgSdgCz6Hw"

def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if "connections" not in st.secrets:
        st.error("❌ 未找到 secrets.toml")
        st.stop()
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

def view_all_movies():
    sheet = get_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["title", "poster_url", "rating", "tags", "review", "created_at"])
    if 'tags' in df.columns:
        df['tags'] = df['tags'].astype(str)
    return df

def add_movie_to_db(title, poster, rating, tags, review):
    sheet = get_sheet()
    date = pd.Timestamp.now().strftime("%Y-%m-%d")
    sheet.append_row([title, poster, rating, tags, review, date])

def update_movie_in_db(index, new_review, new_rating, new_tags):
    sheet = get_sheet()
    row = index + 2
    sheet.update_cell(row, 5, new_review)
    sheet.update_cell(row, 3, new_rating)
    sheet.update_cell(row, 4, new_tags)

def delete_movie_from_db(index):
    sheet = get_sheet()
    row = index + 2
    sheet.delete_rows(row)

# --- 4. 辅助功能 ---
def get_available_tags(df):
    base_tags = ["剧情", "科幻", "动作", "喜剧", "爱情", "悬疑", "动画", "恐怖"]
    used_tags = set()
    if not df.empty and 'tags' in df.columns:
        for tag_str in df['tags']:
            for t in str(tag_str).split(','):
                if t.strip(): used_tags.add(t.strip())
    if 'custom_tags' not in st.session_state:
        st.session_state.custom_tags = []
    all_tags = list(set(base_tags) | used_tags | set(st.session_state.custom_tags))
    all_tags.sort()
    return all_tags

# --- 5. 页面配置 ---
st.set_page_config(page_title="Neon Movie DB", page_icon="🌃", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 6. 登录页 ---
def login_page():
    # 注入简单的登录页CSS
    st.markdown("""
    <style>
        header, footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        .stApp {
            background-color: #000;
            background-image: radial-gradient(circle at center, #222 0%, #000 100%);
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;color:#0fa;text-shadow:0 0 10px #0fa'>SYSTEM ACCESS</h1>", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="PASSWORD", label_visibility="collapsed")
        if st.button("LOGIN") or pwd == "123":
            if pwd == "123":
                st.session_state['logged_in'] = True
                st.rerun()

# --- 7. 主程序 ---
def main_app():
    # 注入炫酷 CSS
    inject_custom_css()

    # 强制深色背景
    st.markdown("""
    <style>
        .stApp {background-color: #050505; color: #fff;}
        [data-testid="stSidebar"] {background-color: #111; border-right: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

    df = view_all_movies()
    tags_options = get_available_tags(df)

    # === 侧边栏 ===
    with st.sidebar:
        st.caption("🟢 SYSTEM ONLINE")
        if st.button("LOGOUT"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()

        with st.expander("➕ 添加新标签"):
            new_t = st.text_input("标签名")
            if new_t and new_t not in st.session_state.custom_tags:
                st.session_state.custom_tags.append(new_t)
                st.toast("标签已缓存")

        st.header("🎬 登记影片")
        with st.form("add"):
            t = st.text_input("片名")
            p = st.text_input("海报URL")

            # 🔥 升级：使用星星反馈组件代替 Slider
            st.write("评分:")
            r = st.feedback("stars") # 返回 0-4 (对应 1-5星)

            tag = st.multiselect("类型", tags_options, default=["剧情"])
            rev = st.text_area("短评")

            if st.form_submit_button("提交数据"):
                if t:
                    final_p = p if p else "https://via.placeholder.com/300?text=No+Poster"
                    # st.feedback 返回的是 0,1,2,3,4，我们需要存成 1,2,3,4,5
                    final_r = r + 1 if r is not None else 3
                    add_movie_to_db(t, final_p, final_r, ",".join(tag), rev)
                    st.toast("✅ 数据已同步", icon="⚡")
                    time.sleep(1)
                    st.rerun()

    # === 主界面 ===
    st.title("🌃 Cyberpunk Movie Log")

    if df.empty:
        st.info("数据库为空...")
    else:
        for idx, row in df.iterrows():
            c1, c2 = st.columns([1, 4])
            with c1:
                try: st.image(row['poster_url'])
                except: st.write("No Image")
            with c2:
                # 生成动态星星字符串 (带HTML类名)
                star_count = int(row['rating'])
                # 这里我们把普通的 emoji 包裹在 span 里，应用 twinkling 动画
                stars_html = f'<span class="twinkle-star">{"★" * star_count}</span>'

                # 渲染卡片 (注意 class="neon-title")
                st.markdown(f"""
                <div class="movie-card">
                    <div class="neon-title">{row['title']}</div>
                    <div style="margin-top:5px; color:#aaa; font-size:0.8em">{row['created_at']}</div>
                    <div style="margin: 10px 0;">{stars_html}</div>
                    <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:10px; border-left: 3px solid #0fa;">
                        “{row['review']}”
                    </div>
                    <div style="margin-top:10px;">🏷️ {row['tags']}</div>
                </div>
                """, unsafe_allow_html=True)

                # 编辑区域
                with st.expander(f"🛠 编辑: {row['title']}"):
                    n_rev = st.text_area("Update Review", row['review'], key=f"rv{idx}")

                    # 编辑时也用星星组件
                    st.write("Update Rating:")
                    # 注意：feedback 接收 0-4，所以要减 1
                    current_r_index = int(row['rating']) - 1
                    n_rat_idx = st.feedback("stars", key=f"fb{idx}")

                    # 如果用户没点，保持原值；点了则更新
                    final_n_rat = n_rat_idx + 1 if n_rat_idx is not None else int(row['rating'])

                    # 标签
                    curr_tags = str(row['tags']).split(',') if row['tags'] else []
                    curr_tags = [x.strip() for x in curr_tags if x.strip() in tags_options]
                    n_tags = st.multiselect("Tags", tags_options, default=curr_tags, key=f"tg{idx}")

                    c_save, c_del = st.columns(2)
                    if c_save.button("SAVE", key=f"s{idx}"):
                        update_movie_in_db(idx, n_rev, final_n_rat, ",".join(n_tags))
                        st.rerun()
                    if c_del.button("DELETE", key=f"d{idx}"):
                        delete_movie_from_db(idx)
                        st.rerun()
            st.divider()

if not st.session_state['logged_in']:
    login_page()
else:
    main_app()
