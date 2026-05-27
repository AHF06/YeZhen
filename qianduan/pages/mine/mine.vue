<template>
  <view class="mine-page">
    <!-- 用户信息头部 -->
    <view class="user-header" @click="editProfile">
      <image class="avatar" :src="userInfo.avatar || defaultAvatar" mode="aspectFill"></image>
      <view class="user-info">
        <view class="nickname-row">
          <text class="nickname">{{ userInfo.nickname }}</text>
          <text class="edit-icon">✎</text>
        </view>
        <text class="username">@{{ userInfo.username }}</text>
        <text class="bio">{{ userInfo.bio || '点击编辑个人资料' }}</text>
      </view>
    </view>

    <!-- 统计数据卡片 -->
    <view class="stats-cards">
      <view class="stat-card" @click="goToDiagnosisRecords">
        <text class="stat-num">{{ diagnosisCount }}</text>
        <text class="stat-label">诊断记录</text>
      </view>
      <view class="stat-card" @click="goToMyPosts">
        <text class="stat-num">{{ postCount }}</text>
        <text class="stat-label">我的动态</text>
      </view>
    </view>

    <!-- 功能菜单列表 -->
    <view class="menu-list">
      <!-- 账户管理组 -->
      <view class="menu-group">
        <view class="menu-group-title">账户管理</view>
        <view class="menu-item" @click="editProfile">
          <view class="menu-left">
            <text class="menu-icon">👤</text>
            <text class="menu-label">个人资料</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="changePhone">
          <view class="menu-left">
            <text class="menu-icon">📱</text>
            <text class="menu-label">更换手机号</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="changePassword">
          <view class="menu-left">
            <text class="menu-icon">🔒</text>
            <text class="menu-label">修改密码</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="changeUsername">
          <view class="menu-left">
            <text class="menu-icon">🏷️</text>
            <text class="menu-label">修改用户名</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 我的农场组 -->
      <view class="menu-group">
        <view class="menu-group-title">我的农场</view>
        <view class="menu-item" @click="goToDiagnosisRecords">
          <view class="menu-left">
            <text class="menu-icon">📋</text>
            <text class="menu-label">诊断记录</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToMyPosts">
          <view class="menu-left">
            <text class="menu-icon">📝</text>
            <text class="menu-label">我的动态</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 其他 -->
      <view class="menu-group">
        <view class="menu-item" @click="goToAbout">
          <view class="menu-left">
            <text class="menu-icon">ℹ️</text>
            <text class="menu-label">关于我们</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item logout-item" @click="handleLogout">
          <view class="menu-left">
            <text class="menu-icon">🚪</text>
            <text class="menu-label">退出登录</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text>病虫害识别助手 v2.0.0</text>
    </view>

    <!-- 编辑资料弹窗 -->
    <view class="modal-mask" v-if="showProfileModal" @click="showProfileModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>编辑资料</text>
          <text class="close-btn" @click="showProfileModal = false">✕</text>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="form-item">
            <text class="form-label">头像</text>
            <view class="avatar-upload" @click="changeAvatar">
              <image class="avatar-preview" :src="tempUserInfo.avatar || defaultAvatar" mode="aspectFill"></image>
              <text class="upload-hint">点击更换</text>
            </view>
          </view>
          <view class="form-item">
            <text class="form-label">昵称</text>
            <input class="form-input" v-model="tempUserInfo.nickname" placeholder="请输入昵称" />
          </view>
          <view class="form-item">
            <text class="form-label">用户名</text>
            <input class="form-input" v-model="tempUserInfo.username" placeholder="用户名" disabled />
            <text class="form-hint">用户名不可在此修改，请前往「修改用户名」</text>
          </view>
          <view class="form-item">
            <text class="form-label">手机号</text>
            <input class="form-input" v-model="tempUserInfo.phone" placeholder="手机号" disabled />
            <text class="form-hint">手机号不可在此修改，请前往「更换手机号」</text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showProfileModal = false">取消</view>
          <view class="save-btn" @click="saveProfile">保存</view>
        </view>
      </view>
    </view>

    <!-- 修改昵称弹窗 -->
    <view class="modal-mask" v-if="showNicknameModal" @click="showNicknameModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>修改昵称</text>
          <text class="close-btn" @click="showNicknameModal = false">✕</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <input class="form-input" v-model="nicknameForm.nickname" placeholder="请输入新昵称" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showNicknameModal = false">取消</view>
          <view class="save-btn" @click="saveNickname">保存</view>
        </view>
      </view>
    </view>

    <!-- 修改用户名弹窗 -->
    <view class="modal-mask" v-if="showUsernameModal" @click="showUsernameModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>修改用户名</text>
          <text class="close-btn" @click="showUsernameModal = false">✕</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <input class="form-input" v-model="usernameForm.username" placeholder="请输入新用户名（2-20字符）" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showUsernameModal = false">取消</view>
          <view class="save-btn" @click="saveUsername">保存</view>
        </view>
      </view>
    </view>

    <!-- 更换手机号弹窗 -->
    <view class="modal-mask" v-if="showPhoneModal" @click="showPhoneModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>更换手机号</text>
          <text class="close-btn" @click="showPhoneModal = false">✕</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">新手机号</text>
            <input class="form-input" v-model="phoneForm.newPhone" placeholder="请输入新手机号" type="number" maxlength="11" />
          </view>
          <view class="form-item">
            <text class="form-label">当前密码</text>
            <input class="form-input" v-model="phoneForm.password" placeholder="请输入当前密码" type="password" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showPhoneModal = false">取消</view>
          <view class="save-btn" @click="savePhone">确认更换</view>
        </view>
      </view>
    </view>

    <!-- 修改密码弹窗 -->
    <view class="modal-mask" v-if="showPasswordModal" @click="showPasswordModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text>修改密码</text>
          <text class="close-btn" @click="showPasswordModal = false">✕</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">原密码</text>
            <input class="form-input" v-model="passwordForm.oldPassword" placeholder="请输入原密码" type="password" />
          </view>
          <view class="form-item">
            <text class="form-label">新密码</text>
            <input class="form-input" v-model="passwordForm.newPassword" placeholder="请输入新密码（至少6位）" type="password" />
          </view>
          <view class="form-item">
            <text class="form-label">确认新密码</text>
            <input class="form-input" v-model="passwordForm.confirmPassword" placeholder="请再次输入新密码" type="password" />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showPasswordModal = false">取消</view>
          <view class="save-btn" @click="savePassword">确认修改</view>
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
      // 用户信息
      userInfo: {
        user_id: 0,
        username: '',
        nickname: '',
        avatar: '',
        phone: '',
        bio: ''
      },
      
      // 统计数据
      diagnosisCount: 0,
      postCount: 0,
      
      // 默认头像
      defaultAvatar: 'https://picsum.photos/id/64/200/200',
      
      // 弹窗控制
      showProfileModal: false,
      showNicknameModal: false,
      showUsernameModal: false,
      showPhoneModal: false,
      showPasswordModal: false,
      
      // 临时数据
      tempUserInfo: {},
      
      // 表单数据
      nicknameForm: { nickname: '' },
      usernameForm: { username: '' },
      phoneForm: { newPhone: '', password: '' },
      passwordForm: { oldPassword: '', newPassword: '', confirmPassword: '' }
    }
  },
  
  onLoad() {
    this.loadUserInfo()
    this.loadStatistics()
  },
  
  onShow() {
    this.loadStatistics()
    this.loadUserInfo()
  },
  
  methods: {
    // ========== 加载用户信息 ==========
    async loadUserInfo() {
      const userId = request.getUserId()
      if (userId && userId !== 0) {
        try {
          const result = await request.request({
            url: '/api/auth/profile',
            data: { user_id: userId },
            showLoading: false
          })
          
          this.userInfo = {
            user_id: result.user_id,
            username: result.username,
            nickname: result.nickname,
            avatar: request.getImageUrl(result.avatar),
            phone: result.phone,
            bio: result.bio || '热爱农业，科技兴农🌱'
          }
          
          // 更新存储的用户信息
          const storedUser = uni.getStorageSync('userInfo') || {}
          storedUser.username = result.username
          storedUser.nickname = result.nickname
          storedUser.avatar = request.getImageUrl(result.avatar)
          storedUser.phone = result.phone
          uni.setStorageSync('userInfo', storedUser)
          
        } catch (err) {
          console.error('加载用户信息失败', err)
          this.loadUserInfoFromStorage()
        }
      } else {
        this.loadUserInfoFromStorage()
      }
    },
    
    loadUserInfoFromStorage() {
      const stored = uni.getStorageSync('userInfo')
      if (stored) {
        this.userInfo = {
          user_id: stored.user_id || 0,
          username: stored.username || '用户',
          nickname: stored.nickname || '农友',
          avatar: stored.avatar || this.defaultAvatar,
          phone: stored.phone || '',
          bio: '热爱农业，科技兴农🌱'
        }
      }
    },
    
    // ========== 统计数据 ==========
    async loadStatistics() {
      try {
        const userId = request.getUserId()
        
        // 获取当前用户的诊断记录数量
        const historyResult = await request.request({
          url: '/api/history/list',
          data: { user_id: userId, page: 1, page_size: 1 },
          showLoading: false
        })
        this.diagnosisCount = historyResult.total || 0
        
        // 获取当前用户的帖子数量
        const postsResult = await request.request({
          url: '/api/social/posts',
          data: { user_id: userId, page: 1, page_size: 1 },
          showLoading: false
        })
        this.postCount = postsResult.total || 0
        
      } catch (err) {
        console.error('加载统计数据失败', err)
      }
    },
    
    // ========== 编辑资料 ==========
    editProfile() {
      this.tempUserInfo = { ...this.userInfo }
      this.showProfileModal = true
    },
    
    async saveProfile() {
      try {
        const userId = request.getUserId()
        
        await request.request({
          url: '/api/auth/update-nickname',
          method: 'POST',
          data: {
            user_id: userId,
            nickname: this.tempUserInfo.nickname
          }
        })
        
        this.userInfo.nickname = this.tempUserInfo.nickname
        
        // 更新存储
        const stored = uni.getStorageSync('userInfo') || {}
        stored.nickname = this.tempUserInfo.nickname
        uni.setStorageSync('userInfo', stored)
        
        this.showProfileModal = false
        uni.showToast({ title: '保存成功', icon: 'success' })
        
      } catch (err) {
        uni.showToast({ title: err.message || '保存失败', icon: 'error' })
      }
    },
    
    async changeAvatar() {
      uni.chooseImage({
        count: 1,
        sourceType: ['album'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          
          uni.showLoading({ title: '上传中...', mask: true })
          
          try {
            const uploadResult = await request.uploadFile({
              url: '/api/upload-avatar',
              filePath: tempFilePath
            })
            
            const userId = request.getUserId()
            await request.request({
              url: '/api/auth/update-avatar',
              method: 'POST',
              data: {
                user_id: userId,
                avatar: uploadResult.url
              }
            })
            
            this.tempUserInfo.avatar = request.getImageUrl(uploadResult.url)
            this.userInfo.avatar = request.getImageUrl(uploadResult.url)
            
            uni.hideLoading()
            uni.showToast({ title: '头像更新成功', icon: 'success' })
            
          } catch (err) {
            uni.hideLoading()
            uni.showToast({ title: '上传失败', icon: 'error' })
          }
        }
      })
    },
    
    // ========== 修改昵称 ==========
    changeNickname() {
      this.nicknameForm.nickname = this.userInfo.nickname
      this.showNicknameModal = true
    },
    
    async saveNickname() {
      if (!this.nicknameForm.nickname) {
        uni.showToast({ title: '昵称不能为空', icon: 'none' })
        return
      }
      
      try {
        const userId = request.getUserId()
        await request.request({
          url: '/api/auth/update-nickname',
          method: 'POST',
          data: {
            user_id: userId,
            nickname: this.nicknameForm.nickname
          }
        })
        
        this.userInfo.nickname = this.nicknameForm.nickname
        this.showNicknameModal = false
        uni.showToast({ title: '昵称修改成功', icon: 'success' })
        
      } catch (err) {
        uni.showToast({ title: err.message || '修改失败', icon: 'error' })
      }
    },
    
    // ========== 修改用户名 ==========
    changeUsername() {
      this.usernameForm.username = ''
      this.showUsernameModal = true
    },
    
    async saveUsername() {
      const username = this.usernameForm.username.trim()
      if (!username) {
        uni.showToast({ title: '用户名不能为空', icon: 'none' })
        return
      }
      if (username.length < 2 || username.length > 20) {
        uni.showToast({ title: '用户名长度应为2-20个字符', icon: 'none' })
        return
      }
      
      try {
        const userId = request.getUserId()
        await request.request({
          url: '/api/auth/update-username',
          method: 'POST',
          data: {
            user_id: userId,
            username: username
          }
        })
        
        this.userInfo.username = username
        this.showUsernameModal = false
        uni.showToast({ title: '用户名修改成功', icon: 'success' })
        
      } catch (err) {
        uni.showToast({ title: err.message || '修改失败', icon: 'error' })
      }
    },
    
    // ========== 更换手机号 ==========
    changePhone() {
      this.phoneForm = { newPhone: '', password: '' }
      this.showPhoneModal = true
    },
    
    async savePhone() {
      if (!this.phoneForm.newPhone) {
        uni.showToast({ title: '请输入新手机号', icon: 'none' })
        return
      }
      if (!/^1[3-9]\d{9}$/.test(this.phoneForm.newPhone)) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }
      if (!this.phoneForm.password) {
        uni.showToast({ title: '请输入当前密码', icon: 'none' })
        return
      }
      
      try {
        const userId = request.getUserId()
        await request.request({
          url: '/api/auth/update-phone',
          method: 'POST',
          data: {
            user_id: userId,
            new_phone: this.phoneForm.newPhone,
            password: this.phoneForm.password
          }
        })
        
        this.userInfo.phone = this.phoneForm.newPhone
        this.showPhoneModal = false
        uni.showToast({ title: '手机号修改成功', icon: 'success' })
        
      } catch (err) {
        uni.showToast({ title: err.message || '修改失败', icon: 'error' })
      }
    },
    
    // ========== 修改密码 ==========
    changePassword() {
      this.passwordForm = { oldPassword: '', newPassword: '', confirmPassword: '' }
      this.showPasswordModal = true
    },
    
    async savePassword() {
      if (!this.passwordForm.oldPassword) {
        uni.showToast({ title: '请输入原密码', icon: 'none' })
        return
      }
      if (!this.passwordForm.newPassword) {
        uni.showToast({ title: '请输入新密码', icon: 'none' })
        return
      }
      if (this.passwordForm.newPassword.length < 6) {
        uni.showToast({ title: '新密码长度不能小于6位', icon: 'none' })
        return
      }
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
        return
      }
      
      try {
        const userId = request.getUserId()
        await request.request({
          url: '/api/auth/update-password',
          method: 'POST',
          data: {
            user_id: userId,
            old_password: this.passwordForm.oldPassword,
            new_password: this.passwordForm.newPassword
          }
        })
        
        this.showPasswordModal = false
        uni.showToast({ title: '密码修改成功，请重新登录', icon: 'success' })
        
        setTimeout(() => {
          this.handleLogout()
        }, 1500)
        
      } catch (err) {
        uni.showToast({ title: err.message || '修改失败', icon: 'error' })
      }
    },
    
    // ========== 页面跳转 ==========
    goToDiagnosisRecords() {
      uni.switchTab({ url: '/pages/history/history' })
    },
    
    goToMyPosts() {
      uni.navigateTo({ url: '/subpages/myposts/myposts' })
    },
    
    goToAbout() {
      uni.showModal({
        title: '关于我们',
        content: '病虫害识别助手 v2.0.0\n\n一款专注于农业病虫害识别与防治的智能工具，助力智慧农业发展。',
        showCancel: false
      })
    },
    
    // ========== 退出登录 ==========
    handleLogout() {
      uni.showModal({
        title: '退出登录',
        content: '确定要退出登录吗？',
        confirmColor: '#e74c3c',
        success: (res) => {
          if (res.confirm) {
            request.clearUserInfo()
            
            uni.showToast({ title: '已退出', icon: 'success' })
            
            setTimeout(() => {
              uni.reLaunch({ url: '/subpages/login/login' })
            }, 500)
          }
        }
      })
    },
    
    openAssistant() {
      uni.navigateTo({ url: '/subpages/ai/ai' })
    }
  }
}
</script>

