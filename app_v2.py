"""
云端小助理 - Streamlit 完整版 v2
启动方式: streamlit run app_v2.py
"""
import streamlit as st
from streamlit_option_menu import option_menu
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    get_config,
    LLMClient, test_llm_connection,
    DocumentProcessor, PDFEditor,
    DocumentTranslator,
    EmailClient, compose_email_with_llm,
    ImageProcessor,
    ProgressTracker, create_offer_application, create_visa_application,
    WebSearcher
)

# 页面配置
st.set_page_config(page_title="云端小助理", page_icon="🤖", layout="wide")

# CSS
st.markdown("""
<style>
.main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; }
.feature-card { background: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

config = get_config()

def get_llm():
    if not config.is_llm_configured():
        return None
    try:
        return LLMClient.from_config(config.get_llm_config())
    except:
        return None

@st.cache_resource
def init_services():
    return {
        'doc_processor': DocumentProcessor("./uploads"),
        'pdf_editor': PDFEditor(),
        'translator': DocumentTranslator(),
        'image_processor': ImageProcessor("./uploads"),
        'progress_tracker': ProgressTracker("./data/progress.db"),
        'web_searcher': WebSearcher()
    }

services = init_services()

# 侧边栏
with st.sidebar:
    st.markdown("## 🤖 云端小助理")
    selected = option_menu(None, 
        ["首页", "文档管理", "内容创作", "文档翻译", "PDF编辑", "邮件助手", "图片处理", "进度追踪", "设置"],
        icons=["house", "folder", "pencil", "translate", "file-pdf", "envelope", "image", "list-check", "gear"])
    st.divider()
    if config.is_llm_configured():
        st.success(f"✅ LLM: {config.get('llm', 'provider')}")
    else:
        st.warning("⚠️ 请配置LLM")

# ===== 设置页面 =====
if selected == "设置":
    st.header("⚙️ 设置")
    
    tab1, tab2 = st.tabs(["🤖 大模型配置", "📧 邮箱配置"])
    
    with tab1:
        st.subheader("大模型API配置")
        st.info("配置后会自动保存到本地，无需每次输入")
        
        llm_config = config.get_section("llm")
        
        provider = st.selectbox("选择提供商", 
            ["openai", "zhipu", "moonshot", "deepseek"],
            index=["openai", "zhipu", "moonshot", "deepseek"].index(llm_config.get("provider", "openai")))
        
        st.markdown("---")
        
        if provider == "openai":
            st.markdown("**OpenAI / GPT**")
            api_key = st.text_input("API Key", value=llm_config.get("openai_api_key", ""), type="password")
            base_url = st.text_input("Base URL", value=llm_config.get("openai_base_url", "https://api.openai.com/v1"))
            model = st.text_input("模型", value=llm_config.get("openai_model", "gpt-4o-mini"))
            
            if st.button("保存OpenAI配置", type="primary"):
                config.set("llm", "provider", "openai")
                config.set("llm", "openai_api_key", api_key)
                config.set("llm", "openai_base_url", base_url)
                config.set("llm", "openai_model", model)
                config.save()
                st.success("✅ 配置已保存")
                st.rerun()
        
        elif provider == "zhipu":
            st.markdown("**智谱GLM**")
            st.markdown("申请地址: https://open.bigmodel.cn")
            api_key = st.text_input("API Key", value=llm_config.get("zhipu_api_key", ""), type="password")
            model = st.selectbox("模型", ["glm-4-flash", "glm-4", "glm-4-plus"], 
                index=["glm-4-flash", "glm-4", "glm-4-plus"].index(llm_config.get("zhipu_model", "glm-4-flash")) if llm_config.get("zhipu_model") in ["glm-4-flash", "glm-4", "glm-4-plus"] else 0)
            
            if st.button("保存智谱配置", type="primary"):
                config.set("llm", "provider", "zhipu")
                config.set("llm", "zhipu_api_key", api_key)
                config.set("llm", "zhipu_model", model)
                config.save()
                st.success("✅ 配置已保存")
                st.rerun()
        
        elif provider == "moonshot":
            st.markdown("**月之暗面 Kimi**")
            st.markdown("申请地址: https://platform.moonshot.cn")
            api_key = st.text_input("API Key", value=llm_config.get("moonshot_api_key", ""), type="password")
            model = st.selectbox("模型", ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
                index=0)
            
            if st.button("保存Kimi配置", type="primary"):
                config.set("llm", "provider", "moonshot")
                config.set("llm", "moonshot_api_key", api_key)
                config.set("llm", "moonshot_model", model)
                config.save()
                st.success("✅ 配置已保存")
                st.rerun()
        
        elif provider == "deepseek":
            st.markdown("**DeepSeek**")
            st.markdown("申请地址: https://platform.deepseek.com")
            api_key = st.text_input("API Key", value=llm_config.get("deepseek_api_key", ""), type="password")
            model = st.text_input("模型", value=llm_config.get("deepseek_model", "deepseek-chat"))
            
            if st.button("保存DeepSeek配置", type="primary"):
                config.set("llm", "provider", "deepseek")
                config.set("llm", "deepseek_api_key", api_key)
                config.set("llm", "deepseek_model", model)
                config.save()
                st.success("✅ 配置已保存")
                st.rerun()
        
        st.markdown("---")
        if st.button("🔍 测试连接"):
            llm_cfg = config.get_llm_config()
            if not llm_cfg.get("api_key"):
                st.error("请先配置API Key")
            else:
                with st.spinner("测试中..."):
                    success, msg = test_llm_connection(llm_cfg["api_key"], llm_cfg["base_url"], llm_cfg["model"])
                if success:
                    st.success(f"✅ 连接成功！响应: {msg}")
                else:
                    st.error(f"❌ 连接失败: {msg}")
    
    with tab2:
        st.subheader("邮箱配置")
        email_config = config.get_section("email")
        
        preset = st.selectbox("预设", ["自定义", "Gmail", "QQ邮箱", "163邮箱", "Outlook"])
        
        if preset == "Gmail":
            smtp_host, smtp_port = "smtp.gmail.com", 587
            imap_host, imap_port = "imap.gmail.com", 993
            st.info("Gmail需要使用应用专用密码")
        elif preset == "QQ邮箱":
            smtp_host, smtp_port = "smtp.qq.com", 587
            imap_host, imap_port = "imap.qq.com", 993
            st.info("QQ邮箱需要使用授权码")
        elif preset == "163邮箱":
            smtp_host, smtp_port = "smtp.163.com", 465
            imap_host, imap_port = "imap.163.com", 993
        elif preset == "Outlook":
            smtp_host, smtp_port = "smtp.office365.com", 587
            imap_host, imap_port = "outlook.office365.com", 993
        else:
            smtp_host = email_config.get("smtp_host", "smtp.gmail.com")
            smtp_port = email_config.get("smtp_port", 587)
            imap_host = email_config.get("imap_host", "imap.gmail.com")
            imap_port = email_config.get("imap_port", 993)
        
        col1, col2 = st.columns(2)
        with col1:
            smtp_host = st.text_input("SMTP服务器", value=smtp_host)
            smtp_port = st.number_input("SMTP端口", value=smtp_port)
        with col2:
            imap_host = st.text_input("IMAP服务器", value=imap_host)
            imap_port = st.number_input("IMAP端口", value=imap_port)
        
        address = st.text_input("邮箱地址", value=email_config.get("address", ""))
        password = st.text_input("密码/授权码", value=email_config.get("password", ""), type="password")
        
        if st.button("保存邮箱配置", type="primary"):
            config.set("email", "smtp_host", smtp_host)
            config.set("email", "smtp_port", int(smtp_port))
            config.set("email", "imap_host", imap_host)
            config.set("email", "imap_port", int(imap_port))
            config.set("email", "address", address)
            config.set("email", "password", password)
            config.save()
            st.success("✅ 邮箱配置已保存")

# ===== 首页 =====
elif selected == "首页":
    st.markdown('<h1 class="main-header">🤖 云端小助理</h1>', unsafe_allow_html=True)
    st.markdown("欢迎使用云端小助理！集成多种AI能力的工具箱。")
    
    if not config.is_llm_configured():
        st.warning("👉 首次使用？请先前往 **设置** 配置大模型API Key")
    
    col1, col2 = st.columns(2)
    features = [
        ("📁 文档管理", "上传、搜索、总结文档"),
        ("✍️ 内容创作", "AI辅助写作"),
        ("🌐 文档翻译", "多语言长文档翻译"),
        ("📄 PDF编辑", "签名、合并、拆分"),
        ("📧 邮件助手", "AI写邮件、收发邮件"),
        ("🖼️ 图片处理", "去背景、裁剪"),
        ("📊 进度追踪", "Offer/签证申请管理"),
    ]
    for i, (title, desc) in enumerate(features):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f'<div class="feature-card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ===== 邮件助手 =====
elif selected == "邮件助手":
    st.header("📧 邮件助手")
    tab1, tab2, tab3 = st.tabs(["AI写邮件", "发送邮件", "收件箱"])
    
    with tab1:
        if not config.is_llm_configured():
            st.warning("请先配置大模型")
        else:
            purpose = st.text_input("邮件目的", placeholder="请假申请、会议邀请...")
            context = st.text_area("背景信息", height=100)
            tone = st.selectbox("语气", ["正式", "友好", "简洁"])
            
            if st.button("生成邮件", type="primary") and purpose:
                llm = get_llm()
                if llm:
                    with st.spinner("生成中..."):
                        try:
                            result = compose_email_with_llm(llm, purpose, context, tone)
                            st.text_input("主题", value=result.get('subject', ''))
                            st.text_area("正文", value=result.get('body', ''), height=200)
                        except Exception as e:
                            st.error(f"生成失败: {e}")
    
    with tab2:
        if not config.is_email_configured():
            st.warning("请先在设置中配置邮箱")
        else:
            to = st.text_input("收件人")
            subject = st.text_input("主题")
            body = st.text_area("正文", height=200)
            
            if st.button("发送", type="primary"):
                if all([to, subject, body]):
                    email_cfg = config.get_email_config()
                    try:
                        client = EmailClient()
                        client.smtp_host = email_cfg["smtp_host"]
                        client.smtp_port = email_cfg["smtp_port"]
                        client.email_address = email_cfg["address"]
                        client.email_password = email_cfg["password"]
                        result = client.send_email(to, subject, body)
                        if result.get("status") == "success":
                            st.success("✅ 发送成功")
                        else:
                            st.error(f"发送失败: {result.get('error')}")
                    except Exception as e:
                        st.error(f"发送失败: {e}")
                else:
                    st.error("请填写完整")
    
    with tab3:
        if not config.is_email_configured():
            st.warning("请先配置邮箱")
        else:
            if st.button("刷新收件箱"):
                email_cfg = config.get_email_config()
                try:
                    client = EmailClient()
                    client.imap_host = email_cfg["imap_host"]
                    client.imap_port = email_cfg["imap_port"]
                    client.email_address = email_cfg["address"]
                    client.email_password = email_cfg["password"]
                    emails = client.fetch_emails(limit=10)
                    for m in emails:
                        if "error" not in m:
                            with st.expander(f"📩 {m.get('subject', '无主题')[:50]}"):
                                st.write(f"**发件人:** {m.get('from', '')}")
                                st.write(f"**日期:** {m.get('date', '')}")
                                st.write(m.get('preview', ''))
                except Exception as e:
                    st.error(f"获取失败: {e}")

# ===== 其他页面简化处理 =====
elif selected == "文档管理":
    st.header("📁 文档管理")
    uploaded = st.file_uploader("上传文档", type=['pdf', 'docx', 'txt'])
    if uploaded:
        path = Path("./uploads") / uploaded.name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(uploaded.getvalue())
        st.success(f"已上传: {uploaded.name}")
        pages = services['doc_processor'].extract_text(str(path))
        st.info(f"共 {len(pages)} 页")
        with st.expander("预览"):
            for p in pages[:3]:
                st.text(p['content'][:500])

elif selected == "内容创作":
    st.header("✍️ 内容创作")
    if not config.is_llm_configured():
        st.warning("请先配置大模型")
    else:
        topic = st.text_input("主题")
        req = st.text_area("要求")
        if st.button("创作", type="primary") and topic:
            llm = get_llm()
            if llm:
                with st.spinner("创作中..."):
                    result = llm.simple_chat(f"请写一篇关于"{topic}"的内容。要求：{req}")
                    st.markdown(result)
                    st.download_button("下载", result, f"{topic}.txt")

elif selected == "文档翻译":
    st.header("🌐 文档翻译")
    target = st.selectbox("目标语言", ["中文", "英文", "日文"])
    text = st.text_area("输入文本", height=200)
    if st.button("翻译") and text:
        with st.spinner("翻译中..."):
            result = services['translator'].translate_text(text, target)
            st.text_area("结果", result, height=200)

elif selected == "PDF编辑":
    st.header("📄 PDF编辑")
    mode = st.selectbox("操作", ["添加签名", "合并PDF", "添加水印"])
    if mode == "添加签名":
        pdf = st.file_uploader("PDF", type=['pdf'])
        sig = st.file_uploader("签名图片", type=['png', 'jpg'])
        text = st.text_input("签名位置文字")
        if pdf and sig and text and st.button("添加"):
            p1 = Path("./uploads")/pdf.name; p1.parent.mkdir(exist_ok=True); p1.write_bytes(pdf.getvalue())
            p2 = Path("./uploads")/sig.name; p2.write_bytes(sig.getvalue())
            out = services['pdf_editor'].add_signature(str(p1), str(p2), text)
            st.download_button("下载", open(out,'rb').read(), "signed.pdf")

elif selected == "图片处理":
    st.header("🖼️ 图片处理")
    img = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg'])
    if img:
        path = Path("./uploads")/img.name; path.parent.mkdir(exist_ok=True); path.write_bytes(img.getvalue())
        st.image(str(path), width=400)
        op = st.selectbox("操作", ["去背景", "调整大小", "旋转"])
        if op == "去背景" and st.button("处理"):
            try:
                out = services['image_processor'].remove_background(str(path))
                st.image(out)
                st.download_button("下载", open(out,'rb').read(), "nobg.png")
            except Exception as e:
                st.error(f"需要安装rembg: {e}")

elif selected == "进度追踪":
    st.header("📊 进度追踪")
    tracker = services['progress_tracker']
    tab1, tab2 = st.tabs(["项目列表", "新建项目"])
    with tab1:
        for p in tracker.get_projects():
            with st.expander(f"{p['name']} ({p['type']})"):
                st.write(f"状态: {p['status']}")
                detail = tracker.get_project(p['id'])
                for t in detail.get('tasks', []):
                    icon = "✅" if t['status']=='completed' else "⏳"
                    st.write(f"{icon} {t['name']}")
    with tab2:
        tpl = st.selectbox("模板", ["Offer申请", "签证申请", "自定义"])
        if tpl == "Offer申请":
            co = st.text_input("公司"); pos = st.text_input("职位")
            if st.button("创建") and co:
                create_offer_application(tracker, co, pos)
                st.success("创建成功"); st.rerun()
        elif tpl == "签证申请":
            country = st.text_input("国家"); vtype = st.selectbox("类型", ["旅游", "商务", "学生"])
            if st.button("创建") and country:
                create_visa_application(tracker, vtype, country)
                st.success("创建成功"); st.rerun()

st.divider()
st.markdown('<div style="text-align:center;color:#888;">云端小助理 v2.0 | Made with ❤️</div>', unsafe_allow_html=True)
