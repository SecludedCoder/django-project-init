# Django分层架构实例说明：Excel文件处理

## 一、功能描述

实现一个Excel文件上传、解析和数据展示功能：
1. 用户通过Web界面上传Excel文件
2. 后端解析Excel内容
3. 将数据保存到数据库
4. 前端页面展示处理结果

## 二、核心Python算法

假设已有以下Excel处理核心算法：

```python
import pandas as pd

def process_excel(file_path):
    """Excel处理核心算法"""
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 数据处理
    processed_data = {
        'total_rows': len(df),
        'columns': df.columns.tolist(),
        'data': df.to_dict('records')
    }
    
    return processed_data
```

## 三、分层实现

### 3.1 Models层
```python
# models.py
from django.db import models

class ExcelFile(models.Model):
    """Excel文件记录"""
    file = models.FileField(upload_to='excels/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

class ExcelData(models.Model):
    """Excel数据记录"""
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    row_data = models.JSONField()  # 存储每行数据
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
```

### 3.2 Services层
```python
# services/excel_service.py
from typing import Dict, Any
from .models import ExcelFile, ExcelData

class ExcelService:
    """Excel处理服务"""
    
    def handle_uploaded_file(self, file_obj) -> Dict[str, Any]:
        """处理上传的Excel文件"""
        # 保存文件
        excel_file = ExcelFile.objects.create(file=file_obj)
        
        try:
            # 调用核心算法
            result = process_excel(excel_file.file.path)
            
            # 保存处理后的数据
            self._save_excel_data(excel_file, result['data'])
            
            # 更新处理状态
            excel_file.processed = True
            excel_file.save()
            
            return {
                'success': True,
                'file_id': excel_file.id,
                'total_rows': result['total_rows'],
                'columns': result['columns']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_excel_data(self, excel_file: ExcelFile, data: list):
        """保存Excel数据"""
        ExcelData.objects.bulk_create([
            ExcelData(excel_file=excel_file, row_data=row)
            for row in data
        ])
    
    def get_excel_data(self, file_id: int) -> Dict[str, Any]:
        """获取Excel数据"""
        try:
            excel_file = ExcelFile.objects.get(id=file_id)
            data = ExcelData.objects.filter(excel_file=excel_file)
            
            return {
                'success': True,
                'data': [item.row_data for item in data]
            }
        except ExcelFile.DoesNotExist:
            return {
                'success': False,
                'error': 'File not found'
            }
```

### 3.3 Views层
```python
# views.py
from django.views import View
from django.http import JsonResponse
from .services.excel_service import ExcelService

class ExcelUploadView(View):
    """Excel上传视图"""
    
    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            })
        
        excel_service = ExcelService()
        result = excel_service.handle_uploaded_file(request.FILES['file'])
        return JsonResponse(result)

class ExcelDataView(View):
    """Excel数据视图"""
    
    def get(self, request, file_id):
        excel_service = ExcelService()
        result = excel_service.get_excel_data(file_id)
        return JsonResponse(result)
```

### 3.4 Templates层
```html
<!-- templates/excel_upload.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <div class="upload-section">
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" id="excelFile" accept=".xlsx,.xls">
            <button type="submit">Upload</button>
        </form>
    </div>
    
    <div id="resultSection" style="display: none;">
        <h3>Processing Results</h3>
        <table id="dataTable" class="table">
            <thead>
                <tr id="headerRow"></tr>
            </thead>
            <tbody id="dataBody"></tbody>
        </table>
    </div>
</div>

{% block extra_js %}
<script>
document.getElementById('uploadForm').onsubmit = async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('file', document.getElementById('excelFile').files[0]);
    
    try {
        const response = await fetch('/api/excel/upload/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            // 获取并显示数据
            await loadExcelData(result.file_id);
        } else {
            alert('Upload failed: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error);
    }
};

async function loadExcelData(fileId) {
    const response = await fetch(`/api/excel/data/${fileId}/`);
    const result = await response.json();
    
    if (result.success) {
        displayData(result.data);
    }
}

function displayData(data) {
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';
    
    // 显示表头
    const headerRow = document.getElementById('headerRow');
    headerRow.innerHTML = Object.keys(data[0])
        .map(key => `<th>${key}</th>`)
        .join('');
    
    // 显示数据
    const dataBody = document.getElementById('dataBody');
    dataBody.innerHTML = data
        .map(row => `
            <tr>
                ${Object.values(row)
                    .map(value => `<td>${value}</td>`)
                    .join('')}
            </tr>
        `)
        .join('');
}
</script>
{% endblock %}
{% endblock %}
```

## 四、开发顺序和重点

### 4.1 开发顺序
1. **Models层**
   - 设计数据模型
   - 定义字段和关系
   - 创建数据库迁移

2. **Services层**
   - 集成核心算法
   - 实现数据处理逻辑
   - 处理文件上传逻辑

3. **Views层**
   - 实现API接口
   - 处理请求响应
   - 调用服务层方法

4. **Templates层**
   - 创建上传界面
   - 实现数据展示
   - 添加交互功能

### 4.2 开发重点

#### Models层重点
- 合理设计文件存储字段
- 使用JSONField存储灵活数据
- 添加必要的索引

#### Services层重点
- 错误处理和异常捕获
- 文件处理的安全性
- 大数据量的性能优化

#### Views层重点
- 请求验证
- 响应格式统一
- 错误信息处理

#### Templates层重点
- 文件上传交互
- 数据展示格式化
- 错误提示友好性

## 五、扩展优化建议

### 5.1 功能扩展
1. 添加文件类型验证
2. 支持大文件异步处理
3. 实现数据导出功能
4. 添加数据可视化

### 5.2 性能优化
1. 使用celery处理大文件
2. 实现文件分片上传
3. 添加数据缓存机制
4. 优化查询性能

### 5.3 用户体验
1. 添加上传进度条
2. 实现预览功能
3. 提供数据筛选功能
4. 支持表格排序

## 六、注意事项

### 6.1 安全性
1. 文件类型验证
2. 文件大小限制
3. 用户权限控制
4. 数据访问控制

### 6.2 可维护性
1. 错误日志记录
2. 代码注释完善
3. 单元测试覆盖
4. 文档更新维护

### 6.3 扩展性
1. 支持多种文件格式
2. 预留功能扩展接口
3. 配置参数化
4. 模块化设计

