<template>
  <view class="myposts-page">
    <view class="post-list">
      <view v-if="posts.length === 0" class="empty-state">
        <text class="empty-icon">📝</text>
        <text>暂无发布动态</text>
        <text class="empty-hint">去农友圈发布你的第一条动态吧</text>
      </view>
      
      <view v-for="post in posts" :key="post.id" class="post-card">
        <!-- 帖子内容 -->
        <view class="post-header">
          <view class="user-info">
            <image class="avatar" :src="userInfo.avatar || defaultAvatar" mode="aspectFill"></image>
            <view class="user-detail">
              <text class="username">{{ userInfo.nickname }}</text>
              <text class="time">{{ post.created_at }}</text>
            </view>
          </view>
          <view class="delete-btn" @click="deletePost(post.id)">
            <text>🗑️</text>
          </view>
        </view>
        
        <view class="post-content">
          <text>{{ post.content }}</text>
        </view>
        
        <view v-if="post.images && post.images.length" class="post-images">
          <image v-for="(img, idx) in post.images" :key="idx" :src="img" mode="aspectFill"></image>
        </view>
        
        <view class="post-stats">
          <text>❤️ {{ post.like_count || 0 }}</text>
          <text>💬 {{ post.comment_count || 0 }}</text>
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
      posts: [],
      userInfo: {},
      defaultAvatar: 'https://picsum.photos/id/64/200/200'
    }
  },
  
  onLoad() {
    this.loadUserInfo()
    this.loadMyPosts()
  },
  
  methods: {
    loadUserInfo() {
      const stored = uni.getStorageSync('userInfo')
      if (stored) {
        this.userInfo = stored
      }
    },
    
    async loadMyPosts() {
      try {
        const userId = request.getUserId()  // 获取当前用户ID
        
        const result = await request.request({
          url: '/api/social/posts',
          data: { 
            user_id: userId,  // 只查询当前用户的帖子
            page: 1, 
            page_size: 50 
          }
        })
        
        this.posts = result.items || []
        
      } catch (err) {
        console.error('加载我的动态失败', err)
      }
    },
    
    async deletePost(postId) {
      uni.showModal({
        title: '确认删除',
        content: '删除后无法恢复',
        success: async (res) => {
          if (res.confirm) {
            try {
              const userId = request.getUserId()
              
              await request.request({
                url: `/api/social/post/${postId}`,
                method: 'DELETE',
                data: { user_id: userId }
              })
              
              this.posts = this.posts.filter(p => p.id !== postId)
              uni.showToast({ title: '删除成功', icon: 'success' })
              
            } catch (err) {
              console.error('删除失败', err)
              uni.showToast({ title: '删除失败', icon: 'error' })
            }
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.myposts-page {
  min-height: 100vh;
  background: #f5f7f0;
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
  .empty-icon { font-size: 64px; display: block; margin-bottom: 16px; }
  .empty-hint { font-size: 12px; margin-top: 8px; display: block; }
}

.post-card {
  background: white;
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 16px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  gap: 10px;
  .avatar { width: 44px; height: 44px; border-radius: 50%; }
  .user-detail { 
    .username { font-weight: 600; font-size: 15px; color: #333; display: block; }
    .time { font-size: 11px; color: #999; }
  }
}

.delete-btn {
  padding: 8px;
  font-size: 20px;
}

.post-content {
  font-size: 15px;
  line-height: 1.5;
  color: #333;
  margin-bottom: 12px;
}

.post-images {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  image { width: 100px; height: 100px; border-radius: 12px; }
}

.post-stats {
  display: flex;
  gap: 20px;
  color: #999;
  font-size: 13px;
}
</style>