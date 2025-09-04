#!/bin/bash

# FeynmanCraft 一键启动脚本
# 启动 ADK Backend 和 Frontend 服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的命令是否存在
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v adk &> /dev/null; then
        print_error "ADK 未安装或不在 PATH 中，请先安装: pip install -r requirements.txt"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 检查环境变量
check_env() {
    print_info "检查环境变量..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在，请确保已配置 GOOGLE_API_KEY"
        if [ ! -f ".env.example" ]; then
            print_error ".env.example 文件不存在"
            exit 1
        fi
        print_info "复制 .env.example 到 .env..."
        cp .env.example .env
        print_warning "请编辑 .env 文件并设置 GOOGLE_API_KEY"
    fi
    
    # 检查是否设置了 GOOGLE_API_KEY
    if [ -f ".env" ]; then
        source .env
        if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key-here" ]; then
            print_warning "GOOGLE_API_KEY 未设置或使用默认值，请检查 .env 文件"
        else
            print_success "环境变量配置正常"
        fi
    fi
}

# 安装前端依赖
install_frontend_deps() {
    print_info "检查前端依赖..."
    
    if [ ! -d "frontend/node_modules" ]; then
        print_info "安装前端依赖..."
        cd frontend
        npm install
        cd ..
        print_success "前端依赖安装完成"
    else
        print_success "前端依赖已存在"
    fi
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    # 创建前端生成文件目录
    mkdir -p frontend/public/generated
    
    # 创建日志目录，按日期组织 
    mkdir -p logs
    mkdir -p logs/archive
    
    print_success "目录创建完成"
}

# 备份旧日志
backup_logs() {
    print_info "备份旧日志文件..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # 如果存在旧日志，备份到 archive 目录
    if [ -f "logs/backend.log" ] && [ -s "logs/backend.log" ]; then
        mv "logs/backend.log" "logs/archive/backend_${timestamp}.log"
        print_info "旧的后端日志已备份到 logs/archive/backend_${timestamp}.log"
    fi
    
    if [ -f "logs/frontend.log" ] && [ -s "logs/frontend.log" ]; then
        mv "logs/frontend.log" "logs/archive/frontend_${timestamp}.log"
        print_info "旧的前端日志已备份到 logs/archive/frontend_${timestamp}.log"
    fi
    
    # 清理超过7天的旧日志
    find logs/archive -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    print_success "日志备份完成"
}

# 清理旧的进程
cleanup_processes() {
    print_info "清理可能存在的旧进程..."
    
    # 清理 ADK 进程
    pkill -f "adk web" || true
    
    # 清理前端进程  
    pkill -f "npm run dev" || true
    
    # 等待进程完全退出
    sleep 2
    
    print_success "进程清理完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    # 创建启动时间戳日志
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    echo "=== FeynmanCraft 启动于: $start_time ===" | tee logs/backend.log logs/frontend.log
    echo "启动用户: $(whoami)" | tee -a logs/backend.log logs/frontend.log
    echo "工作目录: $(pwd)" | tee -a logs/backend.log logs/frontend.log
    echo "=========================================" | tee -a logs/backend.log logs/frontend.log
    echo "" | tee -a logs/backend.log logs/frontend.log
    
    # 设置环境变量并启动后端服务
    print_info "启动 ADK Backend (端口 8000)..."
    export PYTHONPATH=/home/zty/Particle-Physics-Agent-test
    export FEYNMANCRAFT_ADK_LOG_LEVEL=INFO
    
    # 在日志中记录启动命令
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动后端命令: PYTHONPATH=$PYTHONPATH FEYNMANCRAFT_ADK_LOG_LEVEL=$FEYNMANCRAFT_ADK_LOG_LEVEL adk web . --port 8000" >> logs/backend.log
    
    nohup adk web . --port 8000 >> logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # 记录后端PID
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 后端进程 PID: $BACKEND_PID" >> logs/backend.log
    
    # 等待后端启动
    sleep 3
    
    # 检查后端是否启动成功
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "后端启动失败，请检查 logs/backend.log"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 后端启动失败!" >> logs/backend.log
        tail -20 logs/backend.log
        exit 1
    fi
    
    print_success "ADK Backend 启动成功 (PID: $BACKEND_PID)"
    
    # 启动前端服务
    print_info "启动 Frontend (端口 5173)..."
    
    # 在前端日志中记录启动信息
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动前端命令: cd frontend && npm run dev" >> logs/frontend.log
    
    cd frontend
    nohup npm run dev >> ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # 记录前端PID
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 前端进程 PID: $FRONTEND_PID" >> logs/frontend.log
    
    # 等待前端启动
    sleep 3
    
    # 检查前端是否启动成功
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "前端启动失败，请检查 logs/frontend.log"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 前端启动失败!" >> logs/frontend.log
        kill $BACKEND_PID 2>/dev/null || true
        tail -20 logs/frontend.log
        exit 1
    fi
    
    print_success "Frontend 启动成功 (PID: $FRONTEND_PID)"
    
    # 保存 PID 到文件
    echo $BACKEND_PID > logs/backend.pid
    echo $FRONTEND_PID > logs/frontend.pid
    
    # 创建启动成功日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 所有服务启动成功" | tee -a logs/backend.log logs/frontend.log
}

