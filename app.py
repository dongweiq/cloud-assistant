"""
云端小助理 - Streamlit 图形界面
启动方式: streamlit run app.py
"""
import streamlit as st
from streamlit_option_menu import option_menu
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    get_llm, LLMClient,
    DocumentProcessor, PDFEditor, DocumentIndex,
    DocumentTranslator,
    EmailClient, compose_email_with_llm,
    ImageProcessor,
    ProgressTracker, create_offer_application, create_visa_application,
    WebSearcher, search_and_summarize
)

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


# ===== 初始化 =====

@st.cache_resource
def init_services():
    """初始化服务（缓存）"""
    services = {}
    
    # 检查LLM配置
    try:
        services['llm'] = get_llm()
        services['llm_available'] = True
    except:
        services['llm'] = None
        services['llm_available'] = False
    
    # 其他服务
    services['doc_processor'] = DocumentProcessor("./uploads")
    services['pdf_editor'] = PDFEditor()
    services['doc_index'] = DocumentIndex("./data/chroma")
    services['translator'] = DocumentTranslator()
    services['image_processor'] = ImageProcessor("./uploads")
    services['progress_tracker'] = ProgressTracker("./data/progress.db")
    services['web_searcher'] = WebSearcher()
    
    return services

services = init_services()


# ===== 侧边栏 =====

with st.sidebar:
    st.markdown("## 🤖 云端小助理")
    
    selected = option_menu(
        menu_title=None,
        options=["首页", "文档管理", "内容创作", "文档翻译", "PDF编辑", "邮件助手", "图片处理", "进度追踪", "设置"],
        icons=["house", "folder", "pencil", "translate", "file-pdf", "envelope", "image", "list-check", "gear"],
        default_index=0,
    )
    
    st.divider()
    
    # LLM状态
    if services['llm_available']:
        st.success(f"✅ LLM已连接: {os.getenv('LLM_PROVIDER', 'openai')}")
    else:
        st.error("❌ LLM未配置，请在设置中配置API Key")


# ===== 首页 =====

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


