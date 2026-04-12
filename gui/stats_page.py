from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame,
                               QPushButton, QFileDialog, QMessageBox, QProgressBar,
                               QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os

class StatPage(QWidget):
    def __init__(self, manager, main_window):
        super().__init__()
        self.manager = manager
        self.main_window = main_window
        self.setup_ui()
        self.load_stats()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        main_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        title = QLabel("统计概览")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        content_layout.addWidget(title)

        self.desc_label = QLabel("收集进度一览 · 数据实时更新")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setStyleSheet("font-size: 12px; color: #888; margin-top: 5px;")
        content_layout.addWidget(self.desc_label)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        content_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.progress_bar)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        content_layout.addLayout(self.grid_layout)

        self.stat_items = [
            ("总计舰船", "total"),
            ("已获得", "owned"),
            ("未获得", "not_owned"),
            ("已满破", "max_break"),
            ("未满破", "not_max"),
            ("已誓约", "oath"),
            ("已改造", "remodeled"),
            ("可改造未改造", "can_remodel_not"),
            ("120级", "level120"),
            ("已获得特殊兵装", "special_gear_obtained"),
            ("未获得特殊兵装", "special_gear_not_obtained"),
        ]

        self.card_labels = {}  # 存储每个统计项的数值标签
        for idx, (name, key) in enumerate(self.stat_items):
            row = idx // 3
            col = idx % 3
            card = self.create_card(name, key)
            self.grid_layout.addWidget(card, row, col)

        self.export_btn = QPushButton("导出为图片")
        self.export_btn.clicked.connect(self.export_as_image)
        content_layout.addWidget(self.export_btn, alignment=Qt.AlignCenter)

    def create_card(self, title, key):
        card = QFrame()
        card.setObjectName("statCard")
        card.setFrameShape(QFrame.NoFrame)
        card.setFixedHeight(120)
        card.setMinimumWidth(150)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        value_label = QLabel("0")
        value_label.setObjectName("statValue")
        value_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        value_label.setFont(font)
        layout.addWidget(value_label)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.card_labels[key] = value_label
        return card

    def load_stats(self):
        stats_dict = self.manager.stats()
        for key, label in self.card_labels.items():
            label.setText(str(stats_dict.get(key, 0)))

        total = stats_dict.get('total', 1)
        owned = stats_dict.get('owned', 0)
        remodeled = stats_dict.get('remodeled', 0)
        can_remodel_total = stats_dict.get('can_remodel_total', 0)
        numerator = owned + remodeled
        denominator = total + can_remodel_total
        if denominator == 0:
            denominator = 1
        percent = int(numerator / denominator * 100)
        self.progress_label.setText(f"收集进度: {percent}% ({numerator}/{denominator})")
        self.progress_bar.setRange(0, denominator)
        self.progress_bar.setValue(numerator)

    def export_as_image(self):
        # 截图范围：从标题到导出按钮（不包括按钮本身）
        # 获取整个页面中需要截图的区域：标题+描述+卡片网格
        # 为了避免截图到滚动区域外的内容，我们创建一个临时控件来渲染统计内容
        # 简单方法：截取整个页面，但用户可能希望只截取统计部分
        # 这里截取从标题到卡片网格结束的区域
        # 由于 self 是 StatPage，我们可以直接 grab 整个页面，然后裁剪
        scroll_area = self.findChild(QScrollArea)
        if not scroll_area:
            pixmap = self.grab()  # 抓取整个 StatPage 控件
        else:
            content_widget = scroll_area.widget()
            if content_widget:
                # 获取内容部件的实际大小
                size = content_widget.size()
                # 创建足够大的 pixmap
                pixmap = QPixmap(size)
                # 将内容部件渲染到 pixmap
                content_widget.render(pixmap)
            else:
                pixmap = self.grab()
        # 保存到文件
        file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", "statistics.png", "PNG (*.png)")
        if file_path:
            if pixmap.save(file_path):
                QMessageBox.information(self, "成功", f"图片已保存至：{file_path}")
            else:
                QMessageBox.warning(self, "失败", "保存图片失败，请重试。")