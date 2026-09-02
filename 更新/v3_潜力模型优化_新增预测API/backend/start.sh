#!/bin/bash
# 绿茵慧眼 - 球员能力评估系统 一键启动脚本 (Linux/macOS)
set -e

# 切换到脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录（脚本位于 backend/ 下）
cd "$SCRIPT_DIR/.."

echo "========================================"
echo "  绿茵慧眼 - 球员能力评估系统"
echo "  一键启动脚本 (Linux/macOS)"
echo "========================================"
echo ""

# 1. 检查 Python
echo "[1/4] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "  [ERROR] 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi
echo "  [OK] Python: $(python3 --version)"
echo ""

# 2. 检查依赖
echo "[2/4] 检查依赖..."
if ! python3 -c "import fastapi, uvicorn, pandas, numpy, sklearn, pydantic" 2>/dev/null; then
    echo "  缺少核心依赖，正在安装..."
    python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi
echo "  [OK] 依赖检查完成"
echo ""

# 3. 端口检查
echo "[3/4] 检查端口 8000..."
if lsof -i :8000 -sTCP:LISTEN &>/dev/null; then
    echo "  [WARN] 端口 8000 已被占用，可能服务已在运行"
else
    echo "  [OK] 端口 8000 空闲"
fi
echo ""

# 4. 启动服务
echo "[4/4] 启动服务..."
echo ""
echo "========================================"
echo "  正在启动后端服务，请稍候..."
echo "  启动完成后请自行在浏览器打开：http://localhost:8000"
echo "  Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
