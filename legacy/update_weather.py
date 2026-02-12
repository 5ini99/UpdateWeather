import configparser
import sys
import os
import requests
import datetime
import binascii
import re
import hid
import tkinter as tk
from psutil import *
from PIL import Image, ImageDraw, ImageFont
from tkinter import messagebox
from pathlib import Path
from tkinter import simpledialog, messagebox

import tkinter.simpledialog as simpledialog

config = configparser.ConfigParser()

USER_CONFIG_DIR = Path.home() / ".update-weather"
USER_CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_PATH = USER_CONFIG_DIR / "config.ini"

# PyInstaller 打包后临时目录
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding="utf-8")

root = tk.Tk()
root.withdraw()

# 如果没有 key，就弹窗输入
if not config.has_option('weather', 'key') or not config.get('weather', 'key'):
    key = simpledialog.askstring("请输入 Key", "请输入你的和风天气 API key：")
    if not key:
        messagebox.showerror('错误', "未填写和风天气 API key")
        exit()
    if not config.has_section('weather'):
        config.add_section('weather')
    config.set('weather', 'key', key)
else:
    key = config.get('weather', 'key')

# 如果没有 location，就弹窗输入
if not config.has_option('weather', 'location') or not config.get('weather', 'location'):
    location = simpledialog.askstring("请输入 Location", "请输入你的城市：")
    if not location:
        messagebox.showerror('错误', "未填写 'location' 参数")
        exit()
    if not config.has_section('weather'):
        config.add_section('weather')
    config.set('weather', 'location', location)
else:
    location = config.get('weather', 'location')

# 保存回 config.ini
with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    config.write(f)

# 使用和风天气api
params = {
    'key': key,
    'location': location,
    'language': 'zh',
    'unit': 'm'
}

params3 = {
    'key': key,
    'location': location
}

session = requests.Session()

url = 'https://devapi.qweather.com/v7/weather/3d'
url_today = 'https://devapi.qweather.com/v7/weather/now'
url_minutely = 'https://devapi.qweather.com/v7/minutely/5m'
url_name = 'https://geoapi.qweather.com/v2/city/lookup'

try:
    with session.get(url, params=params) as r, session.get(url_today, params=params) as t, session.get(url_name, params=params3) as n:
        r.raise_for_status()
        t.raise_for_status()
        n.raise_for_status()

        try:
            data = r.json()['daily']
        except KeyError:
            raise ValueError(r.text)
        
        data_today = t.json()['now']

        today = data[0]['fxDate']
        
        tempmin = data[0]['tempMin']
        tempmax = data[0]['tempMax']

        textDay = data[0]['textDay']
        textNight = data[0]['textNight']

        tempnow = data_today['temp']

        iconDay = data[0]['iconDay']
        iconNight = data[0]['iconNight']

        print('获取当前天气'+today)
        
        data_name = n.json()['location']
        data_name2 = data_name[0]['name']

        lat = round(float(data_name[0]['lat']), 2)
        lon = round(float(data_name[0]['lon']), 2)
        print('城市名: ' + data_name2)
        print('经纬度: ' + str(lat)+"-"+str(lon))



except requests.exceptions.RequestException as e:
    error_message = str(e)
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('错误', "请检查网络连接")
    exit()

except (KeyError, ValueError) as e:
    error_message = str(e)
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('错误', "请检查key或location输入是否正确\n" + error_message)
    exit()

params2 = {
    'key': key,
    'location': str(lon)+","+str(lat),
    'language': 'zh',
    'unit': 'm'
}

try:
    with session.get(url_minutely, params=params2) as d:
        d.raise_for_status()


        data_minutely = d.json()['summary']
        print('分钟预报: ' + data_minutely)

except requests.exceptions.RequestException as e:
    error_message = str(e)
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('错误', "请检查网络连接")
    exit()

except (KeyError, ValueError) as e:
    error_message = str(e)
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('错误', "请检查key或location输入是否正确\n" + error_message)
    exit()

