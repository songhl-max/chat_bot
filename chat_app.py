import streamlit as st
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms import Tongyi
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

# ==================== 配置区域 ====================
# ⚠️ 安全提示：生产环境请务必使用 st.secrets 或环境变量管理 API Key！
API_KEY = "sk-2b059aabca46463da457976aa219e9a9"  # <--- 修改这里！

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="Qwen 智能助手 ",
    page_icon="🦄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==================== 注入 CSS + HTML 装饰 ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

/* 全局字体 */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* 梦幻动画背景 */
.stApp {
    background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #ff9a9e, #fecfef);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 主内容区毛玻璃卡片 */
.main .block-container {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 30px;
    padding: 2.5rem 3rem;
    margin: 2rem auto;
    max-width: 850px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.5);
}

/* 标题样式 */
h1 {
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    text-align: center;
    letter-spacing: -0.5px;
}

/* ========================================== */
/* 侧边栏深色背景（核心改动 1）               */
/* ========================================== */
[data-testid="stSidebar"] > div:first-child {
    background: rgba(15, 15, 20, 0.69) !important;  /* 近黑深色背景 */
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.08);
    color: #ffffff;
}

/* 侧边栏文字统一设为浅色 */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] .stMarkdown {
    color: rgba(255, 255, 255, 0.9) !important;
}

/* 侧边栏标题白色 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* 侧边栏按钮保持紫渐变并加白字 */
[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.35) !important;
}

/* 侧边栏分割线深色模式 */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}

/* 侧边栏 st.info / alert 深色适配 */
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] [data-baseweb="notification"] {
    background: rgba(35, 35, 50, 0.8) !important;
    border: 1px solid rgba(192, 132, 252, 0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] .stAlert p,
[data-testid="stSidebar"] .stAlert span {
    color: #e0e0e0 !important;
}
/* ========================================== */

/* 聊天输入框 */
.stChatInput {
    border-radius: 25px !important;
    border: 2px solid #c084fc !important;
    background: rgba(255,255,255,0.95) !important;
    box-shadow: 0 4px 15px rgba(192, 132, 252, 0.2) !important;
}

/* 用户消息气泡（渐变紫） */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) .stMarkdown {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 20px 20px 0 20px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3) !important;
}

/* AI 消息气泡（渐变粉） */
.stChatMessage[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    color: white !important;
    border-radius: 20px 20px 20px 0 !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3) !important;
}

/* 强制消息内文字为白色 */
.stChatMessage .stMarkdown p,
.stChatMessage .stMarkdown li,
.stChatMessage .stMarkdown code {
    color: white !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.2);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.5);
    border-radius: 4px;
}

/* ===== 漂浮装饰元素（纯 CSS） ===== */
.floating-decos {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.deco {
    position: absolute;
    opacity: 0;
    animation: floatY linear infinite;
}

.deco1 { left: 5%; top: 110%; animation-duration: 8s; font-size: 20px; }
.deco2 { left: 15%; top: 110%; animation-duration: 10s; animation-delay: 1s; font-size: 16px; }
.deco3 { left: 80%; top: 110%; animation-duration: 9s; animation-delay: 2s; font-size: 24px; }
.deco4 { left: 90%; top: 110%; animation-duration: 11s; animation-delay: 0.5s; font-size: 18px; }
.deco5 { left: 40%; top: 110%; animation-duration: 7s; animation-delay: 3s; font-size: 22px; }
.deco6 { left: 70%; top: 110%; animation-duration: 12s; animation-delay: 1.5s; font-size: 15px; }
.deco7 { left: 25%; top: 110%; animation-duration: 9s; animation-delay: 2.5s; font-size: 20px; }
.deco8 { left: 60%; top: 110%; animation-duration: 8s; animation-delay: 4s; font-size: 17px; }

@keyframes floatY {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    10% { opacity: 0.8; }
    90% { opacity: 0.8; }
    100% { transform: translateY(-120vh) rotate(360deg); opacity: 0; }
}

/* 右下角浮动角色容器 */
.mascot-container {
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 999;
    pointer-events: none;
    filter: drop-shadow(0 10px 20px rgba(124, 58, 237, 0.3));
    animation: mascotFloat 3s ease-in-out infinite;
}

@keyframes mascotFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
}

