from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QBrush

class ShipListWidget(QTableWidget):
    current_ship_changed = Signal(object)   # 发出 Ship 对象
    sort_requested = Signal(str, bool)      # (key, reverse)

    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["编号", "名称", "拥有", "突破", "誓约"])
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.horizontalHeader().setStretchLastSection(False)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 50)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_indicator_changed)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        #self.setDragEnabled(False)          # 允许拖动选择（不影响触摸滚动）
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)  # 平滑滚动
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.current_ships = []  # 当前显示的 Ship 对象列表，与行对应

    def set_ships(self, ships):
        self.itemSelectionChanged.disconnect(self.on_selection_changed)
        
        self.current_ships = ships
        self.setRowCount(len(ships))
        for row, ship in enumerate(ships):
            self.setItem(row, 0, QTableWidgetItem(str(ship.id)))
            self.setItem(row, 1, QTableWidgetItem(ship.name))
            owned_item = QTableWidgetItem("✓" if ship.owned else "✗")
            owned_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, owned_item)

            bt_text = str(ship.breakthrough)
            if ship.is_max_breakthrough():
                bt_text = "满破"
            elif ship.breakthrough == 0:
                bt_text = str(ship.breakthrough)
            bt_item = QTableWidgetItem(bt_text)
            bt_item.setTextAlignment(Qt.AlignCenter)
            bt_item.setData(Qt.UserRole, ship.breakthrough)
            self.setItem(row, 3, bt_item)

            oath_item = QTableWidgetItem("❤" if ship.oath else "✗")
            oath_item.setTextAlignment(Qt.AlignCenter)
            oath_item.setData(Qt.UserRole, ship.oath)  # 存储布尔值用于排序
            self.setItem(row, 4, oath_item)

        # 默认选中第一行
        if ships:
            self.selectRow(0)

        self.itemSelectionChanged.connect(self.on_selection_changed)
        
    def update_ship(self, ship):
        # 临时断开 selection 信号，避免循环
        self.itemSelectionChanged.disconnect(self.on_selection_changed)

        for row, s in enumerate(self.current_ships):
            if s.id == ship.id:
                # 更新 current_ships 中的对象引用
                self.current_ships[row] = ship
                # 更新表格显示
                self.item(row, 2).setText("✓" if ship.owned else "✗")
                bt_text = "满破" if ship.breakthrough == 3 else str(ship.breakthrough)
                self.item(row, 3).setText(bt_text)
                self.item(row, 3).setData(Qt.UserRole, ship.breakthrough)
                self.item(row, 4).setText("❤" if ship.oath else "✗")
                self.item(row, 4).setData(Qt.UserRole, ship.oath)
                # 如果当前选中的就是这一行，可以更新详情（但为避免循环，通常不需要）
                break

        # 重新连接信号
        self.itemSelectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        row = self.currentRow()
        if 0 <= row < len(self.current_ships):
            self.current_ship_changed.emit(self.current_ships[row])
        else:
            self.current_ship_changed.emit(None)

    def on_sort_indicator_changed(self, logicalIndex, order):
        # 根据列索引确定排序字段
        key_map = {0: "id", 1: "name", 3: "rarity", 4: "oath"}  # 突破列也可以排序，但这里简化
        if logicalIndex in key_map:
            reverse = (order == Qt.DescendingOrder)
            self.sort_requested.emit(key_map[logicalIndex], reverse)

    def get_current_ship(self):
        row = self.currentRow()
        if 0 <= row < len(self.current_ships):
            return self.current_ships[row]
        return None