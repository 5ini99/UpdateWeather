#!/usr/bin/env bash

APP_NAME="UpdateWeather"
MAIN_SCRIPT="main.py"
ICON_FILE="icon.icns"

DATA_DIRS=(
  "img:img"
  "font:font"
  "legacy:legacy"
)

echo "========== PyInstaller 打包脚本（改进版） =========="
echo "清理旧构建..."
rm -rf build dist *.spec 2>/dev/null

echo ""
echo "开始打包..."
echo "使用的 Python: $(which python3)"
echo "PyInstaller 版本: $(python3 -m PyInstaller --version)"

# 核心 PyInstaller 命令
CMD="python3 -m PyInstaller \
  --onefile \
  --name ${APP_NAME} \
  --windowed \
  --clean \
  --noupx \
  --hidden-import=pystray \
  --hidden-import=PIL \
  --hidden-import=PIL.Image \
  --hidden-import=PIL.ImageDraw \
  --hidden-import=psutil \
  --hidden-import=requests \
  --hidden-import=hid"

# ============== 重要：添加数据文件 ==============
for dir in "${DATA_DIRS[@]}"; do
  CMD="${CMD} --add-data \"${dir}\""
done

# 添加 icon
if [ -f "${ICON_FILE}" ]; then
  CMD="${CMD} --icon ${ICON_FILE}"
fi

# 主脚本
CMD="${CMD} ${MAIN_SCRIPT}"

echo ""
echo "执行命令："
echo "$CMD"
echo ""

eval "$CMD"

if [ $? -eq 0 ]; then
  echo ""
  echo "✓ 构建成功！"
  echo ""
  echo "输出应用位置:"
  echo "  ./dist/${APP_NAME}"
  echo ""
  echo "运行应用:"
  echo "  ./dist/${APP_NAME}"
  echo ""
else
  echo ""
  echo "✗ 构建失败！请检查错误信息"
  exit 1
fi