/* 打字机动画光标 */
.typing-cursor::after {
    content: '|';
    animation: blink 1s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}
</style>

<!-- 漂浮装饰背景（纯 CSS 驱动，无需 JS） -->
<div class="floating-decos">
    <div class="deco deco1">✨</div>
    <div class="deco deco2">💖</div>
    <div class="deco deco3">🌟</div>
    <div class="deco deco4">💫</div>
    <div class="deco deco5">⭐</div>
    <div class="deco deco6">🌸</div>
    <div class="deco deco7">✨</div>
    <div class="deco deco8">💜</div>
</div>

<!-- 右下角可爱 mascot（纯 SVG + CSS 动画） -->
<div class="mascot-container">
    <svg width="140" height="140" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#c084fc;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#a855f7;stop-opacity:1" />
            </linearGradient>
        </defs>
        <!-- 身体 -->
        <ellipse cx="100" cy="115" rx="55" ry="48" fill="url(#bodyGrad)" opacity="0.95">
            <animate attributeName="ry" values="48;44;48" dur="3s" repeatCount="indefinite"/>
        </ellipse>
        <!-- 耳朵 -->
        <path d="M 55 75 Q 40 40 65 60" fill="#e9d5ff" stroke="#c084fc" stroke-width="3"/>
        <path d="M 145 75 Q 160 40 135 60" fill="#e9d5ff" stroke="#c084fc" stroke-width="3"/>
        <ellipse cx="55" cy="75" rx="18" ry="22" fill="#d8b4fe" transform="rotate(-15 55 75)"/>
        <ellipse cx="145" cy="75" rx="18" ry="22" fill="#d8b4fe" transform="rotate(15 145 75)"/>
        <!-- 眼睛 -->
        <circle cx="78" cy="105" r="9" fill="white"/>
        <circle cx="78" cy="105" r="5" fill="#4c1d95">
            <animate attributeName="cx" values="76;80;76" dur="5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="122" cy="105" r="9" fill="white"/>
        <circle cx="122" cy="105" r="5" fill="#4c1d95">
            <animate attributeName="cx" values="120;124;120" dur="5s" repeatCount="indefinite"/>
        </circle>
        <!-- 腮红 -->
        <ellipse cx="62" cy="120" rx="11" ry="7" fill="#f472b6" opacity="0.5"/>
        <ellipse cx="138" cy="120" rx="11" ry="7" fill="#f472b6" opacity="0.5"/>
        <!-- 嘴巴 -->
        <path d="M 88 120 Q 100 132 112 120" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
        <!-- 手 -->
        <circle cx="42" cy="135" r="13" fill="#d8b4fe"/>
        <circle cx="158" cy="135" r="13" fill="#d8b4fe"/>
        <!-- 脚 -->
        <ellipse cx="75" cy="155" rx="12" ry="8" fill="#c084fc"/>
        <ellipse cx="125" cy="155" rx="12" ry="8" fill="#c084fc"/>
        <!-- 旋转星星 -->
        <g>
            <path d="M100 35 L102 42 L109 42 L104 46 L106 53 L100 49 L94 53 L96 46 L91 42 L98 42Z" fill="#fde047">
                <animateTransform attributeName="transform" type="rotate" from="0 100 44" to="360 100 44" dur="6s" repeatCount="indefinite"/>
            </path>
        </g>
        <!-- 对话气泡 -->
        <g opacity="0.9">
            <ellipse cx="155" cy="55" rx="28" ry="18" fill="white" stroke="#e9d5ff" stroke-width="2"/>
            <circle cx="145" cy="72" r="4" fill="white" stroke="#e9d5ff" stroke-width="2"/>
            <text x="155" y="60" font-family="Arial" font-size="14" fill="#7c3aed" text-anchor="middle" font-weight="bold">Hi!</text>
        </g>
    </svg>
