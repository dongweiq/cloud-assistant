"""
图片处理模块 - 裁剪、换背景等
"""
import os
from PIL import Image, ImageFilter, ImageEnhance
from typing import Tuple, Optional
from pathlib import Path

try:
    from rembg import remove as remove_bg
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self, output_dir: str = "./uploads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_output_path(self, input_path: str, suffix: str) -> str:
        """生成输出文件路径"""
        stem = Path(input_path).stem
        ext = Path(input_path).suffix
        return str(self.output_dir / f"{stem}_{suffix}{ext}")
    
    def crop(self, 
             image_path: str, 
             box: Tuple[int, int, int, int],
             output_path: Optional[str] = None) -> str:
        """
        裁剪图片
        box: (left, top, right, bottom)
        """
        img = Image.open(image_path)
        cropped = img.crop(box)
        
        output = output_path or self._get_output_path(image_path, "cropped")
        cropped.save(output)
        return output
    
    def resize(self,
               image_path: str,
               size: Tuple[int, int],
               keep_aspect: bool = True,
               output_path: Optional[str] = None) -> str:
        """
        调整图片大小
        size: (width, height)
        keep_aspect: 是否保持宽高比
        """
        img = Image.open(image_path)
        
        if keep_aspect:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            resized = img
        else:
            resized = img.resize(size, Image.Resampling.LANCZOS)
        
        output = output_path or self._get_output_path(image_path, "resized")
        resized.save(output)
        return output
    
    def remove_background(self, 
                          image_path: str,
                          output_path: Optional[str] = None) -> str:
        """去除背景"""
        if not REMBG_AVAILABLE:
            raise ImportError("需要安装 rembg: pip install rembg")
        
        with open(image_path, 'rb') as f:
            input_data = f.read()
        
        output_data = remove_bg(input_data)
        
        output = output_path or self._get_output_path(image_path, "nobg").replace('.jpg', '.png').replace('.jpeg', '.png')
        with open(output, 'wb') as f:
            f.write(output_data)
        
        return output
    
    def change_background(self,
                          image_path: str,
                          bg_color: Tuple[int, int, int] = (255, 255, 255),
                          output_path: Optional[str] = None) -> str:
        """
        更换背景颜色
        先去除原背景，再填充新颜色
        """
        # 先去背景
        nobg_path = self.remove_background(image_path)
        
        # 打开去背景后的图片
        img = Image.open(nobg_path)
        
        # 创建新背景
        background = Image.new('RGBA', img.size, bg_color + (255,))
        
        # 合成
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
        else:
            background.paste(img)
        
        # 转换为RGB保存
        output = output_path or self._get_output_path(image_path, f"bg_{bg_color[0]}_{bg_color[1]}_{bg_color[2]}")
        background.convert('RGB').save(output)
        
        # 清理临时文件
        os.remove(nobg_path)
        
        return output
    
    def rotate(self,
               image_path: str,
               angle: float,
               expand: bool = True,
               output_path: Optional[str] = None) -> str:
        """旋转图片"""
        img = Image.open(image_path)
        rotated = img.rotate(angle, expand=expand, resample=Image.Resampling.BICUBIC)
        
        output = output_path or self._get_output_path(image_path, f"rotated_{int(angle)}")
        rotated.save(output)
        return output
    
    def adjust_brightness(self,
                          image_path: str,
                          factor: float = 1.2,
                          output_path: Optional[str] = None) -> str:
        """
        调整亮度
        factor: < 1 变暗, > 1 变亮
        """
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced = enhancer.enhance(factor)
        
        output = output_path or self._get_output_path(image_path, "brightness")
        enhanced.save(output)
        return output
    
    def adjust_contrast(self,
                        image_path: str,
                        factor: float = 1.2,
                        output_path: Optional[str] = None) -> str:
        """
        调整对比度
        factor: < 1 降低对比度, > 1 提高对比度
        """
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(factor)
        
        output = output_path or self._get_output_path(image_path, "contrast")
        enhanced.save(output)
        return output
    
    def blur(self,
             image_path: str,
             radius: int = 5,
             output_path: Optional[str] = None) -> str:
        """高斯模糊"""
        img = Image.open(image_path)
        blurred = img.filter(ImageFilter.GaussianBlur(radius))
        
        output = output_path or self._get_output_path(image_path, "blurred")
        blurred.save(output)
        return output
    
    def convert_format(self,
                       image_path: str,
                       target_format: str,
                       output_path: Optional[str] = None) -> str:
        """
        转换图片格式
        target_format: 'png', 'jpg', 'webp', etc.
        """
        img = Image.open(image_path)
        
        stem = Path(image_path).stem
        output = output_path or str(self.output_dir / f"{stem}.{target_format}")
        
        # 处理透明度
        if target_format.lower() in ['jpg', 'jpeg'] and img.mode == 'RGBA':
            # JPG不支持透明，填充白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        img.save(output)
        return output
    
    def get_info(self, image_path: str) -> dict:
        """获取图片信息"""
        img = Image.open(image_path)
        file_size = os.path.getsize(image_path)
        
        return {
            "path": image_path,
            "format": img.format,
            "mode": img.mode,
            "size": img.size,  # (width, height)
            "file_size": file_size,
            "file_size_human": f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / 1024 / 1024:.1f} MB"
        }
