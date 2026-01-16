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
              <el-tag
                :type="getAnnotationStatusType(item.annotationStatus)"
                effect="light"
                size="small"
                class="annotation-status-tag"
              >
                <template v-if="item.annotationStatus === '标注中'">
                  {{ item.annotationStatus }}{{ getAnnotationProgress(item) }}
                </template>
                <template v-else>
                  {{ item.annotationStatus || '未标注' }}
                </template>
              </el-tag>
              <el-button size="small" @click="exportData(item.id)" :icon="Download">导出</el-button>
              <el-button size="small" @click="exportAnnotation(item)" :icon="Download" :disabled="item.annotationStatus === '未标注'">导出标注</el-button>
              <el-button type="primary" size="small" @click="showHistoryErrors(item.id)">查看错误</el-button>
              <el-button size="small" type="danger" @click="handleDelete(item.id)" :icon="Delete">删除</el-button>
            </div>
            <el-tag :type="item.completedAt ? 'success' : 'info'" effect="light" class="completion-status-tag">
              {{ item.completedAt || '未完成' }}
            </el-tag>
          </div>
        </div>
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
          action="/api/batch/upload"
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
      <div class="upload-actions">
        <el-button type="primary" @click="downloadTemplate" :icon="Download">
          下载测试模板
        </el-button>
      </div>
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

      <!-- 进度条 - 只在有进度时显示 -->
      <div v-if="showProgressBar" class="progress-section">
        <span>{{ processingStarted ? '处理进度' : '上传进度' }}</span>
        <el-progress :percentage="batchProgress" :stroke-width="10" striped/>
      </div>

      <!-- 错误数据列表 - 只在查看历史时显示 -->
      <el-card v-if="showErrorsList" class="box-card errors-card">
        <template #header>
          <div class="card-header">
            <span>错误数据列表</span>
            <div class="header-actions">
              <el-button type="primary" @click="exportData">
                <el-icon>
                  <Download/>
                </el-icon>
                导出数据
              </el-button>
              <el-button type="success" @click="enterAnnotation">
                <el-icon>
                  <Edit/>
                </el-icon>
                进入标注
              </el-button>
            </div>
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
            <!-- 第一段代码的列结构 -->
            <el-table-column prop="originalText" label="影像描述" min-width="250" show-overflow-tooltip/>
            <el-table-column prop="original_diagnosis" label="影像诊断" min-width="250" show-overflow-tooltip/>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="handleEdit(scope.$index, scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-pagination
            v-if="totalErrors > 0"
            background
            layout="total, prev, pager, next"
            :total="totalErrors"
            :current-page="currentPageErrors"
            :page-size="pageSizeErrors"
            @current-change="handleErrorPageChange"
            style="margin-top: 20px; text-align: center;"
        />
      </el-card>

      <!-- 错误修改表单 - 第一段代码的修改对话框 -->
      <el-dialog
          v-model="editDialogVisible"
          title="编辑错误数据"
          width="40%"
          :draggable="true"
          :append-to-body="true"
          :modal="false"
      >
        <div class="dialog-content">
          <p class="label">当前错误内容</p>
          <el-input
              v-model="currentError.content"
              type="textarea"
              :rows="5"
              readonly
          />
          <p class="label">系统建议修改</p>
          <el-input
              v-model="currentError.suggestion"
              type="textarea"
              :rows="5"
              readonly
          />
          <div class="radio-group">
            <el-radio v-model="selectedAction" label="accept">接受修改建议</el-radio>
            <el-radio v-model="selectedAction" label="custom">自定义修改</el-radio>
            <el-radio v-model="selectedAction" label="ignore">标记为"非错误"</el-radio>
          </div>
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

      <!-- 查看错误数据对话框 - 第一段代码的查看对话框 -->
      <el-dialog
          v-model="editInfoVisible"
          title="查看错误数据"
          width="40%"
          :draggable="true"
          :append-to-body="true"
      >
        <div class="dialog-content">
          <p class="label">影像描述</p>
          <el-input
              v-model="currentError.originalText"
              type="textarea"
              :rows="5"
              readonly
          />
          <p class="label">影像诊断</p>
          <div class="diagnosis-content" v-html="formattedDiagnosis"></div>

          <p class="label">生成诊断</p>
          <el-input
              v-model="currentError.genDiagnosis"
              type="textarea"
              :rows="5"
              readonly
          />
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="editInfoVisible = false">关闭</el-button>
            <el-button type="primary" @click="openAnnotationPage">进入标注</el-button>
          </span>
        </template>
      </el-dialog>

    </el-main>
  </el-container>
