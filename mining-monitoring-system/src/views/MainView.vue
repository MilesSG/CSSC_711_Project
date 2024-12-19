<template>
  <div class="main-view-container">
    <el-row :gutter="20">
      <el-col :span="18">
        <!-- 主视野显示区域 -->
        <el-card class="view-card">
          <template #header>
            <div class="card-header">
              <span>主视野拼接（180° × 150°）</span>
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
            <canvas ref="mainCanvas"></canvas>
            
            <!-- 视角指示器 -->
            <div class="view-indicator">
              <div class="horizontal-scale">
                <span>-90°</span>
                <span>0°</span>
                <span>90°</span>
              </div>
              <div class="vertical-scale">
                <span>75°</span>
                <span>0°</span>
                <span>-75°</span>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 相机预览 -->
        <el-card class="preview-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>相机预览</span>
            </div>
          </template>
          <el-row :gutter="10">
            <el-col :span="8" v-for="i in 3" :key="i">
              <div class="camera-preview">
                <div class="preview-title">相机 {{ i }}</div>
                <div class="preview-image"></div>
              </div>
            </el-col>
          </el-row>
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
          
          <!-- 拼接模式 -->
          <div class="control-section">
            <h4>拼接模式</h4>
            <el-radio-group v-model="stitchMode">
              <el-radio label="auto">自动拼接</el-radio>
              <el-radio label="manual">手动调整</el-radio>
            </el-radio-group>
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
            <div class="slider-item">
              <span>拼接重叠度</span>
              <el-slider v-model="overlap" :min="0" :max="100" :step="1" />
            </div>
          </div>
          
          <!-- 视角控制 -->
          <div class="control-section">
            <h4>视角控制</h4>
            <div class="angle-controls">
              <el-row :gutter="10">
                <el-col :span="12">
                  <span>水平角度</span>
                  <el-input-number 
                    v-model="horizontalAngle" 
                    :min="-90" 
                    :max="90"
                    size="small"
                  />
                </el-col>
                <el-col :span="12">
                  <span>垂直角度</span>
                  <el-input-number 
                    v-model="verticalAngle" 
                    :min="-75" 
                    :max="75"
                    size="small"
                  />
                </el-col>
              </el-row>
            </div>
          </div>
          
          <!-- 系统信息 -->
          <div class="control-section">
            <h4>系统信息</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统延迟">
                <el-tag type="success">45ms</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="拼接状态">
                <el-tag type="success">正常</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="分辨率">4K (3840×2160)</el-descriptions-item>
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
const stitchMode = ref('auto')
const brightness = ref(100)
const contrast = ref(100)
const overlap = ref(30)
const horizontalAngle = ref(0)
const verticalAngle = ref(0)
const cameraFrames = ref([])
const isLoading = ref(false)
const updateInterval = ref(null)

// Three.js相关
const canvasContainer = ref(null)
const mainCanvas = ref(null)
let scene, camera, renderer, animationFrameId
let mainViewMeshes = []

// 获取相机数据
const fetchCameraData = async () => {
    try {
        isLoading.value = true
        const response = await getCameraFrames()
        cameraFrames.value = response.frames
        updateMainView()
        updatePreviewImages()
    } catch (error) {
        console.error('Error fetching camera frames:', error)
    } finally {
        isLoading.value = false
    }
}

// 更新主视野显示
const updateMainView = () => {
    if (!cameraFrames.value || mainViewMeshes.length === 0) return

    // 使用前三个相机的图像
    const frontCameras = cameraFrames.value.slice(0, 3)
    frontCameras.forEach((frame, index) => {
        const texture = new THREE.TextureLoader().load(
            `data:image/jpeg;base64,${frame}`,
            (texture) => {
                texture.minFilter = THREE.LinearFilter
                texture.magFilter = THREE.LinearFilter
                texture.format = THREE.RGBFormat
                
                // 更新对应平面的材质
                if (mainViewMeshes[index]) {
                    mainViewMeshes[index].material.map = texture
                    mainViewMeshes[index].material.needsUpdate = true
                }
            }
        )
    })
}

