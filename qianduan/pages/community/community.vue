<template>
  <view class="community-page">
    <!-- 顶部发布栏 -->
    <view class="publish-bar">
      <view class="publish-tabs">
        <view 
          class="publish-tab" 
          :class="{ active: publishType === 'experience' }"
          @click="publishType = 'experience'"
        >
          <text class="tab-icon">📝</text>
          <text>发经验</text>
        </view>
        <view 
          class="publish-tab" 
          :class="{ active: publishType === 'question' }"
          @click="publishType = 'question'"
        >
          <text class="tab-icon">❓</text>
          <text>提问题</text>
        </view>
      </view>
      
      <!-- 话题标签选择 -->
      <view class="topic-selector" v-if="showTopicSelector">
        <scroll-view scroll-x class="topic-scroll">
          <view 
            v-for="tag in hotTopics" 
            :key="tag"
            class="topic-tag"
            :class="{ active: selectedTopic === tag }"
            @click="selectedTopic = tag"
          >
            #{{ tag }}
          </view>
        </scroll-view>
      </view>
      
      <!-- 发布输入框 -->
      <view class="publish-input-area">
        <textarea 
          v-model="publishContent" 
          class="publish-textarea"
          :placeholder="publishType === 'experience' ? '分享你的种植经验...' : '描述你遇到的病虫害问题...'"
          maxlength="500"
          auto-height
        />
        <view class="publish-actions">
          <view class="image-upload" @click="chooseImage">
            <text>📷</text>
            <text class="upload-text">配图</text>
          </view>
          <view class="publish-btn" @click="doPublish">发布</view>
        </view>
      </view>
      
      <!-- 预览图片 -->
      <view class="preview-images" v-if="uploadImages.length > 0">
        <view v-for="(img, idx) in uploadImages" :key="idx" class="preview-img-item">
          <image :src="img" mode="aspectFill" class="preview-img"></image>
          <view class="remove-img" @click="removeImage(idx)">✕</view>
        </view>
      </view>
    </view>

    <!-- 单列帖子列表（从上往下） -->
    <view class="post-list">
      <view 
        v-for="item in allPosts" 
        :key="item.id" 
        class="post-card"
        :class="item.type === 'experience' ? 'experience-card' : 'question-card'"
        @click="viewPostDetail(item)"
      >
        <view class="card-header">
          <view class="user-info">
            <image class="avatar" :src="item.avatar || defaultAvatar" mode="aspectFill"></image>
            <view class="user-detail">
              <text class="username">{{ item.username }}</text>
              <text class="time">{{ item.created_at }}</text>
            </view>
          </view>
          <view class="type-badge" :class="item.type === 'experience' ? 'experience-badge' : 'question-badge'">
            <text>{{ item.type === 'experience' ? '🌾 经验分享' : '❓ 求助问答' }}</text>
          </view>
        </view>
        
        <view class="card-content">
          <text class="content-text">{{ item.content }}</text>
          <view class="question-tags" v-if="item.crop_type || item.disease_name">
            <text v-if="item.crop_type" class="question-tag">#{{ item.crop_type }}</text>
            <text v-if="item.disease_name" class="question-tag">#{{ item.disease_name }}</text>
          </view>
          <image 
            v-if="item.images && item.images[0]" 
            class="content-image" 
            :src="item.images[0]" 
            mode="aspectFill"
            @click.stop="previewImage(item.images[0])"
          ></image>
        </view>
        
        <view class="card-footer">
          <view class="action-btn" @click.stop="toggleLike(item)">
            <text class="action-icon">{{ item.is_liked ? '❤️' : '🤍' }}</text>
            <text>{{ item.like_count || 0 }}</text>
          </view>
          <view class="action-btn" @click.stop="toggleComment(item)">
            <text class="action-icon">💬</text>
            <text>{{ item.comment_count || 0 }}</text>
          </view>
          <view class="action-btn meet-btn" @click.stop="meetToo(item)">
            <text class="action-icon">🤝</text>
            <text>我也遇到了</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore">
      <text>{{ loadingMore ? '加载中...' : '上拉加载更多' }}</text>
    </view>
    <view class="no-more" v-else>
      <text>✨ 已经到底了 ~</text>
    </view>

    <!-- 评论弹窗 -->
    <view class="comment-modal" v-if="showCommentModal" @click.self="closeCommentModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>评论</text>
          <text class="close-btn" @click="closeCommentModal">✕</text>
        </view>
        
        <scroll-view class="comment-list" scroll-y>
          <view v-for="(comment, idx) in currentComments" :key="idx" class="comment-item">
            <view class="comment-left">
              <text class="comment-user">{{ comment.username || '用户' + comment.user_id }}：</text>
              <text class="comment-text">{{ comment.content }}</text>
              <text class="comment-time">{{ comment.created_at || '' }}</text>
            </view>
            <view v-if="comment.user_id === currentUserId" class="comment-delete" @click.stop="deleteComment(comment.id, idx)">
              <text>🗑️</text>
            </view>
          </view>
          
          <view v-if="currentComments.length === 0" class="empty-comment">
            <text>暂无评论，快来抢沙发～</text>
          </view>
        </scroll-view>
        
        <view class="comment-input-area" @click.stop>
          <input 
            v-model="commentInput" 
            class="comment-input" 
            placeholder="写评论..."
            confirm-type="send"
            @confirm="sendComment"
            @click.stop
            @focus.stop
          />
          <view class="send-btn" @click.stop="sendComment">发送</view>
        </view>
      </view>
    </view>

    <!-- 悬浮助手 -->
    <view class="floating-robot" @click="openAssistant">
      <image class="robot-image" src="/static/ai.jpg" mode="aspectFill"></image>
      <view class="breath-ring"></view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      // 发布相关
      publishType: 'experience',
      publishContent: '',
      selectedTopic: '',
      uploadImages: [],
      showTopicSelector: false,
      
      // 热门话题
      hotTopics: ['稻瘟病', '玉米螟', '小麦锈病', '蚜虫防治', '有机种植', '施肥技巧'],
      
      // 帖子数据
      allPosts: [],
      
      // 分页
      page: 1,
      pageSize: 10,
      hasMore: true,
      loadingMore: false,
      
      // 评论弹窗
      showCommentModal: false,
      currentPost: null,
      currentComments: [],
      commentInput: '',
      
      // 默认头像
      defaultAvatar: 'https://picsum.photos/id/64/100/100',
      currentUserId: 0
    }
  },
  
  onLoad() {
    this.currentUserId = request.getUserId()
    this.loadPosts()
  },
  
  onReachBottom() {
    if (this.hasMore && !this.loadingMore) {
      this.loadMore()
    }
  },
  
  onShow() {
    this.currentUserId = request.getUserId()
    if (this.allPosts.length > 0) {
      this.refreshPosts()
    }
  },
  
  methods: {
    // ========== 从后端加载帖子 ==========
    async loadPosts(isLoadMore = false) {
      if (this.loadingMore) return
      
      if (!isLoadMore) {
        this.page = 1
        this.hasMore = true
      }
      
      this.loadingMore = true
      
      try {
        const userId = request.getUserId()
        const result = await request.request({
          url: '/api/social/posts',
          data: {
            page: this.page,
            page_size: this.pageSize,
            current_user: userId
          },
          showLoading: !isLoadMore
        })
        
        const items = result.items || []
        const formattedItems = items.map(item => this.formatPost(item))
        
        if (isLoadMore) {
          this.allPosts = [...this.allPosts, ...formattedItems]
        } else {
          this.allPosts = formattedItems
        }
        
        this.hasMore = items.length === this.pageSize
        if (this.hasMore) {
          this.page++
        }
        
      } catch (err) {
        console.error('加载帖子失败', err)
        if (!isLoadMore && this.allPosts.length === 0) {
          this.generateMockPosts()
        }
      } finally {
        this.loadingMore = false
      }
    },
    
    formatPost(item) {
      let images = []
      if (item.images) {
        try {
          if (typeof item.images === 'string') {
            images = JSON.parse(item.images)
          } else if (Array.isArray(item.images)) {
            images = item.images
          }
        } catch (e) {
          images = []
        }
      }
      images = images.map(img => request.getImageUrl(img))

      return {
        id: item.id,
        user_id: item.user_id,
        username: item.username,
        avatar: request.getImageUrl(item.avatar),
        type: item.type,
        content: item.content,
        crop_type: item.crop_type,
        disease_name: item.disease_name,
        images: images,
        like_count: item.like_count || 0,
        comment_count: item.comment_count || 0,
        is_liked: item.is_liked || false,
        created_at: this.formatTime(item.created_at),
        location: item.location
      }
    },
    
    formatTime(dateStr) {
      if (!dateStr) return '刚刚'
      const date = new Date(dateStr)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000 / 60)
      
      if (diff < 1) return '刚刚'
      if (diff < 60) return `${diff}分钟前`
      if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
      return `${Math.floor(diff / 1440)}天前`
    },
    
    generateMockPosts() {
      const mockPosts = [
        {
          id: 1,
          user_id: 1,
          username: '农技小能手',
          avatar: this.defaultAvatar,
          type: 'experience',
          content: '水稻稻瘟病防治经验分享：发现病斑及时喷施三环唑，间隔7天再喷一次，效果很好！',
          crop_type: '水稻',
          disease_name: '稻瘟病',
          images: [],
          like_count: 45,
          comment_count: 12,
          is_liked: false,
          created_at: '2小时前'
        },
        {
          id: 2,
          user_id: 2,
          username: '草莓种植户',
          avatar: this.defaultAvatar,
          type: 'question',
          content: '求助！番茄叶片卷曲发黄，背面有白色小虫，这是什么病害？',
          crop_type: '番茄',
          disease_name: '虫害',
          images: [],
          like_count: 18,
          comment_count: 7,
          is_liked: false,
          created_at: '昨天'
        }
      ]
      this.allPosts = mockPosts
    },
    
    async refreshPosts() {
      this.page = 1
      this.hasMore = true
      await this.loadPosts(false)
    },
    
    loadMore() {
      if (this.hasMore && !this.loadingMore) {
        this.loadPosts(true)
      }
    },
    
    // ========== 发布帖子 ==========
    async doPublish() {
      if (!this.publishContent.trim()) {
        uni.showToast({ title: '请输入内容', icon: 'none' })
        return
      }
      
      try {
        const userId = request.getUserId()
        
        const uploadedImages = []
        for (const imgPath of this.uploadImages) {
          try {
            uni.showLoading({ title: '上传图片中...', mask: true })
            
            const uploadResult = await request.uploadFile({
              url: '/api/social/upload-image',
              filePath: imgPath
            })
            
            if (uploadResult && uploadResult.url) {
              uploadedImages.push(uploadResult.url)
            }
            
          } catch (err) {
            console.error('图片上传失败', err)
            uni.showToast({ title: '图片上传失败', icon: 'none' })
          }
        }
        
        uni.hideLoading()
        
        const result = await request.request({
          url: '/api/social/post',
          method: 'POST',
          data: {
            user_id: userId,
            content: this.publishContent,
            images: uploadedImages,
            crop_type: this.selectedTopic || null,
            disease_name: this.publishType === 'question' ? this.selectedTopic : null,
            location: null
          }
        })
        
        this.publishContent = ''
        this.uploadImages = []
        this.selectedTopic = ''
        
        uni.showToast({ title: '发布成功', icon: 'success' })
        await this.refreshPosts()
        
      } catch (err) {
        console.error('发布失败', err)
        uni.showToast({ title: err.message || '发布失败', icon: 'error' })
      }
    },
    
    chooseImage() {
      uni.chooseImage({
        count: 3 - this.uploadImages.length,
        success: (res) => {
          this.uploadImages = [...this.uploadImages, ...res.tempFilePaths]
        }
      })
    },
    
    removeImage(index) {
      this.uploadImages.splice(index, 1)
    },
    
    // ========== 点赞/评论 ==========
    async toggleComment(post) {
      if (!post || !post.id) {
        uni.showToast({ title: '帖子信息错误', icon: 'none' })
        return
      }
      
      this.currentPost = post
      this.commentInput = ''
      this.showCommentModal = true
      
      try {
        const result = await request.request({
          url: `/api/social/comments/${post.id}`,
          data: { page: 1, page_size: 20 },
          showLoading: false
        })
        
        if (result && result.items && Array.isArray(result.items)) {
          this.currentComments = result.items.map(item => ({
            ...item,
            created_at: this.formatTime(item.created_at)
          }))
        } else {
          this.currentComments = []
        }
        
      } catch (err) {
        console.error('加载评论失败', err)
        this.currentComments = []
      }
    },
    
    async toggleLike(post) {
      try {
        const userId = request.getUserId()
        
        if (!userId || userId === 0) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          return
        }
        
        const url = post.is_liked ? '/api/social/unlike' : '/api/social/like'
        
        await request.request({
          url: url,
          method: 'POST',
          data: {
            post_id: post.id,
            user_id: userId
          }
        })
        
        post.is_liked = !post.is_liked
        post.like_count += post.is_liked ? 1 : -1
        
        uni.showToast({ 
          title: post.is_liked ? '点赞成功' : '取消点赞', 
          icon: 'none' 
        })
        
      } catch (err) {
        console.error('点赞失败', err)
        uni.showToast({ title: '操作失败', icon: 'error' })
      }
    },
    
    async sendComment() {
      if (!this.commentInput.trim()) {
        uni.showToast({ title: '请输入评论内容', icon: 'none' })
        return
      }
      
      if (!this.currentPost || !this.currentPost.id) {
        uni.showToast({ title: '帖子信息错误', icon: 'none' })
        this.closeCommentModal()
        return
      }
      
      try {
        const userId = request.getUserId()
        
        const result = await request.request({
          url: '/api/social/comment',
          method: 'POST',
          data: {
            post_id: this.currentPost.id,
            user_id: userId,
            content: this.commentInput
          }
        })
        
        const newComment = {
          id: result.comment_id,
          user_id: userId,
          username: '我',
          content: this.commentInput,
          created_at: '刚刚'
        }
        
        this.currentComments.unshift(newComment)
        
        if (this.currentPost.comment_count !== undefined) {
          this.currentPost.comment_count++
        }
        
        this.commentInput = ''
        uni.showToast({ title: '评论成功', icon: 'success' })
        
      } catch (err) {
        console.error('评论失败', err)
        uni.showToast({ title: err.message || '评论失败，请重试', icon: 'error' })
      }
    },
    
    async deleteComment(commentId, index) {
      if (commentId > 1000000) {
        uni.showToast({ title: '该评论数据异常，无法删除', icon: 'none' })
        return
      }
      
      uni.showModal({
        title: '确认删除',
        content: '删除后无法恢复',
        success: async (res) => {
          if (res.confirm) {
            try {
              const userId = request.getUserId()
              
              await request.request({
                url: `/api/social/comment/${commentId}`,
                method: 'DELETE',
                data: { user_id: userId }
              })
              
              this.currentComments.splice(index, 1)
              
              if (this.currentPost && this.currentPost.comment_count > 0) {
                this.currentPost.comment_count--
              }
              
              uni.showToast({ title: '删除成功', icon: 'success' })
              
            } catch (err) {
              console.error('删除失败:', err)
              uni.showToast({ title: err.message || '删除失败', icon: 'error' })
            }
          }
        }
      })
    },
    
    closeCommentModal() {
      if (this.commentInput && this.commentInput.trim()) {
        return
      }
      this.showCommentModal = false
      setTimeout(() => {
        this.currentPost = null
        this.currentComments = []
        this.commentInput = ''
      }, 200)
    },
    
    meetToo(post) {
      uni.showModal({
        title: '同步病情',
        content: `是否将「${post.content.substring(0, 30)}...」同步到诊断页，方便后续识别和记录？`,
        confirmText: '同步',
        success: (res) => {
          if (res.confirm) {
            const syncData = {
              id: Date.now(),
              description: post.content,
              crop_type: post.crop_type,
              disease_name: post.disease_name,
              source: 'community',
              time: new Date().toLocaleString()
            }
            let history = uni.getStorageSync('sync_diseases') || []
            history.unshift(syncData)
            uni.setStorageSync('sync_diseases', history)
            
            uni.showToast({ 
              title: '已同步到诊断页', 
              icon: 'success',
              duration: 2000
            })
          }
        }
      })
    },
    
    viewPostDetail(post) {
      uni.showModal({
        title: post.type === 'experience' ? '经验详情' : '问题详情',
        content: post.content,
        showCancel: false
      })
    },
    
    previewImage(url) {
      uni.previewImage({ urls: [url] })
    },
    
    openAssistant() {
      uni.navigateTo({ url: '/subpages/ai/ai' })
    }
  }
}
</script>