</template>

<script setup>
import {onMounted, ref, computed, onUnmounted} from 'vue';
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
  Edit,
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
const totalRecords = ref(0);
const currentPage = ref(1);
const pageSize = ref(7);

// 状态控制变量
const isViewingHistory = ref(false); // 标识是否在查看历史记录

// 计算属性：控制进度条显示
const showProgressBar = computed(() => {
  return uploading.value || processingStarted.value || batchProgress.value > 0;
});

// 计算属性：控制错误列表显示 - 在手动查看历史或批处理完成后显示
const showErrorsList = computed(() => {
  return isViewingHistory.value || (currentJobId.value && errorData.value.length > 0);
});

const errorData = ref([]);
const totalErrors = ref(0);
const currentPageErrors = ref(1);
const pageSizeErrors = ref(7);

// 第一段代码中的对话框状态
const editDialogVisible = ref(false);
const editInfoVisible = ref(false);
const currentError = ref({});
const selectedAction = ref('accept');
const customInput = ref('');

// 第一段代码中的诊断格式化
const formattedDiagnosis = computed(() => {
  if (!currentError.value.original_diagnosis) return '';

  const text = currentError.value.original_diagnosis;

  return text.replace(
      /\[(.*?)\]/g,
      (match, content) => `<span class="error-text" onclick="window.showErrorDetail('${content}')">${match}</span>`
  );
});

const showErrorDetail = (errorText) => {
  console.log('Clicked error text:', errorText);
  if (currentError.value) {
    editDialogVisible.value = true;
  }
};

const handleMenuSelect = (index) => {
  if (index === 'chat') {
    router.push('/medllm');
  }
};

const handleUserCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile');
  } else if (command === 'logout') {
    localStorage.removeItem('token');
    router.push('/auth');
  }
};

// 第二段代码的文件处理逻辑
const handleFileChange = (uploadFile) => {
  console.log('文件选择事件触发:', uploadFile);

  // 先保存文件，再重置其他状态
  const selectedFile = uploadFile.raw;

  // 重置状态但不清空文件
  batchProgress.value = 0;
  processingStarted.value = false;
  showStartProcessButton.value = false;
  isViewingHistory.value = false;
  uploading.value = false;
  errorData.value = [];
  totalErrors.value = 0;

  // 设置文件并上传
  file.value = selectedFile;
  console.log('设置后的 file.value:', file.value);

  // 立即上传文件
  uploadFileAction();
};

const handleUploadProgress = (event, uploadFile) => {
  if (event.total) {
    const uploadProgress = Math.round((event.loaded * 100) / event.total);
    batchProgress.value = uploadProgress;
  }
};

const handleUploadSuccess = (response) => {
  console.log('Element Plus 上传成功回调:', response);
  ElMessage.success('文件上传成功！点击处理按钮开始分析');
  showStartProcessButton.value = true;
  batchProgress.value = 0;
};

const handleUploadError = () => {
  ElMessage.error('文件上传失败');
  uploading.value = false;
};

const uploadFileAction = async () => {
  console.log('开始上传文件:', file.value);
  if (!file.value) {
    console.error('没有选择文件');
    ElMessage.error('请先选择文件');
    return;
  }

  uploading.value = true;
  batchProgress.value = 0;
  const formData = new FormData();
  formData.append('file', file.value);

  try {
    console.log('正在上传文件...');
    const response = await axios.post('/api/batch/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          batchProgress.value = uploadProgress;
          console.log('上传进度:', uploadProgress);
        }
      },
    });

    console.log('文件上传成功:', response.data);
    ElMessage.success('文件上传成功！点击处理按钮开始分析');
    showStartProcessButton.value = true;
    batchProgress.value = 0; // 上传完成后重置进度条
  } catch (error) {
    console.error('文件上传失败:', error);
    ElMessage.error('文件上传失败: ' + (error.response?.data?.error || error.message));
  } finally {
    uploading.value = false;
  }
};