# 定义数字图片和线条图片的路径
image_path = BASE_DIR / "img/"
line_path = BASE_DIR / "img/line.png"
cpu_path = BASE_DIR / "img/cpu.png"
bai_path = BASE_DIR / "img/%.png"
men_path = BASE_DIR / "img/men.png"
gb_path = BASE_DIR / "img/g.png"
chinese_path = BASE_DIR / "img/"
nowtemp_path = BASE_DIR / "img/nowtemp.png"
wave_path = BASE_DIR / "img/wave.png"
cpu_hx_img_path=BASE_DIR / "img/cpu_img/0.png"
cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/8_hexinkuang.png"

# 定义要解析的日期字符串和中文字符串
date_str = today
iconDay_str = iconDay
iconNight_str  = iconNight
textDay_str = textDay
textNight_str = textNight

# 获取当前是星期几
year, month, day = map(int, date_str.split('-'))
date = datetime.date(year, month, day)
weekday = date.strftime("%A")
# 根据星期切换图片
weekday2 = date.strftime("%A")+"2"

# 将日期字符串解析成数字列表和线条数量
digits = [int(d) if d.isdigit() else "-" for d in date_str]
num_lines = date_str.count("-")

# 将CPU数据解析成数字列表和线条数量
cpu_shiyonglv = cpu_percent(interval=2)

#cpu_shiyonglv = 100.0

if cpu_shiyonglv >=10:
    cpu = str(int(cpu_shiyonglv))
    cpu_xinxi = [int(d) if d.isdigit() else "." for d in cpu]
else:
    cpu = str(cpu_shiyonglv)
    cpu_xinxi = [int(d) if d.isdigit() else "." for d in cpu]

print(cpu_shiyonglv)
print(cpu)
print(cpu_xinxi)

cpu_hexin = cpu_percent(percpu=True)

# 计算cpu字符串的长度
# cpu_str_len = len(cpu)
# if cpu_str_len == 5:
#     cpu_xinxi =[1,0,0]

# print("CPU使用率：",cpu_str_len)
# print("CPU使用率：",cpu)
# print("CPU使用率：",cpu_xinxi)

# 读取内存信息
mem = virtual_memory()

# 获取总内存
mem_total1 = round((float(mem.total) / 1024 / 1024 / 1024),0)
# 总内存字符长度
mem_total_str_len = len(str(mem_total1))
# 如果总内存字符长度不等于4或5则保留小数
mem_total2 = str(mem_total1)
# 果总内存字符长度等于4或5，转为整数
if mem_total_str_len == 5:
    mem_total2 = str(int(mem_total1))
elif mem_total_str_len == 4:
    mem_total2 = str(int(mem_total1))
# 将内存总量数据解析成数字列表
mem_total_xinxi = [int(d) if d.isdigit() else "." for d in mem_total2]


# 获取内存使用率并转为整数
mem_percent = str(int(mem.percent))
# 计算内存使用率字符串的长度
mem_percent_str_len = len(mem_percent)
# 内存使用率字符串在新图片上的水平偏移量
if mem_percent_str_len == 3:
    x_offset4 = 75
elif mem_percent_str_len == 2:
    x_offset4 = 87
else:
    x_offset4 = 99
# 将内存使用率数据解析成数字列表
mem_percent_xinxi = [int(d) if d.isdigit() else "." for d in mem_percent]


print("CPU使用率：",cpu)
print("内存总量: ",mem_total1,"内存使用率：", mem_percent, "%")

# 将温度值转换为带有符号的字符串
tempmin_digits = [d for d in tempmin if d.isdigit() or d == "-"]
tempmin_int = int("".join(tempmin_digits))
tempmin_str = "{:d}".format(tempmin_int)

tempmax_digits = [d for d in tempmax if d.isdigit() or d == "-"]
tempmax_int = int("".join(tempmax_digits))
tempmax_str = "{:d}".format(tempmax_int)