<style lang="scss" scoped>
.mine-page {
  min-height: 100vh;
  background: #f5f7f0;
  padding-bottom: 30px;
  position: relative;
}

.user-header {
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  padding: 40px 20px 30px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: 0 0 32px 32px;
  
  .avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 3px solid white;
  }
  
  .user-info {
    flex: 1;
    .nickname-row {
      display: flex;
      align-items: center;
      gap: 8px;
      .nickname { font-size: 20px; font-weight: bold; color: white; }
      .edit-icon { font-size: 14px; color: rgba(255,255,255,0.8); }
    }
    .username { font-size: 12px; color: rgba(255,255,255,0.7); display: block; margin: 4px 0; }
    .bio { font-size: 12px; color: rgba(255,255,255,0.8); }
  }
}

.stats-cards {
  display: flex;
  gap: 12px;
  padding: 0 16px;
  margin-top: -20px;
  
  .stat-card {
    flex: 1;
    background: white;
    border-radius: 20px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    .stat-num { font-size: 24px; font-weight: bold; color: #2c5e2a; display: block; }
    .stat-label { font-size: 12px; color: #8a9a7a; margin-top: 4px; }
  }
}

.menu-list { padding: 20px 16px; }

.menu-group {
  background: white;
  border-radius: 20px;
  margin-bottom: 16px;
  overflow: hidden;
  .menu-group-title { padding: 12px 16px; background: #f8faf3; font-size: 13px; color: #8a9a7a; }
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0e8;
  &:last-child { border-bottom: none; }
  
  .menu-left { display: flex; align-items: center; gap: 12px; }
  .menu-icon { font-size: 20px; }
  .menu-label { font-size: 15px; color: #333; }
  .menu-arrow { font-size: 18px; color: #ccc; }
  
  &.logout-item .menu-label { color: #e74c3c; }
}

.version-info { text-align: center; padding: 20px; font-size: 12px; color: #bbb; }

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  width: 85%;
  max-height: 80vh;
  background: white;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
  font-size: 18px;
  .close-btn { font-size: 24px; color: #999; }
}

.modal-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #eee;
  .cancel-btn { flex: 1; padding: 10px; text-align: center; background: #f5f7f0; border-radius: 40px; color: #666; }
  .save-btn { flex: 2; padding: 10px; text-align: center; background: #2c5e2a; color: white; border-radius: 40px; }
}

.form-item {
  margin-bottom: 16px;
  .form-label { font-size: 14px; color: #666; margin-bottom: 8px; display: block; }
  .form-input { width: 100%; padding: 12px; background: #f5f7f0; border-radius: 12px; font-size: 14px; }
  .form-hint { font-size: 11px; color: #999; margin-top: 5px; display: block; }
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
  
  .avatar-preview {
    width: 70px;
    height: 70px;
    border-radius: 50%;
  }
  
  .upload-hint {
    font-size: 14px;
    color: #2c5e2a;
  }
}

/* 悬浮助手（带动画） */
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