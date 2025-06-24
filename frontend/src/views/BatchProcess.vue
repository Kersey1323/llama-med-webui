<template>
  <el-container class="batch-process-page">
    <el-aside width="200px" class="sidebar">
      <div class="logo-container">
        <div class="logo">
          <span class="logo-icon">C</span>
        </div>
        <span class="logo-text">CDU-MED</span>
      </div>
      <el-menu
          default-active="batch-process"
          class="el-menu-vertical-demo"
          @select="handleMenuSelect"
      >
        <el-menu-item index="chat">
          <el-icon>
            <ChatDotRound/>
          </el-icon>
          <span>对话模式</span>
        </el-menu-item>
        <el-menu-item index="batch-process">
          <el-icon>
            <Files/>
          </el-icon>
          <span>批量处理</span>
        </el-menu-item>
      </el-menu>
      <div class="user-info">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="dropdown-trigger">
            <el-avatar :size="30" class="user-avatar">{{ username.charAt(0) }}</el-avatar>
            <span class="username">{{ username }}</span>
            <el-icon>
              <ArrowDown/>
            </el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-aside>
    <el-main class="main-content">
      <div class="main-header">
        <h2>批量数据处理</h2>
        <p>上传 Excel 表格，AI 将自动识别并筛选出错误数据</p>
      </div>
      <el-card class="box-card history-card">
        <template #header>
          <div class="card-header">
            <span>历史处理记录</span>
          </div>
        </template>
        <div class="history-scroll-container">
          <div v-for="item in historyData" :key="item.id" class="history-item">
            <div class="history-item-info">
              <span class="history-item-title">{{ item.name }}</span>
              <span>错误数: {{ item.errors }}</span>
              <span>规范率: {{ item.correctionRate }}%</span>
            </div>
            <div class="history-item-actions">
              <el-button size="small" @click="exportData(item.id)" :icon="Download">导出</el-button>
              <el-button type="primary" size="small" @click="showHistoryErrors(item.id)">查看错误</el-button>
              <el-button size="small" type="danger" @click="handleDelete(item.id)" :icon="Delete">删除</el-button>
            </div>
            <el-tag :type="item.completedAt ? 'success' : 'info'" effect="light" style="width: 131px">
              {{ item.completedAt || '未完成' }}
            </el-tag>
          </div>
        </div>
        <!-- 分页控件 -->
        <el-pagination
            v-if="totalRecords > 0"
            background
            layout="total, prev, pager, next"
            :total="totalRecords"
            :current-page="currentPage"
            :page-size="pageSize"
            @current-change="handlePageChange"
            style="margin-top: 20px; text-align: center;"
        />
      </el-card>
      <el-upload
          class="upload-demo"
          drag
          action="/api/batch-process"
          :on-change="handleFileChange"
          :on-progress="handleUploadProgress"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :auto-upload="false"
          ref="uploadRef"
          :limit="1"
          accept=".xlsx, .xls"
      >
        <el-icon class="el-icon--upload">
          <Upload/>
        </el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 .xlsx, .xls 格式</div>
        </template>
      </el-upload>
      <!-- 开始处理按钮 -->
      <el-button
          v-if="showStartProcessButton"
          type="primary"
          @click="startBatchProcessing"
          :disabled="processingStarted"
          style="margin-bottom: 20px"
      >
        <el-icon>
          <VideoPlay/>
        </el-icon>
        开始处理
      </el-button>
      <!-- 进度条 -->
      <div class="progress-section">
        <span>{{ processingStarted ? '处理进度' : '上传进度' }}</span>
        <el-progress :percentage="batchProgress" :stroke-width="10" striped/>
      </div>
      <!-- 错误数据列表 -->
      <el-card class="box-card errors-card">
        <template #header>
          <div class="card-header">
            <span>错误数据列表</span>
            <el-button type="primary" @click="exportData">
              <el-icon>
                <Download/>
              </el-icon>
              导出数据
            </el-button>
          </div>
        </template>
        <div class="table-scroll-container">
          <el-table
              :data="errorData"
              style="width: 100%"
              height="350"
              :header-cell-style="{ background: '#fafafa', color: '#606266' }"
          >
            <el-table-column prop="row" label="行号" width="80" fixed/>
            <el-table-column prop="type" label="错误类型" width="180"/>
            <el-table-column prop="content" label="错误内容" min-width="250" show-overflow-tooltip/>
            <el-table-column prop="suggestion" label="建议修改" min-width="250" show-overflow-tooltip/>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="handleEdit(scope.$index, scope.row)">修改</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
      <!-- 编辑错误数据的对话框 -->
      <el-dialog
          v-model="editDialogVisible"
          title="编辑错误数据"
          width="40%"
      >
        <div class="dialog-content">
          <p class="label">当前错误内容</p>
          <el-input
              v-model="currentError.content"
              type="textarea"
              :rows="2"
              readonly
          />
          <p class="label">系统建议修改</p>
          <el-input
              v-model="currentError.suggestion"
              type="textarea"
              :rows="2"
              readonly
          />
          <div class="radio-group">
            <el-radio v-model="selectedAction" label="accept">接受修改建议</el-radio>
            <el-radio v-model="selectedAction" label="custom">自定义修改</el-radio>
            <el-radio v-model="selectedAction" label="ignore">标记为“非错误”</el-radio>
          </div>
          <!-- 自定义修改输入框 -->
          <el-input
              v-if="selectedAction === 'custom'"
              v-model="customInput"
              placeholder="请输入自定义修改内容"
              type="textarea"
              :rows="2"
          />
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmEdit">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import {useRouter} from 'vue-router';
import axios from '../utils/axios';
import {ElMessage, ElMessageBox} from 'element-plus';
import {
  ChatDotRound,
  Files,
  Upload,
  Download,
  ArrowDown,
  VideoPlay,
  Delete,
} from '@element-plus/icons-vue';

