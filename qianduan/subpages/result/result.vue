<template>
  <view class="container">
    <view v-if="record" class="result-card">
      <image :src="record.annotated_image_url || record.image_url" mode="widthFix"></image>
      
      <view class="info-box">
        <text class="label">病害名称</text>
        <text class="value disease">{{ record.disease_name }}</text>
      </view>
      
      <view class="info-box">
        <text class="label">置信度</text>
        <text class="value">{{ (record.confidence * 100).toFixed(1) }}%</text>
      </view>
      
      <view class="info-box">
        <text class="label">识别时间</text>
        <text class="value">{{ record.created_at }}</text>
      </view>
      
      <!-- 防治建议区域 -->
      <view class="advice-box">
        <text class="advice-title">🌱 AI防治建议</text>
        <text v-if="!advice && !loadingAdvice" class="advice-placeholder">点击下方按钮生成防治建议</text>
        <text v-if="loadingAdvice" class="advice-loading">正在生成建议，请稍候...</text>
        <text v-if="advice" class="advice-content">{{ formatAdvice(advice) }}</text>
      </view>

      <!-- 生成建议按钮（仅在无建议且未生成时显示） -->
      <button v-if="!record.ai_advice && !advice && !loadingAdvice" @click="generateAdvice" type="primary">生成防治建议</button>
      
      <!-- 天气信息 -->
      <view v-if="record.weather_info && record.weather_info.city" class="weather-box">
        <text class="weather-title">📍 天气信息</text>
        <text>📍 {{ record.weather_info.city }}</text>
        <text>☁️ {{ record.weather_info.weather }}</text>
        <text>🌡️ {{ record.weather_info.temperature }}℃</text>
        <text>💧 湿度 {{ record.weather_info.humidity }}%</text>
      </view>

      <button @click="goHome" type="default" size="default">返回首页</button>
    </view>

    <view v-else class="loading-state">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      record: null,
      advice: '',
      loadingAdvice: false
    }
  },
  onLoad(options) {
    const id = options.id
    if (id) {
      this.loadRecord(id)
    }
  },
  methods: {
	formatAdvice(text) {
	    if (!text) return ''
	    // 1. 去掉加粗 **text** -> text
	    let formatted = text.replace(/\*\*(.*?)\*\*/g, '$1')
	    // 2. 去掉斜体或列表 *text* -> text
	    formatted = formatted.replace(/\*([^\*]+?)\*/g, '$1')
	    // 3. 把行首的 * 或 - 列表符号换成 •（圆点），也可以直接删掉
	    formatted = formatted.replace(/^(\s*)[\*\-]\s+/gm, '$1• ')
	    // 4. 去掉连续星号或减号分隔线
	    formatted = formatted.replace(/[\*\-]{3,}/g, '')
	    // 5. 处理列表项内的星号（如果有残留）
	    formatted = formatted.replace(/\*/g, '')
	    return formatted
	},
    async loadRecord(id) {
      try {
        const userId = request.getUserId()
        const result = await request.request({
          url: `/api/history/detail/${id}`,
          data: { user_id: userId }
        })
        this.record = result
        // 如果记录自带 AI 建议，直接显示
        if (result.ai_advice) {
          this.advice = result.ai_advice
        }
      } catch (err) {
        console.error(err)
        uni.showToast({ title: '加载失败', icon: 'error' })
      }
    },
    async generateAdvice() {
      if (!this.record || !this.record.id) return
      this.loadingAdvice = true
      try {
        const result = await request.request({
          url: '/api/advice/generate',
          method: 'POST',
          data: { record_id: this.record.id }
        })
        this.advice = result.ai_advice
        uni.showToast({ title: '建议已生成', icon: 'success' })
      } catch (err) {
        console.error(err)
        uni.showToast({ title: '生成失败', icon: 'error' })
      } finally {
        this.loadingAdvice = false
      }
    },
    goHome() {
      uni.switchTab({ url: '/pages/index/index' })
    }
  }
}
</script>

<style scoped>
.container { min-height: 100vh; background-color: #f5f5f5; padding: 30rpx; }
.result-card { background-color: #fff; border-radius: 20rpx; overflow: hidden; }
.result-card image { width: 100%; }
.info-box { display: flex; justify-content: space-between; padding: 20rpx 30rpx; border-bottom: 1rpx solid #eee; }
.label { font-size: 28rpx; color: #666; }
.value { font-size: 28rpx; color: #333; }
.value.disease { color: #e64340; font-weight: bold; }
.advice-box { background-color: #f8f9fa; border-radius: 16rpx; margin: 20rpx; padding: 20rpx; min-height: 120rpx; }
.advice-title { font-size: 28rpx; font-weight: bold; color: #333; display: block; margin-bottom: 15rpx; }
.advice-content { font-size: 28rpx; color: #555; line-height: 1.6; }
.advice-placeholder { color: #999; font-size: 26rpx; }
.advice-loading { color: #07c160; font-size: 26rpx; }
.weather-box { background-color: #e8f4fd; border-radius: 16rpx; margin: 20rpx; padding: 20rpx; font-size: 26rpx; color: #333; display: flex; flex-direction: column; gap: 10rpx; }
.weather-title { font-size: 28rpx; font-weight: bold; color: #007aff; margin-bottom: 10rpx; }
button { margin: 30rpx; }
.loading-state { text-align: center; padding: 100rpx; color: #999; }
</style>