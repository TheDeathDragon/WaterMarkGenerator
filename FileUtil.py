import os
import tempfile


def save_last_opened_path(path):
    # 获取系统的临时目录
    temp_dir = tempfile.gettempdir()

    # 在临时目录中创建一个文件来保存最后打开的路径
    temp_file_path = os.path.join(temp_dir, "watermark_path.txt")

    # 将路径写入临时文件
    with open(temp_file_path, "w") as temp_file:
        temp_file.write(path)


def load_last_opened_path():
    # 获取系统的临时目录
    temp_dir = tempfile.gettempdir()

    # 拼接临时文件的路径
    temp_file_path = os.path.join(temp_dir, "watermark_path.txt")

    # 检查文件是否存在
    if os.path.exists(temp_file_path):
        with open(temp_file_path, "r") as temp_file:
            last_path = temp_file.read()
            return last_path
    else:
        print("没有保存的最后打开路径")
        return os.getcwd()