</div>
""", unsafe_allow_html=True)

# ==================== 模型与逻辑 ====================
@st.cache_resource
def load_model():
    """缓存模型实例，避免重复初始化"""
    return Tongyi(model="qwen-max", api_key=API_KEY)

model = load_model()
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def get_res(prompt: str) -> str:
    """
    调用阿里云大模型获取回答
    修复：使用 {input} 占位符，让 LangChain 正确注入变量
    """
    pro = ChatPromptTemplate.from_messages([
        ("system", "你是一个超级可爱、温柔又有耐心的AI助手。你能够思考后精准回答用户的问题。"),
        ("human", "{input}")  # ✅ 使用占位符，由 invoke 注入
    ])

    base_chain = pro | model

    chain = RunnableWithMessageHistory(
        runnable=base_chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    res = chain.invoke(
        {"input": prompt},
        config={"configurable": {"session_id": "user_001"}}
    )
    return res

# ==================== 界面主体 ====================

# 初始化会话状态
if "message" not in st.session_state:
    st.session_state["message"] = []
    # 欢迎消息
    st.session_state["message"].append({
        "role": "assistant",
        "content": "你好 ~ 🌸 我是你的专属 人工智能 助手 **千问**！\n\n今天有什么我可以帮你的吗？无论是问题解答、聊天陪伴还是创意灵感，我都在这里哦 ✨💖"
    })

# 精美标题
st.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0;">
    <h1 style="font-size: 2.8rem; margin-bottom: 0;">🦄 千问-Max </h1>
    <p style="color: #6b21a8; font-size: 1.15rem; margin-top: 5px; font-weight: 600;">
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# 显示历史对话
for msg in st.session_state["message"]:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 输入框
prompt = st.chat_input("💭 你有啥问题哇！...")

if prompt:
    # 1. 保存并显示用户消息
    st.session_state["message"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # 2. 获取 AI 回复
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("<span class='typing-cursor'>🤔 让我想一想哦~</span>", unsafe_allow_html=True)
        
        try:
            ai_res = get_res(prompt)
            placeholder.markdown(ai_res)
        except Exception as e:
            ai_res = f"哎呀，好像遇到了一点小状况 😢... \n\n错误信息：`{str(e)}`"
            placeholder.error(ai_res)

    # 3. 保存 AI 回复
    st.session_state["message"].append({"role": "assistant", "content": ai_res})
    st.rerun()

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding-bottom: 15px;">
        <h2 style="color: #c084fc; margin-bottom: 5px;">控制面板</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 关于卡片（深色模式下改用 st.markdown + 自定义底色，更协调）
    st.markdown("""
    <div style="background: rgba(255,255,255,0.08); 
                padding: 16px; border-radius: 12px; 
                border: 1px solid rgba(255,255,255,0.1);
                text-align: center; margin-bottom: 10px;">
        <p style="color: #e0e0e0; margin: 0; font-size: 0.95rem;">
            <b>Developed by</b><br/>
            <span style="color: #c084fc; font-size: 1.05rem;">舒海立</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 状态面板
    st.markdown("""
    <div style="background: linear-gradient(135deg, #c084fc, #a855f7); 
                padding: 18px; border-radius: 20px; color: white; 
                text-align: center; margin: 15px 0;
                box-shadow: 0 8px 20px rgba(168, 85, 247, 0.35);
                border: 2px solid rgba(255,255,255,0.3);">
        <div style="font-size: 1.3rem; margin-bottom: 5px;">🟢 在线运行中</div>
        <div style="font-size: 0.85rem; opacity: 0.9;">Model: qwen-max</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 快捷功能
    if st.button("🧹 清空对话记录", use_container_width=True, type="primary"):
        st.session_state["message"] = []
        store.clear()
        st.rerun()
    
    st.divider()
    
    # 页脚
    st.markdown("""
    <div style="text-align: center; color: #a78bfa; font-size: 0.8rem; padding-top: 10px;">
        <p>感谢使用</p>
    </div>
    """, unsafe_allow_html=True)