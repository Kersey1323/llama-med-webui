<template>
  <div class="annotation-page">
    <div class="annotation-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <h2>标注对应关系</h2>
        <div class="progress-info">
          <span class="progress-text">{{ progressText }}</span>
          <el-progress 
            :percentage="annotationProgress" 
            :stroke-width="8"
            :show-text="false"
            style="width: 100px; margin-left: 10px;"
          />
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="saveAllAnnotations">保存所有标注</el-button>
      </div>
    </div>

    <div class="annotation-main">
      <div class="error-list">
        <h3>错误数据列表</h3>
        <div class="error-list-table">
          <el-table
              :data="errorList"
              style="width: 100%"
              highlight-current-row
          >
            <el-table-column prop="row" label="行号" width="80"/>
            <el-table-column prop="type" label="错误类型" width="80"/>
            <el-table-column prop="originalText" label="影像描述" min-width="100" show-overflow-tooltip/>
            <el-table-column prop="original_diagnosis" label="影像诊断" min-width="100" show-overflow-tooltip/>
            <el-table-column label="标注状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.annotated ? 'success' : 'info'">
                  {{ scope.row.annotated ? '已标注' : '未标注' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button
                    v-if="!scope.row.annotated"
                    type="primary"
                    size="small"
                    @click="startAnnotation(scope.$index)"
                >
                  进行标注
                </el-button>
                <el-button
                    v-else
                    type="success"
                    size="small"
                    @click="viewAnnotation(scope.$index)"
                >
                  查看
                </el-button>
                <el-button
                    v-if="scope.row.annotated"
                    type="warning"
                    size="small"
                    @click="resetAnnotation(scope.$index)"
                >
                  撤销
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div class="annotation-content" v-if="currentError">
        <div class="annotation-panel">
          <div class="panel-header">
            <h3>影像描述</h3>
            <div class="panel-tools">
              <div class="color-palette">
                <div
                    v-for="(color, index) in colorPalette"
                    :key="index"
                    class="color-option"
                    :class="{ 'active': selectedColor === color }"
                    :style="{ backgroundColor: color }"
                    @click="selectColor(index)"
                ></div>
              </div>
            </div>
          </div>
          <div class="panel-content" ref="descriptionPanel">
            <div
                v-for="(paragraph, index) in descriptionParagraphs"
                :key="'desc-' + index"
                class="text-block"
                :class="{
                  'hover': hoveredDescriptionIndex === index,
                  'selected': selectedDescriptionIndices.includes(index),
                  'annotated': isDescriptionAnnotated(index)
                }"
                :style="getAnnotationStyle('description', index)"
                @mouseenter="hoveredDescriptionIndex = index"
                @mouseleave="hoveredDescriptionIndex = -1"
                @click="toggleDescriptionSelection(index)"
            >
              {{ paragraph }}
              <span class="punctuation" v-if="index < descriptionParagraphs.length - 1">,</span>
            </div>
          </div>
        </div>

        <div class="annotation-panel">
          <div class="panel-header">
            <h3>影像诊断</h3>
            <div class="panel-tools">
              <div class="color-palette">
                <div
                    v-for="(color, index) in colorPalette"
                    :key="index"
                    class="color-option"
                    :class="{ 'active': selectedColor === color }"
                    :style="{ backgroundColor: color }"
                    @click="selectColor(index)"
                ></div>
              </div>
            </div>
          </div>
          <div class="panel-content" ref="diagnosisPanel">
            <div
                v-for="(paragraph, index) in diagnosisParagraphs"
                :key="'diag-' + index"
                class="text-block"
                :class="{
                  'hover': hoveredDiagnosisIndex === index,
                  'selected': selectedDiagnosisIndices.includes(index),
                  'annotated': isDiagnosisAnnotated(index)
                }"
                :style="getAnnotationStyle('diagnosis', index)"
                @mouseenter="hoveredDiagnosisIndex = index"
                @mouseleave="hoveredDiagnosisIndex = -1"
                @click="toggleDiagnosisSelection(index)"
            >
              {{ paragraph }}
              <span class="punctuation" v-if="index < diagnosisParagraphs.length - 1">,</span>
            </div>
          </div>
          <div class="panel-actions">
            <el-button-group>
              <el-button @click="clearSelection">清除选择</el-button>
              <el-button 
                  type="primary" 
                  @click="saveAnnotationGroup"
                  :disabled="selectedDescriptionIndices.length === 0 || selectedDiagnosisIndices.length === 0"
              >
                确认当前标注组
              </el-button>
              <el-button type="success" @click="saveCurrentErrorAnnotations">保存当前标注</el-button>
              <el-button type="warning" @click="nextError" :disabled="!hasNextError">下一个</el-button>
            </el-button-group>
          </div>
        </div>
      </div>
    </div>

    <div class="annotation-list" v-if="currentError" >
      <h3>当前错误已保存的标注组</h3>
      <el-table :data="currentAnnotations" style="width: 100%">
        <el-table-column label="描述段落" prop="descriptionText" />
        <el-table-column label="诊断段落" prop="diagnosisText" />
        <el-table-column label="颜色">
          <template #default="scope">
            <div class="color-preview" :style="{ backgroundColor: scope.row.color }"></div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
                type="danger"
                size="small"
                @click="deleteAnnotation(scope.$index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from '../utils/axios';

