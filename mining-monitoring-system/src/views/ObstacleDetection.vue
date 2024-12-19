<template>
  <div class="obstacle-detection">
    <el-row :gutter="20">
      <el-col :span="18">
        <!-- 主显示区域 -->
        <el-card class="main-display">
          <template #header>
            <div class="card-header">
              <span>障碍物检测与识别</span>
              <div class="controls">
                <el-button-group>
                  <el-button type="primary" :icon="ZoomIn">放大</el-button>
                  <el-button type="primary" :icon="ZoomOut">缩小</el-button>
                </el-button-group>
                <el-button type="warning" :icon="Warning" style="margin-left: 10px">
                  碰撞预警
                  <el-badge :value="warningCount" :max="99" class="warning-badge" v-if="warningCount > 0"/>
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="display-container">
            <!-- 3D场景容器 -->
            <div class="scene-container" ref="sceneContainer">
              <canvas ref="sceneCanvas"></canvas>
              
              <!-- 距离指示器 -->
              <div class="distance-indicator">
                <div class="scale-line"></div>
                <div class="scale-labels">
                  <span>0m</span>
                  <span>15m</span>
                  <span>30m</span>
                </div>
              </div>
            </div>
            
            <!-- 实时检测列表 -->
            <div class="detection-list">
              <div class="list-header">
                <h4>实时检测列表</h4>
                <el-tag type="success">{{ detectionCount }}个目标</el-tag>
              </div>
              <el-scrollbar height="200px">
                <div v-for="item in detectionList" :key="item.id" class="detection-item">
                  <div class="item-icon">
                    <el-icon :size="24" :color="item.color">
                      <component :is="item.icon"></component>
                    </el-icon>
                  </div>
                  <div class="item-info">
                    <div class="item-title">{{ item.type }}</div>
                    <div class="item-detail">
                      距离: {{ item.distance }}m / 方向: {{ item.direction }}°
                    </div>
                  </div>
                  <div class="item-status">
                    <el-tag :type="item.status === 'safe' ? 'success' : 'danger'">
                      {{ item.status === 'safe' ? '安全' : '警告' }}
                    </el-tag>
                  </div>
                </div>
              </el-scrollbar>
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
          
          <!-- 检测设置 -->
          <div class="control-section">
            <h4>检测设置</h4>
            <div class="setting-item">
              <span>检测范围</span>
              <el-slider
                v-model="detectionRange"
                :min="5"
                :max="30"
                :step="5"
                :marks="{5: '5m', 15: '15m', 30: '30m'}"
              />
            </div>
            <div class="setting-item">
              <span>最小目标尺寸</span>
              <el-input-number
                v-model="minObjectSize"
                :min="10"
                :max="100"
                :step="10"
                size="small"
              >
                <template #suffix>cm</template>
              </el-input-number>
            </div>
          </div>
          
          <!-- 目标过滤 -->
          <div class="control-section">
            <h4>目标过滤</h4>
            <el-checkbox-group v-model="targetTypes">
              <el-checkbox label="person">人员</el-checkbox>
              <el-checkbox label="vehicle">车辆</el-checkbox>
              <el-checkbox label="rock">大石块</el-checkbox>
            </el-checkbox-group>
          </div>
          
          <!-- 预警设置 -->
          <div class="control-section">
            <h4>预警设置</h4>
            <div class="setting-item">
              <span>预警距离</span>
              <el-slider
                v-model="warningDistance"
                :min="2"
                :max="10"
                :step="1"
                :marks="{2: '2m', 5: '5m', 10: '10m'}"
              />
            </div>
            <el-switch
              v-model="autoWarning"
              active-text="自动预警"
              inactive-text="手动预警"
            />
          </div>
          
          <!-- 系统状态 -->
          <div class="control-section">
            <h4>系统状态</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="雷达状态">
                <el-tag type="success">正常运行</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="系统延迟">
                <el-tag type="success">45ms</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="识别准确率">95%</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ZoomIn, ZoomOut, Warning, User, Van, Box } from '@element-plus/icons-vue'
import * as THREE from 'three'
import { getLidarData, getRadarData } from '../utils/api'

// 响应式状态
const detectionRange = ref(30)
const minObjectSize = ref(50)
const targetTypes = ref(['person', 'vehicle', 'rock'])
const warningDistance = ref(5)
const autoWarning = ref(true)
const warningCount = ref(0)
const detectionCount = ref(0)
const isLoading = ref(false)
const updateInterval = ref(null)

// 检测列表数据
const detectionList = ref([])

// Three.js相关
const sceneContainer = ref(null)
const sceneCanvas = ref(null)
let scene, camera, renderer, animationFrameId
let pointCloud, obstacleMarkers = []

// 获取传感器数据
const fetchSensorData = async () => {
    try {
        isLoading.value = true
        const [lidarResponse, radarResponse] = await Promise.all([
            getLidarData(),
            getRadarData()
        ])
        
        updatePointCloud(lidarResponse.point_clouds)
        updateObstacles(radarResponse.radar_data)
    } catch (error) {
        console.error('Error fetching sensor data:', error)
    } finally {
        isLoading.value = false
    }
}

