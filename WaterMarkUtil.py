from datetime import datetime

from PIL import Image
from PyQt5.QtGui import QImage, QPixmap


def verify_image(file_path):
    try:
        image = Image.open(file_path)
        print("Image format:", image.format)
        return image.format == 'PNG'
    except Exception as e:
        print("不正确的图片格式:", e)
        return False


def convert_image_to_yuv(file_path, value):
    image = Image.open(file_path).convert('L')  # 'L'模式表示灰度图
    width, height = image.size
    pixels = list(image.getdata())

    yuv_data = pixels  # 对于灰度图，Y分量就是像素值

    y_hex_data = [hex(y)[2:] for y in yuv_data]
    # if y < cc then y = 0 else y = ff
    for i in range(len(y_hex_data)):
        if int(y_hex_data[i], 16) < value:  # cc is 255 * 0.8 = 204
            y_hex_data[i] = '0'
        else:
            y_hex_data[i] = 'ff'

    u_hex_data = ['80'] * (width * height // 4)
    v_hex_data = ['80'] * (width * height // 4)

    return y_hex_data, u_hex_data, v_hex_data, width, height


def yuv_to_header_file(file_path, value=0xcc):
    print("当前阈值:", value / 255 * 100, "%")
    y_hex_data, u_hex_data, v_hex_data, width, height = convert_image_to_yuv(file_path, value)

    file_header_0 = "// Generated from WaterMarkGenerator by Wang RuiLong (me@shiro.la)\n"
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    file_header_0 += "// Generate Date " + formatted_time + "\n"
    file_header_0 += "// original image: " + file_path + "\n"
    file_header_0 += "// threshold value: " + str(value * 100 // 255) + "%\n"
    file_header_1 = '''#ifndef __SAMPLE_YUV_IMG__
#define __SAMPLE_YUV_IMG__

'''

    file_header_2 = "#define WATERMASKW " + str(width) + "\n"
    file_header_3 = "#define WATERMASKH " + str(height) + "  //must > 72" + "\n"
    file_header_4 = '''#define WATERMSAKSIZE (int)(WATERMASKW*WATERMASKH*1.5)

#define TIMEMASKW 684
#define TIMEMASKH 72
#define TIMEMSAKSIZE (int)(TIMEMASKW*TIMEMASKH*1.5)

const static unsigned char mWaterMask[WATERMSAKSIZE] ={
'''

    file_header_5 = '''};

struct hct_water_mark_param {

    double ratio_16_9;
    double ratio_1_1;
    double ratio_2_1;
    double ratio_4_3;
    double x_percent;
    double y_percent;
    double onscale_percent;

    hct_water_mark_param(){
        ratio_16_9 = 1.777778;
        ratio_1_1 = 1.000000;
        ratio_2_1 = 2.000000;
        ratio_4_3 =1.333333;
        x_percent = 0.02;
        y_percent = 0.03;
        onscale_percent = 0.270;
    }
};

#endif
    '''

    y_hex_data = ['0x' + x for x in y_hex_data]
    y_hex_data = [x.replace('0x0', '0x00') for x in y_hex_data]
    u_hex_data = ['0x' + x for x in u_hex_data]
    u_hex_data = [x.replace('0x0', '0x00') for x in u_hex_data]
    v_hex_data = ['0x' + x for x in v_hex_data]
    v_hex_data = [x.replace('0x0', '0x00') for x in v_hex_data]

    print("水印图片规格：", width, "x", height)

    file_name = 'yuv_img_para.h'
    full_file_name = file_path[:file_path.rfind('/')] + '/' + file_name
    with open(full_file_name, 'w', newline='\n') as file:
        file.write(file_header_0)
        file.write(file_header_1)
        file.write(file_header_2)
        file.write(file_header_3)
        file.write(file_header_4)
        for i in range(0, len(y_hex_data), 16):
            file.write(','.join(y_hex_data[i:i + 16]) + ',\n')
        for i in range(0, len(u_hex_data), 16):
            file.write(','.join(u_hex_data[i:i + 16]) + ',\n')
        for i in range(0, len(v_hex_data), 16):
            file.write(','.join(v_hex_data[i:i + 16]) + ',\n')
        file.write(file_header_5)


def restore_image(y_hex_data, width, height):
    image = Image.new('RGBA', (width, height))
    pixels = []

    for y in range(height):
        for x in range(width):
            # 获取当前像素的 Y 值（十六进制字符串转为整数）
            y_index = y * width + x
            y_value = int(y_hex_data[y_index], 16)

            # 根据 Y 值设置像素的透明度和颜色
            alpha = 0 if y_value == 0 else 255  # Y值为0时透明，否则不透明
            color = (255, 255, 255) if y_value == 255 else (0, 0, 0)  # Y值为255为白色，否则黑色
            pixels.append(color + (alpha,))

    image.putdata(pixels)
    return image


def read_yuv_data(file_path):
    yuv_data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            yuv_data.extend([int(x, 16) for x in line.strip().split(',') if x])
    return yuv_data


def yuv_to_pil_image(file_path, value=0xcc):
    y_hex_data, u_hex_data, v_hex_data, width, height = convert_image_to_yuv(file_path, value)
    image = restore_image(y_hex_data, width, height)
    return image


def pil_image_to_q_pixmap(pil_image):
    # 将 PIL 图像转换为 RGBA 格式（如果不是）
    pil_image = pil_image.convert("RGBA")
    # 提取原始数据
    data = pil_image.tobytes("raw", "RGBA")
    # 创建 QImage（PyQt 用于显示图像）
    image = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
    # 转为 QPixmap（PyQt 小部件使用的图像格式）
    return QPixmap.fromImage(image)
