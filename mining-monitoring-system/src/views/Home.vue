<template>
  <div class="home-container">
    <el-row :gutter="20">
      <!-- 360环视 -->
      <el-col :span="12">
        <el-card class="view-card">
          <template #header>
            <div class="card-header">
              <span>360环视图</span>
              <el-button type="primary" @click="$router.push('/surround')">查看详情</el-button>
            </div>
          </template>
          <div class="preview-container">
            <img src="https://via.placeholder.com/600x300?text=360环视预览" alt="360环视预览" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 主视野 -->
      <el-col :span="12">
        <el-card class="view-card">
          <template #header>
            <div class="card-header">
              <span>主视野拼接</span>
              <el-button type="primary" @click="$router.push('/main-view')">查看详情</el-button>
            </div>
          </template>
          <div class="preview-container">
            <img src="https://via.placeholder.com/600x300?text=主视野预览" alt="主视野预览" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 障碍物检测 -->
      <el-col :span="12">
        <el-card class="view-card">
          <template #header>
            <div class="card-header">
              <span>障碍物检测</span>
              <el-button type="primary" @click="$router.push('/obstacle')">查看详情</el-button>
            </div>
          </template>
          <div class="preview-container">
            <img src="https://via.placeholder.com/600x300?text=障碍物检测预览" alt="障碍物检测预览" />
          </div>
        </el-card>
      </el-col>
      
      <!-- BEV视图 -->
      <el-col :span="12">
        <el-card class="view-card">
          <template #header>
            <div class="card-header">
              <span>BEV视图</span>
              <el-button type="primary" @click="$router.push('/bev')">查看详情</el-button>
            </div>
          </template>
          <div class="preview-container">
            <img src="https://via.placeholder.com/600x300?text=BEV视图预览" alt="BEV视图预览" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态 -->
    <el-card class="status-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>系统状态</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="status-item">
            <el-icon><VideoCamera /></el-icon>
            <div class="status-info">
              <div class="label">相机状态</div>
              <div class="value">
                <el-tag type="success">正常运行</el-tag>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon><Connection /></el-icon>
            <div class="status-info">
              <div class="label">系统延迟</div>
              <div class="value">45ms</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon><Monitor /></el-icon>
            <div class="status-info">
              <div class="label">CPU使用率</div>
              <div class="value">65%</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <el-icon><Warning /></el-icon>
            <div class="status-info">
              <div class="label">告警信息</div>
              <div class="value">0条</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { VideoCamera, Connection, Monitor, Warning } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.view-card {
  height: 100%;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .preview-container {
    height: 300px;
    background-color: #f5f7fa;
    display: flex;
    justify-content: center;
    align-items: center;
    
    img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }
}

.status-card {
  .status-item {
    display: flex;
    align-items: center;
    padding: 10px;
    
    .el-icon {
      font-size: 24px;
      margin-right: 10px;
      color: #409EFF;
    }
    
    .status-info {
      .label {
        font-size: 14px;
        color: #909399;
      }
      
      .value {
        font-size: 16px;
        font-weight: bold;
        color: #303133;
        margin-top: 5px;
      }
    }
  }
}
</style> 