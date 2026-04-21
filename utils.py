# utils.py
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QSize
import sys
import os

def resource_path(relative_path):
    """获取资源的绝对路径（兼容开发环境和打包后的环境）"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        #base_path = os.path.abspath(".")
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_icon(category, name, state="normal", theme=None):
    """
    加载指定图标
    :param category: 图标分类（如 'ship', 'settings'）
    :param name: 图标名称（如 'ship', 'search', 'up'）
    :param state: 'normal' 或 'selected'
    :param theme: 'light' 或 'dark'，若为 None 则使用当前主题
    """
    if theme is None:
        # 从全局获取当前主题（需要预先设置）
        theme = getattr(load_icon, 'current_theme', 'light')
    suffix = "light" if theme == "light" else "dark"
    filename = f"{name}_{state}_{suffix}.svg"
    path = resource_path(f"assets/icons/{category}/{filename}")
    if os.path.exists(path):
        return QIcon(path)
    else:
        # 降级处理：尝试不带状态的版本（如果存在）
        alt_path = resource_path(f"assets/icons/{category}/{name}_{suffix}.svg")
        if os.path.exists(alt_path):
            return QIcon(alt_path)
        else:
            return QIcon()  # 空图标
    
def svg_to_pixmap_min(category, name, size=18, state="normal", theme=None):
    """从 assets/icons 加载 SVG 并返回 QPixmap"""
    # 获取当前主题（需要从全局或 self.manager 获取）
    if theme is None:
        theme = getattr(svg_to_pixmap_min, 'current_theme', 'light')  # 默认浅色
    filename = f"{name}_normal_{theme}.svg"
    icon_path = resource_path(f"assets/icons/{category}/{filename}")
    if not os.path.exists(icon_path):
        print(f"图标文件不存在: {icon_path}")
        return QPixmap(size, size)  # 返回透明占位图
    return _render_svg_to_pixmap(icon_path, size)

def svg_to_pixmap_max(category, name, size=24, state="normal", theme=None):
    """从 assets/icons 加载 SVG 并返回 QPixmap"""
    # 获取当前主题（需要从全局或 self.manager 获取）
    if theme is None:
        theme = getattr(svg_to_pixmap_min, 'current_theme', 'light')  # 默认浅色
    filename = f"{name}_normal_{theme}.svg"
    icon_path = resource_path(f"assets/icons/{category}/{filename}")
    if not os.path.exists(icon_path):
        print(f"图标文件不存在: {icon_path}")
        return QPixmap(size, size)  # 返回透明占位图
    return _render_svg_to_pixmap(icon_path, size)  # 返回透明占位图

def _render_svg_to_pixmap(svg_path, size):
    """渲染 SVG 到 QPixmap，尺寸为 size x size"""
    if not os.path.exists(svg_path):
        return QPixmap(size, size)
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return pixmap