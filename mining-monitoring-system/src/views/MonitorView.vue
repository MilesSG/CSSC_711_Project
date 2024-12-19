<template>
  <div class="monitor-view">
    <el-container>
      <!-- 左侧菜单 -->
      <el-aside width="200px" class="main-aside">
        <div class="logo-area">
          <img src="../assets/logo.svg" alt="Logo" class="logo" />
          <h3>矿山监控系统</h3>
        </div>
        
        <el-menu 
          default-active="1" 
          class="main-menu"
          background-color="transparent"
        >
          <el-menu-item index="1">
            <el-icon><Monitor /></el-icon>
            <span>实时监控</span>
          </el-menu-item>
          <el-menu-item index="2">
            <el-icon><VideoCamera /></el-icon>
            <span>视频回放</span>
          </el-menu-item>
          <el-menu-item index="3">
            <el-icon><Warning /></el-icon>
            <span>报警记录</span>
          </el-menu-item>
        </el-menu>

        <div class="system-status">
          <div class="status-item">
            <span>CPU使用率</span>
            <el-progress :percentage="45" :color="customColors" />
          </div>
          <div class="status-item">
            <span>内存使用率</span>
            <el-progress :percentage="65" :color="customColors" />
          </div>
          <div class="status-item">
            <span>存储空间</span>
            <el-progress :percentage="30" :color="customColors" />
          </div>
        </div>
      </el-aside>

      <!-- 主要内容区域 -->
      <el-container>
        <el-header height="50px" class="main-header">
          <div class="header-content">
            <h3>360°环视图</h3>
            <div class="header-info">
              <div class="info-item">
                <el-icon><Timer /></el-icon>
                <span>系统延迟</span>
                <el-tag effect="dark" :type="latency > 50 ? 'warning' : 'info'">{{ latency }}ms</el-tag>
              </div>
              <div class="info-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ currentTime }}</span>
              </div>
            </div>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <!-- 相机视图网格 -->
          <div class="camera-grid">
            <div v-for="i in 8" :key="i" class="camera-frame">
              <div class="frame-header">
                <span>Camera {{ i }}</span>
                <el-tag size="small" type="success">在线</el-tag>
              </div>
              <div class="frame-content">
                <img src="https://via.placeholder.com/640x360/1a1a1a/666666?text=Camera+View" alt="Camera View" />
              </div>
            </div>
          </div>

          <!-- 传感器数据显示 -->
          <div class="sensor-row">
            <!-- 激光雷达显示 -->
            <div class="sensor-panel">
              <div class="panel-header">
                <span>激光雷达数据</span>
                <el-tag type="success" size="small">在线</el-tag>
              </div>
              <div ref="lidarCanvas" class="sensor-canvas"></div>
            </div>

            <!-- 毫米波雷达显示 -->
            <div class="sensor-panel">
              <div class="panel-header">
                <span>毫米波雷达数据</span>
                <el-tag type="success" size="small">在线</el-tag>
              </div>
              <div ref="radarCanvas" class="sensor-canvas"></div>
            </div>

            <!-- BEV融合显示 -->
            <div class="sensor-panel">
              <div class="panel-header">
                <span>BEV数据融合</span>
                <div class="panel-controls">
                  <el-tag type="primary" size="small">相机</el-tag>
                  <el-tag type="success" size="small">激光</el-tag>
                  <el-tag type="warning" size="small">毫米波</el-tag>
                </div>
              </div>
              <div ref="bevCanvas" class="sensor-canvas"></div>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import axios from 'axios'
import { 
  Monitor, 
  VideoCamera, 
  Warning, 
  Timer,
  Calendar
} from '@element-plus/icons-vue'

