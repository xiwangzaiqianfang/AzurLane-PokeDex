import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QApplication, QLabel, QSizePolicy,
                                QProgressBar,QStackedWidget, QPushButton, QListWidget,
                                QListWidgetItem, QFrame, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, QSettings, Signal, QUrl, QTimer, QThread, QParallelAnimationGroup,
                            QSize, QPropertyAnimation, QEasingCurve, QPoint)
from PySide6.QtGui import QPixmap, QDesktopServices, QIcon
from gui.navigationlistweidget import NavigationListWidget
from manager import ShipManager
from gui.main_page import MainPage
#from gui.fleet_tech_page import FleetTechPage
from gui.camp_tech_page import CampTechPage
from gui.attr_bonus_page import AttrBonusPage
from gui.stats_page import StatPage
from gui.settings_page import SettingsPage

class LoaderThread(QThread):
    finished = Signal(object)   # 传递 manager 对象

    def run(self):
        manager = ShipManager("ships.json")
        self.finished.emit(manager)

class MainWindow(QMainWindow):
    windowResized = Signal()
    def __init__(self, manager=None):
        print("MainWindow __init__ start")
        super().__init__()
        ##try:
        self.setWindowTitle("碧蓝航线图鉴")
        self.resize(1400, 700)
        self.setMinimumWidth(800)

        # 提前创建设置对象
        self.settings = QSettings("菲梦林光", "AzurLaneDex")

        # 创建 stacked widget 作为中央部件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 1. 加载页面
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignCenter)

        # 应用图标
        icon_label = QLabel()
        pixmap = QPixmap("app_icon.ico").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(icon_label)

        # 进度条（无限循环样式）
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)   # 表示忙碌
        self.progress_bar.setFixedWidth(300)
        loading_layout.addWidget(self.progress_bar)

        # 加载文字
        self.loading_label = QLabel("正在加载数据，请稍候...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(self.loading_label)

        self.stacked_widget.addWidget(self.loading_widget)

        # 2. 主界面占位（稍后填充）
        self.main_widget = QWidget()
        self.stacked_widget.addWidget(self.main_widget)

        # 初始显示加载页
        self.stacked_widget.setCurrentWidget(self.loading_widget)

        # 如果传入了 manager，直接使用并显示主界面
        if manager is not None:
            self.manager = manager
            self.setup_main_ui()
            self.stacked_widget.setCurrentWidget(self.main_widget)
        else:
            # 启动后台加载线程
            self.stacked_widget.setCurrentWidget(self.loading_widget)
            self.loader_thread = LoaderThread()
            self.loader_thread.finished.connect(self.on_loading_finished)
            self.loader_thread.start()
            
    def on_loading_finished(self, manager):
        """数据加载完成，切换到主界面"""
        self.manager = manager
        self.setup_main_ui()
        self.manager.data_changed.connect(self.on_global_data_changed)
        self.stacked_widget.setCurrentWidget(self.main_widget)

    def setup_main_ui(self):
        """构建主界面的所有控件和布局（原来 __init__ 中的内容）""" 
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        #侧边栏
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        self.collapsed = False
        self.auto_collapse_threshold = 1007
        self.collapse_btn = QPushButton("◀ 导航")
        self.collapse_btn.setObjectName("navItem")
        self.collapse_btn.setFixedSize(200, 50)
        self.collapse_btn.clicked.connect(self.toggle_nav)
        nav_layout.addWidget(self.collapse_btn, 0, Qt.AlignTop)

        self.nav_list = NavigationListWidget()
        self.nav_list.rowReleased.connect(self.switch_page)
        self.nav_list.setFixedWidth(200)
        self.nav_list.setMinimumWidth(64)
        self.nav_list.setMaximumWidth(200)
        self.nav_list.setMinimumHeight(400)
        self.nav_list.setIconSize(QSize(24, 24))
        self.nav_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        menu_items = [
            ("舰船图鉴", "icons/ship.png"), ("阵营科技", "icons/camp_tech.png"),
            ("属性加成", "icons/attr_bonus.png"), ("统计", "icons/stats.png"), ("设置", "icons/settings.png"),
        ]
        self.nav_items = []
        for text, icon_path in menu_items:
            item = QListWidgetItem(QIcon(icon_path), text)
            item.setData(Qt.UserRole, text)
            self.nav_list.addItem(item)
            self.nav_items.append(item)
        nav_layout.addWidget(self.nav_list, 1)
        main_layout.addWidget(nav_container, 0, Qt.AlignTop)

        #动画指示器
        self.nav_list.currentRowChanged.connect(self.on_nav_row_changed)
        self.indicator = QFrame(self.nav_list)
        self.indicator.setFixedWidth(4)  # 指示条宽度
        self.indicator.setStyleSheet("border-radius: 2px;")
        self.indicator.hide()  # 初始隐藏，第一次选中时显示

        #堆叠区域
        self.stacked = QStackedWidget()
        self.stacked.setContentsMargins(0, 0, 0, 0)
        self.stacked.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.stacked, 1)

        # 创建页面
        self.main_page = MainPage(self.manager, self)
        self.camp_tech_page = CampTechPage(self.manager,self)
        self.attr_bonus_page = AttrBonusPage(self.manager, self)    
        self.stats_page = StatPage(self.manager, self)
        self.settings_page = SettingsPage(self.manager, self)

        self.stacked.addWidget(self.main_page)
        self.stacked.addWidget(self.camp_tech_page)
        self.stacked.addWidget(self.attr_bonus_page)
        self.stacked.addWidget(self.stats_page)
        self.stacked.addWidget(self.settings_page)

        self.nav_list.setCurrentRow(0)
        self.stacked.setCurrentWidget(self.main_page)

        #theme_mode = self.manager.config.get("theme_mode", "system")
        #self.system_follow = (theme_mode == "system")
        #if self.system_follow:
        app = QApplication.instance()
        if hasattr(app.styleHints(), 'colorScheme'):
            current_scheme = app.styleHints().colorScheme()
            if current_scheme == Qt.ColorScheme.Dark:
                self.manager.current_theme = "dark"
            else:
                self.manager.current_theme = "light"
        else:
            # 对于 Qt < 6.5，需要其他方法获取，例如读取注册表
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                self.manager.current_theme = "dark" if value == 0 else "light"
            except:
                self.manager.current_theme = "light"  # 默认
        self.load_theme()
        #else:
        #    self.manager.current_theme = theme_mode
        #    self.load_theme()
        self.setup_theme_monitor()

    def switch_page(self, row):
        self.switch_page_with_fade(row)

    def switch_page_with_fade(self, new_index):
        print("switch_page_with_fade called, new_index:", new_index)
        current_widget = self.stacked.currentWidget()
        new_widget = self.stacked.widget(new_index)
        if current_widget == new_widget:
            return
        
        # 如果没有当前页面（启动时第一次切换）
        if current_widget is None:
            self.stacked.setCurrentIndex(new_index)
            return

        # 淡出当前页面
        self.fade_out = QGraphicsOpacityEffect(current_widget)
        effect_out = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(effect_out)
        self.fade_out = QPropertyAnimation(effect_out, b"opacity")
        self.fade_out.setDuration(100)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(lambda: self._perform_switch(current_widget, new_widget, new_index))
        self.fade_out.start()


    def _perform_switch(self, old_widget, new_widget, new_index):
        print("_perform_switch called")
        # 先切换页面，但新页面初始透明
        effect_in = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect_in)
        effect_in.setOpacity(0.0)
        self.stacked.setCurrentIndex(new_index)
        # 淡入新页面
        self.fade_in_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(self.fade_in_effect)
        self.fade_in_effect.setOpacity(0.0)
        self.fade_in = QPropertyAnimation(self.fade_in_effect, b"opacity")
        self.fade_in.setDuration(100)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.finished.connect(lambda: new_widget.setGraphicsEffect(None))
        self.fade_in.start()
        # 清理旧页面的效果
        old_widget.setGraphicsEffect(None)
    
    def show_camp_tech(self):
        """切换到阵营科技页面"""
        self.nav_list.setCurrentRow(1)

    def show_attr_bonus(self):
        """切换到属性加成页面"""
        self.nav_list.setCurrentRow(2)

    def show_stats(self):
        """切换到统计页面"""
        self.nav_list.setCurrentRow(3)

    def show_settings(self):
        """切换到设置页面"""
        self.nav_list.setCurrentRow(4)
        
    def load_theme(self):
        """加载保存的主题，并将样式表应用到整个应用"""
        #theme = self.settings.value("theme", "light")  # 默认浅色
        theme = self.manager.current_theme
        #print(f"应用主题: {theme}")
        style_file = f"style_{theme}.qss"
        # 获取当前文件所在目录的绝对路径
        base_dir = os.path.dirname(__file__)
        style_path = os.path.join(base_dir, style_file)
        #print(f"Loading theme: {theme}, path: {style_path}") #1
        if os.path.exists(style_path):
            with open(style_path, "r", encoding='utf-8') as f:
                qss = f.read() #2
                #print(f"QSS content length: {len(qss)}") #3
                #print(f"QSS preview: {qss[:200]}") #4
                QApplication.instance().setStyleSheet(f.read())
            app = QApplication.instance()
            app.setStyleSheet(qss)
            # 强制所有顶级窗口重新应用样式
            for widget in app.topLevelWidgets():
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                self.update_indicator_color()
                widget.update()
                app.processEvents()
        else:
            print(f"样式文件不存在: {style_path}")

    #def toggle_theme(self):
    #    """切换深色/浅色主题"""
    #    current = self.settings.value("theme", "light")
    #    new_theme = "dark" if current == "light" else "light"
    #    self.settings.setValue("theme", new_theme)
    #    self.load_theme()
        # 强制刷新界面
    #    self.repaint()

    def closeEvent(self, event):
        """窗口关闭时保存大小和位置"""
        self.settings.setValue("window_geometry", self.saveGeometry())
        #print("MainWindow closeEvent")
        super().closeEvent(event)

    def showEvent(self, event):
        """窗口显示时恢复上次的大小和位置"""
        # 仅在加载完成后才恢复窗口几何信息
        if hasattr(self, 'settings') and hasattr(self, 'manager'):
            geometry = self.settings.value("window_geometry")
            if geometry:
                self.restoreGeometry(geometry)
            #print("MainWindow showEvent")
        super().showEvent(event)
        QTimer.singleShot(100, self.init_indicator)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.windowResized.emit() # 发出窗口大小改变信号
    
    def init_indicator(self):
        if not hasattr(self, 'nav_list'):
            return
        row = self.nav_list.currentRow()
        if row >= 0:
            self.on_nav_row_changed(row)

    def setup_theme_monitor(self):
        if hasattr(QApplication.instance().styleHints(), 'colorSchemeChanged'):
            # Qt 6.5+ 支持信号
            QApplication.instance().styleHints().colorSchemeChanged.connect(self.on_system_theme_changed)
        else:
            # 低版本 Qt，使用定时器轮询（简单实现）
            self.theme_timer = QTimer(self)
            self.theme_timer.timeout.connect(self.check_system_theme)
            self.theme_timer.start(2000)

    def check_system_theme(self):
        # 简化：读取注册表或判断 Windows 10/11 当前主题
        # 这里用简单方法：判断默认系统颜色，假设 Windows 10/11 深色模式注册表路径
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            system_dark = (value == 0)
        except:
            system_dark = False
        #if self.system_follow:
        new_theme = "dark" if system_dark else "light"
        if new_theme != self.manager.version_theme:
            self.manager.version_theme = new_theme
            self.load_theme()

    def on_system_theme_changed(self, color_scheme):
        #if self.system_follow:
        self.load_theme()
        self.update_indicator_color()
        new_theme = "dark" if color_scheme == Qt.ColorScheme.Dark else "light"
        if new_theme != self.manager.current_theme:
            #print(f"[主题] 系统主题变化，新主题: {new_theme}")
            self.manager.current_theme = new_theme
            self.load_theme()

    #def set_system_theme_follow(self, follow):
    #    print(f"[主题] 跟随系统主题: {follow}")
    #    self.system_follow = follow
    #    if follow:
    #        # 立即根据当前系统主题切换
    #        app = QApplication.instance()
    #        if hasattr(app.styleHints(), 'colorScheme'):
    #            current_scheme = app.styleHints().colorScheme()
    #            new_theme = "dark" if current_scheme == Qt.ColorScheme.Dark else "light"
    #            self.manager.current_theme = new_theme
    #            self.load_theme()
    #        else:
    #            # 低版本 Qt 可读取注册表等
    #            # 这里简单默认浅色
    #            self.manager.current_theme = "light"
    #            self.load_theme()

    #def set_manual_theme(self, theme):
    #    print(f"[主题] 手动设置主题为: {theme}")
    #    self.system_follow = False
    #    self.manager.current_theme = theme
    #    self.load_theme()

    def open_settings(self):
        from gui.settings_page import SettingsDialog
        dlg = SettingsDialog(self.manager, self)
        dlg.exec()

    def reset_window_geometry(self):
        """清除保存的窗口几何信息，并重置当前窗口到默认大小"""
        # 删除保存的几何信息
        self.settings.remove("window_geometry")
        self.resize(1400, 700)
        # 将窗口移动到屏幕中央
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())

    def center(self):
        """将窗口移动到屏幕中央"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())

    def hideEvent(self, event):
        print("MainWindow hideEvent")
        super().hideEvent(event)

    def on_nav_row_changed(self, row):
        if row < 0:
            self.indicator.hide()
            return
        item = self.nav_list.item(row)
        # 计算目标位置：列表项的位置 + 指示器偏移
        rect = self.nav_list.visualItemRect(item)
        target_y = rect.y() + (rect.height() - self.indicator.height()) // 2
        # 使用动画移动指示
        self.anim = QPropertyAnimation(self.indicator, b"pos")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setStartValue(self.indicator.pos())
        self.anim.setEndValue(QPoint(0, target_y))
        self.anim.start()
        self.indicator.show()

    def update_indicator_color(self):
        """根据当前主题设置指示条颜色"""
        theme = self.manager.current_theme
        if theme == "light":
            color = "#0078d4"   # WinUI 蓝色
        else:
            color = "#4cc2ff"   # 深色主题下的亮蓝色
        self.indicator.setStyleSheet(f"background-color: {color}; border-radius: 2px;")

    def toggle_nav(self):
        self.collapsed = not self.collapsed
        # self.collapsed = not getattr(self, 'collapsed', False)
        target_width = 64 if self.collapsed else 200
        # 动画 minimumWidth
        self.anim_min = QPropertyAnimation(self.nav_list, b"minimumWidth")
        self.anim_min.setDuration(100)
        self.anim_min.setStartValue(self.nav_list.minimumWidth())
        self.anim_min.setEndValue(target_width)
        self.anim_min.start()
        # 动画 maximumWidth
        self.anim_max = QPropertyAnimation(self.nav_list, b"maximumWidth")
        self.anim_max.setDuration(100)
        self.anim_max.setStartValue(self.nav_list.maximumWidth())
        self.anim_max.setEndValue(target_width)
        self.anim_max.start()
        if self.collapsed:
            self.collapse_btn.setFixedWidth(64)
            self.collapse_btn.setText("▶")
        else:
            self.collapse_btn.setFixedWidth(200)
            self.collapse_btn.setText("◀ 导航")
        for item in self.nav_items:
            if self.collapsed:
                item.setText("")
                item.setTextAlignment(Qt.AlignCenter)
            else:
                item.setText(item.data(Qt.UserRole))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.collapse_btn.setText("▶" if self.collapsed else "◀ 导航")
        QTimer.singleShot(50, lambda: self.on_nav_row_changed(self.nav_list.currentRow()))

    def update_online(self):
        reply = QMessageBox.question(
            self,
            "检查更新",
            "是否检查程序新版本？\n\n注意：数据更新会同时进行，您可以选择跳过程序更新。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
    
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            # 检查程序版本
            latest_version = self.manager.get_latest_version()
            current_version = "1.0.0"  # 请将当前版本硬编码或从配置文件读取
            if latest_version and latest_version > current_version:
                ret = QMessageBox.question(
                    self,
                    "发现新版本",
                    f"发现新版本 {latest_version}（当前 {current_version}）\n\n是否前往下载页面？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if ret == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl("https://github.com/xiwangzaiqianfang/AzurLane-Dex/releases/latest"))
            else:
                QMessageBox.information(self, "检查更新", "当前已是最新版本。")
        
            """从网络更新数据"""
            # 可以弹出一个对话框让用户输入 URL，或者使用固定的默认 URL
            default_url = "https://raw.githubusercontent.com/xiwangzaiqianfang/AzurLane-Dex/main/ships.json"
            success = self.manager.update_from_github(default_url)
            if success:
                self.apply_filter(self.filter_bar.get_criteria())
                QMessageBox.information(self, "完成", "数据更新成功！")
            else:
                QMessageBox.information(self, "无需更新", "数据已是最新版本。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败：{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def on_global_data_changed(self):
        """数据全局变化时刷新相关页面"""
        if hasattr(self, 'camp_tech_page'):
            self.camp_tech_page.load_data()
        if hasattr(self, 'attr_bonus_page'):
            self.attr_bonus_page.load_data()
        if hasattr(self, 'stats_page'):
            self.stats_page.load_stats()
        # 主页面本身会通过详情页信号更新，无需重复刷新