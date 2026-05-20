<template>
  <view class="register-page">
    <view class="bg-decoration">
      <view class="bg-blur"></view>
    </view>

    <view class="logo-section">
      <view class="logo-icon">
        <text class="logo-emoji">🌾</text>
      </view>
      <text class="app-name">注册账号</text>
      <text class="app-slogan">手机号一键注册</text>
    </view>

    <view class="form-section">
      <view class="input-group">
        <view class="input-icon">📱</view>
        <input 
          class="input-field" 
          v-model="form.phone" 
          placeholder="手机号"
          type="number"
          maxlength="11"
        />
      </view>
      
      <view class="input-group">
        <view class="input-icon">🔒</view>
        <input 
          class="input-field" 
          v-model="form.password" 
          placeholder="密码（至少6位）"
          type="password"
        />
      </view>
      
      <view class="input-group">
        <view class="input-icon">🔒</view>
        <input 
          class="input-field" 
          v-model="form.confirmPassword" 
          placeholder="确认密码"
          type="password"
        />
      </view>
      
      <view class="input-group">
        <view class="input-icon">😊</view>
        <input 
          class="input-field" 
          v-model="form.nickname" 
          placeholder="昵称（选填）"
        />
      </view>

      <view class="agreement" @click="agreeProtocol = !agreeProtocol">
        <view class="checkbox" :class="{ checked: agreeProtocol }">
          <text v-if="agreeProtocol">✓</text>
        </view>
        <text class="agree-text">我已阅读并同意</text>
        <text class="link" @click.stop="showProtocol">《用户协议》</text>
      </view>

      <button class="register-btn" @click="handleRegister" :disabled="isRegistering">
        {{ isRegistering ? '注册中...' : '注册' }}
      </button>

      <view class="login-link" @click="goToLogin">
        已有账号？立即登录
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      form: {
        phone: '',
        password: '',
        confirmPassword: '',
        nickname: ''
      },
      agreeProtocol: false,
      isRegistering: false
    }
  },
  
  methods: {
    async handleRegister() {
      if (!this.form.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }
      if (!/^1[3-9]\d{9}$/.test(this.form.phone)) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }
      if (!this.form.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      if (this.form.password.length < 6) {
        uni.showToast({ title: '密码长度不能小于6位', icon: 'none' })
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
        return
      }
      if (!this.agreeProtocol) {
        uni.showToast({ title: '请阅读并同意用户协议', icon: 'none' })
        return
      }
      
      this.isRegistering = true
      uni.showLoading({ title: '注册中...', mask: true })
      
      try {
        const result = await request.request({
          url: '/api/auth/register',
          method: 'POST',
          data: {
            phone: this.form.phone,
            password: this.form.password,
            nickname: this.form.nickname || ''
          }
        })
        
        uni.hideLoading()
        uni.showToast({ title: '注册成功，请登录', icon: 'success' })

        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: err.message || '注册失败', icon: 'error' })
      } finally {
        this.isRegistering = false
      }
    },
    
    goToLogin() {
      uni.navigateBack()
    },
    
    showProtocol() {
      uni.showModal({
        title: '用户协议',
        content: '欢迎使用病虫害识别助手！本应用致力于为用户提供专业的病虫害识别与防治建议服务。',
        showCancel: false,
        confirmText: '我知道了'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #2c5e2a 0%, #4a9e46 50%, #2c5e2a 100%);
  position: relative;
  padding-bottom: 40px;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}
.bg-blur {
  position: absolute;
  top: -20%;
  left: -20%;
  width: 140%;
  height: 140%;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
}

.logo-section {
  text-align: center;
  margin-top: 60px;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}
.logo-icon {
  width: 70px;
  height: 70px;
  background: rgba(255,255,255,0.2);
  border-radius: 24px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}
.logo-emoji { font-size: 40px; }
.app-name { display: block; font-size: 24px; font-weight: bold; color: white; }
.app-slogan { display: block; font-size: 13px; color: rgba(255,255,255,0.8); margin-top: 5px; }

.form-section {
  padding: 0 40px;
  position: relative;
  z-index: 1;
}

.input-group {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.9);
  border-radius: 50px;
  padding: 12px 20px;
  margin-bottom: 16px;
}
.input-icon { font-size: 20px; margin-right: 12px; }
.input-field { flex: 1; font-size: 15px; background: transparent; }

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 20px 0;
  color: rgba(255,255,255,0.8);
  font-size: 13px;
}
.checkbox {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
}
.checkbox.checked { background: #07c160; border-color: #07c160; }
.link { color: #fff; text-decoration: underline; }

.register-btn {
  width: 100%;
  padding: 14px;
  background: #07c160;
  color: white;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  margin-bottom: 16px;
}

.login-link {
  text-align: center;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
  padding: 10px;
}
</style>