// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// API端点
export const API_ENDPOINTS = {
    CAMERA_FRAMES: `${API_BASE_URL}/camera/frames`,
    LIDAR_DATA: `${API_BASE_URL}/lidar/data`,
    RADAR_DATA: `${API_BASE_URL}/radar/data`,
};

// 获取相机帧数据
export async function getCameraFrames() {
    try {
        const response = await fetch(API_ENDPOINTS.CAMERA_FRAMES);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    } catch (error) {
        console.error('Error fetching camera frames:', error);
        throw error;
    }
}

// 获取激光雷达数据
export async function getLidarData() {
    try {
        const response = await fetch(API_ENDPOINTS.LIDAR_DATA);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    } catch (error) {
        console.error('Error fetching lidar data:', error);
        throw error;
    }
}

// 获取毫米波雷达数据
export async function getRadarData() {
    try {
        const response = await fetch(API_ENDPOINTS.RADAR_DATA);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    } catch (error) {
        console.error('Error fetching radar data:', error);
        throw error;
    }
} 