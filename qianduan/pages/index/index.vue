<template>
  <view class="page-container">
    <!-- 背景图片（整体背景） -->
    <image class="background-image" :src="bgImage" mode="aspectFill"></image>

    <view class="content-wrapper">
      <scroll-view scroll-y class="main-scroll" :style="{ height: scrollHeight + 'px' }">
        
        <!-- Hero 区域（使用 first.jpg 作为背景） -->
        <view class="hero-section" :style="{ backgroundImage: 'url(' + heroBgImage + ')' }">
          <view class="hero-overlay" style="background: rgba(80, 120, 60, 0.35);"></view>
          <view class="hero-content">
            <view class="welcome-title">{{ greetingText }}</view>
            <view class="welcome-sub">病虫害识别助手 · 守护每一寸农田</view>
            
            <!-- 天气和定位 + 宏观预警入口（两个并列卡片） -->
            <view class="insight-row">
              <!-- 天气卡片 -->
              <view class="insight-card weather-card" @click="showWeatherDetail">
                <view class="weather-icon-large">{{ weatherIcon }}</view>
                <view class="weather-temp-large">{{ weatherTemp }}°C</view>
                <view class="weather-desc-large">{{ weatherDesc }}</view>
                <view class="weather-location-large">📍 {{ currentLocation }}</view>
              </view>
              
              <!-- 宏观预警卡片（简化版） -->
              <view class="insight-card warning-card-simple" @click="handleMacroWarning">
                <view class="warning-icon-new">⚠️</view>
                <view class="warning-title-new">宏观预警</view>
                <view class="warning-spacer"></view>
                <view class="warning-desc-new">点击查看区域病虫害动态 →</view>
              </view>
            </view>
          </view>
        </view>

        <!-- 核心功能区：拍照识别按钮（带动画） -->
        <view class="camera-section">
          <view class="camera-btn-wrapper" @click="openCamera">
            <view class="giant-camera-btn">
              <view class="camera-glow"></view>
              <view class="camera-pulse"></view>
              <view class="camera-inner">
                <image class="camera-icon-img" src="/static/xiangji.png" mode="aspectFit"></image>
                <text class="camera-text">拍照识别病害</text>
                <text class="camera-sub">AI智能诊断 · 秒级响应</text>
              </view>
            </view>
          </view>
        </view>
		
        <!-- 快速提示/示例 -->
        <view class="quick-tip">
          <text>🌾 常见病害：稻瘟病 · 小麦锈病 · 玉米大斑病 ｜ 点击相机快速识别</text>
        </view>

        <!-- 最近识别记录预览 -->
        <view class="recent-section">
          <view class="section-header">
            <text class="section-title">最近识别记录</text>
            <text class="section-more" @click="gotoHistory">查看全部 →</text>
          </view>
          <view class="record-list" v-if="recentRecords.length > 0">
            <view class="record-item" v-for="(item, idx) in recentRecords" :key="idx" @click="viewRecordDetail(item)">
              <image class="record-img" :src="item.image_url || item.thumbnail" mode="aspectFill"></image>
              <view class="record-info">
                <text class="record-name">{{ item.disease_name || item.name }}</text>
                <text class="record-date">{{ item.created_at || item.date }}</text>
              </view>
              <view class="record-tag" :class="getSeverityClass(item.confidence)">
                {{ getSeverityText(item.confidence) }}
              </view>
            </view>
          </view>
          <view class="empty-record" v-else @click="gotoHistory">
            <text>暂无识别记录，点击相机开始识别 🌱</text>
          </view>
        </view>
      </scroll-view>

      <!-- 悬浮助手（带动画） -->
      <view class="floating-robot" @click="openAssistant">
        <image class="robot-image" src="/subpages/static/ai.jpg" mode="aspectFill"></image>
        <view class="breath-ring"></view>
        <view class="float-ring ring-1"></view>
        <view class="float-ring ring-2"></view>
      </view>
    </view>

    <!-- 天气详情弹窗 -->
    <view class="weather-modal" v-if="showWeatherModal" @click="showWeatherModal = false">
      <view class="weather-modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">天气详情</text>
          <text class="modal-close" @click="showWeatherModal = false">✕</text>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="weather-main">
            <text class="weather-main-icon">{{ weatherIcon }}</text>
            <view class="weather-main-info">
              <text class="weather-main-temp">{{ weatherTemp }}°C</text>
              <text class="weather-main-desc">{{ weatherDesc }}</text>
            </view>
          </view>
          
          <view class="weather-detail-list">
            <view class="detail-item">
              <text class="detail-label">📍 位置</text>
              <text class="detail-value">{{ currentLocation }}</text>
            </view>
            <view class="detail-item">
              <text class="detail-label">💧 湿度</text>
              <text class="detail-value">{{ weatherHumidity }}%</text>
            </view>
            <view class="detail-item">
              <text class="detail-label">🌧️ 降雨量</text>
              <text class="detail-value">{{ weatherRainfall }}mm</text>
            </view>
            <view class="detail-item">
              <text class="detail-label">🌬️ 风速</text>
              <text class="detail-value">{{ weatherWindSpeed }}km/h</text>
            </view>
            <view class="detail-item">
              <text class="detail-label">🔆 紫外线</text>
              <text class="detail-value">{{ weatherUV }}级</text>
            </view>
          </view>
          
          <view class="weather-tip">
            <text class="tip-icon">💡</text>
            <text class="tip-text">{{ weatherTip }}</text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="refresh-btn" @click="refreshWeather">刷新天气</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      // 整体背景图片（全局背景）
      bgImage: 'https://images.pexels.com/photos/162240/barn-rural-nature-grange-162240.jpeg?auto=compress&cs=tinysrgb&w=800',
      // Hero区域背景图片（first.jpg）
      heroBgImage: '/subpages/static/first.jpg',
      greetingText: '早安，农场主',
      scrollHeight: 0,
      
      // 天气数据
      weatherIcon: '☀️',
      weatherTemp: 22,
      weatherDesc: '晴',
      currentLocation: '南京市',
      weatherHumidity: 65,
      weatherRainfall: 0,
      weatherWindSpeed: 8,
      weatherUV: 3,
      
      // 弹窗控制
      showWeatherModal: false,
      
      // 最近识别记录（从后端获取）
      recentRecords: [],
      
      // 天气建议
      weatherTip: '天气适宜，可进行田间作业',

      // 天气原始数据
      weatherRawData: null
    }
  },
  
  onLoad() {
    this.setGreeting()
    this.calcScrollHeight()
    this.getLocationAndWeather()
    this.loadRecentRecords()
    uni.$on('refreshRecords', () => {
      this.loadRecentRecords()
    })
  },
  
  onUnload() {
    uni.$off('refreshRecords')
  },
  
  onShow() {
    this.checkLoginStatus()
    this.checkSyncData()
    this.loadRecentRecords()
  },
  
  methods: {
    checkLoginStatus() {
      const userInfo = uni.getStorageSync('userInfo')
      const isLogin = uni.getStorageSync('is_login')
      
      if (!isLogin || !userInfo) {
        setTimeout(() => {
          uni.navigateTo({ url: '/subpages/login/login' })
        }, 100)
        return
      }
    },
    
    // ========== 天气相关（调用后端API） ==========
    getLocationAndWeather() {
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.fetchWeatherFromAPI(res.latitude, res.longitude)
        },
        fail: () => {
          this.fetchWeatherFromAPI(30.5, 114.3)
        }
      })
    },
    
    async fetchWeatherFromAPI(lat, lon) {
      try {
        const result = await request.request({
          url: '/api/weather',
          data: { lat: lat, lon: lon },
          showLoading: false
        })
        
        this.weatherRawData = result
        this.currentLocation = result.city || '未知'
        this.weatherDesc = result.weather || '晴'
        this.weatherTemp = parseInt(result.temperature) || 22
        this.weatherHumidity = parseInt(result.humidity) || 65
        
        this.weatherIcon = this.getWeatherIcon(result.weather)
        
      } catch (err) {
        console.error('获取天气失败', err)
        this.useDefaultWeather()
      }
    },
    
    getWeatherIcon(weather) {
      const iconMap = {
        '晴': '☀️',
        '多云': '🌤️',
        '阴': '☁️',
        '小雨': '🌧️',
        '中雨': '🌧️',
        '大雨': '🌧️',
        '雷阵雨': '⛈️',
        '雪': '❄️'
      }
      return iconMap[weather] || '🌤️'
    },
    
    useDefaultWeather() {
      this.weatherIcon = '🌤️'
      this.weatherTemp = 22
      this.weatherDesc = '晴'
      this.currentLocation = '南京市'
      this.weatherHumidity = 65
    },
    
    refreshWeather() {
      uni.showToast({ title: '正在刷新...', icon: 'none' })
      this.getLocationAndWeather()
      setTimeout(() => {
        uni.showToast({ title: '已更新', icon: 'success' })
      }, 1000)
    },
    
    showWeatherDetail() {
      this.showWeatherModal = true
    },
    
    // ========== 最近识别记录（调用后端API） ==========
    async loadRecentRecords() {
      try {
        const userId = request.getUserId()
        
        const result = await request.request({
          url: '/api/history/list',
          data: { 
            user_id: userId,
            page: 1, 
            page_size: 3 
          },
          showLoading: false
        })
        
        const items = result.items || []
        this.recentRecords = items.map(item => ({
          ...item,
          image_url: request.getImageUrl(item.image_url),
          annotated_image_url: request.getImageUrl(item.annotated_image_url),
          thumbnail: request.getImageUrl(item.image_url)
        }))
        
      } catch (err) {
        console.error('加载最近记录失败', err)
        this.recentRecords = []
      }
    },
    
    getSeverityClass(confidence) {
      if (!confidence) return 'mild'
      if (confidence > 0.7) return 'severe'
      if (confidence > 0.4) return 'medium'
      return 'mild'
    },
    
    getSeverityText(confidence) {
      if (!confidence) return '待诊断'
      if (confidence > 0.7) return '严重'
      if (confidence > 0.4) return '中等'
      return '轻度'
    },
    
    setGreeting() {
      const hour = new Date().getHours()
      if (hour < 6) this.greetingText = '凌晨好，农场主'
      else if (hour < 12) this.greetingText = '早安，农场主'
      else if (hour < 18) this.greetingText = '下午好，农场主'
      else this.greetingText = '晚上好，农场主'
    },
    
    calcScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      this.scrollHeight = systemInfo.windowHeight - 50
    },
    
    loadSyncData() {
      const syncList = uni.getStorageSync('sync_diseases') || []
      if (syncList.length > 0) {
        const syncRecords = syncList.slice(0, 3).map(item => ({
          id: item.id,
          name: item.description.substring(0, 20) + (item.description.length > 20 ? '...' : ''),
          date: item.time.split(' ')[0],
          severity: '待诊断',
          thumbnail: 'https://picsum.photos/id/20/100/100',
          isSync: true,
          originalDesc: item.description
        }))
        this.recentRecords = [...syncRecords, ...this.recentRecords].slice(0, 5)
      }
    },
    
    checkSyncData() {
      const syncList = uni.getStorageSync('sync_diseases') || []
      if (syncList.length > 0) {
        const lastSync = syncList[0]
        const lastCheckTime = uni.getStorageSync('last_sync_check') || 0
        if (lastSync.id > lastCheckTime) {
          uni.showToast({
            title: `📋 来自农友圈：${lastSync.description.substring(0, 15)}...`,
            icon: 'none',
            duration: 2500
          })
          uni.setStorageSync('last_sync_check', lastSync.id)
          this.loadSyncData()
        }
      }
    },
    
    // ========== 拍照识别（调用后端API） ==========
    async openCamera() {
      const isLogin = uni.getStorageSync('is_login')
      if (!isLogin) {
        uni.showModal({
          title: '提示',
          content: '请先登录后再使用拍照识别功能',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) uni.navigateTo({ url: '/subpages/login/login' })
          }
        })
        return
      }
      
      const cropResult = await this.showCropPicker()
      if (!cropResult) return
      
      uni.chooseImage({
        count: 1,
        sourceType: ['camera'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          uni.showLoading({ title: '识别中...', mask: true })
          
          try {
            const location = await this.getCurrentLocation()
            const userId = request.getUserId()
            
            const result = await request.uploadFile({
              url: '/api/upload',
              filePath: tempFilePath,
              formData: {
                user_id: userId,
                crop_type: cropResult,
                lat: location.latitude,
                lon: location.longitude
              }
            })
            
            uni.hideLoading()
            
            uni.navigateTo({
              url: `/subpages/result/result?id=${result.record_id}`
            })
            uni.$emit('refreshRecords')
            this.loadRecentRecords()
            
          } catch (err) {
            uni.hideLoading()
            console.error('识别失败', err)
            uni.showToast({ title: '识别失败，请重试', icon: 'error' })
          }
        },
        fail: () => {
          uni.showToast({ title: '拍照失败', icon: 'none' })
        }
      })
    },
    
    showCropPicker() {
      return new Promise((resolve) => {
        uni.showActionSheet({
          itemList: ['水稻', '玉米', '番茄', '草莓'],
          success: (res) => {
            const cropMap = { 0: 'rice', 1: 'corn', 2: 'tomato', 3: 'strawberry' }
            resolve(cropMap[res.tapIndex])
          },
          fail: () => {
            resolve(null)
          }
        })
      })
    },
    
    getCurrentLocation() {
      return new Promise((resolve) => {
        uni.getLocation({
          type: 'gcj02',
          success: (res) => {
            resolve({ latitude: res.latitude, longitude: res.longitude })
          },
          fail: () => {
            resolve({ latitude: 30.5, longitude: 114.3 })
          }
        })
      })
    },
    
    handleMacroWarning() {
      uni.navigateTo({ url: '/subpages/warning/warning' })
    },
    
    viewRecordDetail(item) {
      if (item.isSync && item.originalDesc) {
        uni.showModal({
          title: '同步病情',
          content: item.originalDesc,
          confirmText: '开始诊断',
          success: (res) => {
            if (res.confirm) this.openCamera()
          }
        })
      } else if (item.id) {
        uni.navigateTo({ url: `/subpages/result/result?id=${item.id}` })
      }
    },
    
    gotoHistory() {
      uni.switchTab({ url: '/pages/history/history' })
    },
    
    openAssistant() {
      uni.navigateTo({ url: '/subpages/ai/ai' })
    }
  }
}
</script>

