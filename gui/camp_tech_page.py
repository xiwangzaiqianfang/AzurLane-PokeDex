from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
                               QGridLayout, QLabel, QFrame, QScrollArea, QPushButton,
                               QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class CampTechPage(QWidget):
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
        title = QLabel("阵营科技点")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # 描述
        desc = QLabel("各阵营科技点总和（获得 + 满破 + 120级）")
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

        # 所有阵营列表（可调整顺序）
        self.all_factions = [
            "白鹰", "皇家", "重樱", "铁血", "东煌", "撒丁帝国",
            "北方联合", "自由鸢尾", "维希教廷", "郁金王国", "飓风", "META", "其他"
        ]

        export_btn = QPushButton("导出为图片")
        export_btn.clicked.connect(self.export_as_image)
        main_layout.addWidget(export_btn, alignment=Qt.AlignCenter)

    def load_data(self):
        camp_tech = self.manager.calculate_camp_tech_points()

        # 清空现有卡片
        self.clear_layout(self.grid_layout)

        row, col = 0, 0
        max_cols = 3  # 每行3个卡片

        for faction in self.all_factions:
            camp_data = camp_tech.get(faction, {'obtain': 0, 'max': 0, 'level120': 0})
            obtain = camp_data['obtain']
            max_bt = camp_data['max']
            level120 = camp_data['level120']
            camp_sum = obtain + max_bt + level120

            card = self.create_card(faction, obtain, max_bt, level120, camp_sum)
            self.grid_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加一个伸缩占位，使最后一行左对齐
        self.grid_layout.setRowStretch(row + 1, 1)

    def create_card(self, faction, obtain, max_bt, level120, camp_sum):
        card = QFrame()
        card.setObjectName("statCard")  # 复用统计卡片样式
        card.setMinimumWidth(180)
        card.setFixedHeight(150)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 阵营名称
        faction_label = QLabel(faction)
        faction_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        faction_label.setFont(font)
        layout.addWidget(faction_label)

        # 三阶段数值行（水平布局）
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        obtain_label = QLabel(f"获得: {obtain}")
        obtain_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(obtain_label)

        max_label = QLabel(f"满破: {max_bt}")
        max_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(max_label)

        level120_label = QLabel(f"120级: {level120}")
        level120_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(level120_label)

        layout.addLayout(stats_layout)

        # 总和
        sum_label = QLabel(f"总和: {camp_sum}")
        sum_label.setAlignment(Qt.AlignCenter)
        font_sum = QFont()
        font_sum.setPointSize(12)
        font_sum.setBold(True)
        sum_label.setFont(font_sum)
        layout.addWidget(sum_label)

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