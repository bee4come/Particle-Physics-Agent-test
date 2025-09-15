#!/bin/bash
set -e

# 快速Cloud Run部署脚本

echo "🚀 FeynmanCraft Cloud Run 快速部署"
echo "=================================="

# 1. 检查必需的环境
echo "1️⃣ 检查环境..."

# 检查gcloud是否安装
if ! command -v gcloud &> /dev/null; then
    echo "❌ 请先安装 Google Cloud SDK"
    echo "   curl https://sdk.cloud.google.com | bash"
    exit 1
fi

# 检查docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 请先安装 Docker"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 缺少 .env 文件，请创建包含 GOOGLE_API_KEY 的 .env"
    exit 1
fi

# 加载环境变量
source .env
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ .env 文件中缺少 GOOGLE_API_KEY"
    exit 1
fi

# 2. 设置项目信息
echo "2️⃣ 配置项目..."

# 提示用户输入项目ID
read -p "请输入您的 Google Cloud Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo "❌ 项目ID不能为空"
    exit 1
fi

# 设置变量
REGION="us-central1"
SERVICE_NAME="feynmancraft-adk"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "项目ID: $PROJECT_ID"
echo "区域: $REGION"
echo "服务名: $SERVICE_NAME"
echo "镜像名: $IMAGE_NAME"

# 3. 认证和设置项目
echo "3️⃣ 设置 Google Cloud..."
gcloud auth login --no-launch-browser || true
gcloud config set project $PROJECT_ID

# 4. 启用必需的API
echo "4️⃣ 启用所需的API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 5. 创建密钥
echo "5️⃣ 创建API密钥..."
echo -n "$GOOGLE_API_KEY" | gcloud secrets create feynmancraft-google-api-key --data-file=- --replication-policy="automatic" || echo "密钥已存在，跳过创建"

# 6. 构建镜像
echo "6️⃣ 构建Docker镜像..."
docker build -t $IMAGE_NAME .

# 7. 推送镜像
echo "7️⃣ 推送镜像到容器仓库..."
docker push $IMAGE_NAME

# 8. 部署到Cloud Run
echo "8️⃣ 部署到Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 100 \
    --timeout 300 \
    --port 8080 \
    --set-env-vars "PORT=8080,BACKEND_PORT=8000,FRONTEND_PORT=5173,HOST=0.0.0.0,FEYNMANCRAFT_ADK_LOG_LEVEL=INFO,KB_MODE=local,DEFAULT_SEARCH_K=5,LATEX_COMPILE_ENGINE=lualatex,LATEX_COMPILE_TIMEOUT=30,LATEX_OUTPUT_FORMATS=pdf,svg,png,NODE_ENV=production" \
    --set-secrets "GOOGLE_API_KEY=feynmancraft-google-api-key:latest"

# 9. 获取服务URL
echo "9️⃣ 获取服务信息..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "🎉 部署完成！"
echo "=================================="
echo "🌐 服务URL: $SERVICE_URL"
echo "🔧 后端API: $SERVICE_URL"
echo "🎨 前端界面: $SERVICE_URL"
echo ""
echo "📊 查看日志:"
echo "gcloud run services logs read $SERVICE_NAME --platform managed --region $REGION --follow"
echo ""
echo "🔄 更新服务:"
echo "重新运行此脚本即可更新"
echo ""
echo "🗑️ 删除服务:"
echo "gcloud run services delete $SERVICE_NAME --platform managed --region $REGION"