# 等待服务就绪
wait_for_services() {
    print_info "等待服务就绪..."
    
    # 等待后端就绪
    local backend_ready=false
    local frontend_ready=false
    local timeout=30
    local count=0
    
    while [ $count -lt $timeout ]; do
        if ! $backend_ready && curl -s http://localhost:8000 >/dev/null 2>&1; then
            print_success "后端服务就绪"
            backend_ready=true
        fi
        
        if ! $frontend_ready && curl -s http://localhost:5173 >/dev/null 2>&1; then
            print_success "前端服务就绪"  
            frontend_ready=true
        fi
        
        if $backend_ready && $frontend_ready; then
            break
        fi
        
        sleep 1
        count=$((count + 1))
        printf "."
    done
    
    echo ""
    
    if ! $backend_ready; then
        print_warning "后端服务未在预期时间内就绪，请检查日志"
    fi
    
    if ! $frontend_ready; then
        print_warning "前端服务未在预期时间内就绪，请检查日志"
    fi
    
    if $backend_ready && $frontend_ready; then
        print_success "所有服务已就绪！"
    fi
}

# 显示服务信息
show_info() {
    local backend_pid=$(cat logs/backend.pid 2>/dev/null || echo "未知")
    local frontend_pid=$(cat logs/frontend.pid 2>/dev/null || echo "未知")
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo ""
    echo "========================================="
    echo "       FeynmanCraft 服务信息"
    echo "========================================="
    echo ""
    echo "🌐 服务地址:"
    echo "   前端 UI:     http://localhost:5173"
    echo "   后端 API:    http://localhost:8000"
    echo ""
    echo "⚙️  进程信息:"
    echo "   后端 PID:    $backend_pid"
    echo "   前端 PID:    $frontend_pid"
    echo "   启动时间:    $start_time"
    echo ""
    echo "📋 日志文件:"
    echo "   后端日志:    logs/backend.log"
    echo "   前端日志:    logs/frontend.log"
    echo "   备份目录:    logs/archive/"
    echo ""
    echo "🔧 管理命令:"
    echo "   停止服务:    ./stop.sh"
    echo "   查看状态:    ./status.sh"
    echo "   实时日志:    tail -f logs/backend.log"
    echo "            或  tail -f logs/frontend.log"
    echo "   查看错误:    grep ERROR logs/backend.log"
    echo "            或  grep ERROR logs/frontend.log"
    echo ""
    echo "📊 测试命令:"
    echo "   测试后端:    curl http://localhost:8000"
    echo "   测试前端:    curl http://localhost:5173"
    echo ""
    echo "💡 提示:"
    echo "   - 日志会自动备份，超过7天的旧日志会自动清理"
    echo "   - 如果遇到问题，请先查看日志文件"
    echo "   - 建议在新终端中运行 'tail -f logs/backend.log' 实时查看日志"
    echo ""
    echo "========================================="
    echo ""
}

# 主函数
main() {
    echo ""
    echo "🚀 FeynmanCraft 一键启动脚本"
    echo "========================================="
    echo ""
    
    check_dependencies
    check_env
    install_frontend_deps
    create_directories
    backup_logs
    cleanup_processes
    start_services
    wait_for_services
    show_info
    
    print_success "启动完成！请在浏览器中访问 http://localhost:5173"
    echo ""
}

# 信号处理 - 优雅关闭
cleanup_on_exit() {
    print_info "正在关闭服务..."
    if [ -f logs/backend.pid ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm -f logs/backend.pid
    fi
    if [ -f logs/frontend.pid ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm -f logs/frontend.pid
    fi
    print_success "服务已关闭"
    exit 0
}

trap cleanup_on_exit SIGINT SIGTERM

# 运行主函数
main "$@"