const router = useRouter();
const uploadRef = ref();
const file = ref(null);
const batchProgress = ref(0);
const uploading = ref(false);
const username = ref(localStorage.getItem('username') || 'Kersey1323');
let currentJobId = ref(null);
const processingStarted = ref(false);
const showStartProcessButton = ref(false);
const historyData = ref([]);
const totalRecords = ref(0); // 总记录数
const currentPage = ref(1);  // 当前页码
const pageSize = ref(10);    // 每页记录数

// 新增状态变量
const historyErrorDialogVisible = ref(false);
const currentHistoryJob = ref({});
const historyErrorData = ref([]);
const totalHistoryErrors = ref(0);
const currentHistoryPage = ref(1);
const pageSizeHistory = ref(10);

// 错误数据
const errorData = ref([]);
const totalErrors = ref(0); // 总记录数
const currentPageErrors = ref(1); // 当前页码
const pageSizeErrors = ref(10);   // 每页记录数

// 错误数据修改
const editDialogVisible = ref(false); // 控制对话框显示状态
const currentError = ref({}); // 当前编辑的错误数据
const selectedAction = ref('accept'); // 用户选择的操作
const customInput = ref(''); // 自定义修改的内容

// 菜单选择
const handleMenuSelect = (index) => {
  if (index === 'chat') {
    router.push('/medllm');
  }
};

// 分页切换
const handlePageChange = (page) => {
  currentPage.value = page; // 更新当前页码
  getHistoryData();         // 重新加载数据
};

