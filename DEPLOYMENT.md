# FeynmanCraft Cloud Run 部署指南

## 🚀 一键部署（推荐）

### 快速部署
```bash
# 确保 .env 文件包含 GOOGLE_API_KEY
./cloud-run-quick-deploy.sh
```

---

## 📋 同事部署指南

### 方式1：使用服务账号密钥（推荐）

**管理员操作（你现在执行）：**
```bash
# 创建服务账号
gcloud iam service-accounts create feynmancraft-deployer \
    --display-name="FeynmanCraft Deployer"

# 分配权限
gcloud projects add-iam-policy-binding gen-lang-client-0986192769 \
    --member="serviceAccount:feynmancraft-deployer@gen-lang-client-0986192769.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding gen-lang-client-0986192769 \
    --member="serviceAccount:feynmancraft-deployer@gen-lang-client-0986192769.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding gen-lang-client-0986192769 \
    --member="serviceAccount:feynmancraft-deployer@gen-lang-client-0986192769.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

# 生成密钥文件
gcloud iam service-accounts keys create ./feynmancraft-key.json \
    --iam-account=feynmancraft-deployer@gen-lang-client-0986192769.iam.gserviceaccount.com

echo "✅ 请将 feynmancraft-key.json 发给同事"
```

**同事操作：**
```bash
# 1. 安装依赖
# - 安装 Docker
# - 安装 Google Cloud SDK: curl https://sdk.cloud.google.com | bash

# 2. 认证
export GOOGLE_APPLICATION_CREDENTIALS="./feynmancraft-key.json"
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud config set project gen-lang-client-0986192769

# 3. 部署（自动跳过认证步骤）
./cloud-run-quick-deploy.sh
```

### 方式2：临时访问令牌（简单）

**管理员操作：**
```bash
# 生成访问令牌
gcloud auth print-access-token > access_token.txt
echo "✅ 请将 access_token.txt 发给同事（24小时有效）"
```

**同事操作：**
```bash
# 使用访问令牌认证
export GOOGLE_OAUTH_ACCESS_TOKEN=$(cat access_token.txt)
gcloud config set project gen-lang-client-0986192769

# 构建和部署
docker build -t gcr.io/gen-lang-client-0986192769/feynmancraft-adk .
docker push gcr.io/gen-lang-client-0986192769/feynmancraft-adk

gcloud run deploy feynmancraft-adk \
    --image gcr.io/gen-lang-client-0986192769/feynmancraft-adk \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --port 8080 \
    --set-secrets "GOOGLE_API_KEY=feynmancraft-google-api-key:latest"
```

---

## 🧪 本地测试

### Docker测试
```bash
# 构建并测试Docker镜像
./test-docker.sh

# 或使用Docker Compose
docker-compose up --build
```

### 本地开发
```bash
# 启动本地服务
./start.sh

# 停止服务
./stop.sh

# 查看状态
./status.sh
```

---

## 🔧 手动部署步骤

### 1. 环境准备
```bash
# 安装Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 认证
gcloud auth login
gcloud config set project gen-lang-client-0986192769
```

### 2. 启用API
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. 创建密钥
```bash
# 从.env读取API密钥
source .env
echo -n "$GOOGLE_API_KEY" | gcloud secrets create feynmancraft-google-api-key \
    --data-file=- --replication-policy="automatic"
```

### 4. 构建和推送
```bash
# 构建镜像
docker build -t gcr.io/gen-lang-client-0986192769/feynmancraft-adk .

# 推送镜像
docker push gcr.io/gen-lang-client-0986192769/feynmancraft-adk
```

### 5. 部署到Cloud Run
```bash
gcloud run deploy feynmancraft-adk \
    --image gcr.io/gen-lang-client-0986192769/feynmancraft-adk \
    --platform managed \
    --region us-central1 \
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
```

---

## 📊 监控和管理

### 查看服务状态
```bash
# 列出所有服务
gcloud run services list --platform managed

# 查看服务详情
gcloud run services describe feynmancraft-adk --platform managed --region us-central1

# 查看实时日志
gcloud run services logs read feynmancraft-adk --platform managed --region us-central1 --follow
```

### 更新服务
```bash
# 重新构建和部署
./cloud-run-quick-deploy.sh

# 或手动更新
docker build -t gcr.io/gen-lang-client-0986192769/feynmancraft-adk .
docker push gcr.io/gen-lang-client-0986192769/feynmancraft-adk
gcloud run services update feynmancraft-adk --platform managed --region us-central1
```

### 删除服务
```bash
# 删除Cloud Run服务
gcloud run services delete feynmancraft-adk --platform managed --region us-central1

# 删除容器镜像
gcloud container images delete gcr.io/gen-lang-client-0986192769/feynmancraft-adk

# 删除密钥
gcloud secrets delete feynmancraft-google-api-key
```

---

## 🐛 问题排查

### 常见错误

**1. Docker构建失败**
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker build --no-cache -t gcr.io/gen-lang-client-0986192769/feynmancraft-adk .
```

**2. 推送镜像失败**
```bash
# 配置Docker认证
gcloud auth configure-docker

# 重新推送
docker push gcr.io/gen-lang-client-0986192769/feynmancraft-adk
```

**3. 服务启动失败**
```bash
# 查看详细日志
gcloud run services logs read feynmancraft-adk --platform managed --region us-central1 --limit 100

# 检查环境变量
gcloud run services describe feynmancraft-adk --platform managed --region us-central1
```

**4. API密钥问题**
```bash
# 重新创建密钥
gcloud secrets delete feynmancraft-google-api-key
source .env
echo -n "$GOOGLE_API_KEY" | gcloud secrets create feynmancraft-google-api-key \
    --data-file=- --replication-policy="automatic"
```

### 健康检查
```bash
# 检查服务健康状态
SERVICE_URL=$(gcloud run services describe feynmancraft-adk --platform managed --region us-central1 --format 'value(status.url)')
curl -f $SERVICE_URL/health

# 测试前端
curl -f $SERVICE_URL/

# 测试后端API
curl -f $SERVICE_URL/list-apps
```

---

## 🌐 访问URL

部署完成后，服务将在以下URL可用：
- **主服务**: https://feynmancraft-adk-xxxxxxxxxx-uc.a.run.app
- **前端界面**: 同主服务URL
- **后端API**: 同主服务URL + API端点

---

## 💰 费用控制

### 资源配置
- **内存**: 4GB
- **CPU**: 2核
- **并发**: 100请求/实例
- **超时**: 300秒
- **最小实例**: 0（按需启动）
- **最大实例**: 10

### 估计费用
- **请求费用**: $0.40 / 百万请求
- **CPU费用**: $0.00002400 / vCPU秒
- **内存费用**: $0.00000250 / GB秒
- **预计月费用**: 轻度使用约$5-20

---

## 📞 支持

如有问题，请：
1. 查看日志排查
2. 参考问题排查章节
3. 联系项目维护者

**项目仓库**: https://github.com/your-repo/feynmancraft-adk
**部署时间**: 约5-10分钟
**维护者**: Kevin Zhang