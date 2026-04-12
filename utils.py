# utils.py
import sys
import os

def resource_path(relative_path):
    """获取资源的绝对路径（兼容开发环境和打包后的环境）"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)