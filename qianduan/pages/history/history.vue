<template>
  <view class="history-page">
    <!-- 顶部统计栏 -->
    <view class="stats-bar">
      <view class="stat-item">
        <text class="stat-num">{{ totalCount }}</text>
        <text class="stat-label">总记录数</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ treatedCount }}</text>
        <text class="stat-label">已防治</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ untreatedCount }}</text>
        <text class="stat-label">待处理</text>
      </view>
    </view>

    <!-- 搜索筛选栏 -->
    <view class="search-bar">
      <view class="search-input-area">
        <input v-model="searchKeyword" class="search-input" placeholder="搜索病害名、作物名..." @confirm="handleSearch" />
      </view>
      <view class="search-btn" @click="handleSearch">
        <text class="search-icon">🔍</text>
      </view>
    </view>

    <!-- 快速筛选标签（包含日期） -->
    <scroll-view scroll-x class="filter-tags">
      <view class="tag" :class="{ active: activeFilter === 'all' }" @click="setFilter('all')">全部</view>
      <view class="tag" :class="{ active: activeFilter === '待防治' }" @click="setFilter('待防治')">待防治</view>
      <view class="tag" :class="{ active: activeFilter === '已防治' }" @click="setFilter('已防治')">已防治</view>
      <view class="tag date-tag" :class="{ active: dateFilter !== 'all' }" @click="showDatePicker = true">
        {{ dateFilterText }}
      </view>
    </scroll-view>

    <!-- 记录列表 -->
    <scroll-view scroll-y class="record-list" :style="{ height: listHeight + 'px' }" @scrolltolower="loadMore">
      <view v-if="filteredRecords.length === 0" class="empty-state">
        <text class="empty-icon">📂</text>
        <text class="empty-text">暂无植保档案记录</text>
        <text class="empty-hint">点击首页拍照识别，添加第一条记录</text>
      </view>

      <view v-for="item in filteredRecords" :key="item.id" class="record-card" :class="{ treated: item.status === '已防治' }">
        <view class="card-content" @click="viewDetail(item)">
          <view class="card-left">
            <image class="thumbnail" :src="item.image_url" mode="aspectFill"></image>
          </view>
          <view class="card-middle">
            <view class="disease-name">
              {{ item.disease_name }}
              <view class="status-badge" :class="item.status === '已防治' ? 'treated-badge' : 'pending-badge'">
                {{ item.status || '待防治' }}
              </view>
            </view>
            <view class="crop-name">🌾 {{ item.crop_type || '未知作物' }}</view>
            <view class="date-weather">
              <text class="date">📅 {{ item.created_at }}</text>
            </view>
          </view>
          <view class="card-right">
            <view class="severity" :class="getSeverityClass(item.confidence)">
              {{ getSeverityText(item.confidence) }}
            </view>
          </view>
        </view>
        
        <view class="card-actions">
          <view class="action-btn treat-btn" @click="markTreated(item)">
            <text class="btn-icon">✅</text>
            <text>{{ item.status === '已防治' ? '取消防治' : '标记防治' }}</text>
          </view>
          <view class="action-btn delete-btn" @click="deleteRecord(item)">
            <text class="btn-icon">🗑️</text>
            <text>删除</text>
          </view>
        </view>
      </view>

      <view class="load-more" v-if="hasMore">
        <text>{{ loading ? '加载中...' : '上拉加载更多' }}</text>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="bottom-actions">
      <view class="action-btn report-btn" @click="generateReport">
        <text>📊 生成报告</text>
      </view>
    </view>

    <!-- 日期选择弹窗 -->
    <view class="date-picker-modal" v-if="showDatePicker" @click="showDatePicker = false">
      <view class="date-picker-content" @click.stop>
        <view class="date-picker-header">
          <text class="picker-title">选择日期范围</text>
          <text class="picker-close" @click="showDatePicker = false">✕</text>
        </view>
        <view class="date-picker-body">
          <view class="quick-options">
            <view class="quick-option" @click="setQuickDate('week')">最近一周</view>
            <view class="quick-option" @click="setQuickDate('month')">最近一月</view>
            <view class="quick-option" @click="setQuickDate('all')">全部</view>
          </view>
          <view class="custom-date">
            <view class="date-input-group">
              <text class="date-label">开始日期</text>
              <input type="date" v-model="tempStartDate" class="date-input" />
            </view>
            <view class="date-input-group">
              <text class="date-label">结束日期</text>
              <input type="date" v-model="tempEndDate" class="date-input" />
            </view>
          </view>
        </view>
        <view class="date-picker-footer">
          <view class="reset-btn" @click="resetDatePicker">重置</view>
          <view class="confirm-btn" @click="confirmDateFilter">确定</view>
        </view>
      </view>
    </view>

    <!-- 报告弹窗（增强版） -->
    <view class="report-modal" v-if="showReport" @click="showReport = false">
      <view class="report-content" @click.stop>
        <view class="report-header">
          <view class="report-title-area">
            <text class="report-icon">📊</text>
            <text class="report-title">植保分析报告</text>
          </view>
          <text class="close-btn" @click="showReport = false">✕</text>
        </view>
        
        <scroll-view scroll-y class="report-body">
          <view class="report-date">
            <text>生成时间：{{ reportDate }}</text>
          </view>

          <view class="overview-card">
            <text class="section-title">📋 数据概览</text>
            <view class="overview-stats">
              <view class="overview-item">
                <text class="overview-num">{{ reportData.total }}</text>
                <text class="overview-label">总记录数</text>
              </view>
              <view class="overview-item">
                <text class="overview-num">{{ reportData.treated }}</text>
                <text class="overview-label">已防治</text>
              </view>
              <view class="overview-item">
                <text class="overview-num">{{ reportData.untreated }}</text>
                <text class="overview-label">待处理</text>
              </view>
              <view class="overview-item">
                <text class="overview-num" :class="getRateColor(reportData.rate)">{{ reportData.rate }}%</text>
                <text class="overview-label">防治率</text>
              </view>
            </view>
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: reportData.rate + '%' }"></view>
            </view>
            <text class="progress-text">防治进度 {{ reportData.rate }}%</text>
          </view>

          <view class="disease-stats-card">
            <text class="section-title">🦠 病害分布统计</text>
            <view v-for="(item, idx) in diseaseRanking" :key="idx" class="stat-bar-item">
              <view class="stat-bar-left">
                <text class="stat-rank">{{ idx + 1 }}</text>
                <text class="stat-name">{{ item.name }}</text>
              </view>
              <view class="stat-bar-right">
                <view class="stat-bar-bg">
                  <view class="stat-bar-fill" :style="{ width: (item.count / maxDiseaseCount) * 100 + '%' }"></view>
                </view>
                <text class="stat-count">{{ item.count }}次</text>
              </view>
            </view>
            <view v-if="diseaseRanking.length === 0" class="empty-stats">
              <text>暂无病害数据</text>
            </view>
          </view>

          <view class="trend-card" v-if="monthlyTrend.length > 0">
            <text class="section-title">📈 月度趋势</text>
            <view class="trend-chart">
              <view v-for="(item, idx) in monthlyTrend" :key="idx" class="trend-column">
                <view class="trend-bar-wrapper">
                  <view class="trend-bar" :style="{ height: (item.count / maxMonthlyCount) * 100 + 'px' }"></view>
                </view>
                <text class="trend-label">{{ item.month }}</text>
                <text class="trend-value">{{ item.count }}次</text>
              </view>
            </view>
          </view>

          <view class="crop-stats-card" v-if="cropRanking.length > 0">
            <text class="section-title">🌾 作物分布</text>
            <view class="crop-list">
              <view v-for="(item, idx) in cropRanking" :key="idx" class="crop-item">
                <text class="crop-icon">{{ getCropIcon(item.name) }}</text>
                <text class="crop-name">{{ item.name }}</text>
                <text class="crop-count">{{ item.count }}次</text>
              </view>
            </view>
          </view>

          <view class="pending-card" v-if="pendingList.length > 0">
            <text class="section-title">⚠️ 待处理清单</text>
            <view v-for="(item, idx) in pendingList" :key="idx" class="pending-item">
              <text class="pending-disease">{{ item.disease_name }}</text>
              <text class="pending-date">{{ item.created_at }}</text>
              <view class="pending-tag">待防治</view>
            </view>
          </view>

          <view class="advice-card">
            <text class="section-title">💡 AI 智能建议</text>
            <view class="advice-content">
              <text class="advice-text">{{ reportData.suggestion }}</text>
            </view>
            <view class="advice-tips">
              <text class="tip" v-if="reportData.rate < 50">⚠️ 防治率较低，建议尽快处理待防治病害</text>
              <text class="tip" v-else-if="reportData.rate < 80">📌 防治进度中等，继续保持</text>
              <text class="tip success" v-else>✅ 防治情况良好，请继续保持！</text>
            </view>
          </view>
        </scroll-view>
        
        <view class="report-footer">
          <view class="share-btn" @click="shareReport">📤 分享报告</view>
          <view class="save-btn" @click="saveReport">💾 保存报告</view>
        </view>
      </view>
    </view>

    <!-- 悬浮助手（带动画） -->
    <view class="floating-robot" @click="openAssistant">
      <image class="robot-image" src="/static/ai.jpg" mode="aspectFill"></image>
      <view class="breath-ring"></view>
      <view class="float-ring ring-1"></view>
      <view class="float-ring ring-2"></view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      allRecords: [],
      searchKeyword: '',
      activeFilter: 'all',
      listHeight: 0,
      showReport: false,
      reportData: {},
      diseaseRanking: [],
      cropRanking: [],
      pendingList: [],
      monthlyTrend: [],
      reportDate: '',
      defaultThumb: 'https://picsum.photos/id/15/100/100',
      
      // 分页
      loading: false,
      hasMore: true,
      page: 1,
      pageSize: 10,
      
      // 日期筛选
      showDatePicker: false,
      dateFilter: 'all',
      dateFilterText: '日期',
      startDate: '',
      endDate: '',
      tempStartDate: '',
      tempEndDate: ''
    }
  },
  
  computed: {
    totalCount() {
      return this.allRecords.length
    },
    treatedCount() {
      return this.allRecords.filter(r => r.status === '已防治').length
    },
    untreatedCount() {
      return this.allRecords.filter(r => r.status !== '已防治').length
    },
    maxDiseaseCount() {
      return Math.max(...this.diseaseRanking.map(d => d.count), 1)
    },
    maxMonthlyCount() {
      return Math.max(...this.monthlyTrend.map(m => m.count), 1)
    },
    filteredRecords() {
      let records = [...this.allRecords]
      
      if (this.searchKeyword) {
        records = records.filter(r => 
          r.disease_name.includes(this.searchKeyword) || 
          (r.crop_type && r.crop_type.includes(this.searchKeyword))
        )
      }
      
      if (this.activeFilter !== 'all') {
        records = records.filter(r => r.status === this.activeFilter)
      }
      
      if (this.dateFilter === 'week') {
        const weekAgo = new Date()
        weekAgo.setDate(weekAgo.getDate() - 7)
        const weekAgoStr = weekAgo.toISOString().split('T')[0]
        records = records.filter(r => r.created_at >= weekAgoStr)
      } else if (this.dateFilter === 'month') {
        const monthAgo = new Date()
        monthAgo.setMonth(monthAgo.getMonth() - 1)
        const monthAgoStr = monthAgo.toISOString().split('T')[0]
        records = records.filter(r => r.created_at >= monthAgoStr)
      } else if (this.dateFilter === 'custom' && this.startDate && this.endDate) {
        records = records.filter(r => r.created_at >= this.startDate && r.created_at <= this.endDate)
      }
      
      return records
    }
  },
  
  onLoad() {
    this.calcListHeight()
    this.refreshList()
    uni.$on('refreshRecords', () => {
      this.refreshList()
    })
  },
  
  onShow() {
    this.refreshList()
  },
  
  onUnload() {
    uni.$off('refreshRecords')
  },
  
  methods: {
    refreshList() {
      this.page = 1
      this.hasMore = true
      this.loadRecords(false)
    },
    
    calcListHeight() {
      const systemInfo = uni.getSystemInfoSync()
      this.listHeight = systemInfo.windowHeight - 300
    },
    
    // ========== 从后端加载数据 ==========
    async loadRecords(isLoadMore = false) {
      if (this.loading) return
      
      if (!isLoadMore) {
        this.page = 1
        this.hasMore = true
      }
      
      this.loading = true
      
      try {
        const userId = request.getUserId()
        
        if (!userId || userId === 0) {
          uni.showModal({
            title: '提示',
            content: '请先登录',
            success: () => {
              uni.reLaunch({ url: '/subpages/login/login' })
            }
          })
          return
        }
        
        const result = await request.request({
          url: '/api/history/list',
          data: {
            user_id: userId,
            page: this.page,
            page_size: this.pageSize
          },
          showLoading: !isLoadMore
        })
        
        const items = result.items || []
        const formattedItems = items.map(item => this.formatRecord(item))
        
        if (isLoadMore) {
          this.allRecords = [...this.allRecords, ...formattedItems]
        } else {
          this.allRecords = formattedItems
        }
        
        this.hasMore = items.length === this.pageSize
        if (this.hasMore) {
          this.page++
        }
        
      } catch (err) {
        console.error('加载历史记录失败', err)
      } finally {
        this.loading = false
      }
    },
    
    formatRecord(item) {
      return {
        id: item.id,
        disease_name: item.disease_name,
        crop_type: item.crop_type,
        confidence: item.confidence,
        status: item.status || '待防治',
        created_at: item.created_at,
        image_url: request.getImageUrl(item.image_url),
        weather_info: item.weather_info,
        ai_advice: item.ai_advice
      }
    },
    
    loadMore() {
      if (!this.loading && this.hasMore) {
        this.loadRecords(true)
      }
    },
    
    getSeverityClass(confidence) {
      if (!confidence) return 'severity-mild'
      if (confidence > 0.7) return 'severity-severe'
      if (confidence > 0.4) return 'severity-mid'
      return 'severity-mild'
    },
    
    getSeverityText(confidence) {
      if (!confidence) return '轻度'
      if (confidence > 0.7) return '严重'
      if (confidence > 0.4) return '中等'
      return '轻度'
    },
    
    getRateColor(rate) {
      if (rate >= 80) return 'rate-good'
      if (rate >= 50) return 'rate-medium'
      return 'rate-bad'
    },
    
    getCropIcon(cropName) {
      const icons = {
        '水稻': '🌾',
        '玉米': '🌽',
        '番茄': '🍅',
        '草莓': '🍓'
      }
      return icons[cropName] || '🌱'
    },
    
    async deleteRecord(item) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除「${item.disease_name}」的诊断记录吗？`,
        confirmColor: '#e74c3c',
        success: async (res) => {
          if (res.confirm) {
            try {
              const userId = request.getUserId()
              
              await request.request({
                url: `/api/history/delete/${item.id}`,
                method: 'DELETE',
                data: { user_id: userId }
              })
              
              this.refreshList()
              uni.showToast({ title: '删除成功', icon: 'success' })
              
            } catch (err) {
              console.error('删除失败', err)
              uni.showToast({ title: err.message || '删除失败', icon: 'error' })
            }
          }
        }
      })
    },
    
    async markTreated(item) {
      const newStatus = item.status === '已防治' ? '待防治' : '已防治'
      
      try {
        const userId = request.getUserId()
        
        await request.request({
          url: `/api/history/update-status/${item.id}`,
          method: 'PUT',
          data: {
            user_id: userId,
            status: newStatus
          }
        })
        
        item.status = newStatus
        uni.showToast({ 
          title: newStatus === '已防治' ? '已标记为防治完成' : '已标记为待防治', 
          icon: 'success' 
        })
        
      } catch (err) {
        console.error('更新状态失败', err)
        uni.showToast({ title: '操作失败', icon: 'error' })
      }
    },
    
    viewDetail(item) {
      uni.navigateTo({
        url: `/subpages/result/result?id=${item.id}`
      })
    },
    
    setFilter(type) {
      this.activeFilter = type
    },
    
    handleSearch() {
      uni.hideKeyboard()
      const count = this.filteredRecords.length
      if (count > 0) {
        uni.showToast({ title: `找到 ${count} 条记录`, icon: 'success', duration: 1500 })
      } else {
        uni.showToast({ title: '未找到匹配记录', icon: 'none', duration: 1500 })
      }
    },
    
    // 日期筛选方法
    updateDateFilterText() {
      if (this.dateFilter === 'week') {
        this.dateFilterText = '最近一周'
      } else if (this.dateFilter === 'month') {
        this.dateFilterText = '最近一月'
      } else if (this.dateFilter === 'custom' && this.startDate && this.endDate) {
        this.dateFilterText = `${this.startDate}~${this.endDate}`
      } else {
        this.dateFilterText = '日期'
      }
    },
    
    setQuickDate(type) {
      const today = new Date()
      if (type === 'week') {
        const weekAgo = new Date()
        weekAgo.setDate(today.getDate() - 7)
        this.tempStartDate = weekAgo.toISOString().split('T')[0]
        this.tempEndDate = today.toISOString().split('T')[0]
        this.dateFilter = 'week'
      } else if (type === 'month') {
        const monthAgo = new Date()
        monthAgo.setMonth(today.getMonth() - 1)
        this.tempStartDate = monthAgo.toISOString().split('T')[0]
        this.tempEndDate = today.toISOString().split('T')[0]
        this.dateFilter = 'month'
      } else {
        this.tempStartDate = ''
        this.tempEndDate = ''
        this.dateFilter = 'all'
      }
      this.updateDateFilterText()
    },
    
    confirmDateFilter() {
      if (this.tempStartDate && this.tempEndDate) {
        this.startDate = this.tempStartDate
        this.endDate = this.tempEndDate
        this.dateFilter = 'custom'
      } else {
        this.startDate = ''
        this.endDate = ''
        this.dateFilter = 'all'
      }
      this.updateDateFilterText()
      this.showDatePicker = false
      uni.showToast({ title: '日期筛选已应用', icon: 'success' })
    },
    
    resetDatePicker() {
      this.tempStartDate = ''
      this.tempEndDate = ''
    },
    
    generateReport() {
      const records = this.allRecords
      const total = records.length
      const treated = records.filter(r => r.status === '已防治').length
      const untreated = total - treated
      const rate = total > 0 ? Math.round((treated / total) * 100) : 0
      
      const diseaseCountMap = new Map()
      records.forEach(record => {
        const disease = record.disease_name
        if (disease) {
          diseaseCountMap.set(disease, (diseaseCountMap.get(disease) || 0) + 1)
        }
      })
      this.diseaseRanking = Array.from(diseaseCountMap.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5)
      
      const cropCountMap = new Map()
      records.forEach(record => {
        const crop = record.crop_type
        if (crop) {
          cropCountMap.set(crop, (cropCountMap.get(crop) || 0) + 1)
        }
      })
      this.cropRanking = Array.from(cropCountMap.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
      
      this.pendingList = records.filter(r => r.status !== '已防治').slice(0, 5)
      
      const monthMap = new Map()
      records.forEach(record => {
        const dateStr = record.created_at
        if (dateStr) {
          const month = dateStr.substring(0, 7)
          monthMap.set(month, (monthMap.get(month) || 0) + 1)
        }
      })
      this.monthlyTrend = Array.from(monthMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([name, count]) => ({ month: name.substring(5), count }))
        .slice(-6)
      
      const now = new Date()
      this.reportDate = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
      
      let suggestion = ''
      if (rate >= 80) {
        suggestion = '您的防治情况良好，请继续保持。建议定期巡查，做好预防工作，重点关注高频病害的监测。'
      } else if (rate >= 50) {
        suggestion = '您的防治进度中等，请加强未防治病害的处理。建议优先处理高频病害，合理安排防治时间。'
      } else {
        suggestion = '您的防治率较低，建议立即处理待防治病害。可咨询植保专家获取帮助，或使用AI识别功能获取防治建议。'
      }
      
      this.reportData = {
        total, treated, untreated, rate,
        suggestion: suggestion
      }
      this.showReport = true
    },
    
    shareReport() {
      uni.showToast({ title: '报告已保存到相册', icon: 'success' })
    },
    
    saveReport() {
      uni.showToast({ title: '报告已保存', icon: 'success' })
    },
    
    openAssistant() {
      uni.navigateTo({ url: '/subpages/ai/ai' })
    }
  }
}
</script>

<style lang="scss" scoped>
.history-page {
  min-height: 100vh;
  background: #f5f7f0;
  padding-bottom: 20px;
  position: relative;
}

.stats-bar {
  display: flex;
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  margin: 12px;
  border-radius: 28px;
  padding: 16px 0;
  color: white;
}

.stat-item {
  flex: 1;
  text-align: center;
  .stat-num { font-size: 28px; font-weight: bold; display: block; }
  .stat-label { font-size: 12px; opacity: 0.9; }
}

.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }

.search-bar {
  display: flex;
  gap: 12px;
  padding: 0 12px;
  margin-bottom: 12px;
}

.search-input-area {
  flex: 1;
  display: flex;
  align-items: center;
  background: white;
  border-radius: 40px;
  padding: 10px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  .search-input { flex: 1; font-size: 14px; }
}

.search-btn {
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  .search-icon { font-size: 18px; }
}

.filter-tags {
  white-space: nowrap;
  padding: 0 12px;
  margin-bottom: 16px;
  .tag {
    display: inline-block;
    padding: 6px 16px;
    background: white;
    border-radius: 30px;
    margin-right: 10px;
    font-size: 13px;
    color: #6b7c5e;
    &.active { background: #2c5e2a; color: white; }
  }
  .tag.date-tag {
    &.active {
      background: #2c5e2a;
      color: white;
    }
  }
}

.record-list { padding: 0 12px; }

.record-card {
  background: white;
  border-radius: 20px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  &.treated { opacity: 0.75; background: #f0f5ea; }
}

.card-content {
  display: flex;
  padding: 14px;
  gap: 12px;
}

.card-left .thumbnail { width: 70px; height: 70px; border-radius: 16px; }

.card-middle {
  flex: 1;
  .disease-name {
    font-weight: 700;
    font-size: 16px;
    color: #333;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .crop-name { font-size: 13px; color: #6b7c5e; margin: 4px 0; }
  .date-weather { display: flex; gap: 12px; font-size: 11px; color: #999; }
}

.card-right {
  align-items: flex-end;
  justify-content: space-between;
  display: flex;
  flex-direction: column;
  .severity { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; }
  .severity-severe { background: #ffebee; color: #c62828; }
  .severity-mid { background: #fff3e0; color: #ef6c00; }
  .severity-mild { background: #e8f5e9; color: #2e7d32; }
}

.status-badge { padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: 500; }
.treated-badge { background: #d4edda; color: #155724; }
.pending-badge { background: #fff3cd; color: #856404; }

.card-actions {
  display: flex;
  border-top: 1px solid #f0f0e8;
  .action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 12px;
    font-size: 13px;
    font-weight: 500;
    .btn-icon { font-size: 16px; }
    &.treat-btn { background: #f8faf3; color: #2c5e2a; border-right: 1px solid #f0f0e8; }
    &.delete-btn { background: #fef5f5; color: #e74c3c; }
  }
}

.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 64px; display: block; }
.empty-text { font-size: 16px; color: #999; margin-top: 16px; display: block; }
.empty-hint { font-size: 12px; color: #bbb; margin-top: 8px; display: block; }

.load-more { text-align: center; padding: 20px; color: #999; font-size: 12px; }

.bottom-actions {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  padding: 12px 20px;
  background: transparent;
  .report-btn {
    background: linear-gradient(135deg, #2c5e2a, #3a7a36);
    color: white;
    padding: 14px;
    border-radius: 40px;
    text-align: center;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(44, 94, 42, 0.3);
  }
}

/* 日期选择弹窗 */
.date-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.date-picker-content {
  width: 85%;
  background: white;
  border-radius: 28px;
  display: flex;
  flex-direction: column;
}

.date-picker-header {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #eee;
  .picker-title { font-size: 18px; font-weight: 600; color: #2c5e2a; }
  .picker-close { font-size: 24px; color: #999; }
}

.date-picker-body {
  padding: 20px;
}

.quick-options {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  
  .quick-option {
    flex: 1;
    padding: 10px;
    text-align: center;
    background: #f5f7f0;
    border-radius: 30px;
    font-size: 14px;
    color: #666;
  }
}

.custom-date {
  .date-input-group {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    
    .date-label { font-size: 14px; color: #666; width: 70px; }
    .date-input {
      flex: 1;
      padding: 10px;
      background: #f5f7f0;
      border-radius: 12px;
      font-size: 14px;
    }
  }
}

.date-picker-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #eee;
  
  .reset-btn {
    flex: 1;
    padding: 12px;
    text-align: center;
    background: #f5f7f0;
    border-radius: 40px;
    color: #666;
  }
  
  .confirm-btn {
    flex: 1;
    padding: 12px;
    text-align: center;
    background: #2c5e2a;
    border-radius: 40px;
    color: white;
  }
}

/* 报告弹窗样式 */
.report-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-content {
  width: 90%;
  max-height: 85vh;
  background: white;
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  
  .report-title-area {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .report-icon { font-size: 24px; }
    .report-title { font-size: 18px; font-weight: bold; color: white; }
  }
  
  .close-btn { font-size: 24px; color: white; opacity: 0.8; }
}

.report-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.report-date {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c5e2a;
  display: block;
  margin-bottom: 12px;
}

.overview-card {
  background: #f8faf3;
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 20px;
}

.overview-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  
  .overview-item {
    text-align: center;
    
    .overview-num {
      font-size: 28px;
      font-weight: bold;
      color: #2c5e2a;
      display: block;
      
      &.rate-good { color: #2e7d32; }
      &.rate-medium { color: #ef6c00; }
      &.rate-bad { color: #c62828; }
    }
    
    .overview-label { font-size: 12px; color: #8a9a7a; }
  }
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2c5e2a, #4a9e46);
    border-radius: 4px;
    transition: width 0.3s ease;
  }
}

.progress-text {
  font-size: 12px;
  color: #666;
  text-align: center;
  display: block;
}

.disease-stats-card, .trend-card, .crop-stats-card, .pending-card, .advice-card {
  background: #f8faf3;
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 16px;
}

.stat-bar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  
  .stat-bar-left {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100px;
    
    .stat-rank {
      width: 24px;
      font-weight: bold;
      color: #2c5e2a;
    }
    
    .stat-name { font-size: 14px; color: #333; }
  }
  
  .stat-bar-right {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .stat-bar-bg {
      flex: 1;
      height: 8px;
      background: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
      
      .stat-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #2c5e2a, #4a9e46);
        border-radius: 4px;
      }
    }
    
    .stat-count { font-size: 12px; color: #666; width: 40px; }
  }
}

.trend-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 160px;
  padding: 16px 0;
  
  .trend-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 50px;
    
    .trend-bar-wrapper {
      height: 100px;
      display: flex;
      align-items: flex-end;
      
      .trend-bar {
        width: 30px;
        background: linear-gradient(to top, #2c5e2a, #4a9e46);
        border-radius: 8px 8px 0 0;
        transition: height 0.3s;
        min-height: 8px;
      }
    }
    
    .trend-label { font-size: 11px; color: #999; margin-top: 8px; }
    .trend-value { font-size: 11px; color: #2c5e2a; font-weight: bold; margin-top: 4px; }
  }
}

.crop-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  
  .crop-item {
    display: flex;
    align-items: center;
    gap: 6px;
    background: white;
    padding: 8px 16px;
    border-radius: 30px;
    
    .crop-icon { font-size: 18px; }
    .crop-name { font-size: 14px; color: #333; }
    .crop-count { font-size: 12px; color: #2c5e2a; font-weight: bold; }
  }
}

.pending-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
  
  &:last-child { border-bottom: none; }
  
  .pending-disease { font-size: 14px; font-weight: 500; color: #333; }
  .pending-date { font-size: 11px; color: #999; }
  .pending-tag {
    font-size: 11px;
    padding: 4px 10px;
    background: #fff3cd;
    color: #856404;
    border-radius: 20px;
  }
}

.advice-content {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  
  .advice-text {
    font-size: 14px;
    color: #555;
    line-height: 1.6;
  }
}

.advice-tips {
  .tip {
    font-size: 13px;
    display: block;
    padding: 8px 12px;
    background: #fff3e0;
    border-radius: 12px;
    color: #ef6c00;
    
    &.success {
      background: #e8f5e9;
      color: #2e7d32;
    }
  }
}

.empty-stats {
  text-align: center;
  padding: 20px;
  color: #999;
}

.report-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #eee;
  
  .share-btn {
    flex: 1;
    padding: 12px;
    text-align: center;
    background: #2c5e2a;
    color: white;
    border-radius: 40px;
    font-weight: 600;
  }
  
  .save-btn {
    flex: 1;
    padding: 12px;
    text-align: center;
    background: #f0f5ea;
    color: #2c5e2a;
    border-radius: 40px;
    font-weight: 600;
  }
}

/* 悬浮助手 */
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
</style>