export default {
  name: 'MonitorView',
  components: {
    Monitor,
    VideoCamera,
    Warning,
    Timer,
    Calendar
  },
  setup() {
    const cameraFrames = ref([])
    const lidarScene = ref(null)
    const radarScene = ref(null)
    const bevScene = ref(null)
    const updateInterval = ref(null)
    const latency = ref(0)
    const currentTime = ref('')

    const customColors = [
      { color: '#67C23A', percentage: 20 },
      { color: '#E6A23C', percentage: 40 },
      { color: '#F56C6C', percentage: 80 }
    ]

    // 更新时间
    const updateTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleString()
    }

    // 初始化Three.js场景
    const initThreeJS = (container, isLidar = true) => {
      const width = container.clientWidth
      const height = container.clientHeight
      
      const scene = new THREE.Scene()
      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true
      })
      
      renderer.setSize(width, height)
      renderer.setClearColor(0x000000, 0.1)
      container.appendChild(renderer.domElement)
      
      // 添加网格
      const gridHelper = new THREE.GridHelper(60, 60, 0x444444, 0x222222)
      scene.add(gridHelper)
      
      // 添加环形标记（30m范围）
      const geometry = new THREE.RingGeometry(29.5, 30.5, 64)
      const material = new THREE.MeshBasicMaterial({ 
        color: 0x00ff00,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5
      })
      const ring = new THREE.Mesh(geometry, material)
      ring.rotation.x = -Math.PI / 2
      scene.add(ring)
      
      // 设置相机位置
      camera.position.set(0, 40, 40)
      camera.lookAt(0, 0, 0)
      
      // 动画循环
      const animate = () => {
        requestAnimationFrame(animate)
        renderer.render(scene, camera)
      }
      animate()
      
      return { scene, camera, renderer }
    }

    // 更新数据
    const updateData = async () => {
      const startTime = performance.now()
      try {
        // 获取相机数据
        const cameraResponse = await axios.get('http://localhost:8000/camera/frames')
        if (cameraResponse.data.status === 'success' && Array.isArray(cameraResponse.data.frames)) {
          cameraFrames.value = cameraResponse.data.frames
          console.log('Camera frames updated:', cameraFrames.value.length)
        } else {
          console.error('Invalid camera response:', cameraResponse.data)
        }

        // 获取激光雷达数据
        const lidarResponse = await axios.get('http://localhost:8000/lidar/data')
        if (lidarResponse.data.status === 'success') {
          updateLidarView(lidarResponse.data.point_clouds)
        }

        // 获取毫米波雷达数据
        const radarResponse = await axios.get('http://localhost:8000/radar/data')
        if (radarResponse.data.status === 'success') {
          updateRadarView(radarResponse.data.radar_data)
        }

        // 计算延迟
        latency.value = Math.round(performance.now() - startTime)
      } catch (error) {
        console.error('Error fetching data:', error)
        if (error.response) {
          console.error('Error response:', error.response.data)
        }
      }
    }

    // 更新激光雷达视图
    const updateLidarView = (pointClouds) => {
      if (!lidarScene.value) return
      
      // 清除旧的点云
      lidarScene.value.scene.children = lidarScene.value.scene.children.filter(
        child => child instanceof THREE.GridHelper || child instanceof THREE.Mesh
      )
      
      // 添加新的点云
      pointClouds.forEach(pc => {
        const geometry = new THREE.BufferGeometry()
        const vertices = new Float32Array(pc.points.flat())
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
        
        const material = new THREE.PointsMaterial({ 
          color: 0x00ff00,
          size: 0.2,
          sizeAttenuation: true
        })
        const points = new THREE.Points(geometry, material)
        lidarScene.value.scene.add(points)
      })
    }

    // 更新毫米波雷达视图
    const updateRadarView = (radarData) => {
      if (!radarScene.value) return
      
      // 清除旧的对象
      radarScene.value.scene.children = radarScene.value.scene.children.filter(
        child => child instanceof THREE.GridHelper || child instanceof THREE.Mesh
      )
      
      // 添加新的对象
      radarData.forEach(radar => {
        radar.objects.forEach(obj => {
          const geometry = new THREE.SphereGeometry(0.5, 32, 32)
          const material = new THREE.MeshBasicMaterial({ 
            color: obj.type === 1 ? 0xff0000 : 0xff6600,
            transparent: true,
            opacity: 0.8
          })
          const sphere = new THREE.Mesh(geometry, material)
          
          // 将极坐标转换为笛卡尔坐标
          sphere.position.x = obj.distance * Math.cos(obj.angle)
          sphere.position.z = obj.distance * Math.sin(obj.angle)
          
          radarScene.value.scene.add(sphere)
        })
      })
    }

    onMounted(() => {
      // 初始化Three.js场景
      const lidarContainer = document.querySelector('.sensor-canvas')
      const radarContainer = document.querySelectorAll('.sensor-canvas')[1]
      const bevContainer = document.querySelectorAll('.sensor-canvas')[2]
      
      if (lidarContainer && radarContainer && bevContainer) {
        lidarScene.value = initThreeJS(lidarContainer)
        radarScene.value = initThreeJS(radarContainer)
        bevScene.value = initThreeJS(bevContainer)
      }
      
      // 立即更新一次数据
      updateData()
      
      // 开始定时更新数据
      updateInterval.value = setInterval(updateData, 1000/30) // 30fps更新频率
      
      // 更新时间
      updateTime()
      setInterval(updateTime, 1000)
    })

    onUnmounted(() => {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
      }
    })

    return {
      cameraFrames,
      latency,
      currentTime,
      customColors
    }
  }
}
</script>