# ===== 文档管理 =====

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
            # 保存文件
            save_path = Path("./uploads") / uploaded_file.name
            save_path.parent.mkdir(exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            st.success(f"文件已上传: {uploaded_file.name}")
            
            if st.button("索引此文档", type="primary"):
                with st.spinner("正在索引..."):
                    result = services['doc_index'].add_document(str(save_path))
                    
                if result['status'] == 'success':
                    st.success(f"✅ 索引成功！共 {result['pages']} 页")
                elif result['status'] == 'already_indexed':
                    st.info(f"ℹ️ 文档已索引过")
                else:
                    st.error(f"❌ 索引失败")
    
    with tab2:
        st.subheader("搜索文档")
        
        query = st.text_input("输入搜索内容", placeholder="例如：合同条款...")
        
        if query:
            with st.spinner("搜索中..."):
                results = services['doc_index'].search(query, top_k=5)
            
            if results:
                for i, r in enumerate(results, 1):
                    with st.expander(f"🔍 {r['file']} - 第{r['page']}页 (相似度: {r['score']:.2f})"):
                        st.text(r['content'])
            else:
                st.info("未找到相关内容")
    
    with tab3:
        st.subheader("已索引文档")
        
        files = services['doc_index'].get_all_files()
        
        if files:
            for f in files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {f['file']}")
                with col2:
                    st.write(f"{f['pages']} 页")
                with col3:
                    if st.button("删除", key=f"del_{f['hash']}"):
                        services['doc_index'].remove_document(f['hash'])
                        st.rerun()
        else:
            st.info("暂无已索引的文档")


# ===== 内容创作 =====

elif selected == "内容创作":
    st.header("✍️ 内容创作")
    
    if not services['llm_available']:
        st.error("❌ 请先在设置中配置LLM API Key")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("参考材料")
            
            # 上传参考文档
            ref_file = st.file_uploader("上传参考文档（可选）", type=['pdf', 'docx', 'txt'])
            ref_content = ""
            
            if ref_file:
                save_path = Path("./uploads") / ref_file.name
                with open(save_path, 'wb') as f:
                    f.write(ref_file.getvalue())
                
                pages = services['doc_processor'].extract_text(str(save_path))
                ref_content = "\n\n".join([p['content'] for p in pages[:10]])
                st.success(f"已加载参考材料: {ref_file.name}")
            
            # 网络搜索
            search_query = st.text_input("网络搜索（可选）", placeholder="输入关键词进行网络搜索")
            search_results = ""
            
            if search_query and st.button("搜索"):
                with st.spinner("搜索中..."):
                    results = services['web_searcher'].search(search_query)
                    search_results = "\n\n".join([
                        f"【{r['title']}】\n{r['body']}"
                        for r in results if 'error' not in r
                    ])
                    st.text_area("搜索结果", search_results, height=200)
        
        with col2:
            st.subheader("创作要求")
            
            writing_type = st.selectbox("文档类型", ["报告", "文章", "总结", "方案", "其他"])
            topic = st.text_input("主题/标题")
            requirements = st.text_area("具体要求", placeholder="请描述你希望生成的内容...")
            
            if st.button("🚀 开始创作", type="primary"):
                if not topic:
                    st.error("请输入主题")
                else:
                    prompt = f"""请撰写一篇{writing_type}。

主题：{topic}

要求：
{requirements}

"""
                    if ref_content:
                        prompt += f"""
参考材料：
{ref_content[:8000]}

"""
                    if search_results:
                        prompt += f"""
网络搜索结果：
{search_results[:4000]}

"""
                    
                    prompt += "请基于以上信息，撰写完整的内容："
                    
                    with st.spinner("AI正在创作..."):
                        result = services['llm'].simple_chat(prompt)
                    
                    st.subheader("📝 生成结果")
                    st.markdown(result)
                    
                    # 下载按钮
                    st.download_button(
                        "📥 下载为TXT",
                        result,
                        file_name=f"{topic}.txt",
                        mime="text/plain"
                    )


# ===== 文档翻译 =====

elif selected == "文档翻译":
    st.header("🌐 文档翻译")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_lang = st.selectbox(
            "目标语言",
            ["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"]
        )
        
        use_llm = st.checkbox("使用AI翻译（更准确但较慢）", value=False)
    
    with col2:
        translation_mode = st.radio("翻译模式", ["文本输入", "上传文档"])
    
    if translation_mode == "文本输入":
        source_text = st.text_area("输入要翻译的文本", height=200)
        
        if st.button("翻译", type="primary") and source_text:
            translator = DocumentTranslator(
                use_llm=use_llm and services['llm_available'],
                llm_client=services['llm'] if use_llm else None
            )
            
            with st.spinner("翻译中..."):
                result = translator.translate_text(source_text, target_lang)
            
            st.subheader("翻译结果")
            st.text_area("", result, height=200)
    
    else:
        uploaded_file = st.file_uploader("上传文档", type=['pdf', 'docx', 'txt'])
        
        if uploaded_file:
            save_path = Path("./uploads") / uploaded_file.name
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            if st.button("翻译文档", type="primary"):
                # 提取文本
                pages = services['doc_processor'].extract_text(str(save_path))
                full_text = "\n\n".join([f"[第{p['page']}页]\n{p['content']}" for p in pages])
                
                st.info(f"文档共 {len(pages)} 页，开始翻译...")
                
                translator = DocumentTranslator(
                    use_llm=use_llm and services['llm_available'],
                    llm_client=services['llm'] if use_llm else None
                )
                
                progress_bar = st.progress(0)
                
                def update_progress(current, total):
                    progress_bar.progress(current / total)
                
                result = translator.translate_document(
                    full_text, 
                    target_lang,
                    progress_callback=update_progress
                )
                
                st.success("翻译完成！")
                st.text_area("翻译结果", result, height=400)
                
                st.download_button(
                    "📥 下载翻译结果",
                    result,
                    file_name=f"{uploaded_file.name}_translated.txt",
                    mime="text/plain"
                )


# ===== PDF编辑 =====

elif selected == "PDF编辑":
    st.header("📄 PDF编辑")
    
    edit_mode = st.selectbox(
        "选择操作",
        ["添加签名", "合并PDF", "拆分PDF", "添加水印", "提取页面"]
    )
    
    if edit_mode == "添加签名":
        col1, col2 = st.columns(2)
        
        with col1:
            pdf_file = st.file_uploader("上传PDF", type=['pdf'])
        
        with col2:
            sig_file = st.file_uploader("上传签名图片", type=['png', 'jpg', 'jpeg'])
        
        target_text = st.text_input("在哪个文字上方添加签名", placeholder="例如：签名处")
        
        if pdf_file and sig_file and target_text:
            if st.button("添加签名", type="primary"):
                # 保存文件
                pdf_path = Path("./uploads") / pdf_file.name
                sig_path = Path("./uploads") / sig_file.name
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_file.getvalue())
                with open(sig_path, 'wb') as f:
                    f.write(sig_file.getvalue())
                
                with st.spinner("添加签名中..."):
                    output_path = services['pdf_editor'].add_signature(
                        str(pdf_path), str(sig_path), target_text
                    )
                
                st.success("签名添加成功！")
                
                with open(output_path, 'rb') as f:
                    st.download_button(
                        "📥 下载签名后的PDF",
                        f.read(),
                        file_name=Path(output_path).name,
                        mime="application/pdf"
                    )
    
    elif edit_mode == "合并PDF":
        uploaded_files = st.file_uploader(
            "上传多个PDF文件",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if uploaded_files and len(uploaded_files) > 1:
            if st.button("合并", type="primary"):
                pdf_paths = []
                for f in uploaded_files:
                    path = Path("./uploads") / f.name
                    with open(path, 'wb') as out:
                        out.write(f.getvalue())
                    pdf_paths.append(str(path))
                
                output_path = "./uploads/merged.pdf"
                services['pdf_editor'].merge_pdfs(pdf_paths, output_path)
                
                st.success("合并成功！")
                with open(output_path, 'rb') as f:
                    st.download_button(
                        "📥 下载合并后的PDF",
                        f.read(),
                        file_name="merged.pdf",
                        mime="application/pdf"
                    )
    
    elif edit_mode == "添加水印":
        pdf_file = st.file_uploader("上传PDF", type=['pdf'])
        watermark_text = st.text_input("水印文字", placeholder="例如：机密")
        
        if pdf_file and watermark_text:
            if st.button("添加水印", type="primary"):
                pdf_path = Path("./uploads") / pdf_file.name
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_file.getvalue())
                
                output_path = services['pdf_editor'].add_watermark(
                    str(pdf_path), watermark_text
                )
                
                st.success("水印添加成功！")
                with open(output_path, 'rb') as f:
                    st.download_button(
                        "📥 下载",
                        f.read(),
                        file_name=Path(output_path).name,
                        mime="application/pdf"
                    )


