# UpdateWeather 快速入门

## 🚀 5分钟快速开始

### 第 1 步：下载项目 ✅

你已经下载了项目，现在在 `UpdateWeather_Release` 目录中。

### 第 2 步：安装依赖

打开终端，进入项目目录：

**macOS / Linux:**
```bash
cd UpdateWeather_Release
pip3 install -r requirements.txt
```

**Windows:**
```bash
cd UpdateWeather_Release
pip install -r requirements.txt
```

### 第 3 步：运行程序

**方式 1：使用启动脚本（推荐）**

macOS / Linux:
```bash
./start.sh
```

Windows:
```bash
start.bat
```

**方式 2：直接运行**

```bash
python3 main.py
```

### 第 4 步：配置参数

1. 找到系统托盘中的 **UW** 图标
2. **右键点击** → 选择「**设置**」
3. 在配置窗口中设置：
   - ✅ 刷新间隔（建议 60 分钟）
   - ✅ 夜间模式（建议 23:00 - 7:00）
   - ✅ 天气 API Key（需要自己申请）
   - ✅ 城市名称（如 Beijing）
4. 点击「**保存配置**」

### 第 5 步：测试刷新

右键托盘图标 → 选择「**立即刷新**」，测试是否正常工作。

---

## 📋 获取天气 API Key

### 和风天气（推荐）

1. 访问：https://dev.qweather.com/
2. 注册账号
3. 创建应用 → 获取 API Key
4. 复制 Key 到配置中

### OpenWeather

1. 访问：https://openweathermap.org/api
2. 注册账号
3. 获取 API Key
4. 复制 Key 到配置中

---

## ✅ 验证安装

运行检查脚本：

```bash
python3 check_integrity.py
```

如果看到 ✓ 标记，说明安装成功！

---

## 🎯 下一步

- 📖 查看 [完整使用指南](GUIDE.md)
- 🔧 查看 [项目说明](README.md)
- 📝 查看 [更新日志](CHANGELOG.md)

---

## ❓ 常见问题

### Q: 托盘图标看不到？

**A:** 检查系统托盘设置，确保允许显示第三方图标。

### Q: 配置窗口打不开？

**A:** 删除锁文件重试：
```bash
rm ~/.updateweather/gui.lock
```

### Q: 找不到 tkinter？

**A:** 
- macOS: `brew install python-tk`
- Ubuntu: `sudo apt-get install python3-tk`
- Windows: 重新安装 Python（勾选 tk/tcl）

---

## 📞 需要帮助？

- 💬 查看详细文档：[GUIDE.md](GUIDE.md)
- 🐛 提交问题：创建 Issue
- 📧 联系支持：通过项目仓库

---

**祝使用愉快！** 🌈
