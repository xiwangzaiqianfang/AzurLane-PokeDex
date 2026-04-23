import sys
import os
import json
import argparse
from PySide6 import QtSvg
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtCore import Qt
from gui.main_window import MainWindow, LoaderThread
from gui.account_manager import AccountManager
from gui.splash_screen import SplashScreen
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from utils import resource_path, svg_to_pixmap_min, svg_to_pixmap_max, load_icon

image_dir = resource_path("images")

def is_vscode_debug():
    """检测是否在 VS Code 调试模式下运行"""
    # 方法1：环境变量
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        return True
    # 方法2：检查是否有调试器附加（备选）
    import sys
    if sys.gettrace() is not None:
        return True
    return False

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dev', action='store_true', help='开发模式')
    parser.add_argument('--no-dev', action='store_true', help='强制关闭开发模式（即使在调试环境下）')
    return parser.parse_args()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("app_icon.ico")))
    #app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    
    # 在创建 app 后，加载字体
    font_id = QFontDatabase.addApplicationFont("assets/fonts/MiSansVF_4.009.ttf")
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

    args = parse_args()
    dev_mode = parse_args().dev
    account_manager = AccountManager()
    config_file = "config.json"
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            pass
    ask_on_startup = config.get("ask_account_on_startup", True)
    default_account = config.get("default_account", "")

    # 根据设置决定是否自动登录
    if account_manager.get_regular_account_count() == 0:
        from gui.first_run_dialog import FirstRunDialog
        dlg = FirstRunDialog()
        if dlg.exec() == QDialog.Accepted:
            info = dlg.get_account_info()
            name = info["name"]
            if not name:
                QMessageBox.warning(None, "错误", "账户名不能为空")
                sys.exit(1)
            avatar_path = ""
            if info["avatar"]:
                avatar_path = account_manager.save_avatar(name, info["avatar"])
            if not account_manager.add_account(name, info["password"], avatar=avatar_path, is_developer=False):
                QMessageBox.warning(None, "错误", "账户创建失败")
                sys.exit(1)
            if info["set_default"]:
                account_manager.set_default_account(name)
            account_manager.set_current_account(name)
        else:
            sys.exit(0)
    else:
        default = account_manager.get_default_account()
        if default and account_manager.get_account_info(default):
            account_manager.set_current_account(default)
        else:
            if not ask_on_startup and default_account and account_manager.get_account_info(default_account):
                # 自动登录默认账户
                account_manager.set_current_account(default_account)
                print(f"自动登录默认账户: {default_account}")
            else:
                from gui.account_dialog import AccountDialog
                dlg = AccountDialog(account_manager, dev_mode=dev_mode)
                if dlg.exec() != QDialog.Accepted:
                    sys.exit(0)

    if not dev_mode and is_vscode_debug():
        dev_mode = True
        print("检测到 VS Code 调试环境，自动启用开发模式")
    if not args.no_dev and (args.dev or is_vscode_debug()):
        dev_mode = True
    account_manager = AccountManager()
    splash = SplashScreen()
    splash.show()

    loader = LoaderThread(account_manager, dev_mode=dev_mode)
    loader.finished.connect(lambda result: on_loading_finished(result, splash, app, dev_mode))
    loader.start()

    #app.setStyle("Fusion")
    sys.exit(app.exec())

def on_loading_finished(result, splash, app, dev_mode):
    manager, account_manager = result
    splash.close()
    window = MainWindow(manager=manager, account_manager=account_manager, dev_mode=dev_mode)
    if hasattr(window, 'manager') and window.manager:
        svg_to_pixmap_min.current_theme = window.current_theme
        svg_to_pixmap_max.current_theme = window.current_theme
    window.show()

if __name__ == "__main__":
    main()