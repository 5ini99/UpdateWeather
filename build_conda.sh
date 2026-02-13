#!/usr/bin/env bash
# build_conda.sh
# 针对 Conda 环境的 PyInstaller 打包脚本
# ⚠️ 必须在激活的 conda 环境中运行

set -e  # 任何错误都会退出

echo "=========================================="
echo "Conda 环境 PyInstaller 打包脚本"
echo "=========================================="
echo ""

# 检查是否在 conda 环境中
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ 错误：当前不在 conda 环境中！"
    echo ""
    echo "请先激活 conda 环境："
    echo "  conda activate your_env_name"
    echo ""
    echo "然后再运行此脚本"
    exit 1
fi

echo "✓ 当前 Conda 环境: $CONDA_DEFAULT_ENV"
echo "✓ Python 路径: $(which python)"
echo "✓ Python 版本: $(python --version)"
echo "✓ PyInstaller: $(python -m PyInstaller --version)"
echo ""

# 配置变量
APP_NAME="UpdateWeather"
MAIN_SCRIPT="main.py"
ICON_FILE="icon.icns"

DATA_DIRS=(
  "img:img"
  "font:font"
  "legacy:legacy"
)

# 清理旧构建
echo "清理旧构建..."
rm -rf build dist *.spec 2>/dev/null || true

echo ""
echo "开始打包..."
echo ""

# 🔑 关键：使用 conda 的 Python 而不是系统 Python
# --onedir 对 conda 环境更友好（比 --onefile 更稳定）
CMD="python -m PyInstaller \
  --onedir \
  --name ${APP_NAME} \
  --windowed \
  --clean \
  --noupx \
  --collect-all=app \
  --hidden-import=pystray \
  --hidden-import=PIL \
  --hidden-import=PIL.Image \
  --hidden-import=PIL.ImageDraw \
  --hidden-import=PIL.ImageFont \
  --hidden-import=psutil \
  --hidden-import=requests \
  --hidden-import=hid \
  --hidden-import=threading \
  --hidden-import=configparser \
  --hidden-import=tkinter \
  --hidden-import=tkinter.simpledialog \
  --hidden-import=tkinter.messagebox \
  --hidden-import=tkinter.filedialog \
  --hidden-import=datetime"

# 添加数据文件夹
for dir in "${DATA_DIRS[@]}"; do
  CMD="${CMD} --add-data \"${dir}\""
done

# 添加 icon
if [ -f "${ICON_FILE}" ]; then
  CMD="${CMD} --icon ${ICON_FILE}"
fi

CMD="${CMD} ${MAIN_SCRIPT}"

echo "执行命令："
echo "$CMD"
echo ""
echo "=========================================="

eval "$CMD"

if [ $? -eq 0 ]; then
  echo ""
  echo "✓ 构建成功！"

  # macOS: 隐藏 Dock 图标（仅在托盘显示）
  APP_BUNDLE="./dist/${APP_NAME}.app"
  PLIST_PATH="${APP_BUNDLE}/Contents/Info.plist"
  if [ -f "$PLIST_PATH" ]; then
    echo "配置 macOS 应用为 AgentApp（隐藏 Dock 图标）..."
    /usr/libexec/PlistBuddy -c "Delete :LSUIElement" "$PLIST_PATH" >/dev/null 2>&1 || true
    /usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST_PATH"
  else
    echo "⚠️ 未找到 $PLIST_PATH，跳过 Dock 隐藏配置"
  fi

  echo ""
  echo "输出应用位置:"
  echo "  ./dist/${APP_NAME}/${APP_NAME}"
  echo ""
  echo "运行应用:"
  echo "  ./dist/${APP_NAME}/${APP_NAME}"
  echo ""
  echo "⚠️  提示："
  echo "  - 这是 conda 环境打包的版本"
  echo "  - 在其他没有激活该 conda 环境的终端中可能无法运行"
  echo "  - 如果需要分发，考虑打包整个 conda 环境或使用 conda-pack"
  echo ""
else
  echo ""
  echo "✗ 构建失败！请检查错误信息"
  exit 1
fi