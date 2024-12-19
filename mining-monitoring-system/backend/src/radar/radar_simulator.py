import numpy as np
import time

class RadarSimulator:
    def __init__(self, num_radars=5):
        self.num_radars = num_radars
        self.max_range = 30.0  # 30m radius
        self.radar_positions = [
            (0, 0, 2, "前部"),     # 前部毫米波雷达
            (2, 2, 2, "右前"),     # 右前毫米波雷达
            (2, -2, 2, "左前"),    # 左前毫米波雷达
            (-2, 2, 2, "右后"),    # 右后毫米波雷达
            (-2, -2, 2, "左后"),   # 左后毫米波雷达
        ]
        self.moving_objects = [
            {
                'id': 1,
                'type': 'truck',
                'position': np.array([15.0, 0.0]),
                'velocity': np.array([-2.0, 0.0]),  # 向左移动
                'size': 5.0,
                'confidence': 0.95
            },
            {
                'id': 2,
                'type': 'person',
                'position': np.array([8.0, 5.0]),
                'velocity': np.array([0.5, -0.5]),  # 斜向移动
                'size': 0.5,
                'confidence': 0.85
            },
            {
                'id': 3,
                'type': 'person',
                'position': np.array([12.0, -4.0]),
                'velocity': np.array([0.0, 0.8]),   # 向上移动
                'size': 0.5,
                'confidence': 0.88
            }
        ]
        
    def generate_test_radar_data(self, radar_id):
        """Generate test radar data with some moving objects"""
        # 更新移动物体的位置
        self._update_objects()
        
        # 获取雷达位置
        x, y, z, name = self.radar_positions[radar_id]
        radar_pos = np.array([x, y])
        
        # 计算每个物体相对于雷达的位置和速度
        detected_objects = []
        for obj in self.moving_objects:
            # 计算相对位置
            rel_pos = obj['position'] - radar_pos
            distance = np.linalg.norm(rel_pos)
            
            # 如果在探测范围内
            if distance <= self.max_range:
                # 添加一些噪声
                noisy_pos = rel_pos + np.random.normal(0, 0.1, 2)
                noisy_distance = np.linalg.norm(noisy_pos)
                noisy_angle = np.arctan2(noisy_pos[1], noisy_pos[0])
                
                # 计算径向速度（沿雷达视线方向的速度分量）
                radial_velocity = np.dot(obj['velocity'], rel_pos/distance)
                noisy_velocity = radial_velocity + np.random.normal(0, 0.1)
                
                # 根据距离调整置信度
                distance_factor = 1 - (distance / self.max_range) * 0.3
                adjusted_confidence = obj['confidence'] * distance_factor
                
                detected_objects.append({
                    'id': obj['id'],
                    'type': obj['type'],
                    'distance': float(noisy_distance),
                    'angle': float(noisy_angle),
                    'velocity': float(noisy_velocity),
                    'size': float(obj['size']),
                    'confidence': float(adjusted_confidence)
                })
        
        return {
            'objects': detected_objects,
            'timestamp': time.time(),
            'radar_id': radar_id,
            'radar_position': (x, y, z),
            'radar_name': name
        }
    
    def _update_objects(self):
        """更新移动物体的位置"""
        dt = 0.1  # 时间步长
        
        for obj in self.moving_objects:
            # 更新位置
            obj['position'] += obj['velocity'] * dt
            
            # 检查边界并反弹
            for i in range(2):
                if abs(obj['position'][i]) > self.max_range:
                    obj['position'][i] = np.sign(obj['position'][i]) * self.max_range
                    obj['velocity'][i] *= -1
            
            # 随机改变一下速度（添加一些随机性）
            if np.random.random() < 0.1:  # 10%的概率改变速度
                obj['velocity'] += np.random.normal(0, 0.2, 2)
                # 限制最大速度
                speed = np.linalg.norm(obj['velocity'])
                if speed > 3.0:  # 最大速度3m/s
                    obj['velocity'] *= 3.0 / speed
    
    def get_all_radar_data(self):
        """Get data from all radar sensors"""
        radar_data = []
        for i in range(self.num_radars):
            data = self.generate_test_radar_data(i)
            radar_data.append(data)
        return radar_data