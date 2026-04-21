import sys
import os
from PySide6 import QtSvg
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from utils import resource_path, svg_to_pixmap_min, svg_to_pixmap_max, load_icon

image_dir = resource_path("images")
ship_json = resource_path("ships.json")

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("app_icon.ico")))
    #app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    
    # 在创建 app 后，加载字体
    font_id = QFontDatabase.addApplicationFont("assets/font/MiSansVF_4.009.ttf")
    #print("主界面全局字体ID:", font_id)
    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font = QFont(font_families[0], 11.5)
            font.setFamilies(["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Arial"])
            font.setPixelSize(14)
            app.setFont(font)
    else:
        # 回退到系统字体
        font = QFont("Microsoft YaHei", 11.5)
        app.setFont(font)

    #app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    if hasattr(window, 'manager') and window.manager:
        svg_to_pixmap_min.current_theme = window.manager.current_theme
        svg_to_pixmap_max.current_theme = window.manager.current_theme
    sys.exit(app.exec())

if __name__ == "__main__":
    main()