<style lang="scss" scoped>
.page-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.background-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.content-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.88);
  overflow-y: auto;
}

.main-scroll {
  width: 100%;
  height: 100%;
}

/* Hero 区域 */
.hero-section {
  position: relative;
  background-size: cover;
  background-position: center 35%;
  border-radius: 0 0 32px 32px;
  overflow: hidden;
  margin-bottom: 20px;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(80, 120, 60, 0.35);
  backdrop-filter: brightness(0.95);
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  padding: 40px 24px 32px 24px;
  color: #e8f5e9;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.welcome-title {
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  line-height: 1.2;
  color: #e8f5e9;
}

.welcome-sub {
  font-size: 0.9rem;
  opacity: 0.92;
  margin-top: 6px;
  color: #c8e6c9;
}

/* 两个并列卡片 */
.insight-row {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.insight-card {
  background: rgba(255, 255, 245, 0.93);
  backdrop-filter: blur(8px);
  border-radius: 28px;
  padding: 12px 10px;
  flex: 1;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.15s;
  border: 1px solid rgba(255, 250, 200, 0.6);
}

.insight-card:active {
  transform: scale(0.96);
}

/* 天气卡片 */
.weather-card {
  text-align: center;
  padding: 10px;
}

.weather-icon-large {
  font-size: 36px;
  display: block;
}

.weather-temp-large {
  font-size: 24px;
  font-weight: bold;
  color: #2c5e2a;
  display: block;
  margin-top: 4px;
}

.weather-desc-large {
  font-size: 12px;
  color: #5a7048;
  display: block;
}

.weather-location-large {
  font-size: 11px;
  color: #8a9a7a;
  display: block;
  margin-top: 4px;
}

/* 宏观预警卡片（简化版） */
.warning-card-simple {
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
}

.warning-icon-new {
  font-size: 36px;
  display: block;
  margin-bottom: 4px;
}

.warning-title-new {
  font-weight: 700;
  font-size: 0.9rem;
  color: #2c5e2a;
  margin-bottom: 8px;
}

.warning-spacer {
  flex: 1;
}

.warning-desc-new {
  font-size: 10px;
  color: #5a7048;
}

/* ========== 拍照按钮（带动画） ========== */
.camera-section {
  display: flex;
  justify-content: center;
  margin: 8px 0 12px;
}

.camera-btn-wrapper {
  width: 200px;
  height: 200px;
  cursor: pointer;
}

.giant-camera-btn {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(145deg, #ffffff, #a4ffa7);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 35px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(76, 175, 80, 0.2);
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  position: relative;
  overflow: hidden;
  animation: buttonFloat 3s ease-in-out infinite;
}

@keyframes buttonFloat {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

.giant-camera-btn::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(76, 175, 80, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.5s ease;
}

.camera-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), transparent 60%);
  pointer-events: none;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.camera-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(76, 175, 80, 0.3);
  transform: translate(-50%, -50%) scale(1);
  animation: pulseRing 1.5s ease-out infinite;
  pointer-events: none;
}