tempnow_digits = [d for d in tempnow if d.isdigit() or d == "-"]
tempnow_int = int("".join(tempnow_digits))
tempnow_str = "{:d}".format(tempnow_int)

# 计算温度值字符串的长度
tempmin_str_len = len(tempmin_str)
tempmax_str_len = len(tempmax_str)
tempnow_str_len = len(tempnow_str)

# 计算温度值字符串在新图片上的水平偏移量
if tempmin_str_len == 3:
    tempmin_offset_x =(64 - (12 * 3 + 8)) // 2
elif tempmin_str_len == 2:
    tempmin_offset_x = (64 - (12 * 2 + 8)) // 2
else:
    tempmin_offset_x = (64 - (12 * 1 + 8)) // 2

if tempmax_str_len == 3:
    tempmax_offset_x = 64 + (64 - (12 * 3 + 8)) // 2
elif tempmax_str_len == 2:
    tempmax_offset_x = 64 + (64 - (12 * 2 + 8)) // 2
else:
    tempmax_offset_x = 64 + (64 - (12 * 1 + 8)) // 2

if tempnow_str_len == 3:
    tempnow_offset_x2 = 4
    tempnow_offset_x = 80
elif tempnow_str_len == 2:
    tempnow_offset_x2 = 9
    tempnow_offset_x = 87
else:
    tempnow_offset_x2 = 13
    tempnow_offset_x = 95

# 创建一张128x296的新图片
new_image = Image.new("RGB", (128, 296), color=(255, 255, 255))



# 加载CPU框图片    
cpu_hxsl = int(cpu_count())
cpu_hxsl_str = "8"
cpu_jiange = 4
print("CPU核心数量：",cpu_hxsl)
if cpu_hxsl == 2:
    cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/2_hexinkuang.png"
    cpu_hxsl_str = "2"
    cpu_jiange = 16
    
elif cpu_hxsl == 4:
    cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/4_hexinkuang.png"
    cpu_hxsl_str = "4"
    cpu_jiange = 8
    
elif cpu_hxsl == 6:
    cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/6_hexinkuang.png"
    cpu_hxsl_str = "6"
    cpu_jiange = 5
    
elif cpu_hxsl == 8:
    cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/8_hexinkuang.png"
    cpu_hxsl_str = "8"
    cpu_jiange = 4
    
else:
    cpu_hxsl_img_path = BASE_DIR / "img/cpu_img/8_hexinkuang.png"
    cpu_hxsl_str = "8"
    cpu_jiange = 4
#print("CPU核心数量：",cpu_hxsl_img_path)
cpukuang_img = Image.open(cpu_hxsl_img_path)
new_image.paste(cpukuang_img, (87, 54))


# 将数字图片和线条图片拼接到新图片上
x_offset = (128 - 120) // 2
y_offset = (32 - 14) // 2
for digit in digits:
    if digit == "-":
        # 加载线条图片
        line_image = Image.open(line_path)

        # 将线条图片粘贴到新图片上
        new_image.paste(line_image, (x_offset, y_offset))

        # 更新线条图片在新图片中的水平偏移量
        x_offset += line_image.width
    else:
        # 加载数字图片
        digit_image = Image.open(str(image_path / f"{digit}.png"))

        # 将数字图片粘贴到新图片上
        new_image.paste(digit_image, (x_offset, y_offset))

        # 更新数字图片在新图片中的水平偏移量
        x_offset += digit_image.width

# 将星期粘贴到新图片上
weekday_image = Image.open(chinese_path / f"{weekday}.png")
new_image.paste(weekday_image, (0, 32))

# 将cpu的数字图片和线条图片拼接到新图片上
x_offset2 = (128 - 82) // 2
y_offset2 = 55

