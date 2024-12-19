# 矿山监控系统

本系统实现了矿山电铲的360度环视、主视野拼接、激光雷达障碍物检测、毫米波雷达数据处理等功能。

## 系统要求

- Node.js >= 16.0.0
- Python >= 3.8
- npm 或 yarn

## 项目结构

```
mining-monitoring-system/
├── backend/             # Python后端
│   ├── src/
│   │   ├── camera/     # 相机模拟器
│   │   ├── lidar/      # 激光雷达模拟器
│   │   ├── radar/      # 毫米波雷达模拟器
│   │   ├── fusion/     # 数据融合
│   │   └── api/        # FastAPI接口
│   └── requirements.txt # Python依赖
└── frontend/           # Vue.js前端
    ├── src/
    │   ├── views/      # 页面组件
    │   ├── components/ # 通用组件
    │   └── router/     # 路由配置
    └── package.json    # Node.js依赖
```

## 安装步骤

1. 安装前端依赖：
```bash
cd mining-monitoring-system
npm install
```

2. 安装后端依赖：
```bash
cd backend
pip install -r requirements.txt
```

## 运行项目

1. 启动后端服务：
```bash
cd backend/src/api
python main.py
```

2. 启动前端开发服务器：
```bash
cd ../..  # 回到项目根目录
npm run dev
```

3. 访问系统：
打开浏览器访问 http://localhost:5173

## 功能说明

1. 360环视拼接
   - 8路GMSL2相机实时画面显示
   - IPM图范围：以电铲为中心，半径30m
   - 时延控制在60ms内

2. 主视野拼接
   - 电铲正面180度水平视野
   - 150度垂直视野范围
   - 时延控制在60ms内

3. 激光雷达数据处理
   - 5路激光雷达数据采集
   - 30m范围内障碍物识别
   - 支持识别人、车、大石块(>=50cm)
   - 铲斗土岩面距离识别
   - 防碰撞预警功能

4. 毫米波雷达数据处理
   - 5路雷达数据采集
   - 运动障碍物测距
   - 时延控制在60ms内

5. 数据融合
   - 图像与激光点云融合
   - 毫米波雷达数据融合
   - BEV图实时显示

## 注意事项

1. 当前版本使用模拟数据进行演示
2. 实际部署时需要替换相应的传感器驱动和数据采集模块
3. 性能优化建议：
   - 使用GPU加速图像处理
   - 优化数据传输协议
   - 使用共享内存减少数据拷贝
   - 实现多线程并行处理 