const startBatchProcessing = async () => {
  try {
    // 重置所有状态
    resetProcessingState();
    processingStarted.value = true;
    batchProgress.value = 0;

    ElMessage.info('正在启动批处理...');

    const response = await axios.get('/api/batch/startProcess', {
      timeout: 60000 // 60秒超时，给启动过程更多时间
    });
    
    currentJobId.value = response.data.id;
    
    // 启动进度监控
    monitorProcessingProgress();
    
    ElMessage.success('批处理已启动，正在处理中...');
  } catch (error) {
    console.error('启动批处理失败:', error);
    ElMessage.error('启动批处理失败');
    resetToInitialState();
  }
};

const monitorProcessingProgress = () => {
  let progressInterval = null;
  let checkCount = 0;
  const maxChecks = 3600; // 增加到3600次检查（10小时，每10秒检查一次）
  let lastProgress = 0;
  let noProgressCount = 0;

  const checkProgress = async () => {
    try {
      const response = await axios.get('/api/batch/progress');
      const progress = response.data.progress;
      batchProgress.value = progress;

      // 检查进度是否停滞
      if (progress === lastProgress) {
        noProgressCount++;
        if (noProgressCount > 60) { // 10分钟没有进度变化
          ElMessage.warning('批处理进度停滞，可能正在处理大量数据，请耐心等待');
          noProgressCount = 0; // 重置计数器
        }
      } else {
        noProgressCount = 0;
        lastProgress = progress;
      }

      if (progress >= 100) {
        clearInterval(progressInterval);
        handleProcessingComplete();
      }

      if (checkCount++ > maxChecks) {
        clearInterval(progressInterval);
        ElMessage.warning('处理超时，请检查后台状态');
        resetToInitialState();
      }
    } catch (error) {
      console.error('获取批处理进度失败:', error);
      clearInterval(progressInterval);
      resetToInitialState();
      ElMessage.error('获取批处理进度失败');
    }
  };

  progressInterval = setInterval(checkProgress, 10000); // 每10秒检查一次进度
  checkProgress();
};

const handleProcessingComplete = async () => {
  try {
    // 保存当前任务ID，因为resetToInitialState会清空它
    const completedJobId = currentJobId.value;
    
    // 重置UI状态到初始状态
    resetToInitialState();
    
    // 恢复当前任务ID
    currentJobId.value = completedJobId;

    // 刷新历史记录
    await getHistoryData();

    // 自动显示当前批处理任务的错误数据
    if (completedJobId) {
      isViewingHistory.value = true;
      await getErrors(completedJobId);
    }

    ElMessage.success('批处理完成! 已显示错误数据');

  } catch (error) {
    console.error('完成处理时出错:', error);
    ElMessage.error('完成处理时出错');
  }
};

const resetProcessingState = () => {
  processingStarted.value = false;
  showStartProcessButton.value = false;
  batchProgress.value = 0;
};

const resetToInitialState = () => {
  batchProgress.value = 0;
  processingStarted.value = false;
  showStartProcessButton.value = false;
  isViewingHistory.value = false;
  uploading.value = false;

  // 清除文件状态
  file.value = null;
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }

  // 清除错误数据
  errorData.value = [];
  totalErrors.value = 0;
};

const handlePageChange = (page) => {
  currentPage.value = page;
  getHistoryData();
};

const getHistoryData = async () => {
  try {
    const response = await axios.get('/api/batch/jobs', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
      },
    });
    const {data, total} = response.data;
    historyData.value = data;
    totalRecords.value = total;
  } catch (error) {
    ElMessage.error('获取历史数据失败!');
    console.error(error);
  }
};

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