for cpu_xinxis in cpu_xinxi:
    
    if cpu_xinxis == "-":

        # 加载线条图片
        line_image = Image.open(line_path)

        # 将线条图片粘贴到新图片上
        new_image.paste(line_image, (x_offset2, y_offset2))

        # 更新线条图片在新图片中的水平偏移量
        x_offset2 += line_image.width
    else:
        # 加载cpu图片
        cpu_image = Image.open(cpu_path)
        new_image.paste(cpu_image, (5, 55))
    
        # 加载数字图片
        cpu_image2 = Image.open(str(image_path / f"{cpu_xinxis}.png"))

        # 将数字图片粘贴到新图片上
        new_image.paste(cpu_image2, (x_offset2, y_offset2))

        # 更新数字图片在新图片中的水平偏移量
        x_offset2 += cpu_image2.width

# 加载%图片     s
bai_image = Image.open(bai_path)
new_image.paste(bai_image, (x_offset2+1, y_offset2))


# 将内存的数字图片和线条图片拼接到新图片上
x_offset3 = (128 - 82) // 2
y_offset3 = 76
for mem_total_xinxis in mem_total_xinxi:
    if mem_total_xinxis == "-":

        # 加载线条图片
        line_image = Image.open(line_path)

        # 将线条图片粘贴到新图片上
        new_image.paste(line_image, (x_offset3, y_offset3))

        # 更新线条图片在新图片中的水平偏移量
        x_offset3 += line_image.width
    else:
        # 加载cpu图片
        men_image = Image.open(men_path)
        new_image.paste(men_image, (5, 76))
    
        # 加载数字图片
        cpu_image3 = Image.open(str(image_path / f"{mem_total_xinxis}.png"))

        # 将数字图片粘贴到新图片上
        new_image.paste(cpu_image3, (x_offset3, y_offset3))

        # 更新数字图片在新图片中的水平偏移量
        x_offset3 += cpu_image3.width

# 加载%图片     
mem_total_image = Image.open(gb_path)
new_image.paste(mem_total_image, (x_offset3+1, y_offset3))

# 将内存使用率数字图片和线条图片拼接到新图片上

for mem_percent_xinxis in mem_percent_xinxi:
    if mem_percent_xinxis == "-":

        # 加载线条图片
        line_image = Image.open(line_path)

        # 将线条图片粘贴到新图片上
        new_image.paste(line_image, (x_offset4, y_offset3))

        # 更新线条图片在新图片中的水平偏移量
        x_offset4 += line_image.width
    else:
    
        # 加载数字图片
        cpu_image4 = Image.open(str(image_path / f"{mem_percent_xinxis}.png"))

        # 将数字图片粘贴到新图片上
        new_image.paste(cpu_image4, (x_offset4, y_offset3))

        # 更新数字图片在新图片中的水平偏移量
        x_offset4 += cpu_image4.width

# 加载%图片     
mem_total_image = Image.open(bai_path)
new_image.paste(mem_total_image, (x_offset4 + 1, y_offset3))

# 将天气图标粘贴到新图片上
weather_image = Image.open(str(image_path / f"{iconDay}.jpg"))
new_image.paste(weather_image, (6, 96))

weather_image = Image.open(str(image_path / f"{iconNight}.jpg"))
new_image.paste(weather_image, (70, 96))

#data_name2="飞虎队呀"
data_name_y =103
name_len = len(data_name2)
if name_len == 4:
    name_jiange = 10
    data_name_y = 103
elif name_len == 3:
    name_jiange = 13
    data_name_y = 105
elif name_len == 2:
    name_jiange = 15
    data_name_y = 110
else:
    name_jiange = 20
    data_name_y = 120

# 加载地名

for data_name3 in data_name2:
    ttf_path = BASE_DIR / "font/1657694032434275.ttf";
    fnt = ImageFont.truetype(str(ttf_path), 8)
    ImageDraw.Draw(new_image).text((60,data_name_y), data_name3, fill='black', font=fnt)
    data_name_y = data_name_y + name_jiange

