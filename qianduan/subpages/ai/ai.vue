<template>
  <view class="ai-chat-page">
    <!-- 头部导航栏 -->
    <view class="chat-header">
      <view class="header-left" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-center">
        <view class="robot-avatar-small">
          <image class="robot-image-small" src="/subpages/static/ai.jpg" mode="aspectFill"></image>
        </view>
        <view class="robot-info">
          <text class="robot-name">农小智</text>
          <text class="robot-status">在线 · 随时为您服务</text>
        </view>
      </view>
      <view class="header-right">
        <text class="menu-icon" @click="showMenu">⋯</text>
      </view>
    </view>

    <!-- 聊天消息列表 -->
    <scroll-view 
      class="chat-messages" 
      scroll-y 
      :scroll-into-view="scrollToView"
      scroll-with-animation
      @scrolltoupper="loadMoreHistory"
    >
      <view v-if="messages.length === 0" class="welcome-message">
        <image class="welcome-image" src="/subpages/static/ai.jpg" mode="aspectFill"></image>
        <text class="welcome-title">您好，农场主！</text>
        <text class="welcome-desc">我是您的专属AI农技助手「农小智」</text>
        <text class="welcome-tip">我可以帮您：</text>
        <view class="welcome-actions">
          <view class="welcome-btn" @click="quickAsk('识别病虫害')">🔍 识别病虫害</view>
          <view class="welcome-btn" @click="quickAsk('防治方法')">🌿 防治方法</view>
          <view class="welcome-btn" @click="quickAsk('农药使用')">🧪 农药使用</view>
          <view class="welcome-btn" @click="quickAsk('种植技术')">🌱 种植技术</view>
        </view>
      </view>

      <!-- 消息列表 -->
      <view 
        v-for="(msg, idx) in messages" 
        :key="idx" 
        :id="'msg-' + idx"
        class="message-row"
        :class="msg.role"
      >
        <view v-if="msg.role === 'assistant'" class="message-avatar">
          <image class="avatar-image" src="/subpages/static/ai.jpg" mode="aspectFill"></image>
        </view>
        <view class="message-bubble" :class="msg.role">
          <text v-if="msg.isTyping" class="typing-indicator">
            <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
          </text>
          <text v-else class="message-text">{{ formatMessage(msg.content) }}</text>
        </view>
        <view v-if="msg.role === 'user'" class="message-avatar user-avatar">
          <image class="avatar-image" src="https://picsum.photos/id/64/100/100" mode="aspectFill"></image>
        </view>
      </view>

      <view v-if="isLoading" class="message-row assistant">
        <view class="message-avatar">
          <image class="avatar-image" src="/subpages/static/ai.jpg" mode="aspectFill"></image>
        </view>
        <view class="message-bubble assistant loading-bubble">
          <text class="loading-text">正在思考...</text>
        </view>
      </view>
    </scroll-view>

    <!-- 快捷回复栏 -->
    <scroll-view scroll-x class="quick-replies" v-if="quickReplies.length > 0">
      <view 
        v-for="reply in quickReplies" 
        :key="reply"
        class="quick-reply"
        @click="sendQuickReply(reply)"
      >
        {{ reply }}
      </view>
    </scroll-view>

    <!-- 底部输入栏 -->
    <view class="chat-input-bar">
      <view class="input-left">
        <view class="input-icon" @click="showImagePicker">
          <text>📷</text>
        </view>
        <view class="input-icon" @click="showVoiceInput">
          <text>🎤</text>
        </view>
      </view>
      <view class="input-container">
        <input 
          v-model="inputText" 
          class="chat-input" 
          placeholder="输入您的问题..."
          confirm-type="send"
          @confirm="sendMessage"
          @focus="onInputFocus"
          @blur="onInputBlur"
        />
      </view>
      <view class="send-btn" @click="sendMessage">
        <text>发送</text>
      </view>
    </view>

    <!-- 功能菜单弹窗 -->
    <view class="menu-modal" v-if="showMenuModal" @click="showMenuModal = false">
      <view class="menu-popup" @click.stop>
        <view class="menu-item" @click="clearHistory">
          <text>🗑️</text>
          <text>清空对话</text>
        </view>
        <view class="menu-item" @click="shareChat">
          <text>📤</text>
          <text>分享对话</text>
        </view>
        <view class="menu-item" @click="goToFeedback">
          <text>💬</text>
          <text>意见反馈</text>
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
      messages: [],
      inputText: '',
      isLoading: false,
      scrollToView: '',
      sessionId: '',
      hasMoreHistory: false,
      historyPage: 1,
      showMenuModal: false,
      quickReplies: []
    }
  },
  
  onLoad() {
    this.initSession()
    this.loadHistory()
    this.loadQuickQuestions()
  },
  
  methods: {
    // ========== 格式化消息，去除Markdown ==========
    formatMessage(text) {
      if (!text) return ''
      // 1. 移除加粗 **text**
      let formatted = text.replace(/\*\*(.*?)\*\*/g, '$1')
      // 2. 移除斜体或列表标记 *text*（成对出现）
      formatted = formatted.replace(/\*([^\*]+?)\*/g, '$1')
      // 3. 将行首的 * 或 - 列表标记替换为圆点
      formatted = formatted.replace(/^(\s*)[\*\-]\s+/gm, '$1• ')
      // 4. 移除连续星号或减号分隔线
      formatted = formatted.replace(/[\*\-]{3,}/g, '')
      return formatted
    },
    
    initSession() {
      const userId = request.getUserId()
      if (!userId || userId === 0) {
        console.log('用户未登录，使用临时会话')
        let sessionId = uni.getStorageSync('temp_session_id')
        if (!sessionId) {
          sessionId = 'temp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
          uni.setStorageSync('temp_session_id', sessionId)
        }
        this.sessionId = sessionId
      } else {
        let sessionId = uni.getStorageSync(`chat_session_${userId}`)
        if (!sessionId) {
          sessionId = `session_${userId}_${Date.now()}`
          uni.setStorageSync(`chat_session_${userId}`, sessionId)
        }
        this.sessionId = sessionId
        console.log('初始化会话 - 用户ID:', userId, '会话ID:', sessionId)
      }
    },
    
    loadHistory() {
      const userId = request.getUserId()
      let savedHistory = []
      if (userId && userId !== 0) {
        savedHistory = uni.getStorageSync(`ai_chat_history_${userId}`)
      } else {
        savedHistory = uni.getStorageSync('ai_chat_history_temp')
      }
      if (savedHistory && savedHistory.length > 0) {
        this.messages = savedHistory
      }
    },
    
    saveHistory() {
      const userId = request.getUserId()
      const toSave = this.messages.slice(-50)
      if (userId && userId !== 0) {
        uni.setStorageSync(`ai_chat_history_${userId}`, toSave)
      } else {
        uni.setStorageSync('ai_chat_history_temp', toSave)
      }
    },
    
    async loadQuickQuestions() {
      try {
        const result = await request.request({
          url: '/api/chat/quick-questions',
          showLoading: false
        })
        this.quickReplies = result.questions || []
      } catch (err) {
        console.error('加载快速提问失败', err)
        this.quickReplies = ['识别病虫害', '防治方法', '农药使用', '种植技术']
      }
    },
    
    async sendMessage() {
      const text = this.inputText.trim()
      if (!text) return
      this.addMessage('user', text)
      this.inputText = ''
      this.scrollToBottom()
      this.isLoading = true
      try {
        const userId = request.getUserId()
        const data = { session_id: this.sessionId, message: text }
        if (userId && userId !== 0) data.user_id = userId
        const result = await request.request({
          url: '/api/chat/send',
          method: 'POST',
          data: data
        })
        this.addMessage('assistant', result.reply)
        this.saveHistory()
        this.scrollToBottom()
        this.generateQuickReplies(result.reply)
      } catch (err) {
        console.error('AI请求失败', err)
        this.addMessage('assistant', '抱歉，AI服务暂时不可用，请稍后再试。🌾')
      } finally {
        this.isLoading = false
      }
    },
    
    addMessage(role, content) {
      this.messages.push({
        role: role,
        content: content,
        time: new Date().getTime(),
        isTyping: false
      })
      this.scrollToBottom()
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollToView = 'msg-' + (this.messages.length - 1)
      })
    },
    
    generateQuickReplies(reply) {
      if (reply.includes('拍照识别')) {
        this.quickReplies = ['去拍照识别', '描述症状', '查看防治方法']
      } else if (reply.includes('防治')) {
        this.quickReplies = ['用什么药', '怎么预防', '什么时候防治']
      } else {
        this.loadQuickQuestions()
      }
      setTimeout(() => {
        if (this.quickReplies.length > 0 && this.quickReplies.length <= 4) {
          this.loadQuickQuestions()
        }
      }, 5000)
    },
    
    sendQuickReply(reply) {
      this.inputText = reply
      this.sendMessage()
    },
    
    quickAsk(type) {
      this.inputText = type
      this.sendMessage()
    },
    
    showImagePicker() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera', 'album'],
        success: (res) => {
          const tempFilePath = res.tempFilePaths[0]
          this.addMessage('user', '[图片]')
          this.isLoading = true
          setTimeout(() => {
            this.addMessage('assistant', '收到您的图片！📸\n\n要识别病虫害，建议您返回首页点击「拍照识别病害」按钮，上传照片即可获得AI诊断结果。\n\n您也可以描述一下具体症状，我来帮您初步分析。')
            this.isLoading = false
            this.scrollToBottom()
          }, 1000)
        }
      })
    },
    
    showVoiceInput() {
      uni.showToast({ title: '语音功能开发中', icon: 'none' })
    },
    
    async clearHistory() {
      uni.showModal({
        title: '清空对话',
        content: '确定要清空所有聊天记录吗？',
        success: async (res) => {
          if (res.confirm) {
            const userId = request.getUserId()
            try {
              const data = { session_id: this.sessionId }
              if (userId && userId !== 0) data.user_id = userId
              await request.request({
                url: '/api/chat/clear',
                method: 'POST',
                data: data
              })
            } catch (err) {
              console.error('清空会话失败', err)
            }
            this.messages = []
            this.saveHistory()
            this.showMenuModal = false
            uni.showToast({ title: '已清空', icon: 'success' })
          }
        }
      })
    },
    
    shareChat() {
      uni.showToast({ title: '分享功能开发中', icon: 'none' })
    },
    
    goToFeedback() {
      this.showMenuModal = false
      uni.switchTab({ url: '/pages/mine/mine' })
      setTimeout(() => {
        uni.showToast({ title: '请在「我的-意见反馈」中提交', icon: 'none' })
      }, 500)
    },
    
    loadMoreHistory() {
      if (this.hasMoreHistory) {
        this.hasMoreHistory = false
      }
    },
    
    onInputFocus() {
      this.scrollToBottom()
    },
    
    onInputBlur() {
      setTimeout(() => {
        this.scrollToBottom()
      }, 100)
    },
    
    showMenu() {
      this.showMenuModal = true
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style lang="scss" scoped>
.ai-chat-page {
  width: 100%;
  height: 100vh;
  background: #f5f7f0;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 头部导航栏 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  color: white;
  
  .header-left {
    width: 44px;
    .back-icon { font-size: 28px; font-weight: bold; }
  }
  
  .header-center {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    
    .robot-avatar-small {
      position: relative;
      width: 44px;
      height: 44px;
      background: #f7cd5c;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      
      .robot-image-small {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
    
    .robot-info {
      .robot-name { font-size: 18px; font-weight: bold; display: block; }
      .robot-status { font-size: 11px; opacity: 0.8; }
    }
  }
  
  .header-right {
    width: 44px;
    text-align: right;
    .menu-icon { font-size: 22px; }
  }
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.load-history {
  text-align: center;
  padding: 10px;
  font-size: 12px;
  color: #999;
}

/* 欢迎消息 */
.welcome-message {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin: 20px 0;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  
  .welcome-image {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin-bottom: 16px;
    object-fit: cover;
  }
  
  .welcome-title {
    font-size: 20px;
    font-weight: bold;
    color: #2c5e2a;
    display: block;
    margin-bottom: 8px;
  }
  
  .welcome-desc {
    font-size: 14px;
    color: #666;
    display: block;
    margin-bottom: 16px;
  }
  
  .welcome-tip {
    font-size: 13px;
    color: #999;
    display: block;
    margin-bottom: 12px;
  }
  
  .welcome-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    
    .welcome-btn {
      padding: 8px 16px;
      background: #f0f5ea;
      border-radius: 30px;
      font-size: 13px;
      color: #2c5e2a;
    }
  }
}

/* 消息行 */
.message-row {
  display: flex;
  margin-bottom: 16px;
  
  &.user { justify-content: flex-end; }
  &.assistant { justify-content: flex-start; }
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  flex-shrink: 0;
  overflow: hidden;
  
  &.user-avatar {
    margin-right: 0;
    margin-left: 10px;
  }
  
  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 20px;
  font-size: 15px;
  line-height: 1.5;
  
  &.user {
    background: #2c5e2a;
    color: white;
    border-bottom-right-radius: 4px;
  }
  
  &.assistant {
    background: white;
    color: #333;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }
}

.message-text {
  word-break: break-all;
  white-space: pre-wrap;
  font-size: 15px;
  line-height: 1.5;
}

/* 打字动画 */
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  
  .dot {
    animation: blink 1.4s infinite;
    font-size: 20px;
    
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes blink {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.loading-bubble {
  background: #e8e8e8;
  .loading-text { font-size: 13px; color: #999; }
}

/* 快捷回复栏 */
.quick-replies {
  white-space: nowrap;
  padding: 8px 12px;
  background: transparent;
  
  .quick-reply {
    display: inline-block;
    padding: 6px 16px;
    background: white;
    border-radius: 30px;
    margin-right: 10px;
    font-size: 13px;
    color: #2c5e2a;
    border: 1px solid #e0e0e0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }
}

/* 底部输入栏 */
.chat-input-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #f0f0e8;
  padding-bottom: calc(12px + constant(safe-area-inset-bottom));
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}

.input-left {
  display: flex;
  gap: 12px;
  
  .input-icon {
    width: 36px;
    height: 36px;
    background: #f5f7f0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }
}

.input-container {
  flex: 1;
  .chat-input {
    width: 100%;
    padding: 10px 16px;
    background: #f5f7f0;
    border-radius: 30px;
    font-size: 15px;
  }
}

.send-btn {
  padding: 8px 20px;
  background: #2c5e2a;
  color: white;
  border-radius: 30px;
  font-weight: 500;
}

/* 菜单弹窗 */
.menu-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  padding: 60px 16px 0 0;
}

.menu-popup {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  overflow: hidden;
  
  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 20px;
    border-bottom: 1px solid #f0f0e8;
    font-size: 14px;
    
    &:last-child { border-bottom: none; }
    text:first-child { font-size: 18px; }
  }
}
</style>