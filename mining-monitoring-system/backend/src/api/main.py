from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
import cv2
import numpy as np
import sys
import os

# 添加父目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from camera.camera_simulator import CameraSimulator
from lidar.lidar_simulator import LidarSimulator
from radar.radar_simulator import RadarSimulator

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模拟器
camera_sim = CameraSimulator()
lidar_sim = LidarSimulator()
radar_sim = RadarSimulator()

@app.get("/")
async def root():
    return {"message": "Mining Monitoring System API"}

@app.get("/camera/frames")
async def get_camera_frames():
    try:
        frames = camera_sim.get_all_camera_frames()
        encoded_frames = []
        
        for frame in frames:
            # 确保图像是BGR格式
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
            # 压缩图像质量以减少数据大小
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            encoded_frames.append(jpg_as_text)
        
        return {"frames": encoded_frames, "status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/lidar/data")
async def get_lidar_data():
    try:
        point_clouds = lidar_sim.get_all_lidar_data()
        # 将numpy数组转换为列表以便JSON序列化
        processed_clouds = []
        for pc in point_clouds:
            processed_pc = {
                'points': pc['points'].tolist(),
                'timestamp': pc['timestamp'],
                'lidar_id': pc['lidar_id'],
                'lidar_position': pc['lidar_position'],
                'lidar_name': pc['lidar_name']
            }
            processed_clouds.append(processed_pc)
        return {"point_clouds": processed_clouds, "status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/radar/data")
async def get_radar_data():
    try:
        radar_data = radar_sim.get_all_radar_data()
        return {"radar_data": radar_data, "status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 