# 将温度值字符串中的每个字符分别加载对应的图片，并粘贴到新图片上
tempmin_y_offset = 180
for min, ch in enumerate(tempmin_str):
    if ch == "-":
        minus_image = Image.open(str(image_path / "minus.png"))
        new_image.paste(minus_image, (tempmin_offset_x, tempmin_y_offset))
    else:
        digit_image = Image.open(str(image_path / f"{ch}.png"))
        new_image.paste(digit_image, (tempmin_offset_x + min * 12, tempmin_y_offset))

tempmax_y_offset = 180
for max, ch in enumerate(tempmax_str):
    if ch == "-":
        minus_image = Image.open(str(image_path / "minus.png"))
        new_image.paste(minus_image, (tempmax_offset_x, tempmax_y_offset))
    else:
        digit_image = Image.open(str(image_path / f"{ch}.png"))
        new_image.paste(digit_image, (tempmax_offset_x + max * 12, tempmax_y_offset))

tempnow_y_offset = 209
for now, ch in enumerate(tempnow_str):
    if ch == "-":
        minus_image = Image.open(str(image_path / "minus.png"))
        new_image.paste(minus_image, (tempnow_offset_x, tempnow_y_offset))
    else:
        digit_image = Image.open(str(image_path / f"{ch}.png"))
        new_image.paste(digit_image, (tempnow_offset_x + now * 12, tempnow_y_offset))

# 将中文图片粘贴到新图片上
weather_image = Image.open(str(image_path / f"{textDay}.png"))
new_image.paste(weather_image, (0, 150))
weather_image = Image.open(str(image_path / f"{textNight}.png"))
new_image.paste(weather_image, (72, 150))

# 将温度单位图片粘贴到新图片上
temp_unit_image = Image.open(str(image_path / "temp_unit.png"))
new_image.paste(temp_unit_image, (tempmin_offset_x + min * 12 + 12, tempmin_y_offset))
new_image.paste(temp_unit_image, (tempmax_offset_x + max * 12 + 12, tempmax_y_offset))
new_image.paste(temp_unit_image, (tempnow_offset_x + now * 12 + 12, tempnow_y_offset))

# 将其他图片粘贴到新图片上
nowtemp_image = Image.open(str(nowtemp_path))
new_image.paste(nowtemp_image, (tempnow_offset_x2, 205))
wave_image = Image.open(str(wave_path))
new_image.paste(wave_image, (58, 148))
new_image.paste(wave_image, (58, 175))

if data_minutely == "未来两小时无降水":
    weekday_image = Image.open(str(chinese_path / f"{weekday2}.png"))
    new_image.paste(weekday_image, (0, 227))
else:
    fnt_path = BASE_DIR / "font/DinkieBitmapDemo-9px.ttf"
    fnt = ImageFont.truetype(str(fnt_path), 10)

    int_shuzi = 0
    minutely_len = len(data_minutely)
    minutely_hang = minutely_len / 12
    if minutely_hang != int(minutely_hang):
        minutely_hang = int(minutely_hang) + 1
    minutely_y = 255 - ((minutely_hang*11)/2)

    minutely_x = 52 - (((len(list(filter(str.isdigit, data_minutely))) * 5) + 
                        (len(data_minutely.translate(str.maketrans('', '', '0123456789'))) * 10))/2)
    if minutely_x < 5:
        minutely_x = 0

    for minutely_1 in data_minutely:
        a = "".join(list(filter(str.isdigit, minutely_1)))
        int_shuzi += 10
        if int_shuzi > 108:
            int_shuzi = 1
            minutely_x = 10
            minutely_y += 11
        ImageDraw.Draw(new_image).text((minutely_x + int_shuzi, minutely_y), minutely_1, fill='black', font=fnt)
        if a != "":
            int_shuzi -= 4

print("CPU逻辑核心：",cpu_hexin)
x_cpu_hexin = 90
xunhuan = 0