<style lang="scss" scoped>
.community-page {
  min-height: 100vh;
  background: #f5f7f0;
  padding-bottom: 20px;
  position: relative;
}

.publish-bar {
  background: white;
  margin: 12px;
  border-radius: 24px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.publish-tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e8ecdf;
  padding-bottom: 12px;
}

.publish-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 40px;
  background: #f5f7f0;
  color: #6b7c5e;
  transition: all 0.2s;
  
  .tab-icon { font-size: 18px; }
  &.active { background: #2c5e2a; color: white; }
}

.topic-selector {
  margin-bottom: 12px;
}

.topic-scroll {
  white-space: nowrap;
  display: flex;
  gap: 10px;
}

.topic-tag {
  display: inline-block;
  padding: 6px 16px;
  background: #f0f3e8;
  border-radius: 30px;
  font-size: 13px;
  color: #5a6e4a;
  margin-right: 10px;
  
  &.active {
    background: #2c5e2a;
    color: white;
  }
}

.publish-textarea {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  background: #f8faf3;
  border-radius: 16px;
  font-size: 14px;
}

.publish-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.image-upload {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #eef3e6;
  border-radius: 30px;
  font-size: 14px;
}

.publish-btn {
  padding: 8px 24px;
  background: #2c5e2a;
  color: white;
  border-radius: 30px;
  font-weight: 600;
}