@keyframes pulseRing {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0;
  }
}

.camera-inner {
  text-align: center;
  z-index: 1;
}

.camera-icon-img {
  width: 50px;
  height: 50px;
  display: block;
  margin: 0 auto 8px;
  animation: iconBounce 2s ease-in-out infinite;
}

@keyframes iconBounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.camera-text {
  font-size: 16px;
  font-weight: 700;
  color: #2c5e2a;
  display: block;
  letter-spacing: 1px;
}

.camera-sub {
  font-size: 10px;
  color: #8a9a7a;
  display: block;
  margin-top: 6px;
}

.giant-camera-btn:active {
  transform: scale(0.96);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  animation: none;
}

/* ========== AI悬浮按钮（带动画） ========== */
.floating-robot {
  position: fixed;
  bottom: 70px;
  right: 18px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
  z-index: 999;
  cursor: pointer;
  overflow: hidden;
  background: #ffffff;
  border: 2px solid #fff2cf;
  animation: robotFloat 2.5s ease-in-out infinite;
}

@keyframes robotFloat {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.robot-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.breath-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(247, 205, 92, 0.4);
  animation: breathe 2s infinite;
  z-index: -1;
}

.float-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(247, 205, 92, 0.6);
  opacity: 0;
  pointer-events: none;
}