# ===== 邮件助手 =====

elif selected == "邮件助手":
    st.header("📧 邮件助手")
    
    tab1, tab2 = st.tabs(["写邮件", "收件箱"])
    
    with tab1:
        st.subheader("AI辅助写邮件")
        
        if services['llm_available']:
            purpose = st.text_input("邮件目的", placeholder="例如：请假申请")
            context = st.text_area("背景信息", placeholder="提供一些背景信息...")
            tone = st.selectbox("语气", ["正式", "友好", "简洁"])
            
            if st.button("🤖 AI生成邮件"):
                with st.spinner("生成中..."):
                    result = compose_email_with_llm(
                        services['llm'], purpose, context, tone
                    )
                
                st.text_input("主题", value=result['subject'], key="gen_subject")
                st.text_area("正文", value=result['body'], height=200, key="gen_body")
        
        st.divider()
        
        st.subheader("发送邮件")
        to_email = st.text_input("收件人")
        subject = st.text_input("主题", key="send_subject")
        body = st.text_area("正文", height=200, key="send_body")
        
        if st.button("📤 发送", type="primary"):
            if not all([to_email, subject, body]):
                st.error("请填写完整信息")
            else:
                try:
                    client = EmailClient()
                    result = client.send_email(to_email, subject, body)
                    
                    if result.get('status') == 'success':
                        st.success("✅ 发送成功！")
                    else:
                        st.error(f"发送失败: {result.get('error')}")
                except Exception as e:
                    st.error(f"发送失败: {e}")
    
    with tab2:
        st.subheader("收件箱")
        
        if st.button("🔄 刷新"):
            try:
                client = EmailClient()
                emails = client.fetch_emails(limit=10)
                
                for mail in emails:
                    if 'error' not in mail:
                        with st.expander(f"📩 {mail['subject']} - {mail['from'][:30]}..."):
                            st.write(f"**日期:** {mail['date']}")
                            st.write(f"**预览:** {mail['preview']}")
            except Exception as e:
                st.error(f"获取邮件失败: {e}")


