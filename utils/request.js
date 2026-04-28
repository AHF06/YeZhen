// utils/request.js
import config from './config.js'

// ========== 用户信息管理 ==========
const getStorageUser = () => {
  try {
    const user = uni.getStorageSync('userInfo')
    console.log('存储的用户信息:', user)
    return user || null
  } catch (e) {
    return null
  }
}

const getUserId = () => {
  const user = getStorageUser()
  const userId = user ? user.user_id : 0
  console.log('获取到的用户ID:', userId)
  return userId
}

const getToken = () => {
  const user = getStorageUser()
  return user ? user.token : ''
}

const setUserInfo = (userInfo) => {
  uni.setStorageSync('userInfo', userInfo)
  uni.setStorageSync('is_login', true)
}

const clearUserInfo = () => {
  uni.removeStorageSync('userInfo')
  uni.removeStorageSync('is_login')
}

// ========== 请求封装 ==========
const request = (options) => {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    // API请求：必须拼接完整域名
    const fullUrl = config.baseUrl + url
    
    const defaultHeader = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
      ...header
    }
    
    if (options.showLoading !== false) {
      uni.showLoading({ title: '加载中...', mask: true })
    }
    
    uni.request({
      url: fullUrl,
      method: method,
      data: data,
      header: defaultHeader,
      timeout: config.timeout,
      success: (res) => {
        if (config.debug) {
          console.log(`[API] ${method} ${url}`, data, '->', res.data)
        }
        
        if (res.statusCode === 200) {
          if (res.data.code === 200) {
            resolve(res.data.data)
          } else {
            uni.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(res.data)
          }
        } else {
          uni.showToast({
            title: `网络错误: ${res.statusCode}`,
            icon: 'none'
          })
          reject(res)
        }
      },
      fail: (err) => {
        console.error('[API Error]', err)
        uni.showToast({
          title: '网络连接失败，请检查后端服务',
          icon: 'none',
          duration: 2000
        })
        reject(err)
      },
      complete: () => {
        if (options.showLoading !== false) {
          uni.hideLoading()
        }
      }
    })
  })
}

// 上传文件
const uploadFile = (options) => {
  return new Promise((resolve, reject) => {
    const { url, filePath, name = 'file', formData = {} } = options
    
    // 上传请求：必须拼接完整域名
    const fullUrl = config.baseUrl + url
    
    uni.showLoading({ title: '上传中...', mask: true })
    
    uni.uploadFile({
      url: fullUrl,
      filePath: filePath,
      name: name,
      formData: formData,
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          if (data.code === 200) {
            resolve(data.data)
          } else {
            uni.showToast({ title: data.message || '上传失败', icon: 'none' })
            reject(data)
          }
        } else {
          uni.showToast({ title: '上传失败', icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        console.error('[Upload Error]', err)
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      },
      complete: () => {
        uni.hideLoading()
      }
    })
  })
}

// ========== 导出 ==========
export default {
  request,
  uploadFile,
  getUserId,
  getToken,
  setUserInfo,
  clearUserInfo,
  config
}