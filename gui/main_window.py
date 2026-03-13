import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QSplitter, QMessageBox, QFileDialog, QApplication, QPushButton, QDialog)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QFont

from manager import ShipManager
from gui.filter_bar import FilterBar
from gui.ship_list_widget import ShipListWidget
from gui.detail_widget import DetailWidget
from gui.stat_dialog import StatDialog
from gui.add_ship_dialog import AddShipDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("碧蓝航线本地图鉴")
        self.resize(1200, 800)

        # 初始化设置存储（使用公司名和应用名，可自定义）
        self.settings = QSettings("菲梦林光", "AzurLanePokedex")

        # 加载样式表
        #with open("gui/style.qss", "r", encoding='utf-8') as f:
        #    self.setStyleSheet(f.read())

        # 初始化数据管理器
        self.manager = ShipManager("ships.json")

        # 创建中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # 顶部工具栏布局（包含筛选栏和主题切换按钮）
        top_layout = QHBoxLayout()
        self.filter_bar = FilterBar()
        top_layout.addWidget(self.filter_bar)
        
        # 主题切换按钮
        self.theme_btn = QPushButton("切换主题")
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_btn)

        main_layout.addLayout(top_layout)

        # 中间分割区域
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)  # 拉伸因子1

        # 左侧列表
        self.ship_list = ShipListWidget()
        splitter.addWidget(self.ship_list)

        # 右侧详情
        self.detail_widget = DetailWidget()
        splitter.addWidget(self.detail_widget)

        # 设置初始比例
        splitter.setSizes([300, 900])

        # 连接信号
        self.filter_bar.filter_changed.connect(self.apply_filter)
        self.filter_bar.reset_clicked.connect(self.reset_filter)
        self.filter_bar.stat_clicked.connect(self.show_stat_dialog)
        self.filter_bar.add_ship_clicked.connect(self.show_add_ship_dialog)
        self.filter_bar.switch_file_clicked.connect(self.switch_file)
        self.filter_bar.export_clicked.connect(self.export_data)
        self.filter_bar.import_clicked.connect(self.import_data)
        self.filter_bar.update_online_clicked.connect(self.update_online)

        self.ship_list.current_ship_changed.connect(self.on_ship_selected)
        self.ship_list.sort_requested.connect(self.on_sort_requested)

        self.detail_widget.data_changed.connect(self.on_ship_updated)

        # 加载主题
        self.load_theme()

        # 初始加载全部舰船
        self.apply_filter({})

        
    def load_theme(self):
        """加载保存的主题，并将样式表应用到整个应用"""
        theme = self.settings.value("theme", "light")  # 默认浅色
        style_file = f"./style_{theme}.qss"
        # 获取当前文件所在目录的绝对路径
        base_dir = os.path.dirname(__file__)
        style_path = os.path.join(base_dir, style_file)
        #print(f"Loading theme: {theme}, path: {style_path}") #1
        if os.path.exists(style_path):
            with open(style_path, "r", encoding='utf-8') as f:
                #qss = f.read() #2
                #print(f"QSS content length: {len(qss)}") #3
                #print(f"QSS preview: {qss[:200]}") #4
                QApplication.instance().setStyleSheet(f.read())
        else:
            print(f"样式文件不存在: {style_path}")

    def toggle_theme(self):
        """切换深色/浅色主题"""
        current = self.settings.value("theme", "light")
        new_theme = "dark" if current == "light" else "light"
        self.settings.setValue("theme", new_theme)
        self.load_theme()
        # 强制刷新界面
        self.repaint()

    def apply_filter(self, criteria):
        filtered = self.manager.filter(criteria)
        # 排序（默认按编号）
        filtered = self.manager.sort(filtered, key="id")
        self.ship_list.set_ships(filtered)
        if filtered:
            self.ship_list.selectRow(0)   # 默认选中第一项
        else:
            self.detail_widget.clear()

    def reset_filter(self):
        self.filter_bar.reset()
        self.apply_filter({})

    def on_ship_selected(self, ship):
        if ship:
            self.detail_widget.set_ship(ship)
        else:
            self.detail_widget.clear()
        
    def on_ship_updated(self, ship):
        # 更新数据管理器中的对应船
        for i, s in enumerate(self.manager.ships):
            if s.id == ship.id:
                self.manager.ships[i] = ship
                break
        self.manager.save()
        # 刷新左侧列表显示
        self.ship_list.update_ship(ship)
        if ship:
            print(f"Selected ship: {ship.id}, owned={ship.owned}, oath={ship.oath}, level120={ship.level_120}")
            self.detail_widget.set_ship(ship)
        else:
            self.detail_widget.clear()

        # 连接信号（确保在创建 detail_widget 之后）
        #self.detail_widget.data_changed.connect(self.on_ship_updated)

    def on_sort_requested(self, key, reverse):
        filtered = self.ship_list.current_ships  # 当前显示的列表
        sorted_ships = self.manager.sort(filtered, key, reverse)
        self.ship_list.set_ships(sorted_ships)

    def show_stat_dialog(self):
        not_owned, not_max = self.manager.stats()
        dlg = StatDialog(not_owned, not_max, self)
        dlg.exec()

    def show_add_ship_dialog(self):
        print("打开新增舰船对话框")
        dlg = AddShipDialog(self)
        if dlg.exec() == QDialog.Accepted:
            print("用户点击确定")
            new_ship = dlg.get_ship()
            print(f"获取到新船: {new_ship.name}")
            self.manager.add_ship(new_ship)
            print("已调用 manager.add_ship")
            # 刷新列表（可能需要重新应用当前筛选）
            self.apply_filter(self.filter_bar.get_criteria())
        else:
            print("用户取消")

    def switch_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 JSON 数据文件", "", "JSON (*.json)")
        if path:
            try:
                self.manager.switch_file(path)
                self.apply_filter({})
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载文件失败: {e}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出数据", "", "CSV (*.csv);;Excel (*.xlsx)")
        if path:
            if path.endswith('.csv'):
                self.manager.export_csv(path)
            elif path.endswith('.xlsx'):
                self.manager.export_excel(path)
            QMessageBox.information(self, "完成", "导出成功！")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入数据", "", "CSV (*.csv);;Excel (*.xlsx)")
        if path:
            try:
                self.manager.import_csv(path)  # 仅支持 CSV，Excel 也可用 pandas 读取
                self.apply_filter({})
                QMessageBox.information(self, "完成", "导入成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def update_online(self):
        """从网络更新数据"""
    # 可以弹出一个对话框让用户输入 URL，或者使用固定的默认 URL
        default_url = "https://raw.githubusercontent.com/xiwangzaiqianfang/AzurLane-Dex/main/ships.json"
    
    # 简单的确认对话框
        reply = QMessageBox.question(
            self, 
            "确认更新", 
            f"将从以下地址更新数据：\n{default_url}\n\n您的当前状态（拥有、突破等）会被保留，是否继续？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            success = self.manager.update_from_github(default_url)
            if success:
                self.apply_filter(self.filter_bar.get_criteria())
                QMessageBox.information(self, "完成", "数据更新成功！")
            else:
                QMessageBox.information(self, "无需更新", "当前已是最新版本。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败：{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()