// 显示历史错误 - 第二段代码的逻辑，只有这里可以查看错误数据
const showHistoryErrors = async (jobId) => {
  currentJobId.value = jobId;
  isViewingHistory.value = true; // 设置为查看历史状态
  await getErrors(jobId);
};

const getErrors = async (jobId) => {
  // 在手动查看历史或批处理完成后都可以获取错误数据
  if (!isViewingHistory.value && !currentJobId.value) {
    console.log('非查看历史状态且无当前任务ID，不获取错误数据');
    return;
  }

  try {
    const response = await axios.get(`/api/batch/jobs/${jobId}/errors`, {
      params: {
        page: currentPageErrors.value,
        page_size: pageSizeErrors.value,
      },
    });
    const {data, total} = response.data;
    errorData.value = data;
    totalErrors.value = total;
  } catch (error) {
    ElMessage.error('获取错误数据失败!');
    console.error(error);
  }
};

const handleErrorPageChange = (page) => {
  currentPageErrors.value = page;
  getErrors(currentJobId.value);
};

// 第一段代码中的处理编辑逻辑 - 打开查看对话框
const handleEdit = (index, row) => {
  currentError.value = {...row};
  editInfoVisible.value = true;
};

// 第一段代码中的标注页面跳转
const openAnnotationPage = () => {
  if (!currentJobId.value) {
    ElMessage.warning('请先选择或处理一个批次');
    return;
  }
  router.push({
    path: '/annotation',
    query: {
      jobId: currentJobId.value
    }
  });
};

// 第一段代码中的修改确认逻辑
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

const exportData = async (job_id) => {
  // 如果没有传入job_id且当前不是在查看历史，则提示用户
  if (!Number.isInteger(job_id) && !isViewingHistory.value) {
    ElMessage.warning('请先选择要导出的历史记录');
    return;
  }

  // 使用传入的job_id或当前查看的历史记录ID
  const targetJobId = Number.isInteger(job_id) ? job_id : currentJobId.value;

  try {
    const response = await axios.get(`/api/batch/jobs/${targetJobId}/export`, {
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

// 第一段代码中的进入标注功能
const enterAnnotation = () => {
  if (!currentJobId.value) {
    ElMessage.warning('请先选择或处理一个批次');
    return;
  }
  router.push({
    path: '/annotation',
    query: {
      jobId: currentJobId.value
    }
  });
};

// 第一段代码中的标注状态相关功能
const getAnnotationStatusType = (status) => {
  switch (status) {
    case '标注完成':
      return 'success';
    case '未标注':
      return 'info';
    case '标注中':
      return 'warning';
    default:
      return 'info';
  }
};

const exportAnnotation = async (item) => {
  if (item.annotationStatus === '未标注') return;
  try {
    const response = await axios.get(`/api/batch/jobs/${item.id}/export-annotation`, {
      responseType: 'blob'
    });
    const fileName = `annotation_job_${item.id}.xlsx`;
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success('标注内容导出成功');
  } catch (error) {
    ElMessage.error('导出标注失败: ' + (error.response?.data?.error || error.message));
    console.error('导出标注错误:', error);
  }
};

const getAnnotationProgress = (item) => {
  if (item.annotationStatus === '标注中' && item.errors > 0 && item.annotatedCount !== undefined) {
    const percent = Math.round((item.annotatedCount / item.errors) * 100);
    return percent > 0 ? `${percent}%` : '';
  }
  return '';
};

const downloadTemplate = async () => {
  try {
    const response = await axios.get('/api/batch/download-template', {
      responseType: 'blob'
    });
    
    const contentDisposition = response.headers['content-disposition'];
    let fileName = 'test.xlsx';
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
    ElMessage.success('模板下载成功');
  } catch (error) {
    ElMessage.error('下载模板失败: ' + (error.response?.data?.error || error.message));
    console.error('下载模板错误:', error);
  }
};

onMounted(() => {
  getHistoryData();
  // 第一段代码中的全局函数
  window.showErrorDetail = (errorText) => {
    console.log('Global showErrorDetail called with:', errorText);
    if (currentError.value) {
      editDialogVisible.value = true;
    }
  };
  
  // 将 ElMessage 暴露到全局，供 axios 拦截器使用
  window.ElMessage = ElMessage;
  
  // 定期检查token有效性（每5分钟检查一次）
  const tokenCheckInterval = setInterval(async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        // 发送一个简单的请求来验证token
        await axios.get('/api/auth/verify');
      } catch (error) {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          clearInterval(tokenCheckInterval);
          ElMessage.error('登录已过期，请重新登录');
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          setTimeout(() => {
            window.location.href = '/auth';
          }, 1500);
        }
      }
    }
  }, 5 * 60 * 1000); // 5分钟
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(tokenCheckInterval);
  });
});