for fruit in cpu_hexin:
    # 显示各个CPU核心占用率
    cpu_jianges = 0
    if cpu_hxsl_str == "6":
        if xunhuan in (0, 4):
            cpu_jianges = 1

    # 根据 CPU 占用率选择图片
    if fruit < 10:
        suffix = "0"
    elif fruit < 20:
        suffix = "10"
    elif fruit < 30:
        suffix = "20"
    elif fruit < 40:
        suffix = "30"
    elif fruit < 50:
        suffix = "40"
    elif fruit < 60:
        suffix = "50"
    elif fruit < 70:
        suffix = "60"
    elif fruit < 80:
        suffix = "70"
    elif fruit < 90:
        suffix = "80"
    elif fruit < 94:
        suffix = "90"
    elif fruit <= 100:
        suffix = "100"
    else:
        suffix = "0"

    cpu_hx_img_path = BASE_DIR / f"img/cpu_img/{cpu_hxsl_str}_{suffix}.png"
    cpu_hx_img = Image.open(str(cpu_hx_img_path))  # <-- 注意加 str()
    new_image.paste(cpu_hx_img, (x_cpu_hexin, 57))

    if xunhuan == 7:
        break

    x_cpu_hexin += cpu_jiange + cpu_jianges
    xunhuan += 1

    #print("CPU核心：",fruit)
    #print("CPU核心2：",cpu_hx_img_path)

# 保存新图片
new_image.save(BASE_DIR / "output.png")
print('创建图片')

# 刷新墨水屏
if __name__ == '__main__':
    img = Image.open(BASE_DIR / "output.png")

    black_img = img.convert("L")  # 转化为黑白图片#进行灰度处理
    bdata_list = list(black_img.getdata())

    threshold = 128
    bvalue_list = [0 if i < threshold else 1 for i in bdata_list]
    # 将8位一组放在一起
    ob_list = []
    s = "0b"
    for i in range(1, len(bvalue_list) + 1):
        s += str(bvalue_list[i - 1])
        if i % 8 == 0:
            ob_list.append(s)
            s = "0b"
    # 转换为16进制字符串 格式定位两位
    ox_list = ['%02x' % int(i, 2) for i in ob_list]
    j = 0
    firstPackage = '013e8d2508072a8825080b1080251a8025'
    nextPackage = '013e'
    lastPackage = '0128'
    hexStr = ''
    hexStr += firstPackage
    for i in range(0, 47):
        hexStr += ox_list[j]
        j += 1
    packCount = int((len(ox_list) - 47) / 62)
    for i in range(0, packCount):
        hexStr += nextPackage
        for k in range(0, 62):
            if j >= len(ox_list):
                hexStr += '00'
            else:
                hexStr += ox_list[j]
            j += 1
    hexStr += lastPackage
    for k in range(0, 62):
        if j >= len(ox_list):
            hexStr += '00'
        else:
            hexStr += ox_list[j]
        j += 1
    st2 = re.findall(r'.{128}', hexStr)
    # print(st2)
    st2.append(hexStr[int(int(len(hexStr) / 128) * 128):])
    
    VID = 0x1d50
    PID = 0x615e

    devices = hid.enumerate(VID, PID)
    if not devices:
        raise RuntimeError("墨水屏未连接，跳过本次刷新")

    path = None
    for info in devices:
        if info.get("usage_page") == 65300:
            path = info["path"]
            break

    if not path:
        raise RuntimeError("未找到符合条件的 HID 设备")

    d = hid.device()
    d.open_path(path)

    print("HID device opened")

    d.write(binascii.unhexlify(
        '01050408011200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'))
    
    raw = d.read(1000)
    pack = bytes(raw).decode("utf8", "ignore")

    print('Zephyr 版本:' + pack[9:16])
    print('ZMK 版本:' + pack[18:25])
    print('固件版本:' + pack[27:34])
    #print(str(cpu_percent(interval=5)))
    for i in st2:
        if i == '':
            continue
        d.write(binascii.unhexlify(i))
    print('图片刷新完成')
