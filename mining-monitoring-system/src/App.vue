<template>
  <el-container class="app-container">
    <el-header height="60px">
      <div class="header-content">
        <h1>矿山电铲智能监控系统</h1>
        <el-menu mode="horizontal" :router="true">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/surround">360环视</el-menu-item>
          <el-menu-item index="/main-view">主视野</el-menu-item>
          <el-menu-item index="/obstacle">障碍物检测</el-menu-item>
          <el-menu-item index="/bev">BEV视图</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}

.app-container {
  height: 100%;
}

.el-header {
  background-color: #001529;
  padding: 0;
  color: white;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0 20px 0 0;
  font-size: 20px;
}

.el-menu {
  background-color: transparent;
  border: none;
}

.el-menu-item {
  color: #fff !important;
}

.el-menu-item:hover, .el-menu-item.is-active {
  background-color: #1890ff !important;
}

.el-main {
  padding: 0;
  background-color: #f0f2f5;
}
</style> 