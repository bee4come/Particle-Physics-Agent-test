#!/bin/bash
set -e

echo "🔐 创建 FeynmanCraft 部署服务账号..."

PROJECT_ID="gen-lang-client-0986192769"
SERVICE_ACCOUNT="feynmancraft-deployer"
KEY_FILE="feynmancraft-key.json"

# 创建服务账号
echo "📋 创建服务账号..."
gcloud iam service-accounts create $SERVICE_ACCOUNT \
    --display-name="FeynmanCraft Deployer" \
    --project=$PROJECT_ID || echo "服务账号已存在，跳过创建"

# 分配权限
echo "🔑 分配权限..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

# 生成密钥文件
echo "🔐 生成密钥文件..."
gcloud iam service-accounts keys create ./$KEY_FILE \
    --iam-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com

echo ""
echo "✅ 服务账号创建完成！"
echo "📁 密钥文件: $KEY_FILE"
echo ""
echo "🚀 给同事的部署命令："
echo "export GOOGLE_APPLICATION_CREDENTIALS='./$KEY_FILE'"
echo "gcloud auth activate-service-account --key-file=\$GOOGLE_APPLICATION_CREDENTIALS"
echo "gcloud config set project $PROJECT_ID"
echo "./cloud-run-quick-deploy.sh"
echo ""
echo "📤 请将 $KEY_FILE 安全地发送给同事"