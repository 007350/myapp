import streamlit as st
import os
from openai import OpenAI
import base64
st.set_page_config(
    page_title="ai",
    page_icon="🦄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
def get_base64_image(image_path):
    """把图片转成 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# 假设图片叫 background.jpg，和 test.py 同一目录
img_base64 = get_base64_image("R-C.jpg")

st.markdown(f"""
<style>
    .stApp {{
        background-image: url(data:image/jpg;base64,{img_base64});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* 让内容区域半透明，能看清背景 */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.75);
        border-radius: 15px;
        padding: 20px;
    }}

    /* 侧边栏半透明 */
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.8);
    }}
</style>
""", unsafe_allow_html=True)
st.title("AI 智能伴侣")
st.logo("R-C.jpg")
USER_AVATAR = "😎"      # 用户头像，你随便换
BOT_AVATAR = "🌸"       # 机器人头像，你随便换
# ========== 动态生成 system_prompt ==========
def get_system_prompt(name, nature):
    return f"""
你的名字叫 {name}。

## 你的性格特点
- {nature}
- 可以使用表情包

## 你的能力
- 可以回答各种问题
- 会讲冷笑话
- 能给建议和陪伴

## 注意事项
- 如果不知道答案，诚实地告诉用户
- 保持积极乐观的态度
- 偶尔开点有点色情玩笑

## 回复格式
- 每句话不要太长
- 适当使用表情包描述
- 偶尔撒个娇
"""

# ========== 初始化 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "name" not in st.session_state:
    st.session_state.name = "橙橙小宝"

if "nature" not in st.session_state:
    st.session_state.nature = "软萌可爱"

# ========== 侧边栏 ==========
st.sidebar.subheader("伴侣信息")

with st.sidebar:
    name = st.text_input("名字", st.session_state.name)
    if name:
        st.session_state.name = name

    nature = st.text_area("性格特点", st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# ========== 显示历史消息 ==========
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ========== 初始化 API 客户端 ==========
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# ========== 聊天输入 ==========
prompt = st.chat_input("请输入你的问题")

if prompt:
    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 动态生成 system_prompt
    system_prompt = get_system_prompt(
        st.session_state.name,
        st.session_state.nature
    )

    # 调用 API
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ],
        stream=True,
    )

    # 流式显示
    response_msg = st.chat_message("assistant").empty()  # ✅ 正确写法
    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_msg.markdown(full_response + "▌")  # ✅ 用 markdown

    response_msg.markdown(full_response)  # 最终显示（去掉光标）

    # 保存助手消息
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )