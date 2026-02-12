"""
云端小助理 - 演示版本（截图用）
"""
import streamlit as st
from streamlit_option_menu import option_menu

# 页面配置
st.set_page_config(
    page_title="云端小助理",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("## 🤖 云端小助理")
    
    selected = option_menu(
        menu_title=None,
        options=["首页", "文档管理", "内容创作", "文档翻译", "PDF编辑", "邮件助手", "图片处理", "进度追踪", "设置"],
        icons=["house", "folder", "pencil", "translate", "file-pdf", "envelope", "image", "list-check", "gear"],
        default_index=0,
    )
    
    st.divider()
    st.success("✅ LLM已连接: openai")

# 首页
if selected == "首页":
    st.markdown('<h1 class="main-header">🤖 云端小助理</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    欢迎使用云端小助理！这是一个集成了多种AI能力的工具箱。
    
    ### 📦 功能模块
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>📁 文档管理</h4>
        <p>上传、索引、搜索文档，支持PDF、Word、TXT</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>✍️ 内容创作</h4>
        <p>基于材料+网络搜索，AI辅助写作</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>🌐 文档翻译</h4>
        <p>支持长文档翻译，多语言互译</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>📄 PDF编辑</h4>
        <p>签名、合并、拆分、水印等</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>📧 邮件助手</h4>
        <p>AI撰写邮件，收发邮件</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>🖼️ 图片处理</h4>
        <p>裁剪、换背景、格式转换等</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>📊 进度追踪</h4>
        <p>Offer申请、签证申请等进度管理</p>
        </div>
        """, unsafe_allow_html=True)

elif selected == "文档管理":
    st.header("📁 文档管理")
    
    tab1, tab2, tab3 = st.tabs(["上传文档", "搜索文档", "已索引文档"])
    
    with tab1:
        st.subheader("上传并索引文档")
        uploaded_file = st.file_uploader(
            "选择文件",
            type=['pdf', 'docx', 'txt'],
            help="支持 PDF、Word、TXT 文件"
        )
        if uploaded_file:
            st.success(f"文件已上传: {uploaded_file.name}")
            st.button("索引此文档", type="primary")
    
    with tab2:
        st.subheader("搜索文档")
        query = st.text_input("输入搜索内容", placeholder="例如：合同条款...")
        if query:
            st.info("搜索功能演示")
    
    with tab3:
        st.subheader("已索引文档")
        st.write("📄 sample.pdf - 10页")
        st.write("📄 report.docx - 5页")

elif selected == "文档翻译":
    st.header("🌐 文档翻译")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_lang = st.selectbox(
            "目标语言",
            ["中文", "英文", "日文", "韩文", "法文", "德文"]
        )
        use_llm = st.checkbox("使用AI翻译（更准确但较慢）", value=False)
    
    with col2:
        translation_mode = st.radio("翻译模式", ["文本输入", "上传文档"])
    
    source_text = st.text_area("输入要翻译的文本", height=200, value="Hello, this is a demo text for translation.")
    st.button("翻译", type="primary")

elif selected == "PDF编辑":
    st.header("📄 PDF编辑")
    
    edit_mode = st.selectbox(
        "选择操作",
        ["添加签名", "合并PDF", "拆分PDF", "添加水印", "提取页面"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.file_uploader("上传PDF", type=['pdf'])
    with col2:
        st.file_uploader("上传签名图片", type=['png', 'jpg', 'jpeg'])
    
    st.text_input("在哪个文字上方添加签名", placeholder="例如：签名处")
    st.button("添加签名", type="primary")

elif selected == "图片处理":
    st.header("🖼️ 图片处理")
    
    uploaded_image = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg', 'webp'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://via.placeholder.com/400x300?text=原图预览", caption="原图", use_container_width=True)
        st.write("尺寸: 1920 x 1080")
        st.write("大小: 256 KB")
    
    with col2:
        operation = st.selectbox(
            "选择操作",
            ["去除背景", "更换背景颜色", "调整大小", "旋转", "裁剪"]
        )
        
        if operation == "更换背景颜色":
            st.color_picker("选择背景颜色", "#FFFFFF")
        
        st.button("处理", type="primary")

elif selected == "进度追踪":
    st.header("📊 进度追踪")
    
    tab1, tab2, tab3 = st.tabs(["项目列表", "创建项目", "报表"])
    
    with tab1:
        with st.expander("📋 Google - 软件工程师 (offer申请)"):
            st.write("**状态:** active")
            st.write("**创建时间:** 2024-02-01")
            st.write("**任务列表:**")
            st.write("✅ 准备简历")
            st.write("✅ 撰写求职信")
            st.write("⏳ 投递申请")
            st.write("⬜ 等待反馈")
        
        with st.expander("📋 美国 旅游签证 (签证申请)"):
            st.write("**状态:** active")
            st.write("**任务列表:**")
            st.write("✅ 准备护照")
            st.write("⏳ 填写DS-160")
            st.write("⬜ 预约面签")
    
    with tab2:
        template = st.selectbox("选择模板", ["自定义", "Offer申请", "签证申请"])
        st.text_input("公司名称")
        st.text_input("职位")
        st.button("创建", type="primary")
    
    with tab3:
        import pandas as pd
        df = pd.DataFrame({
            "项目名称": ["Google - 软件工程师", "美国 旅游签证"],
            "类型": ["offer申请", "签证申请"],
            "总任务": [9, 9],
            "已完成": [2, 1],
            "进行中": [1, 1]
        })
        st.dataframe(df, use_container_width=True)
        st.button("📥 导出Excel")

elif selected == "设置":
    st.header("⚙️ 设置")
    
    st.subheader("大模型配置")
    st.info("当前提供商: openai")
    
    st.markdown("""
    ### 配置方法
    
    1. 复制 `.env.example` 为 `.env`
    2. 在 `.env` 中填入你的 API Key
    
    **支持的大模型提供商：**
    
    | 提供商 | 环境变量 | 获取方式 |
    |--------|----------|----------|
    | OpenAI | `OPENAI_API_KEY` | https://platform.openai.com |
    | 智谱GLM | `ZHIPU_API_KEY` | https://open.bigmodel.cn |
    | 月之暗面 | `MOONSHOT_API_KEY` | https://platform.moonshot.cn |
    | DeepSeek | `DEEPSEEK_API_KEY` | https://platform.deepseek.com |
    """)
    
    st.button("测试LLM连接")

else:
    st.header(f"{selected}")
    st.info("功能开发中...")

# 页脚
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem;">
    云端小助理 v1.0 | Made with ❤️ by 小龙虾 🦞
</div>
""", unsafe_allow_html=True)
