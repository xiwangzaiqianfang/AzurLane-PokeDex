import sys
import os
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def resource_path(relative_path):
    """获取资源文件的绝对路径（兼容开发环境和打包后的环境）"""
    try:
        # PyInstaller/Nuitka 打包后临时目录
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境：当前文件所在目录
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

image_dir = resource_path("images")
ship_json = resource_path("ships.json")

def main():
    app = QApplication(sys.argv)
    #app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()