import numpy as np
import time
import cv2

class CameraSimulator:
    def __init__(self, num_cameras=8):
        self.num_cameras = num_cameras
        self.frame_size = (1920, 1080)  # 1080P resolution
        self.camera_positions = [
            (0, 0, 0, "前视"),      # 前
            (45, 0, 0, "右前"),     # 右前
            (90, 0, 0, "右侧"),     # 右
            (135, 0, 0, "右后"),    # 右后
            (180, 0, 0, "后视"),    # 后
            (-135, 0, 0, "左后"),   # 左后
            (-90, 0, 0, "左侧"),    # 左
            (-45, 0, 0, "左前"),    # 左前
        ]
        
    def generate_test_image(self, camera_id):
        """Generate a test image with some visual elements"""
        image = np.zeros((self.frame_size[1], self.frame_size[0], 3), dtype=np.uint8)
        
        # 添加网格背景
        cell_size = 50
        for y in range(0, self.frame_size[1], cell_size):
            cv2.line(image, (0, y), (self.frame_size[0], y), (30, 30, 30), 1)
        for x in range(0, self.frame_size[0], cell_size):
            cv2.line(image, (x, 0), (x, self.frame_size[1]), (30, 30, 30), 1)
        
        # 添加地平线
        horizon_y = self.frame_size[1] // 3
        cv2.line(image, (0, horizon_y), (self.frame_size[0], horizon_y), (50, 50, 50), 2)
        
        # 添加相机信息
        yaw, pitch, roll, direction = self.camera_positions[camera_id]
        cv2.putText(image, 
                   f"Camera {camera_id + 1} - {direction}", 
                   (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (255, 255, 255), 
                   2)
        
        # 添加时间戳和帧率
        timestamp = time.time()
        cv2.putText(image, 
                   f"Time: {timestamp:.3f} | FPS: 30", 
                   (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (255, 255, 255), 
                   2)
        
        # 添加距离标记
        for distance in range(5, 31, 5):
            y = int(self.frame_size[1] * (1 - distance/30))
            cv2.line(image, (0, y), (self.frame_size[0], y), (0, 255, 0), 1)
            cv2.putText(image, 
                       f"{distance}m", 
                       (10, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, 
                       (0, 255, 0), 
                       1)
        
        # 添加视场角指示器
        self._add_fov_indicator(image)
        
        # 模拟一些障碍物
        self._add_obstacles(image, camera_id)
        
        return image
    
    def _add_fov_indicator(self, image):
        """添加视场角指示器"""
        center_x = self.frame_size[0] // 2
        center_y = self.frame_size[1]
        fov = 90  # 度
        radius = 100
        
        # 绘制扇形
        start_angle = -fov // 2
        end_angle = fov // 2
        for angle in range(start_angle, end_angle + 1, 1):
            x = int(center_x + radius * np.sin(np.radians(angle)))
            y = int(center_y - radius * np.cos(np.radians(angle)))
            cv2.line(image, (center_x, center_y), (x, y), (0, 255, 0), 1)
    
    def _add_obstacles(self, image, camera_id):
        """添加障碍物"""
        # 添加矿车
        self._add_mining_truck(image, (960, 700))
        
        # 添加人
        self._add_person(image, (500, 800))
        self._add_person(image, (1400, 750))
        
        # 添加大石块
        self._add_rock(image, (700, 600))
        self._add_rock(image, (1200, 650))
        
        # 添加障碍物标记框和距离信息
        self._add_obstacle_info(image)
    
    def _add_mining_truck(self, image, position):
        """添加矿车"""
        x, y = position
        # 车身
        cv2.rectangle(image, (x-100, y-50), (x+100, y+30), (200, 200, 0), -1)
        # 车轮
        cv2.circle(image, (x-70, y+30), 20, (100, 100, 100), -1)
        cv2.circle(image, (x+70, y+30), 20, (100, 100, 100), -1)
        # 驾驶室
        cv2.rectangle(image, (x-30, y-80), (x+30, y-50), (150, 150, 0), -1)
        
        # 添加标记框
        cv2.rectangle(image, (x-110, y-90), (x+110, y+40), (0, 255, 0), 2)
        cv2.putText(image, "Mining Truck - 15.2m", (x-100, y-100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def _add_person(self, image, position):
        """添加人形"""
        x, y = position
        # 头
        cv2.circle(image, (x, y-40), 15, (0, 0, 255), -1)
        # 身体
        cv2.line(image, (x, y-25), (x, y+10), (0, 0, 255), 3)
        # 腿
        cv2.line(image, (x, y-10), (x-20, y+40), (0, 0, 255), 3)
        cv2.line(image, (x, y-10), (x+20, y+40), (0, 0, 255), 3)
        # 手
        cv2.line(image, (x, y-20), (x-20, y-20), (0, 0, 255), 3)
        cv2.line(image, (x, y-20), (x+20, y-20), (0, 0, 255), 3)
        
        # 添加标记框
        cv2.rectangle(image, (x-30, y-50), (x+30, y+50), (0, 255, 0), 2)
        cv2.putText(image, "Person - 8.5m", (x-40, y-60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def _add_rock(self, image, position):
        """添加石块"""
        x, y = position
        points = np.array([
            [x-40, y+30],
            [x-30, y-30],
            [x+40, y-20],
            [x+30, y+40]
        ], np.int32)
        cv2.fillPoly(image, [points], (128, 128, 128))
        
        # 添加标记框
        cv2.rectangle(image, (x-50, y-40), (x+50, y+50), (0, 255, 0), 2)
        cv2.putText(image, "Rock - 12.3m", (x-40, y-50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def _add_obstacle_info(self, image):
        """添加障碍物信息面板"""
        panel_width = 300
        panel_height = 120
        x = 20
        y = self.frame_size[1] - panel_height - 20
        
        # 半透明背景
        overlay = image.copy()
        cv2.rectangle(overlay, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
        
        # 信息文本
        cv2.putText(image, "Obstacles Detected:", (x + 10, y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, "- Mining Trucks: 1", (x + 20, y + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 1)
        cv2.putText(image, "- Personnel: 2", (x + 20, y + 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        cv2.putText(image, "- Large Rocks: 2", (x + 20, y + 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 1)
    
    def get_all_camera_frames(self):
        """Get frames from all cameras"""
        frames = []
        for i in range(self.num_cameras):
            frame = self.generate_test_image(i)
            frames.append(frame)
        return frames