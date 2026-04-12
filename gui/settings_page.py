# gui/settings_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QCheckBox, QInputDialog,
                               QMessageBox, QFrame, QScrollArea, QLineEdit)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QPixmap
from manager import ShipManager

class SettingsPage(QWidget):
    def __init__(self, manager: ShipManager, main_window):
        super().__init__()
        self.manager = manager
        self.main_window = main_window
        self.setup_ui()
        self.main_window.windowResized.connect(self.update_window_size_label)

    def setup_ui(self):
        # 主布局：垂直布局，包含一个滚动区域
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        main_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ---- 应用信息卡片 ----
        app_card = QFrame()
        app_card.setObjectName("card")
        app_layout = QVBoxLayout(app_card)
        app_layout.setContentsMargins(15, 15, 15, 15)
        app_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap("app_icon.ico").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        app_layout.addWidget(logo_label)

        name_label = QLabel("碧蓝航线本地图鉴")
        name_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignCenter)
        app_layout.addWidget(name_label)

        layout.addWidget(app_card)

        # ---- 编辑密码卡片 ----
        pwd_card = QFrame()
        pwd_card.setObjectName("card")
        pwd_layout = QVBoxLayout(pwd_card)
        pwd_layout.setContentsMargins(15, 15, 15, 15)

        pwd_title = QLabel("编辑密码")
        pwd_title.setObjectName("cardTitle")
        pwd_layout.addWidget(pwd_title)

        pwd_row = QHBoxLayout()
        self.pwd_btn = QPushButton("修改编辑密码")
        self.pwd_btn.clicked.connect(self.change_password)
        pwd_row.addWidget(self.pwd_btn)
        pwd_row.addStretch()
        pwd_layout.addLayout(pwd_row)
        layout.addWidget(pwd_card)

        # ---- 窗口设置卡片 ----
        window_card = QFrame()
        window_card.setObjectName("card")
        window_layout = QVBoxLayout(window_card)
        window_layout.setContentsMargins(15, 15, 15, 15)

        window_title = QLabel("窗口设置")
        window_title.setObjectName("cardTitle")
        window_layout.addWidget(window_title)

        # 显示当前窗口大小
        self.window_size_label = QLabel()
        self.update_window_size_label()
        window_layout.addWidget(self.window_size_label)

        # 重置按钮
        reset_btn = QPushButton("重置窗口大小")
        reset_btn.clicked.connect(self.reset_window_geometry)
        window_layout.addWidget(reset_btn)

        layout.addWidget(window_card)

        # ---- 数据更新卡片 ----
        update_card = QFrame()
        update_card.setObjectName("card")
        update_layout = QVBoxLayout(update_card)
        update_layout.setContentsMargins(15, 15, 15, 15)

        update_title = QLabel("数据更新")
        update_title.setObjectName("cardTitle")
        update_layout.addWidget(update_title)

        update_row = QHBoxLayout()
        self.update_btn = QPushButton("从网络更新舰船数据")
        self.update_btn.clicked.connect(self.update_data)
        update_row.addWidget(self.update_btn)
        update_row.addStretch()
        update_layout.addLayout(update_row)
        layout.addWidget(update_card)

        # ---- 日志记录卡片 ----
        log_card = QFrame()
        log_card.setObjectName("card")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(15, 15, 15, 15)

        log_title = QLabel("日志记录")
        log_title.setObjectName("cardTitle")
        log_layout.addWidget(log_title)

        log_row = QHBoxLayout()
        self.log_cb = QCheckBox("记录编辑操作日志")
        self.log_cb.setChecked(self.manager.config.get("log_edits", True))
        self.log_cb.toggled.connect(self.on_log_toggled)
        log_row.addWidget(self.log_cb)
        log_row.addStretch()
        log_layout.addLayout(log_row)
        layout.addWidget(log_card)

        # ---- 关于卡片（可点击展开） ----
        about_card = QFrame()
        about_card.setObjectName("card")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(15, 15, 15, 15)

        # 标题行
        about_title_row = QHBoxLayout()
        about_title = QLabel("关于")
        about_title.setObjectName("cardTitle")
        about_title_row.addWidget(about_title)
        about_title_row.addStretch()
        self.about_btn = QPushButton("▼")
        self.about_btn.setFixedSize(30, 30)
        self.about_btn.setFlat(True)
        self.about_btn.clicked.connect(self.toggle_about)
        about_title_row.addWidget(self.about_btn)
        about_layout.addLayout(about_title_row)

        # 可展开内容
        self.about_content = QWidget()
        self.about_content.setVisible(False)
        about_content_layout = QVBoxLayout(self.about_content)
        about_content_layout.setContentsMargins(0, 10, 0, 0)
        about_content_layout.setSpacing(8)

        version = getattr(self.manager, 'get_program_version', lambda: "1.0.0")()
        about_content_layout.addWidget(QLabel(f"版本: {version}"))
        about_content_layout.addWidget(QLabel("作者: 菲梦林光"))
        about_content_layout.addWidget(QLabel("开源协议: CC BY-NC-SA 4.0"))
        project_link = QLabel('项目主页：<a href="https://github.com/xiwangzaiqianfang/AzurLane-Dex">GitHub 仓库</a>')
        project_link.setOpenExternalLinks(True)
        about_content_layout.addWidget(project_link)
        wiki_link = QLabel('Wiki主页：<a href="https://wiki.biligame.com/blhx/首页">碧蓝航线WIKI</a>')
        wiki_link.setOpenExternalLinks(True)
        about_content_layout.addWidget(wiki_link)

        check_update_btn = QPushButton("检查程序更新")
        check_update_btn.clicked.connect(self.check_program_update)
        about_content_layout.addWidget(check_update_btn)

        about_content_layout.addStretch()
        about_layout.addWidget(self.about_content)
        layout.addWidget(about_card)

    def change_password(self):
        if self.manager.need_password_for_edit():
            old_pwd, ok = QInputDialog.getText(self, "验证原密码", "请输入当前编辑密码:", QLineEdit.Password)
            if not ok or not self.manager.verify_edit_password(old_pwd):
                QMessageBox.warning(self, "错误", "原密码错误")
                return
        new_pwd, ok = QInputDialog.getText(self, "设置新密码", "请输入新密码（留空清除）:", QLineEdit.Password)
        if ok:
            self.manager.set_edit_password(new_pwd)
            if new_pwd:
                QMessageBox.information(self, "完成", "编辑密码已设置")
            else:
                QMessageBox.information(self, "完成", "编辑密码已清除")

    def update_data(self):
        if hasattr(self.main_window, 'update_online'):
            self.main_window.update_online()
        else:
            QMessageBox.warning(self, "错误", "无法调用更新功能")

    def on_log_toggled(self, checked):
        self.manager.config["log_edits"] = checked
        self.manager.save_config()

    def toggle_about(self):
        visible = not self.about_content.isVisible()
        self.about_content.setVisible(visible)
        self.about_btn.setText("▲" if visible else "▼")

    def check_program_update(self):
        QDesktopServices.openUrl(QUrl("https://github.com/xiwangzaiqianfang/AzurLane-Dex/releases"))

    def reset_window_geometry(self):
        self.main_window.reset_window_geometry()
        QMessageBox.information(self, "重置", "窗口大小已重置，下次启动将使用默认大小。")

    def update_window_size_label(self):
        size = self.main_window.size()
        self.window_size_label.setText(f"当前窗口大小: {size.width()} x {size.height()}")

    def showEvent(self, event):
        super().showEvent(event)
        self.update_window_size_label()