<style lang="scss" scoped>
.monitor-view {
  height: 100vh;
  background-color: #1a1a1a;
  color: #fff;
}

.main-header {
  background-color: var(--bg-color-light);
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  height: 60px;
  position: relative;
  z-index: 1000;
  box-shadow: var(--box-shadow-light);
}

.header-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  height: 40px;
  width: 40px;
}

.header-info {
  display: flex;
  gap: 30px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-container {
  height: calc(100vh - 60px);
}

.main-aside {
  background-color: var(--bg-color-light);
  border-right: 1px solid var(--border-color);
  padding: 20px 0;
  transition: var(--transition);
}

.user-info {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: var(--text-color);
}

.status {
  font-size: 12px;
  color: var(--success-color);
}

.main-menu {
  border: none;
}

.system-status {
  padding: 20px;
  margin-top: auto;
}

.status-item {
  margin-bottom: 15px;
}

.status-item span {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: var(--text-color-light);
}

.main-content {
  padding: 20px;
  height: calc(100vh - 50px);
  overflow-y: auto;
}

.monitor-section {
  background-color: var(--bg-color-light);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--box-shadow);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-controls {
  display: flex;
  gap: 20px;
}

.camera-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  padding: 10px;
}

.camera-container.ipm {
  grid-template-columns: repeat(2, 1fr);
}

.camera-container.fusion {
  grid-template-columns: repeat(1, 1fr);
}

.camera-frame {
  aspect-ratio: 16/9;
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  position: relative;
  transition: var(--transition);
  border: 1px solid var(--border-color);
}

.camera-frame:hover {
  transform: scale(1.02);
  box-shadow: var(--box-shadow);
}

.camera-frame.selected {
  border: 2px solid var(--primary-color);
}

.frame-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 10px;
  background: linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, transparent 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.frame-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.camera-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sensor-section {
  margin-top: 20px;
}

.sensor-card {
  background-color: var(--bg-color-light);
  border-radius: var(--border-radius);
  padding: 20px;
  height: 100%;
  box-shadow: var(--box-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 500;
}

.sensor-canvas {
  width: 100%;
  height: 250px;
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.grid-item .label {
  font-size: 12px;
  color: var(--text-color-light);
}

.fusion-progress {
  padding: 15px;
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
}

.fusion-details {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item .label {
  font-size: 12px;
  color: var(--text-color-light);
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 8px 0;
  border-radius: var(--border-radius);
  margin: 0 10px;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--primary-color) !important;
  color: var(--text-color);
}

:deep(.el-menu-item:hover) {
  background-color: var(--bg-color-lighter);
}

:deep(.el-progress-bar__outer) {
  background-color: var(--bg-color-lighter) !important;
}

:deep(.el-tag) {
  border: none;
}

:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border: none;
}

:deep(.el-button--success) {
  background-color: var(--success-color);
  border: none;
}

:deep(.el-button--warning) {
  background-color: var(--warning-color);
  border: none;
}

:deep(.el-radio-button__inner) {
  background-color: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: -1px 0 0 0 var(--primary-color);
}

.camera-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  
  .camera-frame {
    background: #1a1a1a;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #333;
    
    .frame-header {
      padding: 8px;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 1;
    }
    
    .frame-content {
      aspect-ratio: 16/9;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
}

.sensor-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
  height: 300px;
}

.sensor-panel {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-small);
  overflow: hidden;
}

.panel-header {
  padding: 5px 10px;
  background-color: var(--bg-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sensor-canvas {
  width: 100%;
  height: calc(100% - 30px);
}

.panel-controls {
  display: flex;
  gap: 5px;
}

.main-header {
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}

.header-content {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  gap: 20px;
}

.main-aside {
  background-color: var(--bg-color-light);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.logo-area {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  width: 40px;
  height: 40px;
}

.system-status {
  margin-top: auto;
  padding: 20px;
}

.main-content {
  padding: 10px;
  background-color: var(--bg-color);
  height: calc(100vh - 50px);
  display: flex;
  flex-direction: column;
}
</style> 