.ring-1 {
  animation: floatRing 2s ease-out infinite;
}

.ring-2 {
  animation: floatRing 2s ease-out infinite 0.6s;
}

@keyframes floatRing {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

@keyframes breathe {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.28); opacity: 0.2; }
  100% { transform: scale(1); opacity: 0.6; }
}

.floating-robot:active {
  transform: scale(0.92);
  animation: none;
}

.quick-tip {
  text-align: center;
  font-size: 0.7rem;
  color: #6e8656;
  background: #eef5e4;
  margin: 10px 20px;
  padding: 8px 12px;
  border-radius: 30px;
}

.recent-section {
  margin: 20px 16px 30px;
  background: #ffffffd9;
  border-radius: 28px;
  padding: 16px;
  backdrop-filter: blur(2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 14px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e0ecce;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c5e2a;
}

.section-more {
  font-size: 0.7rem;
  color: #7c9a60;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  background: #fefef7;
  border-radius: 20px;
  padding: 10px;
  gap: 12px;
}

.record-img {
  width: 50px;
  height: 50px;
  border-radius: 16px;
}

.record-info {
  flex: 1;
}

.record-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #2f4d2d;
}

.record-date {
  font-size: 0.65rem;
  color: #8faa7a;
  display: block;
}

.record-tag {
  font-size: 0.65rem;
  padding: 4px 10px;
  border-radius: 20px;
  background: #f3f5e7;
  color: #5a6e4a;
}