# ===== 图片处理 =====

elif selected == "图片处理":
    st.header("🖼️ 图片处理")
    
    uploaded_image = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg', 'webp'])
    
    if uploaded_image:
        # 保存并显示
        img_path = Path("./uploads") / uploaded_image.name
        img_path.parent.mkdir(exist_ok=True)
        with open(img_path, 'wb') as f:
            f.write(uploaded_image.getvalue())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(str(img_path), caption="原图", use_container_width=True)
            
            # 图片信息
            info = services['image_processor'].get_info(str(img_path))
            st.write(f"尺寸: {info['size'][0]} x {info['size'][1]}")
            st.write(f"大小: {info['file_size_human']}")
        
        with col2:
            operation = st.selectbox(
                "选择操作",
                ["去除背景", "更换背景颜色", "调整大小", "旋转", "裁剪"]
            )
            
            if operation == "去除背景":
                if st.button("处理", type="primary"):
                    with st.spinner("处理中..."):
                        try:
                            output = services['image_processor'].remove_background(str(img_path))
                            st.image(output, caption="处理结果")
                            
                            with open(output, 'rb') as f:
                                st.download_button("📥 下载", f.read(), file_name="nobg.png")
                        except Exception as e:
                            st.error(f"处理失败: {e}")
            
            elif operation == "更换背景颜色":
                bg_color = st.color_picker("选择背景颜色", "#FFFFFF")
                # 转换颜色
                r = int(bg_color[1:3], 16)
                g = int(bg_color[3:5], 16)
                b = int(bg_color[5:7], 16)
                
                if st.button("处理", type="primary"):
                    with st.spinner("处理中..."):
                        try:
                            output = services['image_processor'].change_background(
                                str(img_path), (r, g, b)
                            )
                            st.image(output, caption="处理结果")
                            
                            with open(output, 'rb') as f:
                                st.download_button("📥 下载", f.read(), file_name="new_bg.jpg")
                        except Exception as e:
                            st.error(f"处理失败: {e}")
            
            elif operation == "调整大小":
                new_width = st.number_input("宽度", value=800, min_value=10)
                new_height = st.number_input("高度", value=600, min_value=10)
                keep_aspect = st.checkbox("保持宽高比", value=True)
                
                if st.button("处理", type="primary"):
                    output = services['image_processor'].resize(
                        str(img_path), (new_width, new_height), keep_aspect
                    )
                    st.image(output, caption="处理结果")
                    
                    with open(output, 'rb') as f:
                        st.download_button("📥 下载", f.read(), file_name="resized.jpg")
            
            elif operation == "旋转":
                angle = st.slider("旋转角度", -180, 180, 0)
                
                if st.button("处理", type="primary"):
                    output = services['image_processor'].rotate(str(img_path), angle)
                    st.image(output, caption="处理结果")
                    
                    with open(output, 'rb') as f:
                        st.download_button("📥 下载", f.read(), file_name="rotated.jpg")


# ===== 进度追踪 =====

