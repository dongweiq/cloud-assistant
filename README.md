# 云端小助理 🤖

一站式AI办公助手，集成文档管理、内容创作、翻译、PDF编辑、邮件、图片处理、进度追踪等功能。

**无需编程基础，开箱即用！**

## 📸 界面预览

### 首页
![首页](screenshots/home.png)

### 文档管理
![文档管理](screenshots/doc-management.png)

### 进度追踪
![进度追踪](screenshots/progress-tracking.png)

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 📁 文档管理 | 上传、搜索、AI总结文档（PDF/Word/TXT） |
| ✍️ 内容创作 | 基于参考材料+网络搜索，AI辅助写作 |
| 🌐 文档翻译 | 支持长文档翻译，多语言互译 |
| 📄 PDF编辑 | 添加签名、合并、拆分、水印、提取页面 |
| 📧 邮件助手 | AI撰写邮件，收发邮件 |
| 🖼️ 图片处理 | 去背景、换背景色、裁剪、旋转等 |
| 📊 进度追踪 | Offer申请、签证申请等进度管理与报表导出 |

## 🚀 快速开始

### Windows用户（推荐）

1. **下载并解压** 项目文件
2. **双击运行** `安装.bat`（首次安装）
3. **以后使用** 双击桌面的"云端小助理"快捷方式

> ⚠️ 需要先安装 [Python 3.10+](https://www.python.org/downloads/)（安装时勾选"Add to PATH"）

### macOS/Linux用户

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动
streamlit run app_v2.py
```

## ⚙️ 配置说明

### 大模型配置（必需）

启动后在 **设置** 页面配置，支持以下大模型：

| 提供商 | 特点 | 申请地址 |
|--------|------|----------|
| **OpenAI** | GPT-4o，能力最强 | https://platform.openai.com |
| **智谱GLM** | 国产，性价比高 | https://open.bigmodel.cn |
| **月之暗面** | Kimi，长文本强 | https://platform.moonshot.cn |
| **DeepSeek** | 价格便宜 | https://platform.deepseek.com |

> 💡 配置保存在本地 `data/config.json`，无需每次输入

### 邮箱配置（可选）

如需使用邮件功能，在 **设置** 页面配置邮箱：

- **Gmail**: 需使用"应用专用密码"
- **QQ邮箱**: 需使用"授权码"
- **163邮箱/Outlook**: 使用邮箱密码

## 📁 项目结构

```
cloud-assistant/
├── app_v2.py             # 主程序
├── 启动.bat              # Windows启动脚本
├── 安装.bat              # Windows一键安装
├── requirements.txt      # 依赖列表
├── modules/              # 功能模块
│   ├── config_manager.py # 配置管理（界面配置）
│   ├── llm_client.py     # 大模型客户端
│   ├── document_processor.py
│   ├── translator.py
│   ├── email_client.py
│   ├── image_processor.py
│   └── progress_tracker.py
├── data/                 # 数据存储
│   └── config.json       # 用户配置（自动生成）
├── uploads/              # 上传的文件
└── screenshots/          # 界面截图
```

## ❓ 常见问题

### Q: 启动失败，提示"未检测到Python"？
A: 请先安装Python 3.10+，安装时务必勾选 "Add Python to PATH"。

### Q: 图片去背景失败？
A: 需要安装rembg: `pip install rembg`，首次使用会下载模型。

### Q: 翻译速度慢？
A: 默认使用免费Google翻译。勾选"AI翻译"会更准确但需要消耗API额度。

### Q: 邮件发送失败？
A: 检查邮箱配置。Gmail需要"应用专用密码"，QQ邮箱需要"授权码"。

### Q: 如何更新？
A: 下载新版本覆盖即可，`data/config.json` 中的配置会保留。

## 📝 更新日志

### v2.0.0
- ✨ 新增界面配置功能（无需编辑.env文件）
- ✨ 新增Windows一键安装脚本
- ✨ 完善邮件助手功能
- ✨ 完善所有功能模块
- 🔧 优化用户体验

### v1.0.0
- 初始版本

---

Made with ❤️ by 小龙虾 🦞

**GitHub:** https://github.com/dongweiq/cloud-assistant
**Gitee:** https://gitee.com/dongweiq/cloud-assistant
