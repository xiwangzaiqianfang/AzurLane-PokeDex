from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QCheckBox, QDialogButtonBox, QTextEdit, QGroupBox, QGridLayout, QSpinBox, QScrollArea,
                               QLabel, QWidget, QHBoxLayout, QPushButton, QAbstractSpinBox)
from PySide6.QtCore import Qt
from models import Ship

class AddShipDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增舰船")
        self.resize(600, 700)
        main_layout = QVBoxLayout(self)
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll)
        # 滚动区域的内容容器
        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        # ---- 基本信息区域 ----
        basic_group = QGroupBox("基本信息")
        basic_form = QFormLayout(basic_group)
        id_layout = QHBoxLayout()
        self.id_spin = QSpinBox()
        self.id_spin.setRange(0, 9999)       # 允许范围，0 表示自动分配
        self.id_spin.setSpecialValueText("自动")  # 显示“自动”表示自动分配
        self.id_spin.setValue(0)              # 默认自动
        self.id_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.id_spin.setFixedWidth(80)
        id_minus = QPushButton("-")
        id_plus = QPushButton("+")
        id_minus.setFixedSize(25, 25)
        id_plus.setFixedSize(25, 25)
        id_minus.clicked.connect(lambda: self.id_spin.setValue(self.id_spin.value() - 1))
        id_plus.clicked.connect(lambda: self.id_spin.setValue(self.id_spin.value() + 1))
        id_layout.addWidget(self.id_spin)
        id_layout.addWidget(id_minus)
        id_layout.addWidget(id_plus)
        basic_form.addRow("编号 (0=自动):", self.id_spin)
        self.name_edit = QLineEdit()
        self.faction_combo = QComboBox()
        self.faction_combo.addItems(["白鹰", "皇家", "重樱", "铁血", "东煌", "撒丁帝国", "北方联合", "自由鸢尾", "维希教廷", "郁金王国", "飓风", "META", "其他"])
        self.class_combo = QComboBox()
        self.class_combo.addItems(["驱逐", "轻巡", "重巡", "超巡", "战巡", "战列", "航母", "轻航", "航战", "重炮", "维修", "潜艇", "潜母", "运输", "风帆"])
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["普通", "稀有", "精锐", "超稀有", "海上传奇", "最高方案", "决战方案"])
        self.acquire_main_edit = QLineEdit()
        self.acquire_detail_edit = QLineEdit()
        self.build_time_edit = QLineEdit()
        self.drop_locations_edit = QLineEdit()
        self.shop_exchange_edit = QLineEdit()
        self.is_permanent_cb = QCheckBox("常驻")
        self.is_permanent_cb.setChecked(True)
        self.debut_event_edit = QLineEdit()
        self.release_date_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        self.notes_edit.setMaximumHeight(80)
        self.image_path_edit = QLineEdit()

        basic_form.addRow("名称:", self.name_edit)
        basic_form.addRow("阵营:", self.faction_combo)
        basic_form.addRow("舰种:", self.class_combo)
        basic_form.addRow("稀有度:", self.rarity_combo)
        basic_form.addRow("主要获取方式:", self.acquire_main_edit)
        basic_form.addRow("详细信息:", self.acquire_detail_edit)
        basic_form.addRow("建造时间:", self.build_time_edit)
        basic_form.addRow("打捞地点(分号分隔):", self.drop_locations_edit)
        basic_form.addRow("商店兑换:", self.shop_exchange_edit)
        basic_form.addRow("", self.is_permanent_cb)
        basic_form.addRow("首次登场活动:", self.debut_event_edit)
        basic_form.addRow("实装时间:", self.release_date_edit)
        basic_form.addRow("备注:", self.notes_edit)
        basic_form.addRow("立绘地址:", self.image_path_edit)

        content_layout.addWidget(basic_group)

        # ---- 科技点组（三阶段） ----
        tech_group = QGroupBox("属性加成数值 (获得 / 满破 / 120级)")
        tech_layout = QGridLayout(tech_group)

        # 表头
        tech_layout.addWidget(QLabel("属性"), 0, 0)
        tech_layout.addWidget(QLabel("获得"), 0, 1)
        tech_layout.addWidget(QLabel(""), 0, 2)  # 留空用于按钮
        tech_layout.addWidget(QLabel("满破"), 0, 3)
        tech_layout.addWidget(QLabel(""), 0, 4)
        tech_layout.addWidget(QLabel("120级"), 0, 5)
        tech_layout.addWidget(QLabel(""), 0, 6)

        # 定义科技点属性列表
        tech_items = [
            ("耐久", "durability"),
            ("炮击", "firepower"),
            ("雷击", "torpedo"),
            ("防空", "aa"),
            ("航空", "aviation"),
            ("命中", "accuracy"),
            ("装填", "reload"),
            ("机动", "mobility"),
            ("反潜", "antisub")
        ]

        self.tech_spins = {}  # 用于存储所有科技点输入控件

        for row, (label, base) in enumerate(tech_items, start=1):
            tech_layout.addWidget(QLabel(label), row, 0)
            for col, suffix in enumerate(["obtain", "max", "120"]):
                # 创建水平布局放置 SpinBox 和两个按钮
                container = QWidget()
                hbox = QHBoxLayout(container)
                hbox.setContentsMargins(0, 0, 0, 0)
                hbox.setSpacing(2)

                spin = QSpinBox()
                spin.setRange(0, 10)
                spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
                spin.setAlignment(Qt.AlignRight)
                spin.setFixedWidth(70)  # 固定宽度
                hbox.addWidget(spin)

                minus_btn = QPushButton("-")
                #minus_btn.setFixedSize(25, 25)
                plus_btn = QPushButton("+")
                #plus_btn.setFixedSize(25, 25)

                # 连接按钮信号
                minus_btn.clicked.connect(lambda checked, s=spin: s.setValue(s.value() - 1))
                plus_btn.clicked.connect(lambda checked, s=spin: s.setValue(s.value() + 1))

                hbox.addWidget(minus_btn)
                hbox.addWidget(plus_btn)

                tech_layout.addWidget(container, row, col * 2 + 1, 1, 2)  # 跨越两列
                self.tech_spins[f"tech_{base}_{suffix}"] = spin

        content_layout.addWidget(tech_group)


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        content_layout.addWidget(button_box)

    def get_ship(self):
        # 获取用户输入的 ID
        manual_id = self.id_spin.value()
        ship_id = 0 if manual_id == 0 else manual_id  # 0 表示需要自动分配

        # 从科技点SpinBox收集值
        tech_kwargs = {}
        for key, spin in self.tech_spins.items():
            tech_kwargs[key] = spin.value()
        
        ship = Ship(
            id=ship_id, # 将由管理器自动分配
            name=self.name_edit.text(),
            faction=self.faction_combo.currentText(),
            ship_class=self.class_combo.currentText(),
            rarity=self.rarity_combo.currentText(),
            owned=False,
            breakthrough=0,
            can_remodel=False,
            remodeled=False,
            oath=False,
            level_120=False,
            acquire_main=self.acquire_main_edit.text(),
            acquire_detail=self.acquire_detail_edit.text(),
            build_time=self.build_time_edit.text(),
            drop_locations=[s.strip() for s in self.drop_locations_edit.text().split(';') if s.strip()],
            shop_exchange=self.shop_exchange_edit.text(),
            is_permanent=self.is_permanent_cb.isChecked(),
            debut_event=self.debut_event_edit.text(),
            release_date=self.release_date_edit.text(),
            notes=self.notes_edit.toPlainText(),
            **tech_kwargs,
            image_path = self.image_path_edit.text()
        )
        print(f"新建舰船: id={ship.id}, name={ship.name}, 科技点: {ship.tech_durability_obtain}")
        return ship