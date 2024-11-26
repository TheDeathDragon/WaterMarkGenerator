from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QGroupBox, \
    QFileDialog, QMessageBox, QDialog

import WaterMarkUtil
from FileUtil import save_last_opened_path


class DetailWindow(QDialog):
    def __init__(self, app, path):
        super().__init__()
        self.app = app
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowMaximizeButtonHint |
                            Qt.WindowCloseButtonHint)

        print("参数传递路径 >", path)
        self.path = path
        self.setWindowTitle("当前路径 > " + self.path)

        # 创建主窗口布局
        self.main_layout = QVBoxLayout()
        self.upper_layout = QHBoxLayout()

        # 创建滑块布局
        self.slider_layout = QHBoxLayout()
        self.slider_layout.setAlignment(Qt.AlignCenter)

        # 创建按钮布局
        self.button_layout = QHBoxLayout()

        # 图片预览布局
        self.image_layout = QHBoxLayout()

        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(80)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider_layout.addWidget(self.slider)

        # 滑块值标签
        self.value_label = QLabel("阈值： 80%")  # 初始值
        self.value_label.setFixedWidth(150)  # 固定宽度以对齐
        self.value_label.setAlignment(Qt.AlignCenter)
        self.slider_layout.addWidget(self.value_label)

        # 切换背景颜色按钮
        self.change_bg_button = QPushButton("切换预览背景")
        self.change_bg_button.setFixedHeight(40)
        self.change_bg_button.setFixedWidth(220)
        self.change_bg_button.clicked.connect(self.on_change_bg_button_click)
        self.button_layout.addWidget(self.change_bg_button)
        self.current_bg_state = 0

        # 重新选择文件按钮
        self.reset_button = QPushButton("重新选择文件")
        self.reset_button.setFixedHeight(40)
        self.reset_button.setFixedWidth(220)
        self.reset_button.clicked.connect(self.on_reset_button_click)
        self.button_layout.addWidget(self.reset_button)

        # 生成按钮
        self.generate_button = QPushButton("生成水印文件")
        self.generate_button.setFixedHeight(40)
        self.generate_button.setFixedWidth(220)
        self.generate_button.clicked.connect(self.on_generate_button_click)
        self.button_layout.addWidget(self.generate_button)

        # 图片预览组件
        self.image_preview = QLabel()
        self.image_preview.setPixmap(QPixmap(200, 150))  # 设置初始空白图片大小
        self.image_preview.setScaledContents(False)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("background-color: black;")
        self.image_layout.addWidget(self.image_preview)
        self.color_index = 0

        # 将滑块和按钮的布局加入 GroupBox
        config_group_box = QGroupBox("水印配置")
        config_group_box.setFixedHeight(100)
        config_group_box.setFixedWidth(600)
        config_group_box.setLayout(self.slider_layout)

        opt_group_box = QGroupBox("文件操作")
        opt_group_box.setFixedHeight(100)
        opt_group_box.setLayout(self.button_layout)

        self.preview_group_box = QGroupBox("水印预览")
        self.preview_group_box.setLayout(self.image_layout)

        self.upper_layout.addWidget(config_group_box)
        self.upper_layout.addWidget(opt_group_box)
        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addWidget(self.preview_group_box)
        self.setLayout(self.main_layout)
        self.draw_preview_image(self.slider.value())

    def slider_value_changed(self, value):
        # 滑块值改变时更新标签
        self.value_label.setText("阈值： " + str(value) + "%")
        self.draw_preview_image(value)

    def on_generate_button_click(self):
        # 按钮点击时的处理逻辑
        self.save_header_file()

    def on_reset_button_click(self):
        # 重新选择文件
        self.reset_button.setEnabled(False)
        self.open_log_folder()
        self.reset_button.setEnabled(True)

    def set_clipboard_text(self):
        clipboard = self.app.clipboard()
        clipboard.setText("alps/vendor/mediatek/proprietary/hardware/mtkcam3/3rdparty/customer/cp_watermark/")

    def change_color(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#D3D3D3", "#A9A9A9", "#FFFFFF", "#000000"]
        self.image_preview.setStyleSheet(f"background-color: {colors[self.color_index]};")
        self.image_preview.repaint()
        self.color_index = (self.color_index + 1) % len(colors)

    def on_change_bg_button_click(self):
        self.change_color()

    def open_log_folder(self):
        dir_path = self.path[:self.path.rfind('/')]
        image_path, _ = QFileDialog.getOpenFileName(self, "选择黑底白字图片", dir_path, "Images (*.png)")
        if not image_path or WaterMarkUtil.verify_image(image_path) is False:
            self.show_error_message("请选择正确的图片路径")
            return
        self.setWindowTitle("当前路径 > " + image_path)
        self.path = image_path
        self.draw_preview_image(self.slider.value())
        save_last_opened_path(image_path)

    def draw_preview_image(self, value):
        # 绘制预览图片
        image = WaterMarkUtil.yuv_to_pil_image(self.path, value * 255 // 100)
        self.image_preview.setPixmap(WaterMarkUtil.pil_image_to_q_pixmap(image))

    def save_header_file(self):
        # 保存头文件
        WaterMarkUtil.yuv_to_header_file(self.path, self.slider.value() * 255 // 100)
        self.set_clipboard_text()
        self.show_info_message("头文件保存在图片同目录下的 yuv_img_para.h 文件中\n同时已将服务器路径复制到剪贴板")

    def show_info_message(self, info):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("信息")
        msg_box.setText(info)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_error_message(self, error_message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
