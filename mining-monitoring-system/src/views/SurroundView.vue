<template>
  <div class="surround-view">
    <el-row :gutter="20">
      <el-col :span="18">
        <!-- 主显示区域 -->
        <el-card class="main-view">
          <template #header>
            <div class="card-header">
              <span>360° 环视图</span>
              <div class="controls">
                <el-button-group>
                  <el-button type="primary" :icon="ZoomIn">放大</el-button>
                  <el-button type="primary" :icon="ZoomOut">缩小</el-button>
                </el-button-group>
                <el-button type="success" :icon="Camera" style="margin-left: 10px">截图</el-button>
              </div>
            </div>
          </template>
          <div class="canvas-container" ref="canvasContainer">
            <!-- Canvas将在mounted时初始化 -->
            <canvas ref="mainCanvas"></canvas>
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
          
          <!-- 视图模式选择 -->
          <div class="control-section">
            <h4>视图模式</h4>
            <el-radio-group v-model="viewMode">
              <el-radio label="360">360°环视</el-radio>
              <el-radio label="top">俯视图</el-radio>
              <el-radio label="single">单相机</el-radio>
            </el-radio-group>
          </div>
          
          <!-- 相机选择 -->
          <div class="control-section" v-if="viewMode === 'single'">
            <h4>相机选择</h4>
            <el-select v-model="selectedCamera" style="width: 100%">
              <el-option v-for="i in 8" :key="i" :label="'相机 ' + i" :value="i" />
            </el-select>
          </div>
          
          <!-- 图像调节 -->
          <div class="control-section">
            <h4>图像调节</h4>
            <div class="slider-item">
              <span>亮度</span>
              <el-slider v-model="brightness" :min="0" :max="200" :step="1" />
            </div>
            <div class="slider-item">
              <span>对比度</span>
              <el-slider v-model="contrast" :min="0" :max="200" :step="1" />
            </div>
          </div>
          
          <!-- 系统信息 -->
          <div class="control-section">
            <h4>系统信息</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统延迟">
                <el-tag type="success">45ms</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="帧率">
                <el-tag type="success">30fps</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="分辨率">1920×1080</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ZoomIn, ZoomOut, Camera } from '@element-plus/icons-vue'
import * as THREE from 'three'
import { getCameraFrames } from '../utils/api'

// 响应式状态
const viewMode = ref('360')
const selectedCamera = ref(1)
const brightness = ref(100)
const contrast = ref(100)
const cameraFrames = ref([])
const isLoading = ref(false)
const updateInterval = ref(null)

// Three.js相关
const canvasContainer = ref(null)
const mainCanvas = ref(null)
let scene, camera, renderer, animationFrameId
let cameraTextures = []
let cylinderMesh

// 获取相机数据
const fetchCameraData = async () => {
    try {
        isLoading.value = true
        const response = await getCameraFrames()
        cameraFrames.value = response.frames
        updateCameraTextures()
    } catch (error) {
        console.error('Error fetching camera frames:', error)
    } finally {
        isLoading.value = false
    }
}

// 更新相机纹理
const updateCameraTextures = () => {
    if (!cameraFrames.value || !cylinderMesh) return

    cameraFrames.value.forEach((frame, index) => {
        const texture = cameraTextures[index] || new THREE.Texture()
        const img = new Image()
        img.onload = () => {
            texture.image = img
            texture.needsUpdate = true
        }
        img.src = `data:image/jpeg;base64,${frame}`
    })

    // 更新圆柱体材质
    if (cylinderMesh && cameraTextures.length > 0) {
        const materials = cameraTextures.map(texture => 
            new THREE.MeshBasicMaterial({ 
                map: texture,
                side: THREE.DoubleSide
            })
        )
        cylinderMesh.material = materials
    }
}

// 初始化Three.js场景
const initThreeJS = () => {
    // 创建场景
    scene = new THREE.Scene()
    
    // 创建相机
    const aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
    camera.position.set(0, 0, 5)
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({
        canvas: mainCanvas.value,
        antialias: true
    })
    renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
    
    // 创建圆柱体几何体
    const geometry = new THREE.CylinderGeometry(2, 2, 4, 8, 1, true)
    
    // 初始化纹理
    cameraTextures = Array(8).fill(null).map(() => new THREE.Texture())
    
    // 创建材质
    const materials = cameraTextures.map(texture => 
        new THREE.MeshBasicMaterial({ 
            map: texture,
            side: THREE.DoubleSide
        })
    )
    
    // 创建圆柱体网格
    cylinderMesh = new THREE.Mesh(geometry, materials)
    scene.add(cylinderMesh)
    
    // 动画循环
    const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        cylinderMesh.rotation.y += 0.001
        renderer.render(scene, camera)
    }
    animate()
}

// 监听窗口大小变化
const handleResize = () => {
    if (camera && renderer && canvasContainer.value) {
        const width = canvasContainer.value.clientWidth
        const height = canvasContainer.value.clientHeight
        camera.aspect = width / height
        camera.updateProjectionMatrix()
        renderer.setSize(width, height)
    }
}

// 生命周期钩子
onMounted(() => {
    initThreeJS()
    window.addEventListener('resize', handleResize)
    
    // 开始定期获取相机数据
    fetchCameraData()
    updateInterval.value = setInterval(fetchCameraData, 1000/30) // 30fps
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
.surround-view {
  padding: 20px;
  
  .main-view {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .canvas-container {
      height: calc(100vh - 220px);
      min-height: 400px;
      position: relative;
      
      canvas {
        width: 100%;
        height: 100%;
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
      
      .slider-item {
        margin: 10px 0;
        
        span {
          display: block;
          margin-bottom: 5px;
          color: #909399;
        }
      }
    }
  }
}
</style> 