.preview-images {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.preview-img-item {
  position: relative;
  width: 70px;
  height: 70px;
  .preview-img { width: 100%; height: 100%; border-radius: 12px; }
  .remove-img {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 20px;
    height: 20px;
    background: red;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
  }
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 12px;
}

.post-card {
  background: white;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s;
  &:active { transform: scale(0.98); }
}

.experience-card { border-left: 4px solid #4caf50; }
.question-card { border-left: 4px solid #ff9800; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  gap: 10px;
  align-items: center;
  .avatar { width: 44px; height: 44px; border-radius: 50%; }
  .user-detail {
    display: flex;
    flex-direction: column;
    .username { font-weight: 600; font-size: 15px; color: #333; }
    .time { font-size: 11px; color: #999; }
  }
}

.type-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}
.experience-badge { background: #e8f5e9; color: #2e7d32; }
.question-badge { background: #fff3e0; color: #ef6c00; }

.card-content {
  .content-text { font-size: 15px; line-height: 1.5; color: #333; }
  .content-image { width: 100%; max-height: 240px; border-radius: 12px; margin-top: 12px; }
}

.question-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  .question-tag { font-size: 11px; padding: 4px 12px; background: #f0f3e8; border-radius: 20px; color: #5a6e4a; }
}

.card-footer {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0e8;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #888;
  padding: 6px 16px;
  border-radius: 30px;
  background: #fafbf6;
  .action-icon { font-size: 18px; }
  &.meet-btn { background: #eef3e6; color: #2c5e2a; }
}

.load-more, .no-more {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 12px;
}

.comment-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  width: 100%;
  background: white;
  border-radius: 24px 24px 0 0;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
  .close-btn { font-size: 20px; cursor: pointer; }
}

.comment-list {
  flex: 1;
  max-height: 50vh;
  padding: 12px;
}

.comment-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  .comment-left { flex: 1; }
  .comment-user { font-weight: 600; color: #2c5e2a; margin-right: 8px; }
  .comment-text { font-size: 14px; color: #333; }
  .comment-time { font-size: 10px; color: #aaa; margin-left: 8px; }
}

.comment-delete {
  padding: 4px 8px;
  font-size: 16px;
  color: #e74c3c;
}

.empty-comment {
  text-align: center;
  padding: 30px;
  color: #999;
  font-size: 13px;
}

.comment-input-area {
  display: flex;
  padding: 12px;
  border-top: 1px solid #eee;
  gap: 10px;
  background: white;
  .comment-input { flex: 1; padding: 10px; background: #f5f7f0; border-radius: 30px; font-size: 14px; }
  .send-btn { padding: 10px 20px; background: #2c5e2a; color: white; border-radius: 30px; }
}

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

@keyframes breathe {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.28); opacity: 0.2; }
  100% { transform: scale(1); opacity: 0.6; }
}

.floating-robot:active {
  transform: scale(0.92);
}
</style>