from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QCheckBox, QDialogButtonBox, QTextEdit, QGroupBox, QGridLayout, QSpinBox, QScrollArea,
                               QLabel, QWidget, QHBoxLayout, QPushButton, QAbstractSpinBox, QDateEdit, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QDate
from gui.add_ship_dialog import AddShipDialog
from models import Ship

class EditShipDialog(AddShipDialog):
    def __init__(self, ship: Ship, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"编辑舰船 - {ship.name}")
        self.ship = ship
        self.load_ship_data()

    def load_ship_data(self):
        """将现有船的数据填入各个控件"""
        self.id_spin.setValue(self.ship.id)
        self.name_edit.setText(self.ship.name)
        self.faction_combo.setCurrentText(self.ship.faction)
        self.class_combo.setCurrentText(self.ship.ship_class)
        self.rarity_combo.setCurrentText(self.ship.rarity)
        self.can_remodel_cb.setChecked(self.ship.can_remodel)
        if self.ship.remodel_date:
            self.remodel_date_edit.setDate(QDate.fromString(self.ship.remodel_date, "yyyy-MM-dd"))
        self.acquire_main_edit.setText(self.ship.acquire_main)
        self.acquire_detail_edit.setText(self.ship.acquire_detail)
        self.build_time_edit.setText(self.ship.build_time)
        self.drop_locations_edit.setText(";".join(self.ship.drop_locations))
        self.shop_exchange_edit.setText(self.ship.shop_exchange)
        self.is_permanent_cb.setChecked(self.ship.is_permanent)
        self.debut_event_edit.setText(self.ship.debut_event)
        self.release_date_edit.setDate(QDate.fromString(self.ship.release_date, "yyyy-MM-dd"))
        self.notes_edit.setText(self.ship.notes)
        self.image_path_edit.setText(self.ship.image_path)

        # 属性加成
        for key, spin in self.attr_spins.items():
            spin.setValue(getattr(self.ship, key, 0))

        # 科技点总和
        self.tech_points_obtain.setValue(self.ship.tech_points_obtain)
        self.tech_points_max.setValue(self.ship.tech_points_max)
        self.tech_points_120.setValue(self.ship.tech_points_120)

        # 适用舰种
        for sc in self.ship.tech_affects:
            if sc in self.affect_checkboxes:
                self.affect_checkboxes[sc].setChecked(True)

        # 其他状态（如 owned 等）在编辑时通常不修改，保持原样
        # 但也可以开放，根据需要决定

    def get_changes(self):
        """返回修改的字段字典，用于日志"""
        new_ship = self.get_ship()
        changes = {}
        for field in Ship.__dataclass_fields__.keys():
            old_val = getattr(self.ship, field)
            new_val = getattr(new_ship, field)
            if old_val != new_val:
                changes[field] = {"old": old_val, "new": new_val}
        return changes

    def get_ship(self):
        """复用父类的 get_ship，但返回新的 Ship 对象，不自动分配 ID"""
        # 调用父类方法，但跳过 ID 自动分配部分
        # 可以直接复用，只需确保 id 从原船保留
        ship = super().get_ship()
        ship.id = self.ship.id  # 保持原ID
        return ship