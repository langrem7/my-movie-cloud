import os
import streamlit as st
import pandas as pd
import time
import gspread
import random
from google.oauth2.service_account import Credentials

# --- 1. 🧠 智能网络配置 ---
if st.secrets.get("is_local"):
    PROXY_PORT = "7890"  # 请确认你的端口
    os.environ["http_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"
    os.environ["https_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"

# --- 2. 🎨 CSS & HTML 注入 ---
def inject_custom_css():
    st.markdown("""
    <style>
        :root { --neon-color: #0fa; }

        /* 霓虹灯标题动画 */
        @keyframes neon-flicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
                text-shadow: 0 0 4px #fff, 0 0 10px #fff, 0 0 20px var(--neon-color), 0 0 40px var(--neon-color);
                color: #fff;
            }
            20%, 24%, 55% { text-shadow: none; color: rgba(255,255,255,0.1); }
        }

        /* 入场动画 */
        @keyframes slide-up {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .neon-title {
            font-family: 'Courier New', Courier, monospace;
            animation: neon-flicker 3s infinite alternate;
            font-size: 1.6em;
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--neon-color);
        }

        .score-badge {
            font-family: 'Impact', sans-serif;
            font-size: 2.2em;
            color: #FFD700; 
            text-shadow: 0 0 10px #FFD700;
            margin-right: 5px;
            line-height: 1em;
        }
        
        .score-suffix { color: #888; font-size: 0.9em; }

        .movie-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
            /* 应用入场动画 */
            animation: slide-up 0.6s ease-out;
        }
        .movie-card:hover {
            transform: translateY(-3px) scale(1.01);
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        
        /* 针对输入框的美化 */
        input[type="number"] {
            font-weight: bold;
            color: #0fa;
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
    inject_custom_css()
    
    st.markdown("""
    <style>
        .stApp {background-color: #050505; color: #fff;}
        [data-testid="stSidebar"] {background-color: #111; border-right: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

    df = view_all_movies()
    tags_options = get_available_tags(df)
    NEON_PALETTE = ["#0fa", "#f0f", "#0ff", "#ff0055", "#ccff00", "#bd00ff", "#00ccff"]

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
            
            # 🔥 更改点：使用 number_input 输入框
            # min_value=0.0, max_value=10.0 限制范围
            r = st.number_input("评分 (0-10)", min_value=0.0, max_value=10.0, value=8.5, step=0.1)
            
            tag = st.multiselect("类型", tags_options, default=["剧情"])
            rev = st.text_area("短评")
            
            if st.form_submit_button("提交数据"):
                if t:
                    final_p = p if p else "https://via.placeholder.com/300?text=No+Poster"
                    add_movie_to_db(t, final_p, r, ",".join(tag), rev)
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
                random.seed(idx) 
                this_neon_color = random.choice(NEON_PALETTE)
                try: score = float(row['rating'])
                except: score = 0.0
                
                # 🔥 关键修复点：unsafe_allow_html=True
                # 如果这个参数没设为True，你看到的就是代码
                st.markdown(f"""
                <div class="movie-card">
                    <div class="neon-title" style="--neon-color: {this_neon_color};">
                        {row['title']}
                    </div>
                    
                    <div style="display: flex; align-items: baseline; margin: 10px 0;">
                        <span class="score-badge">{score}</span>
                        <span class="score-suffix">/ 10</span>
                    </div>

                    <div style="color:#aaa; font-size:0.8em; margin-bottom: 8px;">
                        📅 {row['created_at']} | 🏷️ {row['tags']}
                    </div>

                    <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:10px; border-left: 3px solid {this_neon_color}; color: #ddd;">
                        “{row['review']}”
                    </div>
                </div>
                """, unsafe_allow_html=True) # <--- 这里必须是 True
                
                # 编辑区域
                with st.expander(f"🛠 编辑: {row['title']}"):
                    n_rev = st.text_area("Update Review", row['review'], key=f"rv{idx}")
                    
                    # 编辑区域也改为输入框
                    n_rat = st.number_input("Update Score", 0.0, 10.0, score, step=0.1, key=f"sl{idx}")
                    
                    curr_tags = str(row['tags']).split(',') if row['tags'] else []
                    curr_tags = [x.strip() for x in curr_tags if x.strip() in tags_options]
                    n_tags = st.multiselect("Tags", tags_options, default=curr_tags, key=f"tg{idx}")
                    
                    c_save, c_del = st.columns(2)
                    if c_save.button("SAVE", key=f"s{idx}"):
                        update_movie_in_db(idx, n_rev, n_rat, ",".join(n_tags))
                        st.rerun()
                    if c_del.button("DELETE", key=f"d{idx}", type="primary"):
                        delete_
