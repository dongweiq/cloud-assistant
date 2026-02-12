"""
Windows打包脚本
在Windows环境下运行此脚本来创建可执行文件

使用方法：
1. 安装依赖: pip install -r requirements.txt
2. 安装打包工具: pip install pyinstaller
3. 运行打包: python build_windows.py
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 50)
    print("云端小助理 - Windows打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # 创建spec文件内容
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(
    ['app_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('modules', 'modules'),
        ('screenshots', 'screenshots'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit_option_menu',
        'PIL',
        'fitz',
        'docx',
        'pandas',
        'openpyxl',
        'deep_translator',
        'duckduckgo_search',
        'httpx',
        'chromadb',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='云端小助理',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='云端小助理',
)
'''
    
    # 写入spec文件
    with open("cloud_assistant.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("\n正在打包...")
    print("(这可能需要几分钟时间)\n")
    
    # 运行PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "cloud_assistant.spec"
    ])
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("✓ 打包成功！")
        print("=" * 50)
        print(f"\n输出目录: {Path('dist/云端小助理').absolute()}")
        print("\n使用方法:")
        print("1. 进入 dist/云端小助理 目录")
        print("2. 双击运行 云端小助理.exe")
        print("   或在命令行运行: streamlit run app_v2.py")
    else:
        print("\n打包失败，请检查错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
