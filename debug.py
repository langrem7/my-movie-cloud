import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# 设置页面宽一点，方便看报错
st.set_page_config(layout="wide")

st.title("🔧 数据库连接诊断工具")

try:
    # 1. 读取配置
    st.info("正在读取 secrets.toml...")
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    st.success("✅ Secrets 读取成功")

    # 2. 尝试认证
    st.info("正在向 Google 验证身份...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
    client = gspread.authorize(creds)
    st.success("✅ 身份验证通过")

    # 3. 尝试打开表格
    st.info(f"正在尝试打开表格: {secrets_dict['spreadsheet']}")
    sheet = client.open_by_url(secrets_dict["spreadsheet"]).sheet1
    st.success("✅ 表格连接成功")

    # 4. 尝试读取数据
    st.info("正在读取第一行标题...")
    records = sheet.get_all_records()
    st.write("📊 读取到的原始数据如下：")
    st.write(records)

except Exception as e:
    st.error("❌ 发生严重错误！详情如下：")
    st.exception(e) # 这行代码会把最真实的错误打印在网页上