.record-tag.severe {
  background: #ffedea;
  color: #c23d2b;
}

.record-tag.medium {
  background: #fff3e0;
  color: #e6a017;
}

.empty-record {
  text-align: center;
  padding: 32px 0;
  color: #98af82;
  font-size: 0.8rem;
}

/* 天气弹窗样式 */
.weather-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.weather-modal-content {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0e8;
  background: white;
  flex-shrink: 0;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c5e2a;
}

.modal-close {
  font-size: 28px;
  color: #999;
  padding: 8px;
}

.modal-body {
  flex: 1;
  padding: 24px 20px 32px;
  overflow-y: auto;
}

.weather-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid #ecf0e6;
  flex-wrap: wrap;
}

.weather-main-icon {
  font-size: 80px;
}

.weather-main-temp {
  font-size: 48px;
  font-weight: bold;
  color: #2c5e2a;
}

.weather-main-desc {
  font-size: 18px;
  color: #666;
  margin-top: 8px;
  text-align: center;
}

.weather-detail-list {
  margin-bottom: 32px;
}

.detail-item {
  display: flex;
  justify-content: flex-start;
  align-items: baseline;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0e8;
}

.detail-label {
  min-width: 80px;
  flex-shrink: 0;
}

.detail-value {
  margin-left: 160px;
}

.weather-tip {
  display: flex;
  gap: 14px;
  background: #eef3e9;
  padding: 20px;
  border-radius: 24px;
  margin: 24px 0 16px;
}

.tip-icon {
  font-size: 24px;
}

.tip-text {
  flex: 1;
  font-size: 15px;
  color: #2c5e2a;
  line-height: 1.5;
}

.modal-footer {
  padding: 20px 24px 32px;
  border-top: 1px solid #f0f0e8;
  background: white;
  flex-shrink: 0;
}

.refresh-btn {
  padding: 16px;
  text-align: center;
  background: #2c5e2a;
  color: white;
  border-radius: 48px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>