const route = useRoute();
const router = useRouter();

// 状态变量
const errorList = ref([]);
const totalErrors = ref(0);
const currentPage = ref(1);
const pageSize = ref(7);
const currentErrorIndex = ref(-1);
const currentError = ref(null);
const descriptionParagraphs = ref([]);
const diagnosisParagraphs = ref([]);
const selectedColor = ref('rgba(255, 193, 7, 0.5)'); // 黄色
const selectedDescriptionIndices = ref([]);
const selectedDiagnosisIndices = ref([]);
const hoveredDescriptionIndex = ref(-1);
const hoveredDiagnosisIndex = ref(-1);
const currentAnnotations = ref([]);

// 预定义颜色数组
const colorPalette = [
  'rgba(255, 193, 7, 0.5)',   // 黄色
  'rgba(220, 53, 69, 0.5)',   // 红色
  'rgba(13, 110, 253, 0.5)',  // 蓝色
  'rgba(25, 135, 84, 0.5)',   // 绿色
  'rgba(111, 66, 193, 0.5)',  // 紫色
  'rgba(253, 126, 20, 0.5)'   // 橙色
];

let currentColorIndex = 0;

// 计算属性
const hasNextError = computed(() => {
  return currentErrorIndex.value < errorList.value.length - 1;
});

const annotationProgress = computed(() => {
  if (errorList.value.length === 0) return 0;
  const annotatedCount = errorList.value.filter(error => error.annotated).length;
  return Math.round((annotatedCount / errorList.value.length) * 100);
});

const progressText = computed(() => {
  if (errorList.value.length === 0) return '0/0';
  const annotatedCount = errorList.value.filter(error => error.annotated).length;
  return `${annotatedCount}/${errorList.value.length}`;
});

