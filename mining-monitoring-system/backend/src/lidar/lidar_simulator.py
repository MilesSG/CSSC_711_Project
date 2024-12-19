import numpy as np
import time

class LidarSimulator:
    def __init__(self, num_lidars=5):
        self.num_lidars = num_lidars
        self.max_range = 30.0  # 30m radius
        self.angle_resolution = 0.5  # degrees
        self.num_points = int(360 / self.angle_resolution)
        self.lidar_positions = [
            (0, 0, 2, "前部"),     # 前部激光雷达
            (2, 2, 2, "右前"),     # 右前激光雷达
            (2, -2, 2, "左前"),    # 左前激光雷达
            (-2, 2, 2, "右后"),    # 右后激光雷达
            (-2, -2, 2, "左后"),   # 左后激光雷达
        ]
        
    def generate_test_point_cloud(self, lidar_id):
        """Generate a test point cloud with some obstacles"""
        # 生成基础点云
        angles = np.linspace(0, 2*np.pi, self.num_points)
        distances = np.random.uniform(0.5, self.max_range, self.num_points)
        
        # 添加地面点云
        ground_points = self._generate_ground_points()
        
        # 添加障碍物
        obstacles = [
            # 矿车
            {'type': 'truck', 'position': (15, 0, 0), 'size': (5, 3, 2.5)},
            # 人
            {'type': 'person', 'position': (8, 5, 0), 'size': (0.5, 0.5, 1.7)},
            {'type': 'person', 'position': (12, -4, 0), 'size': (0.5, 0.5, 1.7)},
            # 大石块
            {'type': 'rock', 'position': (10, 8, 0), 'size': (2, 2, 1.5)},
            {'type': 'rock', 'position': (18, -6, 0), 'size': (1.5, 1.5, 1)},
        ]
        
        obstacle_points = []
        for obstacle in obstacles:
            points = self._generate_obstacle_points(obstacle)
            obstacle_points.extend(points)
        
        # 合并所有点云
        all_points = np.vstack([ground_points, obstacle_points])
        
        # 添加噪声
        noise = np.random.normal(0, 0.02, all_points.shape)
        all_points += noise
        
        # 从激光雷达位置转换坐标
        x, y, z, name = self.lidar_positions[lidar_id]
        transformed_points = all_points + np.array([x, y, z])
        
        return {
            'points': transformed_points,
            'timestamp': time.time(),
            'lidar_id': lidar_id,
            'lidar_position': (x, y, z),
            'lidar_name': name,
            'obstacles': obstacles
        }
    
    def _generate_ground_points(self):
        """生成地面点云"""
        x = np.linspace(-self.max_range, self.max_range, 100)
        y = np.linspace(-self.max_range, self.max_range, 100)
        xx, yy = np.meshgrid(x, y)
        zz = np.zeros_like(xx) + np.random.normal(0, 0.05, xx.shape)  # 添加一些起伏
        
        points = np.stack([xx.flatten(), yy.flatten(), zz.flatten()], axis=1)
        return points
    
    def _generate_obstacle_points(self, obstacle):
        """生成障碍物点云"""
        obstacle_type = obstacle['type']
        position = np.array(obstacle['position'])
        size = np.array(obstacle['size'])
        
        if obstacle_type == 'truck':
            return self._generate_truck_points(position, size)
        elif obstacle_type == 'person':
            return self._generate_person_points(position, size)
        else:  # rock
            return self._generate_rock_points(position, size)
    
    def _generate_truck_points(self, position, size):
        """生成矿车点云"""
        num_points = 1000
        points = []
        
        # 车身
        x = np.random.uniform(-size[0]/2, size[0]/2, num_points) + position[0]
        y = np.random.uniform(-size[1]/2, size[1]/2, num_points) + position[1]
        z = np.random.uniform(0, size[2], num_points) + position[2]
        
        points = np.stack([x, y, z], axis=1)
        return points
    
    def _generate_person_points(self, position, size):
        """生成人的点云"""
        num_points = 200
        points = []
        
        # 身体
        x = np.random.uniform(-size[0]/2, size[0]/2, num_points) + position[0]
        y = np.random.uniform(-size[1]/2, size[1]/2, num_points) + position[1]
        z = np.random.uniform(0, size[2], num_points) + position[2]
        
        points = np.stack([x, y, z], axis=1)
        return points
    
    def _generate_rock_points(self, position, size):
        """生成石块点云"""
        num_points = 300
        points = []
        
        # 不规则形状
        theta = np.random.uniform(0, 2*np.pi, num_points)
        phi = np.random.uniform(0, np.pi, num_points)
        r = np.random.uniform(0, 1, num_points)
        
        x = r * np.sin(phi) * np.cos(theta) * size[0]/2 + position[0]
        y = r * np.sin(phi) * np.sin(theta) * size[1]/2 + position[1]
        z = r * np.cos(phi) * size[2]/2 + position[2]
        
        points = np.stack([x, y, z], axis=1)
        return points
    
    def get_all_lidar_data(self):
        """Get point clouds from all lidars"""
        point_clouds = []
        for i in range(self.num_lidars):
            point_cloud = self.generate_test_point_cloud(i)
            point_clouds.append(point_cloud)
        return point_clouds