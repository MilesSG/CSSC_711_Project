# CSSC_711_Project

## 项目说明
这是一个采矿监控系统项目，采用前后端分离架构开发。前端使用Vue 3 + Vite技术栈，后端使用Python开发。

## 系统要求
- Node.js 16+
- Python 3.8+
- npm 或 yarn包管理器

## 项目结构
```
mining-monitoring-system/
├── frontend/                # 前端Vue项目
│   ├── src/                # 源代码
│   ├── dist/               # 构建输出目录
│   └── public/             # 静态资源
├── backend/                # 后端Python项目
│   ├── src/               # 源代码
│   └── requirements.txt    # Python依赖
└── docs/                   # 项目文档
```

## 安装和运行

### 前端部分
1. 进入前端项目目录：
```bash
cd mining-monitoring-system
```

2. 安装依赖：
```bash
npm install
# 或
yarn install
```

3. 开发环境运行：
```bash
npm run dev
# 或
yarn dev
```

4. 生产环境构建：
```bash
npm run build
# 或
yarn build
```

### 后端部分
1. 进入后端项目目录：
```bash
cd mining-monitoring-system/backend
```

2. 创建并激活Python虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行后端服务：
```bash
python src/main.py
```

## 配置说明
- 前端开发环境默认运行在 http://localhost:5173
- 生产环境配置可在 `.env.production` 文件中修改
- 后端服务配置在 `mining-monitoring.conf` 文件中

## 部署说明
项目使用Supervisor进行进程管理，配置文件为 `mining-monitoring.supervisor.conf`。

## 技术栈
### 前端
- Vue 3
- Vite
- Vue Router
- Pinia (状态管理)
- Element Plus (UI组件库)
- Three.js (3D渲染)
- ECharts (图表)

### 后端
- Python
- FastAPI/Flask (具体根据后端实现选择)

## 开发团队
[在此添加开发团队信息]

## 许可证
[在此添加许可证信息]