// 更新点云显示
const updatePointCloud = (pointClouds) => {
    if (!scene) return
    
    // 移除旧的点云
    if (pointCloud) {
        scene.remove(pointCloud)
    }
    
    // 合并所有激光雷达的点云数据
    const allPoints = []
    pointClouds.forEach(pc => {
        allPoints.push(...pc.points)
    })
    
    // 创建点云几何体
    const geometry = new THREE.BufferGeometry()
    const vertices = new Float32Array(allPoints.flat())
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
    
    // 创建点云材质
    const material = new THREE.PointsMaterial({
        size: 0.1,
        color: 0x00ff00,
        transparent: true,
        opacity: 0.8
    })
    
    // 创建点云对象
    pointCloud = new THREE.Points(geometry, material)
    scene.add(pointCloud)
}

// 更新障碍物标记
const updateObstacles = (radarData) => {
    // 清除旧的障碍物标记
    obstacleMarkers.forEach(marker => scene.remove(marker))
    obstacleMarkers = []
    
    // 更新检测列表
    const newDetectionList = []
    let warnings = 0
    
    radarData.forEach(radar => {
        radar.objects.forEach(obj => {
            // 创建障碍物3D标记
            const geometry = new THREE.SphereGeometry(0.5, 32, 32)
            const material = new THREE.MeshBasicMaterial({
                color: getObstacleColor(obj.type),
                transparent: true,
                opacity: 0.8
            })
            const marker = new THREE.Mesh(geometry, material)
            
            // 计算障碍物位置
            const x = obj.distance * Math.cos(obj.angle)
            const z = obj.distance * Math.sin(obj.angle)
            marker.position.set(x, 0.5, z)
            
            scene.add(marker)
            obstacleMarkers.push(marker)
            
            // 添加到检测列表
            const isSafe = obj.distance > warningDistance.value
            if (!isSafe) warnings++
            
            newDetectionList.push({
                id: Math.random(),
                type: getObstacleType(obj.type),
                distance: obj.distance.toFixed(1),
                direction: (obj.angle * 180 / Math.PI).toFixed(0),
                status: isSafe ? 'safe' : 'warning',
                icon: getObstacleIcon(obj.type),
                color: getObstacleColor(obj.type)
            })
        })
    })
    
    detectionList.value = newDetectionList
    detectionCount.value = newDetectionList.length
    warningCount.value = warnings
}

// 辅助函数
const getObstacleType = (type) => {
    switch (type) {
        case 'truck': return '车辆'
        case 'person': return '人员'
        default: return '大石块'
    }
}

const getObstacleIcon = (type) => {
    switch (type) {
        case 'truck': return 'Van'
        case 'person': return 'User'
        default: return 'Box'
    }
}

const getObstacleColor = (type) => {
    switch (type) {
        case 'truck': return 0x67C23A
        case 'person': return 0x409EFF
        default: return 0xE6A23C
    }
}

// 初始化Three.js场景
const initThreeJS = () => {
    // 创建场景
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x000000)
    
    // 创建相机
    const aspect = sceneContainer.value.clientWidth / sceneContainer.value.clientHeight
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
    camera.position.set(0, 20, 20)
    camera.lookAt(0, 0, 0)
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({
        canvas: sceneCanvas.value,
        antialias: true
    })
    renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight)
    
    // 添加地面网格
    const gridHelper = new THREE.GridHelper(30, 30, 0x404040, 0x404040)
    scene.add(gridHelper)
    
    // 添加环形标记（探测范围）
    const rangeGeometry = new THREE.RingGeometry(29.5, 30.5, 64)
    const rangeMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5
    })
    const rangeRing = new THREE.Mesh(rangeGeometry, rangeMaterial)
    rangeRing.rotation.x = -Math.PI / 2
    scene.add(rangeRing)
    
    // 动画循环
    const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        
        // 更新障碍物标记的旋转
        obstacleMarkers.forEach(marker => {
            marker.rotation.y += 0.01
        })
        
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
    
    // 开始定期获取传感器数据
    fetchSensorData()
    updateInterval.value = setInterval(fetchSensorData, 1000/30) // 30fps
})

onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
    }
    if (renderer) {
        renderer.dispose()
    }
    if (updateInterval.value) {
        clearInterval(updateInterval.value)
    }
})
</script>

<style lang="scss" scoped>
.obstacle-detection {
  padding: 20px;
  
  .main-display {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .warning-badge {
        margin-top: -2px;
        margin-left: 2px;
      }
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
        
        .distance-indicator {
          position: absolute;
          bottom: 20px;
          right: 20px;
          background: rgba(0, 0, 0, 0.5);
          padding: 10px;
          border-radius: 4px;
          color: white;
          
          .scale-line {
            width: 200px;
            height: 4px;
            background: linear-gradient(to right, #409EFF, #67C23A);
            margin-bottom: 5px;
          }
          
          .scale-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
          }
        }
      }
      
      .detection-list {
        margin-top: 20px;
        
        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
          
          h4 {
            margin: 0;
          }
        }
        
        .detection-item {
          display: flex;
          align-items: center;
          padding: 10px;
          border-bottom: 1px solid #EBEEF5;
          
          &:last-child {
            border-bottom: none;
          }
          
          .item-icon {
            margin-right: 15px;
          }
          
          .item-info {
            flex: 1;
            
            .item-title {
              font-weight: bold;
              margin-bottom: 5px;
            }
            
            .item-detail {
              font-size: 12px;
              color: #909399;
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
    }
  }
}
</style> 