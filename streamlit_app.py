import streamlit as st
import pandas as pd
from PIL import Image
import os

st.set_page_config(page_title="车牌与摩托车管理系统", layout="wide")
st.title("🏍️ 跨州属摩托车与车牌查询系统")

IMAGE_DIR = "motor_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 初始化包含新字段（Price、Remarks）的空白表格
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Plate", "State", "Model", "Engine", "Price", "Remarks", "Image"])

# --- 侧边栏：录入新数据 ---
st.sidebar.header("➕ 录入新摩托车")
new_plate = st.sidebar.text_input("车牌号码 (Plate)").upper().strip()
new_state = st.sidebar.text_input("所属州属 (State)").strip()  # 修改为自填
new_model = st.sidebar.text_input("摩托型号 (Model)")
new_engine = st.sidebar.text_input("Engine 号码")
new_price = st.sidebar.number_input("价格 (Price - RM)", min_value=0.0, step=100.0, format="%.2f")  # 添加价格填写项
new_remarks = st.sidebar.text_area("备注信息 (Remarks)")  # 加上备注栏
new_img = st.sidebar.file_uploader("上传摩托照片", type=["jpg", "png", "jpeg"])

if st.sidebar.button("保存数据"):
    if new_plate and new_state and new_model and new_engine:  # 州属自填后也设为必填项
        # 检查车牌是否已存在
        if new_plate in st.session_state.db['Plate'].values:
            st.sidebar.error(f"车牌 {new_plate} 已存在，请勿重复录入！")
        else:
            img_path = ""
            if new_img:
                img_path = os.path.join(IMAGE_DIR, f"{new_plate}.jpg")
                with open(img_path, "wb") as f:
                    f.write(new_img.getbuffer())
            
            # 整合新数据插入表格
            new_data = {
                "Plate": new_plate, 
                "State": new_state, 
                "Model": new_model, 
                "Engine": new_engine, 
                "Price": new_price, 
                "Remarks": new_remarks, 
                "Image": img_path
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
            st.sidebar.success(f"成功录入车牌: {new_plate}")
            st.rerun()
    else:
        st.sidebar.error("请填写所有必填项（车牌、州属、型号、Engine号）！")

# --- 主界面：查询与搜索 ---
st.header("🔍 车辆与车牌检索")
search_query = st.text_input("输入车牌、型号、Engine号、州属或备注进行搜索:").strip()

df = st.session_state.db
if search_query:
    # 搜索范围扩大至包含备注栏
    filtered_df = df[
        df['Plate'].str.contains(search_query, case=False) |
        df['Model'].str.contains(search_query, case=False) |
        df['Engine'].str.contains(search_query, case=False) |
        df['State'].str.contains(search_query, case=False) |
        df['Remarks'].str.contains(search_query, case=False)
    ]
else:
    filtered_df = df

# --- 显示结果 ---
if filtered_df.empty:
    st.warning("没有找到匹配的摩托车记录。")
else:
    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1.5, 2, 1])
            with col1:
                if row['Image'] and os.path.exists(row['Image']):
                    st.image(Image.open(row['Image']), use_container_width=True)
                else:
                    st.image("https://placeholder.com", use_container_width=True)
            with col2:
                st.subheader(f"车牌: {row['Plate']} ({row['State']})")
                st.markdown(f"💰 **销售价格**: <span style='color:red; font-size:20px; font-weight:bold;'>RM {row['Price']:,.2f}</span>", unsafe_allow_html=True)
                st.text(f"🏍️ 摩托型号: {row['Model']}")
                st.text(f"⚙️ 引擎号码: {row['Engine']}")
                st.info(f"📝 备注: {row['Remarks'] if row['Remarks'] else '暂无备注'}")
            with col3:
                if st.button(f"❌ 删除记录", key=f"del_{row['Plate']}"):
                    st.session_state.db = st.session_state.db[st.session_state.db['Plate'] != row['Plate']]
                    st.success(f"车牌 {row['Plate']} 已成功删除！")
                    st.rerun()
            st.markdown("---")