onUnmounted(() => {
  delete window.showErrorDetail;
});
</script>


<style scoped>
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

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
}

.logo {
  width: 40px;
  height: 40px;
  background-color: #673ab7;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo-icon {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

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

.user-info {
  margin-top: auto;
  padding: 20px;
  border-top: 1px solid #e6e6e6;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.main-header {
  margin-bottom: 20px;
}

.main-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.main-header p {
  color: #909399;
  font-size: 14px;
}

.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-scroll-container {
  /* 移除高度限制，让分页正常工作 */
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  gap: 16px;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item-info {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.history-item-info > span {
  white-space: nowrap;
}

.history-item-title {
  font-weight: 500;
  color: #303133;
}

.history-item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: center;
  flex-wrap: wrap;
}

.upload-demo {
  margin: 20px 0;
}

.upload-actions {
  margin: 20px 0;
}

.progress-section {
  margin: 20px 0;
}

.errors-card {
  margin-top: 20px;
}

.table-scroll-container {
  margin-top: 10px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.diagnosis-content {
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 100px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.error-text {
  color: #f56c6c;
  cursor: pointer;
  text-decoration: underline;
}

.error-text:hover {
  opacity: 0.8;
}

.error-detail {
  padding: 20px;
}

.error-detail p {
  margin-bottom: 15px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .el-aside {
    width: 64px !important;
  }

  .logo-text,
  .username,
  .el-menu-item span {
    display: none;
  }

  .logo-container {
    justify-content: center;
    padding: 10px;
  }

  .user-info {
    padding: 10px;
  }

  .dropdown-trigger {
    justify-content: center;
  }

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .history-item-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .annotation-status-tag {
    align-self: flex-start;
    margin-top: 4px;
  }

  .history-item-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 6px;
  }

  .completion-status-tag {
    align-self: flex-start;
    margin-top: 8px;
  }

  .el-dialog {
    width: 90% !important;
  }
}

/* 修改错误文本样式，确保在v-html中生效 */
:deep(.error-text) {
  color: #f56c6c !important;
  cursor: pointer !important;
  text-decoration: underline;
}

:deep(.error-text:hover) {
  opacity: 0.8;
}

/* 关闭居中定位、设置左右位置 */
.leftDialog {
  top: 15vh !important;
  left: 5vw !important;
  margin: 0 !important;
  transform: none !important;
  position: fixed !important;
  z-index: 2000;
}

.rightDialog {
  top: 15vh !important;
  left: 52vw !important; /* 40%宽度 + 7%间距 */
  margin: 0 !important;
  transform: none !important;
  position: fixed !important;
  z-index: 2001;
}

.annotation-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.annotation-column {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.annotation-column h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}

.text-content {
  max-height: 500px;
  overflow-y: auto;
}

.paragraph {
  padding: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.paragraph:hover {
  background-color: #f5f7fa;
}

.paragraph.selected {
  background-color: v-bind('selectedColor');
  color: white;
}

.annotation-tools {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 10px;
}

.annotation-actions {
  display: flex;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.annotation-status-tag {
  min-width: 80px;
  text-align: center;
  flex-shrink: 0;
  white-space: nowrap;
}

.completion-status-tag {
  min-width: 120px;
  text-align: center;
  flex-shrink: 0;
}

</style>