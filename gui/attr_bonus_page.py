from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
                               QGridLayout, QLabel, QFrame, QScrollArea, QPushButton,
                               QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class AttrBonusPage(QWidget):
    def __init__(self, manager, main_window):
        super().__init__()
        self.manager = manager
        self.main_window = main_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 标题
        title = QLabel("属性加成")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # 描述
        desc = QLabel("全舰队属性加成汇总")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 12px; color: #888; margin-bottom: 10px;")
        main_layout.addWidget(desc)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        main_layout.addWidget(scroll)

        # 卡片容器
        self.card_container = QWidget()
        scroll.setWidget(self.card_container)

        # 网格布局
        self.grid_layout = QGridLayout(self.card_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # 属性列表（中文显示，对应 global_bonuses 中的属性键）
        self.attr_list = [
            "耐久", "炮击", "雷击", "防空", "航空",
            "命中", "装填", "机动", "反潜"
        ]

        # 存储卡片中的数值标签
        self.card_labels = {}

        export_btn = QPushButton("导出为图片")
        export_btn.clicked.connect(self.export_as_image)
        main_layout.addWidget(export_btn, alignment=Qt.AlignCenter)

    def load_data(self):
        global_bonuses = self.manager.calculate_global_bonuses()

        # 清空现有卡片
        self.clear_layout(self.grid_layout)

        row, col = 0, 0
        max_cols = 3  # 每行3个卡片

        attr_totals = {attr: 0 for attr in self.attr_list}
        for (ship_class, attr), value in global_bonuses.items():
            if attr in attr_totals:
                attr_totals[attr] += value

        self.clear_layout(self.grid_layout)
        row, col = 0, 0
        max_cols = 3
        for attr, total in attr_totals.items():
            card = self.create_card(attr, total)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        self.grid_layout.setRowStretch(row + 1, 1)

    def create_card(self, attr, total):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumWidth(150)
        card.setFixedHeight(100)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        attr_label = QLabel(attr)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        attr_label.setFont(font)
        layout.addWidget(attr_label)

        value_label = QLabel(str(total))
        value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(value_label)
        return card

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def export_as_image(self):
        # 截取整个页面
        pixmap = self.grab()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", "fleet_tech.png", "PNG (*.png)")
        if file_path:
            if pixmap.save(file_path):
                QMessageBox.information(self, "成功", f"图片已保存至：{file_path}")
            else:
                QMessageBox.warning(self, "失败", "保存图片失败，请重试。")