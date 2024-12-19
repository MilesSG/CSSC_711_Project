<template>
  <div class="bev-view">
    <el-row :gutter="20">
      <el-col :span="18">
        <!-- 主显示区域 -->
        <el-card class="main-display">
          <template #header>
            <div class="card-header">
              <span>BEV 鸟瞰图</span>
              <div class="controls">
                <el-button-group>
                  <el-button type="primary" :icon="ZoomIn">放大</el-button>
                  <el-button type="primary" :icon="ZoomOut">缩小</el-button>
                </el-button-group>
                <el-button type="success" :icon="Camera" style="margin-left: 10px">截图</el-button>
              </div>
            </div>
          </template>
          
          <div class="display-container">
            <!-- 3D场景容器 -->
            <div class="scene-container" ref="sceneContainer">
              <canvas ref="sceneCanvas"></canvas>
              
              <!-- 图例 -->
              <div class="legend">
                <div class="legend-item">
                  <div class="color-box" style="background: #409EFF"></div>
                  <span>相机数据</span>
                </div>
                <div class="legend-item">
                  <div class="color-box" style="background: #67C23A"></div>
                  <span>激光雷达数据</span>
                </div>
                <div class="legend-item">
                  <div class="color-box" style="background: #E6A23C"></div>
                  <span>毫米波雷达数据</span>
                </div>
              </div>
            </div>
            
            <!-- 数据融合信息 -->
            <div class="fusion-info">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="info-card">
                    <div class="info-title">
                      <el-icon><VideoCamera /></el-icon>
                      相机数据
                    </div>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">视野范围:</span>
                        <span class="value">360°</span>
                      </div>
                      <div class="info-item">
                        <span class="label">分辨率:</span>
                        <span class="value">1080P</span>
                      </div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-card">
                    <div class="info-title">
                      <el-icon><Aim /></el-icon>
                      激光雷达数据
                    </div>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">点云密度:</span>
                        <span class="value">高</span>
                      </div>
                      <div class="info-item">
                        <span class="label">扫描范围:</span>
                        <span class="value">30m</span>
                      </div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-card">
                    <div class="info-title">
                      <el-icon><Monitor /></el-icon>
                      毫米波雷达数据
                    </div>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">探测范围:</span>
                        <span class="value">30m</span>
                      </div>
                      <div class="info-item">
                        <span class="label">精度:</span>
                        <span class="value">±5cm</span>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <!-- 控制面板 -->
        <el-card class="control-panel">
          <template #header>
            <div class="card-header">
              <span>控制面板</span>
            </div>
          </template>
          
          <!-- 显示设置 -->
          <div class="control-section">
            <h4>显示设置</h4>
            <el-checkbox-group v-model="displayLayers">
              <el-checkbox label="camera">相机数据层</el-checkbox>
              <el-checkbox label="lidar">激光雷达层</el-checkbox>
              <el-checkbox label="radar">毫米波雷达层</el-checkbox>
              <el-checkbox label="fusion">融合数据层</el-checkbox>
            </el-checkbox-group>
          </div>
          
          <!-- 视图控制 -->
          <div class="control-section">
            <h4>视图控制</h4>
            <div class="setting-item">
              <span>显示范围</span>
              <el-slider
                v-model="displayRange"
                :min="10"
                :max="30"
                :step="5"
                :marks="{10: '10m', 20: '20m', 30: '30m'}"
              />
            </div>
            <div class="setting-item">
              <span>点云密度</span>
              <el-select v-model="pointCloudDensity" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
              </el-select>
            </div>
          </div>
          
          <!-- 数据融合设置 -->
          <div class="control-section">
            <h4>数据融合设置</h4>
            <div class="setting-item">
              <span>融合算法</span>
              <el-radio-group v-model="fusionAlgorithm">
                <el-radio label="kalman">卡尔曼滤波</el-radio>
                <el-radio label="bayesian">贝叶斯融合</el-radio>
              </el-radio-group>
            </div>
            <div class="setting-item">
              <span>置信度阈值</span>
              <el-slider
                v-model="confidenceThreshold"
                :min="0"
                :max="100"
                :step="5"
                :format-tooltip="value => value + '%'"
              />
            </div>
          </div>
          
          <!-- 系统状态 -->
          <div class="control-section">
            <h4>系统状态</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="融合状态">
                <el-tag type="success">正常</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="系统延迟">
                <el-tag type="success">45ms</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据同步">
                <el-tag type="success">已同步</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ZoomIn, ZoomOut, Camera, VideoCamera, Aim, Monitor } from '@element-plus/icons-vue'
import * as THREE from 'three'

