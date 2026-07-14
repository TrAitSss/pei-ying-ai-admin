<template>
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", "PingFang SC", sans-serif;
  background: #212121;
  color: #ececec;
  -webkit-font-smoothing: antialiased;
}

/* 全局滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #4a4a4a;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #5a5a5a;
}

/* Element Plus 深色主题覆盖 */
.el-card {
  --el-card-bg-color: #2f2f2f;
  --el-card-border-color: #3f3f3f;
  border-radius: 12px !important;
  border: 1px solid #3f3f3f !important;
  color: #ececec;
}
.el-card__header {
  border-bottom-color: #3f3f3f !important;
  color: #ececec;
}

.el-dialog {
  --el-dialog-bg-color: #2f2f2f;
  border: 1px solid #3f3f3f;
  border-radius: 16px !important;
}
.el-dialog__header {
  color: #ececec;
}
.el-dialog__title {
  color: #ececec !important;
}

.el-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #262626;
  --el-table-row-hover-bg-color: #383838;
  --el-table-border-color: #3f3f3f;
  --el-table-text-color: #ececec;
  --el-table-header-text-color: #9ca3af;
  color: #ececec;
}

.el-input__wrapper,
.el-textarea__inner {
  background-color: #1e1e1e !important;
  box-shadow: 0 0 0 1px #3f3f3f inset !important;
  color: #ececec !important;
  border-radius: 8px !important;
}
.el-input__inner,
.el-textarea__inner {
  color: #ececec !important;
}
.el-input__inner::placeholder {
  color: #6b7280 !important;
}

.el-select .el-input__wrapper {
  background-color: #1e1e1e !important;
}

.el-form-item__label {
  color: #9ca3af !important;
}

.el-button--primary {
  --el-button-bg-color: #10a37f;
  --el-button-border-color: #10a37f;
  --el-button-hover-bg-color: #0d8c6d;
  --el-button-hover-border-color: #0d8c6d;
  border-radius: 8px !important;
}

.el-button--default {
  --el-button-bg-color: #2f2f2f;
  --el-button-border-color: #3f3f3f;
  --el-button-text-color: #ececec;
  --el-button-hover-bg-color: #383838;
  --el-button-hover-border-color: #4a4a4a;
  --el-button-hover-text-color: #ececec;
  border-radius: 8px !important;
}

.el-button--danger {
  border-radius: 8px !important;
}

.el-tag {
  border-radius: 6px !important;
}

.el-menu {
  border-right: none !important;
}

.el-overlay {
  background-color: rgba(0,0,0,0.6) !important;
}

.el-message-box {
  --el-messagebox-bg-color: #2f2f2f;
  border: 1px solid #3f3f3f;
  border-radius: 16px !important;
}
.el-message-box__title {
  color: #ececec !important;
}
.el-message-box__message {
  color: #9ca3af !important;
}

.el-timeline-item__content {
  color: #ececec !important;
}

.el-empty__description p {
  color: #6b7280 !important;
}

.el-loading-mask {
  background-color: rgba(33, 33, 33, 0.8) !important;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>