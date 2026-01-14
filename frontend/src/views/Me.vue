<script setup lang="ts">
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push('/login');
};
</script>

<template>
  <div class="page-container">
    <div class="header-area">
      <div class="user-profile">
        <div class="avatar">
          <van-icon name="user-o" size="30" />
        </div>
        <div class="user-info">
          <div class="username">用户名</div>
          <div class="userid">微信号：wxid_123456</div>
        </div>
        <div class="qr-code">
          <van-icon name="qr" />
          <van-icon name="arrow" class="arrow" />
        </div>
      </div>
    </div>
    
    <div class="menu-group">
      <van-cell title="服务" is-link icon="gold-coin-o" />
    </div>
    
    <div class="menu-group">
      <van-cell title="收藏" is-link icon="star-o" />
      <van-cell title="朋友圈" is-link icon="photo-o" />
      <van-cell title="卡包" is-link icon="coupon-o" />
      <van-cell title="表情" is-link icon="smile-o" />
    </div>
    
    <div class="menu-group">
      <van-cell title="设置" is-link icon="setting-o" />
    </div>
    
    <div class="menu-group logout-group">
      <van-cell title="退出登录" @click="logout" center style="text-align: center; color: #fa5151;" />
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100%;
  background-color: #ededed;
  padding-bottom: 20px;
}

.header-area {
  background-color: #fff;
  padding: 30px 24px 30px 24px;
  margin-bottom: 8px;
}

.user-profile {
  display: flex;
  align-items: center;
}

.avatar {
  width: 64px;
  height: 64px;
  background-color: #e0e0e0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 20px;
  font-weight: 600;
  color: #191919;
  margin-bottom: 8px;
}

.userid {
  font-size: 14px;
  color: #7f7f7f;
}

.qr-code {
  display: flex;
  align-items: center;
  color: #7f7f7f;
}

.arrow {
  margin-left: 10px;
  color: #b2b2b2;
}

.menu-group {
  margin-top: 8px;
  background-color: #fff;
}

:deep(.van-cell__left-icon) {
  margin-right: 12px;
  font-size: 20px;
}
</style>