// 初始化数据
onMounted(async () => {
  // 将 ElMessage 暴露到全局，供 axios 拦截器使用
  window.ElMessage = ElMessage;
  
  const { jobId } = route.query;
  if (!jobId) {
    ElMessage.error('缺少批次ID');
    router.back();
    return;
  }
  await loadErrorList(jobId);
  
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

// 加载错误列表
const loadErrorList = async (jobId) => {
  try {
    const response = await axios.get(`/api/batch/jobs/${jobId}/errors`, {
      params: {
        page: 1,
        page_size: 1000 // 获取全部错误数据
      }
    });
    errorList.value = response.data.data.map(error => ({
      ...error,
      annotated: Boolean(error.annotated)
    }));
    // 找到第一个未标注的数据
    const firstUnannotatedIndex = errorList.value.findIndex(error => !error.annotated);
    if (firstUnannotatedIndex !== -1) {
      currentErrorIndex.value = firstUnannotatedIndex;
      loadCurrentError();
    }
  } catch (error) {
    ElMessage.error('加载错误列表失败');
    console.error(error);
  }
};

// 开始标注
const startAnnotation = (index) => {
  currentErrorIndex.value = index;
  loadCurrentError();
  // 确保页面内容显示
  nextTick(() => {
    if (currentError.value) {
      currentError.value = { ...currentError.value };
    }
  });
};

// 查看标注
const viewAnnotation = async (index) => {
  currentErrorIndex.value = index;
  await loadCurrentError();
  await loadAnnotationGroups();
  // 确保页面内容显示
  nextTick(() => {
    if (currentError.value) {
      currentError.value = { ...currentError.value };
    }
  });
};

// 撤销标注
const resetAnnotation = async (index) => {
  try {
    const errorId = errorList.value[index].id;
    await axios.post(`/api/annotation/error/${errorId}/reset`);
    ElMessage.success('标注重置成功');
    // 更新列表状态
    errorList.value[index].annotated = false;
    // 如果当前正在查看这个错误，清空标注
    if (currentErrorIndex.value === index) {
      currentAnnotations.value = [];
    }
  } catch (error) {
    ElMessage.error('标注重置失败');
    console.error(error);
  }
};

// 加载标注组
const loadAnnotationGroups = async () => {
  try {
    const errorId = currentError.value.id;
    const response = await axios.get(`/api/annotation/error/${errorId}/groups`);
    if (response.data.success) {
      currentAnnotations.value = response.data.data;
    }
  } catch (error) {
    console.error('加载标注组失败:', error);
  }
};

// 加载当前错误
const loadCurrentError = () => {
  currentError.value = errorList.value[currentErrorIndex.value];
  // 按标点符号分割文本
  descriptionParagraphs.value = splitTextByPunctuation(currentError.value.originalText);
  diagnosisParagraphs.value = splitTextByPunctuation(currentError.value.original_diagnosis);
  currentAnnotations.value = [];
  clearSelection();
  // 重置颜色索引
  currentColorIndex = 0;
  selectedColor.value = colorPalette[currentColorIndex];
};

// 按标点符号分割文本
const splitTextByPunctuation = (text) => {
  if (!text) return [];
  // 按逗号、分号、句号等标点符号分割
  return text.split(/[,，;；.。!！?？]/).filter(p => p.trim());
};

// 方法
const goBack = () => {
  router.back();
};

const toggleDescriptionSelection = (index) => {
  const idx = selectedDescriptionIndices.value.indexOf(index);
  if (idx > -1) {
    selectedDescriptionIndices.value.splice(idx, 1);
  } else {
    selectedDescriptionIndices.value.push(index);
  }
};

const toggleDiagnosisSelection = (index) => {
  const idx = selectedDiagnosisIndices.value.indexOf(index);
  if (idx > -1) {
    selectedDiagnosisIndices.value.splice(idx, 1);
  } else {
    selectedDiagnosisIndices.value.push(index);
  }
};

const clearSelection = () => {
  selectedDescriptionIndices.value = [];
  selectedDiagnosisIndices.value = [];
};

const isDescriptionAnnotated = (index) => {
  return currentAnnotations.value.some(a => a.descriptionIndices.includes(index));
};

const isDiagnosisAnnotated = (index) => {
  return currentAnnotations.value.some(a => a.diagnosisIndices.includes(index));
};

const getAnnotationStyle = (type, index) => {
  const annotation = currentAnnotations.value.find(a => 
    type === 'description' ? a.descriptionIndices.includes(index) : a.diagnosisIndices.includes(index)
  );
  if (annotation) {
    return { backgroundColor: annotation.color };
  }
  if (type === 'description' && selectedDescriptionIndices.value.includes(index)) {
    return { backgroundColor: selectedColor.value };
  }
  if (type === 'diagnosis' && selectedDiagnosisIndices.value.includes(index)) {
    return { backgroundColor: selectedColor.value };
  }
  return {};
};

const saveAnnotationGroup = () => {
  if (selectedDescriptionIndices.value.length === 0 || selectedDiagnosisIndices.value.length === 0) {
    ElMessage.warning('请先选择要关联的段落');
    return;
  }

  // 合并选中的描述段落
  const descriptionText = selectedDescriptionIndices.value
    .sort((a, b) => a - b)
    .map(index => descriptionParagraphs.value[index])
    .join(', ');

  // 合并选中的诊断段落
  const diagnosisText = selectedDiagnosisIndices.value
    .sort((a, b) => a - b)
    .map(index => diagnosisParagraphs.value[index])
    .join(', ');

  const annotation = {
    descriptionIndices: [...selectedDescriptionIndices.value],
    diagnosisIndices: [...selectedDiagnosisIndices.value],
    descriptionText: descriptionText,
    diagnosisText: diagnosisText,
    color: selectedColor.value
  };

  currentAnnotations.value.push(annotation);
  ElMessage.success('标注组已保存');
  clearSelection();
  
  // 自动切换到下一个颜色
  currentColorIndex = (currentColorIndex + 1) % colorPalette.length;
  selectedColor.value = colorPalette[currentColorIndex];
};

const deleteAnnotation = (index) => {
  currentAnnotations.value.splice(index, 1);
  ElMessage.success('标注已删除');
};

const saveCurrentErrorAnnotations = async () => {
  try {
    const errorId = currentError.value.id;
    const annotationGroups = currentAnnotations.value.map(group => ({
      descriptionIndices: group.descriptionIndices,
      diagnosisIndices: group.diagnosisIndices,
      descriptionText: group.descriptionText,
      diagnosisText: group.diagnosisText,
      color: group.color
    }));

    await axios.post(`/api/annotation/error/${errorId}/groups`, {
      annotationGroups: annotationGroups
    });

    // 更新列表状态
    errorList.value[currentErrorIndex.value].annotated = true;
    ElMessage.success('当前错误标注已保存');
    
    // 自动跳转到下一个未标注的记录
    await jumpToNextUnannotated();
  } catch (error) {
    ElMessage.error('保存失败');
    console.error(error);
  }
};

// 跳转到下一个未标注的记录
const jumpToNextUnannotated = async () => {
  const nextUnannotatedIndex = errorList.value.findIndex((error, index) => 
    index > currentErrorIndex.value && !error.annotated
  );
  
  if (nextUnannotatedIndex !== -1) {
    currentErrorIndex.value = nextUnannotatedIndex;
    loadCurrentError();
    ElMessage.info('已自动跳转到下一个未标注的记录');
  } else {
    // 如果没有下一个未标注的记录，检查是否还有未标注的记录
    const anyUnannotated = errorList.value.some(error => !error.annotated);
    if (!anyUnannotated) {
      ElMessage.success('所有记录都已标注完成！');
    } else {
      // 从头开始找第一个未标注的记录
      const firstUnannotatedIndex = errorList.value.findIndex(error => !error.annotated);
      if (firstUnannotatedIndex !== -1) {
        currentErrorIndex.value = firstUnannotatedIndex;
        loadCurrentError();
        ElMessage.info('已跳转到第一个未标注的记录');
      }
    }
  }
};

const saveAllAnnotations = async () => {
  try {
    // TODO: 实现保存到后端的逻辑
    ElMessage.success('所有标注已保存');
  } catch (error) {
    ElMessage.error('保存失败');
  }
};

const nextError = () => {
  if (currentErrorIndex.value < errorList.value.length - 1) {
    currentErrorIndex.value++;
    loadCurrentError();
  }
};

const selectColor = (index) => {
  currentColorIndex = index;
  selectedColor.value = colorPalette[index];
};
</script>

<style scoped>
.annotation-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  padding: 20px;
  overflow: hidden;
}

.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.annotation-main {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.error-list {
  width: 40%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.error-list h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  flex-shrink: 0;
}

.error-list-table {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.error-list-table .el-table {
  height: 100%;
}

.error-list-table .el-table__body-wrapper {
  overflow-y: auto !important;
  max-height: calc(100vh - 300px);
}

.annotation-content {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
  min-height: 0;
}

.annotation-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
}

.panel-content {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  min-height: 0;
}

.panel-actions {
  padding: 15px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.text-block {
  padding: 5px;
  margin-bottom: 5px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
  position: relative;
  display: inline-block;
  //margin-right: 4px;
}

.text-block:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.text-block.hover {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
}

.text-block.selected {
  border-color: #409eff;
}

.text-block.annotated {
  border-left: 3px solid #409eff;
}

.punctuation {
  color: #909399;
  margin: 0 2px;
}

.color-palette {
  display: flex;
  gap: 8px;
}

.color-option {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.active {
  border-color: #303133;
  transform: scale(1.1);
}

.annotation-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-top: 20px;
  flex-shrink: 0;
}

.annotation-list h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

/* 确保表格内容可以滚动 */
:deep(.el-table__body-wrapper) {
  overflow-y: auto !important;
}

:deep(.el-table__fixed-body-wrapper) {
  overflow-y: auto !important;
}
</style> 