// 删除历史记录
const handleDelete = async (jobId) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？删除后不可恢复', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await axios.delete(`/api/batch/jobs/${jobId}`);
    ElMessage.success('删除成功');
    await getHistoryData();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.response?.data?.error || error.message}`);
    }
  }
};

// 获取历史记录
const getHistoryData = async () => {
  try {
    const response = await axios.get('/api/batch/jobs', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
      },
    });
    const {data, total} = response.data;
    historyData.value = data;       // 更新历史记录数据
    totalRecords.value = total;     // 更新总记录数
  } catch (error) {
    ElMessage.error('获取历史数据失败!');
    console.error(error);
  }
};

// 显示历史错误
const showHistoryErrors = async (jobId) => {
  currentHistoryJob.value = historyData.value.find(item => item.id === jobId);
  await getErrors(jobId);
  currentJobId = jobId;
};

// 获取错误数据
const getErrors = async (jobId) => {
  try {
    const response = await axios.get(`/api/batch/jobs/${jobId}/errors`, {
      params: {
        page: currentPageErrors.value,
        page_size: pageSizeErrors.value,
      },
    });
    const {data, total} = response.data;
    errorData.value = data;       // 更新错误数据
    totalErrors.value = total;    // 更新总记录数
  } catch (error) {
    ElMessage.error('获取错误数据失败!');
    console.error(error);
  }
};

// 导出数据
const exportData = async (job_id) => {
  if (!Number.isInteger(job_id)) {
    job_id = currentJobId;
  }
  try {
    const response = await axios.get(`/api/batch/jobs/${job_id}/export`, {
      responseType: 'blob'
    });
    const contentDisposition = response.headers['content-disposition'];
    let fileName = 'processed_data.xlsx';
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename="?(.+?)"?(;|$)/);
      if (fileNameMatch && fileNameMatch[1]) {
        fileName = decodeURIComponent(fileNameMatch[1]);
      }
    }
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success('文件导出成功');
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.response?.data?.error || error.message));
    console.error('导出错误:', error);
  }
};

// 确认编辑操作
const confirmEdit = async () => {
  try {
    let params = {action_type: selectedAction.value};
    if (selectedAction.value === 'custom') {
      if (!customInput.value.trim()) {
        ElMessage.warning('请输入自定义修改内容');
        return;
      }
      params.corrected_text = customInput.value;
    }
    await axios.put(`/api/batch/errors/${currentError.value.id}`, params);
    const index = errorData.value.findIndex(e => e.id === currentError.value.id);
    if (index !== -1) {
      errorData.value[index].status =
          selectedAction.value === 'ignore' ? 'ignored' : 'corrected';
      errorData.value[index].content =
          selectedAction.value === 'accept' ? currentError.value.suggestion :
              selectedAction.value === 'custom' ? customInput.value :
                  currentError.value.content;
    }
    ElMessage.success('修改成功');
    editDialogVisible.value = false;
  } catch (error) {
    console.error('修改失败:', error);
    ElMessage.error(`修改失败: ${error.response?.data?.error || error.message}`);
  }
};

// 文件选择
const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw;
  batchProgress.value = 0; // 重置进度
  showStartProcessButton.value = false; // 隐藏按钮
  uploadFileAction(); // 自动上传文件
};

// 文件上传
const uploadFileAction = async () => {
  if (!file.value) {
    ElMessage.error('请先选择文件');
    return;
  }
  uploading.value = true;
  const formData = new FormData();
  formData.append('file', file.value);
  try {
    const response = await axios.post('/api/batch/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          batchProgress.value = uploadProgress;
        }
      },
    });
    ElMessage.success('文件上传成功！点击处理按钮开始分析');
    showStartProcessButton.value = true;
  } catch (error) {
    ElMessage.error('文件上传失败!');
    console.error(error);
  } finally {
    uploading.value = false;
  }
};

// 开始批处理
const startBatchProcessing = async () => {
  try {
    batchProgress.value = 0; // 重置进度
    processingStarted.value = true; // 标记处理已开始
    ElMessage.info('正在处理，请稍候...');
    monitorProcessingProgress();
    const response = await axios.get('/api/batch/startProcess');
    currentJobId = response.data.id;
    await getErrors(currentJobId);
  } catch (error) {
    console.error('启动批处理失败:', error);
    ElMessage.error('启动批处理失败');
    processingStarted.value = false;
    batchProgress.value = 0;
  }
};

// 监控批处理进度
const monitorProcessingProgress = () => {
  const interval = setInterval(async () => {
    try {
      const response = await axios.get('/api/batch/progress');
      const progress = response.data.progress;
      batchProgress.value = progress;
      console.log(batchProgress.value)
      if (progress >= 100) {
        clearInterval(interval);
        showStartProcessButton.value = false;
        ElMessage.success('批处理完成!');
      }
    } catch (error) {
      console.error('获取批处理进度失败:', error);
      clearInterval(interval);
      processingStarted.value = false;
      batchProgress.value = 0;
      ElMessage.error('获取批处理进度失败');
    }
  }, 10000); // 每10秒检查一次
};

// 处理编辑按钮点击事件
const handleEdit = (index, row) => {
  currentError.value = {...row}; // 深拷贝当前错误数据
  editDialogVisible.value = true; // 打开对话框
};

onMounted(() => {
  getHistoryData();
});
</script>

<style scoped>
/* 全局样式 */
body {
  font-family: Arial, Helvetica, sans-serif;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f4f4f4;
}

.batch-process-page {
  height: 100vh;
  background-color: #f5f7fa;
}

.sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  padding-top: 20px;
}

/* logo 容器 */
.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* logo 图标 */
.logo {
  width: 40px;
  height: 40px;
  background-color: #673ab7;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* logo 图标中的字母 C */
.logo-icon {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

/* logo 文字 */
.logo-text {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.el-menu {
  border-right: none;
  flex-grow: 1;
}

.el-menu-item {
  color: #303133;
}

.el-menu-item.is-active {
  background-color: #8e44ad !important;
  color: #ffffff !important;
}

.user-info {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  margin-right: auto;
  font-weight: 500;
}

.main-content {
  padding: 30px;
}

.main-header {
  margin-bottom: 20px;
}

.main-header h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #303133;
}

.main-header p {
  color: #606266;
  font-size: 14px;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.history-card .card-header span {
  font-size: 16px;
}

.history-card .card-header span {
  font-size: 16px;
}

.history-item {

  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item-info {
  width: 320px;
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.history-item-title {
  font-weight: 500;
  color: #303133;
  min-width: 120px;
}

.history-item-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-end; /* 右对齐 */
  margin-left: 50 %;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-item {
    flex-direction: column;
    align-items: start;
  }

  .history-item-info {
    margin-bottom: 10px;
  }

  .history-item-actions {
    justify-content: flex-start; /* 在小屏幕上左对齐 */
  }
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-demo .el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}

.upload-demo :deep(.el-upload-dragger) {
  padding: 40px 15px;
  background-color: #fafafa;
  border: 1px dashed #d9d9d9;
}

.upload-demo :deep(.el-upload-dragger:hover) {
  border-color: #8e44ad;
}

.upload-demo .el-icon--upload {
  font-size: 50px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.progress-section span {
  font-size: 14px;
  color: #606266;
  min-width: 60px;
}

.el-progress {
  flex-grow: 1;
}

.errors-card .el-button--primary {
  background-color: #8e44ad;
  border-color: #8e44ad;
}

.errors-card .el-button--primary:hover {
  background-color: #7b3a9b;
  border-color: #7b3a9b;
}

.table-scroll-container {
  max-height: 350px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #8e44ad #f1f1f1;
}

.table-scroll-container::-webkit-scrollbar {
  width: 6px;
}

.table-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.table-scroll-container::-webkit-scrollbar-thumb {
  background-color: #8e44ad;
  border-radius: 3px;
}

.dialog-content .label {
  margin-bottom: 5px;
  font-size: 14px;
  color: #909399;
}

.radio-group {
  margin-top: 15px;
}

.custom-input {
  margin-top: 10px;
}

.history-item-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}




</style>