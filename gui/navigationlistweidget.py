from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Signal, Qt

class NavigationListWidget(QListWidget):
    rowReleased = Signal(int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressed_row = -1

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # 记录按下的行
        self.pressed_row = self.currentRow()
        print("按下行:", self.pressed_row)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # 只有当释放的行和按下的行相同时才发出信号
        current_row = self.currentRow()
        print("释放行:", current_row)
        if current_row == self.pressed_row and current_row != -1:
            self.rowReleased.emit(current_row)
            print("发射信号")
        self.pressed_row = -1