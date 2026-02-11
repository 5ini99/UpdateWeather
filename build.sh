#!/usr/bin/env bash

# build.sh - 一键打包 UpdateWeather 为 macOS 可执行文件

# ================== 配置区 ==================
APP_NAME="UpdateWeather"
MAIN_SCRIPT="main.py"
ICON_FILE="icon.icns"

# 要打包的额外数据文件夹（冒号分隔 SOURCE:DEST）
DATA_DIRS=(
  "app:app"
  "img:img"
  "font:font"
  "legacy:legacy"
)

# ================== 脚本开始 ==================

echo "开始清理旧构建文件..."
rm -rf build dist *.spec 2>/dev/null

echo "开始 PyInstaller 打包..."

# 基础参数
PYINSTALLER_CMD="pyinstaller --onefile \
  --name ${APP_NAME} \
  --windowed \
  --clean \
  --noupx"

# 添加所有 --add-data
for dir in "${DATA_DIRS[@]}"; do
  PYINSTALLER_CMD="${PYINSTALLER_CMD} --add-data \"${dir}\""
done

# 添加图标（如果存在）
if [ -f "${ICON_FILE}" ]; then
  PYINSTALLER_CMD="${PYINSTALLER_CMD} --icon ${ICON_FILE}"
else
  echo "警告：未找到 ${ICON_FILE}，将使用默认图标"
fi

# 最后添加入口脚本
PYINSTALLER_CMD="${PYINSTALLER_CMD} ${MAIN_SCRIPT}"

# 执行打包
echo "执行命令："
echo "$PYINSTALLER_CMD"
echo ""

eval "$PYINSTALLER_CMD"

# 检查是否成功
if [ $? -eq 0 ] && [ -f "dist/${APP_NAME}" ]; then
  echo ""
  echo "打包成功！"
  echo "可执行文件位置：dist/${APP_NAME}"
  echo "测试运行：./dist/${APP_NAME}"
  echo ""
  ls -lh dist/
else
  echo ""
  echo "打包失败，请检查上面错误日志"
  echo "常见原因："
  echo "1. 缺少模块 → 加 --hidden-import xxx"
  echo "2. 图标文件不存在 → 检查 icon.icns"
  echo "3. 路径问题 → 确认当前目录有 main.py 和 app/"
  echo ""
fi