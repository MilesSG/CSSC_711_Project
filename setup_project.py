import os

def create_directories():
    base_dir = "mining-monitoring-system"
    
    # Backend directories
    backend_dirs = [
        "backend/src/camera",
        "backend/src/lidar",
        "backend/src/radar",
        "backend/src/fusion",
        "backend/src/utils",
        "backend/src/api",
    ]
    
    for dir_path in backend_dirs:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        # Create an empty __init__.py file in each directory
        with open(os.path.join(full_path, "__init__.py"), "w") as f:
            pass

if __name__ == "__main__":
    create_directories() 