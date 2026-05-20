<template>
  <view class="login-page">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="bg-blur"></view>
    </view>

    <!-- 顶部Logo区域 -->
    <view class="logo-section">
      <view class="logo-icon">
        <text class="logo-emoji">🌾</text>
      </view>
      <text class="app-name">叶诊</text>
      <text class="app-slogan">智慧农业 · 精准防控</text>
    </view>

    <!-- 微信一键登录 -->
    <view class="wechat-login-section">
      <button class="wechat-login-btn" @click="wechatLogin">
        <text class="wechat-icon">💚</text>
        <text class="wechat-text">微信一键登录</text>
      </button>
    </view>

    <!-- 分割线 -->
    <view class="divider">
      <view class="line"></view>
      <text class="divider-text">其他登录方式</text>
      <view class="line"></view>
    </view>

    <!-- 手机号密码登录 -->
    <view class="phone-login-entry" @click="showPhoneLogin = true">
      <text class="phone-icon">📱</text>
      <text class="phone-text">手机号密码登录</text>
      <text class="phone-arrow">›</text>
    </view>

    <!-- 注册入口 -->
    <view class="register-entry" @click="goToRegister">
      <text class="register-icon">📝</text>
      <text class="register-text">没有账号？立即注册</text>
      <text class="register-arrow">›</text>
    </view>

    <!-- 协议提示 -->
    <view class="agreement">
      <view class="checkbox small" :class="{ checked: agreeProtocol }" @click="agreeProtocol = !agreeProtocol">
        <text v-if="agreeProtocol">✓</text>
      </view>
      <text>登录即代表同意</text>
      <text class="link" @click="showProtocol('user')">《用户协议》</text>
      <text>和</text>
      <text class="link" @click="showProtocol('privacy')">《隐私政策》</text>
    </view>

    <!-- 手机号密码登录弹窗 -->
    <view class="login-modal" v-if="showPhoneLogin" @click="showPhoneLogin = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">手机号密码登录</text>
          <text class="modal-close" @click="showPhoneLogin = false">✕</text>
        </view>
        
        <view class="modal-body">
          <view class="login-form">
            <view class="input-group">
              <view class="input-icon">📱</view>
              <input 
                class="input-field" 
                v-model="loginForm.phone" 
                placeholder="请输入手机号"
                type="number"
                maxlength="11"
              />
            </view>
            <view class="input-group">
              <view class="input-icon">🔒</view>
              <input 
                class="input-field" 
                v-model="loginForm.password" 
                placeholder="请输入密码"
                :type="showPassword ? 'text' : 'password'"
              />
              <view class="input-eye" @click="showPassword = !showPassword">
                <text>{{ showPassword ? '👁️' : '👁️‍🗨️' }}</text>
              </view>
            </view>
            <view class="form-options">
              <view class="remember" @click="rememberMe = !rememberMe">
                <view class="checkbox" :class="{ checked: rememberMe }">
                  <text v-if="rememberMe">✓</text>
                </view>
                <text>记住密码</text>
              </view>
              <text class="forgot" @click="forgotPassword">忘记密码？</text>
            </view>
            <button class="login-btn" @click="handlePhoneLogin" :disabled="isLogining">
              {{ isLogining ? '登录中...' : '登 录' }}
            </button>
          </view>
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
      agreeProtocol: true,
      showPhoneLogin: false,
      loginForm: {
        phone: '',
        password: ''
      },
      showPassword: false,
      rememberMe: false,
      isLogining: false
    }
  },
  
  onLoad() {
    this.loadSavedAccount()
    // 检查是否已登录
    const isLogin = uni.getStorageSync('is_login')
    if (isLogin) {
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 500)
    }
  },
  
  methods: {
    loadSavedAccount() {
      const saved = uni.getStorageSync('saved_account')
      if (saved && saved.phone) {
        this.loginForm.phone = saved.phone
        this.loginForm.password = saved.password
        this.rememberMe = true
      }
    },
    
    saveAccount() {
      if (this.rememberMe) {
        uni.setStorageSync('saved_account', {
          phone: this.loginForm.phone,
          password: this.loginForm.password
        })
      } else {
        uni.removeStorageSync('saved_account')
      }
    },
    
    async wechatLogin() {
      if (!this.agreeProtocol) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }
      
      uni.showLoading({ title: '微信登录中...', mask: true })
      
      uni.login({
        provider: 'weixin',
        success: async (loginRes) => {
          try {
            const result = await request.request({
              url: '/api/auth/wechat-login',
              method: 'POST',
              data: { code: loginRes.code }
            })
            
            request.setUserInfo({
              user_id: result.user_id,
              username: result.username,
              nickname: result.nickname,
              phone: result.phone,
              avatar: result.avatar,
              token: result.token
            })
            
            uni.hideLoading()
            uni.showToast({ title: '登录成功', icon: 'success' })
            
            setTimeout(() => {
              uni.switchTab({ url: '/pages/index/index' })
            }, 500)
            
          } catch (err) {
            uni.hideLoading()
            uni.showToast({ title: err.message || '登录失败', icon: 'error' })
          }
        },
        fail: (err) => {
          uni.hideLoading()
          console.error('微信登录失败', err)
          uni.showToast({ title: '微信登录失败', icon: 'error' })
        }
      })
    },
    
    async handlePhoneLogin() {
      if (!this.loginForm.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }
      if (!this.loginForm.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      if (!this.agreeProtocol) {
        uni.showToast({ title: '请先同意用户协议', icon: 'none' })
        return
      }

      this.isLogining = true
      uni.showLoading({ title: '登录中...', mask: true })

      try {
        const result = await request.request({
          url: '/api/auth/login',
          method: 'POST',
          data: {
            phone: this.loginForm.phone.trim(),
            password: this.loginForm.password.trim()
          }
        })
        console.log('登录返回:', result)
        request.setUserInfo({
          user_id: result.user_id,
          username: result.username,
          nickname: result.nickname,
          phone: result.phone,
          avatar: result.avatar,
          token: result.token
        })
        
        this.saveAccount()
        this.showPhoneLogin = false
        
        uni.hideLoading()
        uni.showToast({ title: '登录成功', icon: 'success' })
        
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 500)
        
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: err.message || '手机号或密码错误', icon: 'error' })
      } finally {
        this.isLogining = false
      }
    },
    
    goToRegister() {
      uni.navigateTo({ url: '/subpages/register/register' })
    },
    
    forgotPassword() {
      uni.showModal({
        title: '找回密码',
        content: '请联系管理员重置密码',
        confirmText: '确定',
        showCancel: false
      })
    },
    
    showProtocol(type) {
      const title = type === 'user' ? '用户协议' : '隐私政策'
      const content = type === 'user' 
        ? '欢迎使用病虫害识别助手！本应用致力于为用户提供专业的病虫害识别与防治建议服务。'
        : '我们重视您的隐私保护。我们会收集您的设备信息、使用记录等以提供更好的服务。'
      
      uni.showModal({
        title: title,
        content: content,
        showCancel: false,
        confirmText: '我知道了'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #2c5e2a 0%, #4a9e46 50%, #2c5e2a 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  padding-bottom: 40px;
}

.logo-section {
  text-align: center;
  margin-top: 80px;
  margin-bottom: 50px;
  z-index: 1;
}
.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255,255,255,0.2);
  border-radius: 24px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-emoji {
  font-size: 48px;
}
.app-name {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: white;
}
.wechat-login-section {
  padding: 0 40px;
  margin-bottom: 30px;
}
.wechat-login-btn {
  width: 100%;
  background: #07c160;
  border-radius: 50px;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: white;
}
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 40px;
  margin-bottom: 24px;
}
.line {
  flex: 1;
  height: 1px;
  background: rgba(255,255,255,0.3);
}
.divider-text {
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}
.phone-login-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  margin: 0 40px 16px;
  background: rgba(255,255,255,0.15);
  border-radius: 50px;
}
.register-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  margin: 12px 40px 30px;
  background: rgba(255,255,255,0.1);
  border-radius: 50px;
}
.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  padding: 20px;
}
.checkbox.small {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: white;
}
.checkbox.small.checked {
  background: #07c160;
  border-color: #07c160;
}
.link {
  color: #fff;
  text-decoration: underline;
}
.login-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  width: 85%;
  background: white;
  border-radius: 28px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid #f0f0e8;
}
.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: #2c5e2a;
}
.modal-close {
  font-size: 24px;
  color: #999;
}
.modal-body {
  padding: 20px;
}
.input-group {
  display: flex;
  align-items: center;
  background: #f5f7f0;
  border-radius: 16px;
  padding: 12px 16px;
  margin-bottom: 16px;
}
.input-icon {
  font-size: 20px;
  margin-right: 12px;
}
.input-field {
  flex: 1;
  font-size: 15px;
  background: transparent;
}
.input-eye {
  padding: 4px 8px;
}
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.checkbox {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.checkbox.checked {
  background: #2c5e2a;
  border-color: #2c5e2a;
  color: white;
}
.forgot {
  color: #999;
  font-size: 13px;
}
.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #2c5e2a, #3a7a36);
  color: white;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 600;
  border: none;
}
</style>