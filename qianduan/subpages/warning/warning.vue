<template>
  <view class="warning-page">
    <!-- 头部 -->
    <view class="warning-header">
      <view class="header-left" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-center">
        <text class="header-title">病虫害预警</text>
      </view>
      <view class="header-right">
        <text class="refresh-icon" @click="refreshData">🔄</text>
      </view>
    </view>

    <!-- 预警类型切换 -->
    <view class="warning-type-switch">
      <view 
        class="type-btn" 
        :class="{ active: warningType === 'weather' }"
        @click="switchType('weather')"
      >
        <text class="type-icon">🌤️</text>
        <text class="type-text">天气预警</text>
      </view>
      <view 
        class="type-btn" 
        :class="{ active: warningType === 'region' }"
        @click="switchType('region')"
      >
        <text class="type-icon">🗺️</text>
        <text class="type-text">区域预警</text>
      </view>
    </view>

    <!-- 天气预警视图 -->
    <view v-if="warningType === 'weather'" class="weather-view">
      <!-- 当前天气 -->
      <view class="weather-card">
        <view class="weather-icon">{{ weather.icon }}</view>
        <view class="weather-info">
          <text class="weather-temp">{{ weather.temp }}°C</text>
          <text class="weather-desc">{{ weather.desc }}</text>
          <text class="weather-location">📍 {{ weather.location }}</text>
        </view>
        <view class="weather-detail">
          <text>💧 {{ weather.humidity }}%</text>
          <text>🌬️ {{ weather.wind }}</text>
        </view>
      </view>

      <!-- 风险等级 -->
      <view class="risk-card" :class="getRiskClass(riskLevel)">
        <text class="risk-level">{{ riskLevel }}</text>
        <text class="risk-desc">{{ riskDesc }}</text>
      </view>

      <!-- 未来天气预报曲线图 -->
      <view class="forecast-section" v-if="forecast.length > 0">
        <view class="forecast-title">📈 未来天气趋势</view>
        <view class="forecast-chart">
          <!-- Y轴温度标尺 -->
          <view class="y-axis">
            <text class="y-label">{{ maxTemp }}°</text>
            <text class="y-label">{{ midTemp }}°</text>
            <text class="y-label">{{ minTemp }}°</text>
          </view>
          <!-- 曲线图区域 -->
          <view class="chart-area">
            <!-- 网格线 -->
            <view class="grid-line"></view>
            <view class="grid-line"></view>
            <view class="grid-line"></view>
            <!-- 温度曲线 -->
            <view class="curve-container">
              <!-- 柱状温度条 -->
              <view
                v-for="(day, idx) in forecast"
                :key="idx"
                class="bar-column"
              >
                <view class="temp-bar-wrapper">
                  <!-- 夜间温度(低温) 到 白天温度(高温) -->
                  <view
                    class="temp-bar"
                    :style="getBarStyle(day)"
                  ></view>
                </view>
                <text class="day-temp">{{ day.daytemp }}°</text>
                <text class="night-temp">{{ day.nighttemp }}°</text>
              </view>
            </view>
            <!-- 天气图标行 -->
            <view class="icon-row">
              <view
                v-for="(day, idx) in forecast"
                :key="'i' + idx"
                class="icon-col"
              >
                <text class="weather-emoji">{{ getWeatherEmoji(day.dayweather) }}</text>
              </view>
            </view>
            <!-- 日期标签行 -->
            <view class="date-row">
              <view
                v-for="(day, idx) in forecast"
                :key="'d' + idx"
                class="date-col"
              >
                <text class="date-text">{{ formatDate(day.date) }}</text>
              </view>
            </view>
          </view>
        </view>
        <!-- 图例 -->
        <view class="forecast-legend">
          <view class="legend-item">
            <view class="legend-bar"></view>
            <text>温度范围（夜~昼）</text>
          </view>
        </view>
      </view>

      <!-- 病害预测列表 -->
      <view class="predict-list">
        <view class="list-title">⚠️ 易发病害预测</view>
        <view v-for="(item, idx) in predictions" :key="idx" class="predict-item">
          <view class="predict-header">
            <text class="disease-name">{{ item.disease }}</text>
            <view class="risk-badge" :class="getRiskClass(item.risk)">{{ item.risk }}</view>
          </view>
          <text class="predict-reason">天气条件：{{ item.condition }}</text>
          <text class="predict-advice">💊 {{ item.advice }}</text>
        </view>
        <view v-if="predictions.length === 0" class="empty-state">
          <text>当前天气条件良好，暂无病害预警</text>
        </view>
      </view>
    </view>

    <!-- 区域预警视图 -->
    <view v-else class="region-view">
      <!-- 区域选择 -->
      <scroll-view scroll-x class="region-scroll">
        <view 
          v-for="r in regions" 
          :key="r"
          class="region-tab"
          :class="{ active: currentRegion === r }"
          @click="selectRegion(r)"
        >
          {{ r }}
        </view>
      </scroll-view>

      <!-- 区域分析结果 -->
      <view v-if="regionAnalysis" class="region-analysis">
        <!-- 水稻预警 -->
        <view class="crop-section" v-if="regionAnalysis.rice && regionAnalysis.rice.length">
          <view class="crop-title">🌾 水稻</view>
          <view v-for="(item, idx) in regionAnalysis.rice" :key="idx" class="warning-item">
            <view class="warning-header">
              <text class="disease">{{ item.disease }}</text>
              <view class="risk-badge" :class="getRiskClass(item.risk)">{{ item.risk }}</view>
            </view>
            <text class="warning-reason">{{ item.reason }}</text>
            <text class="warning-advice">💊 {{ item.advice }}</text>
          </view>
        </view>

        <!-- 玉米预警 -->
        <view class="crop-section" v-if="regionAnalysis.corn && regionAnalysis.corn.length">
          <view class="crop-title">🌽 玉米</view>
          <view v-for="(item, idx) in regionAnalysis.corn" :key="idx" class="warning-item">
            <view class="warning-header">
              <text class="disease">{{ item.disease }}</text>
              <view class="risk-badge" :class="getRiskClass(item.risk)">{{ item.risk }}</view>
            </view>
            <text class="warning-reason">{{ item.reason }}</text>
            <text class="warning-advice">💊 {{ item.advice }}</text>
          </view>
        </view>

        <!-- 番茄预警 -->
        <view class="crop-section" v-if="regionAnalysis.tomato && regionAnalysis.tomato.length">
          <view class="crop-title">🍅 番茄</view>
          <view v-for="(item, idx) in regionAnalysis.tomato" :key="idx" class="warning-item">
            <view class="warning-header">
              <text class="disease">{{ item.disease }}</text>
              <view class="risk-badge" :class="getRiskClass(item.risk)">{{ item.risk }}</view>
            </view>
            <text class="warning-reason">{{ item.reason }}</text>
            <text class="warning-advice">💊 {{ item.advice }}</text>
          </view>
        </view>

        <!-- 草莓预警 -->
        <view class="crop-section" v-if="regionAnalysis.strawberry && regionAnalysis.strawberry.length">
          <view class="crop-title">🍓 草莓</view>
          <view v-for="(item, idx) in regionAnalysis.strawberry" :key="idx" class="warning-item">
            <view class="warning-header">
              <text class="disease">{{ item.disease }}</text>
              <view class="risk-badge" :class="getRiskClass(item.risk)">{{ item.risk }}</view>
            </view>
            <text class="warning-reason">{{ item.reason }}</text>
            <text class="warning-advice">💊 {{ item.advice }}</text>
          </view>
        </view>
      </view>

      <view v-else class="loading-state">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      warningType: 'weather',
      regions: ['华东', '华南', '华中', '华北', '西南', '西北', '东北'],
      currentRegion: '华东',
      
      // 天气预警数据
      weather: {
        icon: '☀️',
        temp: '--',
        desc: '加载中',
        location: '--',
        humidity: '--',
        wind: '--'
      },
      riskLevel: '低风险',
      riskDesc: '正在获取天气数据...',
      predictions: [],
      
      // 区域预警数据
      regionAnalysis: null,

      // 天气预报数据
      forecast: []
    }
  },
  
  computed: {
    maxTemp() {
      if (this.forecast.length === 0) return 40
      return Math.max(...this.forecast.map(d => parseInt(d.daytemp) || 0)) + 5
    },
    minTemp() {
      if (this.forecast.length === 0) return 0
      return Math.min(...this.forecast.map(d => parseInt(d.nighttemp) || 0)) - 5
    },
    midTemp() {
      return Math.round((this.maxTemp + this.minTemp) / 2)
    }
  },

  onLoad() {
    this.loadWeatherWarning()
    this.loadForecast()
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    switchType(type) {
      this.warningType = type
      if (type === 'weather') {
        this.loadWeatherWarning()
        this.loadForecast()
      } else {
        this.loadRegionWarning()
      }
    },
    
    selectRegion(region) {
      this.currentRegion = region
      this.loadRegionWarning()
    },
    
    async refreshData() {
      uni.showToast({ title: '正在更新...', icon: 'none' })
      if (this.warningType === 'weather') {
        await this.loadWeatherWarning()
        await this.loadForecast()
      } else {
        await this.loadRegionWarning()
      }
      uni.showToast({ title: '更新成功', icon: 'success' })
    },
    
    async loadForecast() {
      try {
        const location = await this.getLocation()
        const result = await request.request({
          url: '/api/weather/forecast',
          data: { lat: location.latitude, lon: location.longitude }
        })
        this.forecast = result.forecasts || []
      } catch (err) {
        console.error('加载天气预报失败', err)
        this.forecast = []
      }
    },

    getBarStyle(day) {
      const high = parseInt(day.daytemp) || 30
      const low = parseInt(day.nighttemp) || 20
      const range = this.maxTemp - this.minTemp
      const bottomPct = ((low - this.minTemp) / range) * 100
      const heightPct = ((high - low) / range) * 100
      return {
        bottom: bottomPct + '%',
        height: Math.max(heightPct, 8) + '%'
      }
    },

    getWeatherEmoji(weather) {
      if (!weather) return '🌤️'
      const w = weather
      if (w.includes('晴')) return '☀️'
      if (w.includes('多云')) return '⛅'
      if (w.includes('阴')) return '☁️'
      if (w.includes('雨') && (w.includes('大') || w.includes('暴'))) return '🌧️'
      if (w.includes('雨')) return '🌦️'
      if (w.includes('雪')) return '🌨️'
      if (w.includes('风')) return '💨'
      return '🌤️'
    },

    formatDate(dateStr) {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      if (parts.length === 3) {
        return parts[1] + '/' + parts[2]
      }
      return dateStr
    },

    async loadWeatherWarning() {
      try {
        // 获取位置
        const location = await this.getLocation()
        
        // 获取天气预警
        const result = await request.request({
          url: '/api/warning/weather',
          data: {
            lat: location.latitude,
            lon: location.longitude,
            crop_type: 'rice'
          }
        })
        
        // 更新天气显示
        this.weather = {
          icon: this.getWeatherIcon(result.weather?.weather),
          temp: result.weather?.temperature || '--',
          desc: result.weather?.weather || '--',
          location: result.location || '--',
          humidity: result.weather?.humidity || '--',
          wind: result.weather?.wind || '--'
        }
        
        this.riskLevel = result.risk_level || '低风险'
        this.riskDesc = this.getRiskDesc(this.riskLevel)
        this.predictions = result.predictions || []
        
      } catch (err) {
        console.error('加载天气预警失败', err)
      }
    },
    
    async loadRegionWarning() {
      try {
        const result = await request.request({
          url: '/api/warning/region',
          data: { region: this.currentRegion }
        })
        
        // 检查是否有错误
        if (result.error) {
          uni.showToast({ title: result.error, icon: 'none' })
          this.regionAnalysis = null
          return
        }
        
        this.regionAnalysis = result.analysis
        
      } catch (err) {
        console.error('加载区域预警失败', err)
        uni.showToast({ title: err.message || 'AI服务请求失败', icon: 'none' })
        this.regionAnalysis = null
      }
    },
    
    getLocation() {
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
    
    getWeatherIcon(weather) {
      const iconMap = { '晴': '☀️', '多云': '🌤️', '阴': '☁️', '小雨': '🌧️', '中雨': '🌧️', '大雨': '🌧️' }
      return iconMap[weather] || '🌤️'
    },
    
    getRiskClass(level) {
      if (level === '高危') return 'risk-high'
      if (level === '中风险') return 'risk-medium'
      return 'risk-low'
    },
    
    getRiskDesc(level) {
      if (level === '高危') return '当前天气条件极易诱发病害，请立即采取防治措施！'
      if (level === '中风险') return '天气条件有利于病害发生，建议做好预防准备。'
      return '当前天气条件较安全，保持常规监测即可。'
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式保持你原有的不变，这里只列出新增样式 */
.warning-page {
  min-height: 100vh;
  background: #f5f7f0;
  padding-bottom: 20px;
}

.warning-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  color: white;
}

.warning-type-switch {
  display: flex;
  gap: 16px;
  margin: 16px;
  background: white;
  border-radius: 50px;
  padding: 4px;
  
  .type-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px;
    border-radius: 40px;
    
    &.active {
      background: #2c5e2a;
      .type-text { color: white; }
    }
  }
}

.weather-card {
  display: flex;
  align-items: center;
  background: white;
  margin: 0 16px 16px;
  padding: 16px;
  border-radius: 20px;
}

.risk-card {
  margin: 0 16px 16px;
  padding: 16px;
  border-radius: 20px;
  text-align: center;
  
  &.risk-high { background: linear-gradient(135deg, #ff6b6b, #ee5a5a); color: white; }
  &.risk-medium { background: linear-gradient(135deg, #ffa502, #e67e22); color: white; }
  &.risk-low { background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; }
  
  .risk-level { font-size: 28px; font-weight: bold; display: block; }
  .risk-desc { font-size: 13px; margin-top: 8px; }
}

.predict-list, .region-scroll, .region-analysis {
  margin: 0 16px;
}

.predict-item, .warning-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
}

.predict-header, .warning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.disease-name, .disease {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.risk-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  
  &.risk-high { background: #ffebee; color: #c62828; }
  &.risk-medium { background: #fff3e0; color: #ef6c00; }
  &.risk-low { background: #e8f5e9; color: #2e7d32; }
}

.predict-reason, .warning-reason {
  font-size: 12px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.predict-advice, .warning-advice {
  font-size: 13px;
  color: #2c5e2a;
  display: block;
}

.crop-section {
  margin-bottom: 20px;
  
  .crop-title {
    font-size: 18px;
    font-weight: bold;
    color: #2c5e2a;
    margin-bottom: 12px;
    padding-left: 8px;
    border-left: 4px solid #2c5e2a;
  }
}

.region-scroll {
  white-space: nowrap;
  margin-bottom: 16px;
  
  .region-tab {
    display: inline-block;
    padding: 8px 20px;
    background: white;
    border-radius: 30px;
    margin-right: 10px;
    font-size: 14px;
    
    &.active {
      background: #2c5e2a;
      color: white;
    }
  }
}

.empty-state, .loading-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 天气预报曲线图 */
.forecast-section {
  margin: 0 16px 16px;
  background: white;
  border-radius: 20px;
  padding: 20px 16px 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.forecast-title {
  font-size: 16px;
  font-weight: 700;
  color: #2c5e2a;
  margin-bottom: 20px;
  padding-left: 4px;
}

.forecast-chart {
  display: flex;
  height: 260px;
}

.y-axis {
  width: 36px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0 0 8px 0;

  .y-label {
    font-size: 11px;
    color: #aaa;
    text-align: right;
  }
}

.chart-area {
  flex: 1;
  position: relative;
  margin-left: 4px;
  margin-bottom: 8px;
}

.grid-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: #f0f0e8;
}

.grid-line:nth-child(1) { top: 0; }
.grid-line:nth-child(2) { top: 50%; }
.grid-line:nth-child(3) { bottom: 0; }

.curve-container {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 55px;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 0 8px;
}

.bar-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  height: 100%;
  max-width: 50px;
}

.temp-bar-wrapper {
  position: absolute;
  left: 20%;
  right: 20%;
  top: 0;
  bottom: 0;
}

.temp-bar {
  position: absolute;
  left: 0;
  right: 0;
  border-radius: 6px 6px 0 0;
  background: linear-gradient(to top, #4a90d9, #f5a623);
  min-height: 8px;
}

.day-temp {
  position: absolute;
  top: -18px;
  font-size: 11px;
  font-weight: 600;
  color: #f5a623;
  width: 100%;
  text-align: center;
}

.night-temp {
  position: absolute;
  bottom: -18px;
  font-size: 11px;
  font-weight: 600;
  color: #4a90d9;
  width: 100%;
  text-align: center;
}

.icon-row {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 24px;
  display: flex;
  justify-content: space-around;
  padding: 0 8px;
}

.icon-col {
  flex: 1;
  text-align: center;
  max-width: 50px;

  .weather-emoji {
    font-size: 18px;
  }
}

.date-row {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  padding: 0 8px;
}

.date-col {
  flex: 1;
  text-align: center;
  max-width: 50px;

  .date-text {
    font-size: 11px;
    color: #999;
  }
}

.forecast-legend {
  display: flex;
  justify-content: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f5f5f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

.legend-bar {
  width: 24px;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #4a90d9, #f5a623);
}
</style>