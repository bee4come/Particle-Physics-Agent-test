#!/bin/bash

# FeynmanCraft 停止服务脚本

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

# 记录停止日志
log_stop_event() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] 🛑 FeynmanCraft 服务停止" | tee -a logs/backend.log logs/frontend.log 2>/dev/null || true
}

# 停止服务
stop_services() {
    print_info "停止 FeynmanCraft 服务..."
    
    local stopped_any=false
    
    # 停止后端服务
    if [ -f "logs/backend.pid" ]; then
        local backend_pid=$(cat logs/backend.pid)
        if [ -n "$backend_pid" ] && kill -0 $backend_pid 2>/dev/null; then
            print_info "停止后端服务 (PID: $backend_pid)..."
            kill $backend_pid 2>/dev/null || true
            
            # 等待进程停止
            local count=0
            while [ $count -lt 10 ] && kill -0 $backend_pid 2>/dev/null; do
                sleep 1
                count=$((count + 1))
            done
            
            # 如果进程仍然存在，强制杀死
            if kill -0 $backend_pid 2>/dev/null; then
                print_warning "后端进程未响应，强制停止..."
                kill -9 $backend_pid 2>/dev/null || true
            fi
            
            print_success "后端服务已停止"
            stopped_any=true
        else
            print_warning "后端进程不存在或已停止"
        fi
        rm -f logs/backend.pid
    else
        print_warning "未找到后端 PID 文件"
    fi
    
    # 停止前端服务
    if [ -f "logs/frontend.pid" ]; then
        local frontend_pid=$(cat logs/frontend.pid)
        if [ -n "$frontend_pid" ] && kill -0 $frontend_pid 2>/dev/null; then
            print_info "停止前端服务 (PID: $frontend_pid)..."
            kill $frontend_pid 2>/dev/null || true
            
            # 等待进程停止
            local count=0
            while [ $count -lt 10 ] && kill -0 $frontend_pid 2>/dev/null; do
                sleep 1
                count=$((count + 1))
            done
            
            # 如果进程仍然存在，强制杀死
            if kill -0 $frontend_pid 2>/dev/null; then
                print_warning "前端进程未响应，强制停止..."
                kill -9 $frontend_pid 2>/dev/null || true
            fi
            
            print_success "前端服务已停止"
            stopped_any=true
        else
            print_warning "前端进程不存在或已停止"
        fi
        rm -f logs/frontend.pid
    else
        print_warning "未找到前端 PID 文件"
    fi
    
    # 停止 LaTeX MCP 服务
    if [ -f "logs/mcp_latex.pid" ]; then
        local latex_mcp_pid=$(cat logs/mcp_latex.pid)
        if [ -n "$latex_mcp_pid" ] && kill -0 $latex_mcp_pid 2>/dev/null; then
            print_info "停止 LaTeX MCP 服务 (PID: $latex_mcp_pid)..."
            kill $latex_mcp_pid 2>/dev/null || true
            
            # 等待进程停止
            local count=0
            while [ $count -lt 5 ] && kill -0 $latex_mcp_pid 2>/dev/null; do
                sleep 1
                count=$((count + 1))
            done
            
            # 如果进程仍然存在，强制杀死
            if kill -0 $latex_mcp_pid 2>/dev/null; then
                kill -9 $latex_mcp_pid 2>/dev/null || true
            fi
            
            print_success "LaTeX MCP 服务已停止"
            stopped_any=true
        else
            print_warning "LaTeX MCP 进程不存在或已停止"
        fi
        rm -f logs/mcp_latex.pid
    else
        print_info "未找到 LaTeX MCP PID 文件"
    fi
    
    # 额外清理：使用进程名杀死可能遗漏的进程
    print_info "清理可能遗漏的进程..."
    pkill -f "adk web" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "experimental.latex_mcp.server" 2>/dev/null || true
    pkill -f "particlephysics_mcp_server" 2>/dev/null || true
    
    # 记录停止事件
    log_stop_event
    
    if [ "$stopped_any" = true ]; then
        print_success "所有服务已停止"
    else
        print_info "没有运行中的服务需要停止"
    fi
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用情况..."
    
    # 检查端口 8000 (后端)
    if lsof -i :8000 >/dev/null 2>&1; then
        print_warning "端口 8000 仍被占用："
        lsof -i :8000 | head -5
        print_info "如需强制清理，请运行: lsof -ti :8000 | xargs kill -9"
    else
        print_success "端口 8000 已释放"
    fi
    
    # 检查端口 5174 (前端)
    if lsof -i :5174 >/dev/null 2>&1; then
        print_warning "端口 5174 仍被占用："
        lsof -i :5174 | head -5
        print_info "如需强制清理，请运行: lsof -ti :5174 | xargs kill -9"
    else
        print_success "端口 5174 已释放"
    fi
    
    # 检查端口 8003 (LaTeX MCP)
    if lsof -i :8003 >/dev/null 2>&1; then
        print_warning "端口 8003 仍被占用："
        lsof -i :8003 | head -5
        print_info "如需强制清理，请运行: lsof -ti :8003 | xargs kill -9"
    else
        print_success "端口 8003 已释放"
    fi
}

# 显示服务状态
show_status() {
    echo ""
    echo "========================================="
    echo "       FeynmanCraft 服务状态"
    echo "========================================="
    echo ""
    
    # 检查服务状态
    local backend_running=false
    local frontend_running=false
    
    if [ -f "logs/backend.pid" ]; then
        local backend_pid=$(cat logs/backend.pid)
        if [ -n "$backend_pid" ] && kill -0 $backend_pid 2>/dev/null; then
            backend_running=true
            echo "🟢 后端服务:    运行中 (PID: $backend_pid)"
        else
            echo "🔴 后端服务:    已停止"
        fi
    else
        echo "🔴 后端服务:    已停止"
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        local frontend_pid=$(cat logs/frontend.pid)
        if [ -n "$frontend_pid" ] && kill -0 $frontend_pid 2>/dev/null; then
            frontend_running=true
            echo "🟢 前端服务:    运行中 (PID: $frontend_pid)"
        else
            echo "🔴 前端服务:    已停止"
        fi
    else
        echo "🔴 前端服务:    已停止"
    fi
    
    echo ""
    
    if [ "$backend_running" = false ] && [ "$frontend_running" = false ]; then
        echo "✅ 所有服务已停止"
        echo ""
        echo "💡 下次启动请运行: ./start.sh"
    else
        echo "⚠️  仍有服务在运行"
        echo ""
        echo "🔧 管理命令:"
        echo "   重新停止:    ./stop.sh"
        echo "   查看状态:    ./status.sh"
        echo "   强制清理:    pkill -f 'adk web' && pkill -f 'npm run dev'"
    fi
    
    echo ""
    echo "📋 日志文件:"
    echo "   后端日志:    logs/backend.log"
    echo "   前端日志:    logs/frontend.log"
    echo "   日志备份:    logs/archive/"
    echo ""
    echo "========================================="
    echo ""
}

# 主函数
main() {
    echo ""
    echo "🛑 FeynmanCraft 服务停止脚本"
    echo "========================================="
    echo ""
    
    stop_services
    sleep 1
    check_ports
    show_status
    
    print_success "停止脚本执行完成"
    echo ""
}

# 运行主函数
main "$@"