// 响应式状态
const displayLayers = ref(['camera', 'lidar', 'radar', 'fusion'])
const displayRange = ref(30)
const pointCloudDensity = ref('high')
const fusionAlgorithm = ref('kalman')
const confidenceThreshold = ref(75)

// Three.js相关
const sceneContainer = ref(null)
const sceneCanvas = ref(null)
let scene, camera, renderer, animationFrameId

// 初始化Three.js场景
const initThreeJS = () => {
  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f2f5)
  
  // 创建相机
  const aspect = sceneContainer.value.clientWidth / sceneContainer.value.clientHeight
  camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
  camera.position.set(0, 30, 0)
  camera.lookAt(0, 0, 0)
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: sceneCanvas.value,
    antialias: true
  })
  renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight)
  
  // 添加地面网格
  const gridHelper = new THREE.GridHelper(30, 30)
  scene.add(gridHelper)
  
  // 添加中心点标记（电铲位置）
  const geometry = new THREE.BoxGeometry(2, 2, 2)
  const material = new THREE.MeshBasicMaterial({ color: 0xff0000 })
  const centerCube = new THREE.Mesh(geometry, material)
  scene.add(centerCube)
  
  // 添加检测范围圈
  const circleGeometry = new THREE.CircleGeometry(displayRange.value, 32)
  const circleMaterial = new THREE.MeshBasicMaterial({
    color: 0x409EFF,
    transparent: true,
    opacity: 0.2,
    side: THREE.DoubleSide
  })
  const circle = new THREE.Mesh(circleGeometry, circleMaterial)
  circle.rotation.x = -Math.PI / 2
  scene.add(circle)
  
  // 模拟点云数据
  const pointsGeometry = new THREE.BufferGeometry()
  const pointsCount = 1000
  const positions = new Float32Array(pointsCount * 3)
  
  for (let i = 0; i < pointsCount; i++) {
    const angle = Math.random() * Math.PI * 2
    const radius = Math.random() * displayRange.value
    positions[i * 3] = Math.cos(angle) * radius
    positions[i * 3 + 1] = Math.random() * 2
    positions[i * 3 + 2] = Math.sin(angle) * radius
  }
  
  pointsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const pointsMaterial = new THREE.PointsMaterial({
    color: 0x67C23A,
    size: 0.1
  })
  const points = new THREE.Points(pointsGeometry, pointsMaterial)
  scene.add(points)
  
  // 动画循环
  const animate = () => {
    animationFrameId = requestAnimationFrame(animate)
    points.rotation.y += 0.001
    renderer.render(scene, camera)
  }
  animate()
}

// 监听窗口大小变化
const handleResize = () => {
  if (camera && renderer && sceneContainer.value) {
    const width = sceneContainer.value.clientWidth
    const height = sceneContainer.value.clientHeight
    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
  }
}

// 生命周期钩子
onMounted(() => {
  initThreeJS()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  if (renderer) {
    renderer.dispose()
  }
})
</script>

<style lang="scss" scoped>
.bev-view {
  padding: 20px;
  
  .main-display {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .display-container {
      .scene-container {
        height: calc(100vh - 500px);
        min-height: 400px;
        position: relative;
        
        canvas {
          width: 100%;
          height: 100%;
        }
        
        .legend {
          position: absolute;
          top: 20px;
          right: 20px;
          background: rgba(255, 255, 255, 0.9);
          padding: 10px;
          border-radius: 4px;
          box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
          
          .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
            
            .color-box {
              width: 16px;
              height: 16px;
              margin-right: 8px;
              border-radius: 2px;
            }
            
            span {
              font-size: 12px;
              color: #606266;
            }
          }
        }
      }
      
      .fusion-info {
        margin-top: 20px;
        
        .info-card {
          background: #f5f7fa;
          border-radius: 4px;
          padding: 15px;
          
          .info-title {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #303133;
            
            .el-icon {
              margin-right: 5px;
            }
          }
          
          .info-content {
            .info-item {
              display: flex;
              justify-content: space-between;
              margin: 5px 0;
              
              .label {
                color: #909399;
              }
              
              .value {
                color: #303133;
                font-weight: 500;
              }
            }
          }
        }
      }
    }
  }
  
  .control-panel {
    .control-section {
      margin-bottom: 20px;
      
      h4 {
        margin: 0 0 10px 0;
        color: #606266;
      }
      
      .setting-item {
        margin: 10px 0;
        
        span {
          display: block;
          margin-bottom: 5px;
          color: #909399;
        }
      }
      
      .el-checkbox-group {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      
      .el-radio-group {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
    }
  }
}
</style> 