elif selected == "进度追踪":
    st.header("📊 进度追踪")
    
    tab1, tab2, tab3 = st.tabs(["项目列表", "创建项目", "报表"])
    
    tracker = services['progress_tracker']
    
    with tab1:
        projects = tracker.get_projects()
        
        if projects:
            for p in projects:
                with st.expander(f"{'✅' if p['status']=='completed' else '📋'} {p['name']} ({p['type']})"):
                    st.write(f"**状态:** {p['status']}")
                    st.write(f"**创建时间:** {p['created_at'][:10]}")
                    
                    # 获取详情
                    detail = tracker.get_project(p['id'])
                    
                    if detail['tasks']:
                        st.write("**任务列表:**")
                        for t in detail['tasks']:
                            status_icon = "✅" if t['status'] == 'completed' else "⏳" if t['status'] == 'in_progress' else "⬜"
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"{status_icon} {t['name']}")
                            with col2:
                                new_status = st.selectbox(
                                    "状态",
                                    ["pending", "in_progress", "completed"],
                                    index=["pending", "in_progress", "completed"].index(t['status']) if t['status'] in ["pending", "in_progress", "completed"] else 0,
                                    key=f"task_{t['id']}",
                                    label_visibility="collapsed"
                                )
                                if new_status != t['status']:
                                    tracker.update_task_status(t['id'], new_status)
                                    st.rerun()
        else:
            st.info("暂无项目，去创建一个吧！")
    
    with tab2:
        st.subheader("创建新项目")
        
        template = st.selectbox(
            "选择模板",
            ["自定义", "Offer申请", "签证申请"]
        )
        
        if template == "Offer申请":
            company = st.text_input("公司名称")
            position = st.text_input("职位")
            
            if st.button("创建", type="primary"):
                if company and position:
                    project_id = create_offer_application(tracker, company, position)
                    st.success(f"✅ 项目创建成功！ID: {project_id}")
                    st.rerun()
        
        elif template == "签证申请":
            country = st.text_input("国家")
            visa_type = st.selectbox("签证类型", ["旅游", "商务", "学生", "工作"])
            
            if st.button("创建", type="primary"):
                if country:
                    project_id = create_visa_application(tracker, visa_type, country)
                    st.success(f"✅ 项目创建成功！ID: {project_id}")
                    st.rerun()
        
        else:
            name = st.text_input("项目名称")
            project_type = st.text_input("项目类型")
            description = st.text_area("描述")
            
            if st.button("创建", type="primary"):
                if name:
                    project_id = tracker.create_project(name, project_type or "自定义", description)
                    st.success(f"✅ 项目创建成功！ID: {project_id}")
                    st.rerun()
    
    with tab3:
        st.subheader("进度报表")
        
        df = tracker.generate_report()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # 导出
            if st.button("📥 导出Excel"):
                output_path = "./data/progress_report.xlsx"
                tracker.export_to_excel(output_path)
                
                with open(output_path, 'rb') as f:
                    st.download_button(
                        "下载报表",
                        f.read(),
                        file_name="progress_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.info("暂无数据")


# ===== 设置 =====

elif selected == "设置":
    st.header("⚙️ 设置")
    
    st.subheader("大模型配置")
    
    # 显示当前配置
    current_provider = os.getenv("LLM_PROVIDER", "openai")
    st.info(f"当前提供商: {current_provider}")
    
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
    
    ### 邮件配置
    
    如需使用邮件功能，请配置：
    - `EMAIL_ADDRESS`: 你的邮箱地址
    - `EMAIL_PASSWORD`: 邮箱密码或应用专用密码
    - `EMAIL_SMTP_HOST`: SMTP服务器（默认Gmail）
    
    **Gmail用户注意：** 需要开启"应用专用密码"
    """)
    
    # 测试LLM连接
    st.subheader("测试连接")
    
    if st.button("测试LLM连接"):
        try:
            llm = get_llm()
            result = llm.simple_chat("说'连接成功'")
            st.success(f"✅ 连接成功！响应: {result[:100]}")
        except Exception as e:
            st.error(f"❌ 连接失败: {e}")


# ===== 页脚 =====

st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem;">
    云端小助理 v1.0 | 
    <a href="https://github.com" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)