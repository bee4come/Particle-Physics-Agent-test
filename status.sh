#!/bin/bash

# FeynmanCraft 服务状态检查脚本

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

# 检查进程状态
check_process_status() {
    local service_name="$1"
    local pid_file="$2"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "🟢 $service_name: 运行中 (PID: $pid)"
            return 0
        else
            echo "🔴 $service_name: 已停止 (PID 文件存在但进程不存在)"
            return 1
        fi
    else
        echo "🔴 $service_name: 已停止 (无 PID 文件)"
        return 1
    fi
}

# 检查端口状态
check_port_status() {
    local port="$1"
    local service_name="$2"
    
    if lsof -i :"$port" >/dev/null 2>&1; then
        local process_info=$(lsof -i :"$port" | tail -n +2 | head -1)
        echo "🟢 端口 $port ($service_name): 已占用"
        echo "   进程信息: $process_info"
        return 0
    else
        echo "🔴 端口 $port ($service_name): 未占用"
        return 1
    fi
}

# 检查网络连接
check_network_status() {
    local url="$1"
    local service_name="$2"
    
    if curl -s --connect-timeout 3 "$url" >/dev/null 2>&1; then
        echo "🟢 $service_name 网络: 可访问"
        return 0
    else
        echo "🔴 $service_name 网络: 不可访问"
        return 1
    fi
}

# 获取系统资源使用情况
get_system_resources() {
    echo ""
    echo "💻 系统资源使用情况:"
    
    # CPU 使用率
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "   CPU 使用率: ${cpu_usage}%"
    
    # 内存使用率
    local mem_info=$(free | grep Mem)
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_percent=$(echo "scale=1; $used_mem * 100 / $total_mem" | bc 2>/dev/null || echo "N/A")
    echo "   内存使用率: ${mem_percent}%"
    
    # 磁盘使用率
    local disk_usage=$(df -h . | tail -1 | awk '{print $5}')
    echo "   磁盘使用率: $disk_usage"
}

# 显示日志统计
show_log_stats() {
    echo ""
    echo "📊 日志统计:"
    
    if [ -f "logs/backend.log" ]; then
        local backend_lines=$(wc -l < logs/backend.log)
        local backend_size=$(du -sh logs/backend.log | cut -f1)
        local backend_errors=$(grep -c "ERROR\|Error\|error" logs/backend.log 2>/dev/null || echo "0")
        echo "   后端日志: $backend_lines 行, $backend_size, $backend_errors 个错误"
    else
        echo "   后端日志: 不存在"
    fi
    
    if [ -f "logs/frontend.log" ]; then
        local frontend_lines=$(wc -l < logs/frontend.log)
        local frontend_size=$(du -sh logs/frontend.log | cut -f1)
        local frontend_errors=$(grep -c "ERROR\|Error\|error" logs/frontend.log 2>/dev/null || echo "0")
        echo "   前端日志: $frontend_lines 行, $frontend_size, $frontend_errors 个错误"
    else
        echo "   前端日志: 不存在"
    fi
    
    # 备份日志统计
    if [ -d "logs/archive" ] && [ "$(ls -A logs/archive)" ]; then
        local archive_count=$(ls logs/archive/*.log 2>/dev/null | wc -l)
        local archive_size=$(du -sh logs/archive 2>/dev/null | cut -f1 || echo "0")
        echo "   备份日志: $archive_count 个文件, $archive_size"
    else
        echo "   备份日志: 无"
    fi
}

# 显示最近的日志
show_recent_logs() {
    echo ""
    echo "📋 最近日志 (最后 5 行):"
    
    if [ -f "logs/backend.log" ]; then
        echo ""
        echo "后端日志:"
        echo "----------------------------------------"
        tail -5 logs/backend.log | sed 's/^/   /'
    fi
    
    if [ -f "logs/frontend.log" ]; then
        echo ""
        echo "前端日志:"
        echo "----------------------------------------"
        tail -5 logs/frontend.log | sed 's/^/   /'
    fi
}

# 检查生成的文件
check_generated_files() {
    echo ""
    echo "📁 生成文件统计:"
    
    if [ -d "frontend/public/generated" ]; then
        local file_count=$(find frontend/public/generated -type f 2>/dev/null | wc -l)
        local dir_count=$(find frontend/public/generated -type d -mindepth 1 2>/dev/null | wc -l)
        local total_size=$(du -sh frontend/public/generated 2>/dev/null | cut -f1 || echo "0")
        echo "   生成目录: $dir_count 个文件夹, $file_count 个文件, $total_size"
        
        # 显示最近生成的文件
        if [ $dir_count -gt 0 ]; then
            echo "   最近生成:"
            find frontend/public/generated -type d -mindepth 1 | tail -3 | sed 's/^/     /'
        fi
    else
        echo "   生成目录: 不存在"
    fi
}

# 主状态检查
main_status_check() {
    echo ""
    echo "========================================="
    echo "       FeynmanCraft 服务状态"
    echo "========================================="
    echo ""
    
    # 进程状态
    echo "🔍 进程状态:"
    local backend_running=false
    local frontend_running=false
    
    if check_process_status "后端服务" "logs/backend.pid"; then
        backend_running=true
    fi
    
    if check_process_status "前端服务" "logs/frontend.pid"; then
        frontend_running=true
    fi
    
    echo ""
    
    # 端口状态
    echo "🌐 端口状态:"
    check_port_status "8000" "后端"
    check_port_status "5173" "前端"
    
    echo ""
    
    # 网络连接状态
    echo "🔗 网络连接:"
    check_network_status "http://localhost:8000" "后端 API"
    check_network_status "http://localhost:5173" "前端 UI"
    
    # 系统资源
    get_system_resources
    
    # 日志统计
    show_log_stats
    
    # 生成文件统计
    check_generated_files
    
    # 最近日志
    if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
        show_recent_logs
    fi
    
    echo ""
    echo "========================================="
    echo ""
    
    # 总结状态
    if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
        print_success "✅ 所有服务运行正常"
        echo ""
        echo "🌐 访问地址:"
        echo "   前端 UI: http://localhost:5173"
        echo "   后端 API: http://localhost:8000"
    elif [ "$backend_running" = true ] || [ "$frontend_running" = true ]; then
        print_warning "⚠️  部分服务未运行"
        echo ""
        echo "🔧 建议操作:"
        echo "   重新启动: ./start.sh"
        echo "   停止所有: ./stop.sh"
    else
        print_info "ℹ️  所有服务已停止"
        echo ""
        echo "🚀 启动服务: ./start.sh"
    fi
    
    echo ""
    echo "🔧 可用命令:"
    echo "   启动服务:    ./start.sh"
    echo "   停止服务:    ./stop.sh"
    echo "   详细状态:    ./status.sh --verbose"
    echo "   实时日志:    tail -f logs/backend.log"
    echo "            或  tail -f logs/frontend.log"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "📊 FeynmanCraft 服务状态检查"
    echo "========================================="
    
    main_status_check "$@"
    
    print_success "状态检查完成"
    echo ""
}

# 运行主函数
main "$@"