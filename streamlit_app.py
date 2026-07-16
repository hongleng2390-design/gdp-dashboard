import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import os

st.set_page_config(page_title="车牌与摩托车管理系统", layout="wide")
st.title("🏍️ 跨州属摩托车与车牌查询系统 (谷歌完美同步版)")

IMAGE_DIR = "motor_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 1. 建立与 Google Sheets 的真实永久连接
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 读取谷歌表格中已有的数据
    df_existing = conn.read(worksheet="Sheet1", ttl="0d")
    df_existing.columns = df_existing.columns.str.strip()
except Exception as e:
    st.error("⚠️ 未能成功连接到云端数据库，请确保 Secrets 配置正确。")
    df_existing = pd.DataFrame(columns=["Plate", "State", "Model", "Engine", "Price", "Remarks", "Image"])

# 确保字段齐全
for col in ["Plate", "State", "Model", "Engine", "Price", "Remarks", "Image"]:
    if col not in df_existing.columns:
        df_existing[col] = None

# --- 侧边栏：录入新数据 ---
st.sidebar.header("➕ 录入新摩托车")
new_plate = st.sidebar.text_input("车牌号码 (Plate)").upper().strip()
new_state = st.sidebar.text_input("所属州属 (State)").strip()
new_model = st.sidebar.text_input("摩托型号 (Model)")
new_engine = st.sidebar.text_input("Engine 号码")
new_price = st.sidebar.number_input("价格 (Price - RM)", min_value=0.0, step=100.0, format="%.2f")
new_remarks = st.sidebar.text_area("备注信息 (Remarks)")
new_img = st.sidebar.file_uploader("上传摩托照片", type=["jpg", "png", "jpeg"])

if st.sidebar.button("保存数据"):
    if new_plate and new_state and new_model and new_engine:
        # 查重
        if not df_existing.empty and new_plate in df_existing['Plate'].dropna().values:
            st.sidebar.error(f"车牌 {new_plate} 已存在，请勿重复录入！")
        else:
            img_path = ""
            if new_img:
                img_path = os.path.join(IMAGE_DIR, f"{new_plate}.jpg")
                with open(img_path, "wb") as f:
                    f.write(new_img.getbuffer())
            
            new_row = pd.DataFrame([{
                "Plate": new_plate, 
                "State": new_state, 
                "Model": new_model, 
                "Engine": new_engine, 
                "Price": new_price, 
                "Remarks": new_remarks, 
                "Image": img_path
            }])
            
            # 合并数据并更新到 Google Sheets
            df_updated = pd.concat([df_existing.dropna(how='all'), new_row], ignore_index=True)
            try:
                conn.update(worksheet="Sheet1", data=df_updated)
                st.sidebar.success(f"成功录入并永久同步车牌: {new_plate}")
                st.rerun()
            except Exception as e:
                st.sidebar.error("保存失败，请检查 Secrets 后台是否成功锁定密码。")
    else:
        st.sidebar.error("请填写所有必填项（车牌、州属、型号、Engine号）！")

# --- 主界面：查询与搜索 ---
st.header("🔍 车辆与车牌检索")
search_query = st.text_input("输入车牌、型号、Engine号、州属或备注进行搜索:").strip()

df_clean = df_existing.dropna(subset=['Plate']) if not df_existing.empty else df_existing

if search_query and not df_clean.empty:
    filtered_df = df_clean[
        df_clean['Plate'].astype(str).str.contains(search_query, case=False) |
        df_clean['Model'].astype(str).str.contains(search_query, case=False) |
        df_clean['Engine'].astype(str).str.contains(search_query, case=False) |
        df_clean['State'].astype(str).str.contains(search_query, case=False) |
        df_clean['Remarks'].astype(str).str.contains(search_query, case=False)
    ]
else:
    filtered_df = df_clean

# --- 显示结果 ---
if filtered_df.empty:
    st.warning("没有找到匹配的摩托车记录。")
else:
    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1.5, 2, 1])
            with col1:
                if pd.notna(row['Image']) and row['Image'] and os.path.exists(str(row['Image'])):
                    st.image(Image.open(str(row['Image'])), use_container_width=True)
                else:
                    st.image("https://placeholder.com", use_container_width=True)
            with col2:
                st.subheader(f"车牌: {row['Plate']} ({row['State']})")
                price_val = float(row['Price']) if pd.notna(row['Price']) else 0.0
                st.markdown(f"💰 **销售价格**: <span style='color:red; font-size:20px; font-weight:bold;'>RM {price_val:,.2f}</span>", unsafe_allow_html=True)
                st.text(f"🏍️ 摩托型号: {row['Model']}")
                st.text(f"⚙️ 引擎号码: {row['Engine']}")
                st.info(f"📝 备注: {row['Remarks'] if pd.notna(row['Remarks']) and row['Remarks'] else '暂无备注'}")
            with col3:
                if st.button(f"❌ 删除记录", key=f"del_{row['Plate']}"):
                    df_after_del = df_existing[df_existing['Plate'] != row['Plate']]
                    try:
                        conn.update(worksheet="Sheet1", data=df_after_del)
                        st.success(f"车牌 {row['Plate']} 已从云端彻底删除！")
                        st.rerun()
                    except Exception as e:
                        st.error("删除失败，请检查密码箱权限。")
            st.markdown("---")
