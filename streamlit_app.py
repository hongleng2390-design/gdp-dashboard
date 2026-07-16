import streamlit as st
import pandas as pd
from PIL import Image
import os

st.set_page_config(page_title="车牌与摩托车管理系统", layout="wide")
st.title("🏍️ 跨州属摩托车与车牌查询系统")

IMAGE_DIR = "motor_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame([
        {"Plate": "WQQ1234", "State": "WPKL", "Model": "Yamaha Y15ZR", "Engine": "E34567E", "Image": ""},
        {"Plate": "JSS8888", "State": "Johor", "Model": "Honda RSX", "Engine": "E98765H", "Image": ""}
    ])

st.sidebar.header("➕ 录入新摩托车")
new_plate = st.sidebar.text_input("车牌号码 (Plate)").upper().strip()
new_state = st.sidebar.selectbox("所属州属 (State)", ["WPKL", "Johor", "Penang", "Selangor", "Perak"])
new_model = st.sidebar.text_input("摩托型号 (Model)")
new_engine = st.sidebar.text_input("Engine 号码")
new_img = st.sidebar.file_uploader("上传摩托照片", type=["jpg", "png", "jpeg"])

if st.sidebar.button("保存数据"):
    if new_plate and new_model and new_engine:
        img_path = ""
        if new_img:
            img_path = os.path.join(IMAGE_DIR, f"{new_plate}.jpg")
            with open(img_path, "wb") as f:
                f.write(new_img.getbuffer())
        new_data = {"Plate": new_plate, "State": new_state, "Model": new_model, "Engine": new_engine, "Image": img_path}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
        st.sidebar.success(f"成功录入车牌: {new_plate}")
    else:
        st.sidebar.error("请填写所有必填项！")

st.header("🔍 车辆与车牌检索")
search_query = st.text_input("输入车牌、型号、Engine号或州属进行搜索:").strip()

df = st.session_state.db
if search_query:
    filtered_df = df[
        df['Plate'].str.contains(search_query, case=False) |
        df['Model'].str.contains(search_query, case=False) |
        df['Engine'].str.contains(search_query, case=False) |
        df['State'].str.contains(search_query, case=False)
    ]
else:
    filtered_df = df

if filtered_df.empty:
    st.warning("没有找到匹配的摩托车记录。")
else:
    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                if row['Image'] and os.path.exists(row['Image']):
                    st.image(Image.open(row['Image']), use_container_width=True)
                else:
                    st.image("https://placeholder.com", use_container_width=True)
            with col2:
                st.subheader(f"车牌: {row['Plate']} ({row['State']})")
                st.text(f"🏍️ 摩托型号: {row['Model']}")
                st.text(f"⚙️ 引擎号码: {row['Engine']}")
            st.markdown("---")
