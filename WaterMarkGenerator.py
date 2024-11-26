import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, \
    QWidget, QFileDialog, QMessageBox, QGroupBox, QSizePolicy, QSpacerItem

import FileUtil
import WaterMarkUtil
from FileUtil import load_last_opened_path, save_last_opened_path
from WaterMarkDetail import DetailWindow


class MainWindow(QWidget):
    def __init__(self, _):
        super().__init__()
        self.QSpacerItem: QSpacerItem = None
        self.file_group_box: QGroupBox = None
        self.open_folder_button_clicked: bool = False
        self.line_edit_log_path: QLineEdit = None
        self.analyze_button: QPushButton = None
        self.open_folder_button: QPushButton = None
        self.app = _
        self.init()

    def init(self):
        self.setWindowTitle("MTK 平台相机水印生成 > Build 241126")
        self.setWindowIcon(QIcon(FileUtil.getRealPath(r'\favicon.ico')))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # 设置窗口大小
        screen_size = QApplication.primaryScreen().size()
        except_width = 600
        except_height = 160

        # 设置不允许拉伸窗口
        self.setFixedSize(except_width, except_height)
        self.setGeometry(int((screen_size.width() - except_width) / 2),
                         int((screen_size.height() - except_height) / 2),
                         except_width, except_height)

        # 创建布局
        file_layout = QVBoxLayout()
        file_layout.setAlignment(Qt.AlignVCenter)
        button_layout = QHBoxLayout()
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignTop)

        # 添加输入框
        self.line_edit_log_path = QLineEdit(self)
        self.line_edit_log_path.setFixedHeight(30)
        self.line_edit_log_path.setPlaceholderText("请选择黑底白字图片路径...")
        self.line_edit_log_path.setText(load_last_opened_path())
        file_layout.addWidget(self.line_edit_log_path)

        self.QSpacerItem = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        file_layout.addItem(self.QSpacerItem)

        # 添加按钮
        self.open_folder_button = QPushButton('选择水印图片', self)
        self.open_folder_button.setFixedHeight(40)
        self.open_folder_button.clicked.connect(self.open_log_folder)
        button_layout.addWidget(self.open_folder_button)

        self.analyze_button = QPushButton('开始编辑', self)
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.clicked.connect(self.start_generate)
        button_layout.addWidget(self.analyze_button)
        file_layout.addLayout(button_layout)

        # 分组布局
        self.file_group_box = QGroupBox("选择黑底白字图片", self)
        self.file_group_box.setLayout(file_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.file_group_box)

        # 设置主布局
        self.setLayout(main_layout)

    def open_log_folder(self):
        folder_path, _ = QFileDialog.getOpenFileName(self, "选择黑底白字图片", load_last_opened_path(), "Images (*.png)")
        if folder_path:
            self.line_edit_log_path.setText(folder_path)
            save_last_opened_path(folder_path)

    def start_generate(self):
        self.analyze_button.setEnabled(False)
        self.line_edit_log_path.setEnabled(False)

        image_path = self.line_edit_log_path.text()
        if not image_path or WaterMarkUtil.verify_image(image_path) is False:
            self.show_error_message("请选择正确的图片路径")
            self.analyze_button.setEnabled(True)
            self.line_edit_log_path.setEnabled(True)
            return
        detail_window = DetailWindow(app, image_path)
        detail_window.exec_()

        self.analyze_button.setEnabled(True)
        self.line_edit_log_path.setEnabled(True)

    def show_error_message(self, error_message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    real_path = FileUtil.getRealPath(r'\favicon.ico')
    app.setWindowIcon(QIcon(real_path))
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())