// 更新预览图像
const updatePreviewImages = () => {
    const frontCameras = cameraFrames.value.slice(0, 3)
    const previewElements = document.querySelectorAll('.preview-image')
    
    frontCameras.forEach((frame, index) => {
        if (previewElements[index]) {
            previewElements[index].style.backgroundImage = `url(data:image/jpeg;base64,${frame})`
            previewElements[index].style.backgroundSize = 'cover'
            previewElements[index].style.backgroundPosition = 'center'
        }
    })
}

// 初始化Three.js场景
const initThreeJS = () => {
    // 创建场景
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x000000)
    
    // 创建相机
    const aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
    camera.position.set(0, 0, 5)
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({
        canvas: mainCanvas.value,
        antialias: true,
        alpha: true
    })
    renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
    
    // 创建三个平面，分别对应三个相机视角
    const planeWidth = 4
    const planeHeight = 3
    const gap = 0.05 // 平面之间的间隙
    
    // 左侧平面
    const leftGeometry = new THREE.PlaneGeometry(planeWidth/2, planeHeight)
    const leftMaterial = new THREE.MeshBasicMaterial({
        color: 0x808080,
        side: THREE.DoubleSide
    })
    const leftPlane = new THREE.Mesh(leftGeometry, leftMaterial)
    leftPlane.position.x = -planeWidth/2 - gap
    leftPlane.rotation.y = THREE.MathUtils.degToRad(30)
    scene.add(leftPlane)
    mainViewMeshes.push(leftPlane)
    
    // 中间平面
    const centerGeometry = new THREE.PlaneGeometry(planeWidth, planeHeight)
    const centerMaterial = new THREE.MeshBasicMaterial({
        color: 0x808080,
        side: THREE.DoubleSide
    })
    const centerPlane = new THREE.Mesh(centerGeometry, centerMaterial)
    scene.add(centerPlane)
    mainViewMeshes.push(centerPlane)
    
    // 右侧平面
    const rightGeometry = new THREE.PlaneGeometry(planeWidth/2, planeHeight)
    const rightMaterial = new THREE.MeshBasicMaterial({
        color: 0x808080,
        side: THREE.DoubleSide
    })
    const rightPlane = new THREE.Mesh(rightGeometry, rightMaterial)
    rightPlane.position.x = planeWidth/2 + gap
    rightPlane.rotation.y = THREE.MathUtils.degToRad(-30)
    scene.add(rightPlane)
    mainViewMeshes.push(rightPlane)
    
    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    scene.add(ambientLight)
    
    // 动画循环
    const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        
        // 根据控制面板的角度更新整个场景的旋转
        scene.rotation.y = THREE.MathUtils.degToRad(horizontalAngle.value)
        scene.rotation.x = THREE.MathUtils.degToRad(verticalAngle.value)
        
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
.main-view-container {
  padding: 20px;
  
  .view-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .canvas-container {
      height: calc(100vh - 500px);
      min-height: 400px;
      position: relative;
      background-color: var(--bg-color);
      border-radius: var(--border-radius);
      overflow: hidden;
      
      canvas {
        width: 100%;
        height: 100%;
      }
      
      .view-indicator {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.7);
        padding: 10px;
        border-radius: 4px;
        color: white;
        z-index: 1;
        
        .horizontal-scale, .vertical-scale {
          display: flex;
          justify-content: space-between;
          margin: 5px 0;
          width: 150px;
          
          span {
            font-size: 12px;
          }
        }
      }
    }
  }
  
  .preview-card {
    .camera-preview {
      margin-bottom: 10px;
      
      .preview-title {
        font-size: 14px;
        color: var(--text-color);
        margin-bottom: 5px;
      }
      
      .preview-image {
        height: 120px;
        background-color: var(--bg-color-light);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-small);
        transition: var(--transition);
        
        &:hover {
          transform: scale(1.02);
          box-shadow: var(--box-shadow);
        }
      }
    }
  }
  
  .control-panel {
    .control-section {
      margin-bottom: 20px;
      
      h4 {
        margin: 0 0 10px 0;
        color: var(--text-color);
      }
      
      .slider-item {
        margin: 10px 0;
        
        span {
          display: block;
          margin-bottom: 5px;
          color: var(--text-color-light);
        }
      }
      
      .angle-controls {
        span {
          display: block;
          margin-bottom: 5px;
          color: var(--text-color-light);
        }
        
        .el-input-number {
          width: 100%;
        }
      }
    }
  }
}
</style> 