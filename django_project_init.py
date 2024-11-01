#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: django_project_init.py
Purpose: Django项目初始化脚本，用于创建符合最佳实践的项目结构
"""


import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

# 初始应用列表配置（当没有通过命令行指定应用时使用）
INITIAL_APPS = [
    'main',  # 默认主应用，表示系统的主要功能
]

# 运行模式
MODE_INIT = 'init'      # 初始化模式
MODE_ADD_APP = 'add'    # 增加应用模式


def get_default_project_name():
    """获取默认项目名（当前目录名）"""
    return Path.cwd().name


def check_project_exists(project_name):
    """检查项目是否已存在"""
    project_dir = Path.cwd() / project_name
    return project_dir.exists()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Django项目初始化/应用添加脚本',
        epilog='''
        示例:
          # 初始化新项目:
          python django_project_init.py --mode init -p myproject
          python django_project_init.py --mode init -p myproject -a user blog admin

          # 在现有项目中添加应用:
          python django_project_init.py --mode add -p myproject -a newapp1 newapp2
          python django_project_init.py --mode add -a newapp --auto-update

          # 还原配置到最新备份:
          python django_project_init.py --restore              # 在项目内执行
          python django_project_init.py -p myproject --restore # 在项目外执行
                '''
    )

    # restore操作作为独立的运行模式
    parser.add_argument('--restore',
                      action='store_true',
                      default=False,
                      help='还原配置文件到最新备份')

    # 运行模式,当有restore参数时忽略
    parser.add_argument('--mode',
                      choices=[MODE_INIT, MODE_ADD_APP],
                      default=MODE_INIT,
                      help=f'运行模式: {MODE_INIT}=初始化项目, {MODE_ADD_APP}=添加应用')

    # 项目名称参数
    parser.add_argument('-p', '--project',
                      default=None,
                      help='项目名称（默认：当前目录名）')

    # 应用名称参数
    parser.add_argument('-a', '--apps',
                      nargs='*',
                      default=None,
                      help='要创建的应用列表（默认：main）')

    # 自动更新设置参数
    parser.add_argument('--auto-update',
                      action='store_true',
                      default=False,
                      help='自动更新项目配置文件（settings.py和urls.py）')

    # 开发指南输出参数
    parser.add_argument('--guide',
                        action='store_true',
                        default=False,
                        help='只输出开发指南文档')

    # 开发指南输出文件名参数
    parser.add_argument('--guide-output',
                        default='app_development_guide.md',
                        help='开发指南输出文件名(默认: app_development_guide.md)')

    args = parser.parse_args()

    # 当使用restore时,不需要检查其他参数
    if args.restore:
        if args.apps:
            print("警告: 还原模式下不需要指定应用名称,将忽略 -a/--apps 参数")
        if args.mode != MODE_INIT:
            print("警告: 还原模式下不需要指定运行模式,将忽略 --mode 参数")
        if args.auto_update:
            print("警告: 还原模式下不需要指定自动更新,将忽略 --auto-update 参数")

    # 如果没有指定项目名,使用当前目录名
    if args.project is None:
        args.project = get_default_project_name()

    return args


def create_directory(path):
    """创建目录，如果目录不存在"""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"? 创建目录: {path}")
    except Exception as e:
        print(f"? 创建目录失败 {path}: {str(e)}")
        return False
    return True


def create_file(path, content=''):
    """创建文件，如果文件不存在"""
    try:
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"? 创建文件: {path}")
        else:
            print(f"! 文件已存在: {path}")
    except Exception as e:
        print(f"? 创建文件失败 {path}: {str(e)}")
        return False
    return True


def create_app_structure(app_name, project_name, base_dir):
    """创建应用的完整目录结构和文件"""
    app_dir = base_dir / 'apps' / app_name

    # 创建应用基础目录
    directories = [
        'migrations',  # [Django必需] 数据库迁移文件目录
        'core',  # [自定义] 核心业务逻辑目录 - 存放所有与Django无关的业务逻辑、算法、数据处理等代码
        f'templates/{app_name}',  # [Django] 应用级HTML模板目录
        f'templates/{app_name}/components',  # [Django] 可重用的模板组件目录
        f'static/{app_name}/css',  # [Django] CSS样式文件目录
        f'static/{app_name}/js',  # [Django] JavaScript文件目录
        f'static/{app_name}/images',  # [Django] 图片资源目录
        'services',  # [Django集成] 服务层目录 - 主要用于连接core层和Django层的facade服务
        'helpers',  # [Django集成] 辅助函数目录 - 处理Django相关的工具函数
        'api',  # [Django REST] REST API相关代码目录
        'tests/test_services',  # [测试] 服务层测试目录
        'management/commands',  # [Django] 自定义管理命令目录
    ]

    for directory in directories:
        create_directory(app_dir / directory)
        # 修改：优化__init__.py创建逻辑
        if not any(directory.startswith(prefix) for prefix in ['templates/', 'static/']):
            create_file(app_dir / directory / '__init__.py',
                        f'"""\nFile: apps/{app_name}/{directory}/__init__.py\nPurpose: {directory}包的初始化文件\n"""\n')

    # 创建应用基础文件
    files = {
        '__init__.py': f'"""\nFile: apps/{app_name}/__init__.py\nPurpose: {app_name}应用的初始化文件\n"""\n',

        'apps.py': f'''"""
File: apps/{app_name}/apps.py
Purpose: {app_name}应用的配置类
Warning: 此文件由系统自动生成，请勿手动修改
"""

from django.apps import AppConfig

class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_name.title()}模块'
''',

        'models.py': f'''"""
File: apps/{app_name}/models.py
Purpose: {app_name}应用的数据模型定义
"""

from django.db import models

# Create your models here.
''',

        'views.py': f'''"""
File: apps/{app_name}/views.py
Purpose: {app_name}应用的视图处理函数
"""

from django.shortcuts import render

def index(request):
    """主页视图"""
    context = {{
        'title': '{"欢迎访问"+project_name if app_name == "main" else app_name.title()+"模块"}',
        'project_name': '{project_name}'
    }}
    return render(request, '{app_name}/index.html', context)  # 移除重复的app_name
''',

        'urls.py': f'''"""
File: apps/{app_name}/urls.py
Purpose: {app_name}应用的URL配置
"""

from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
]
''',

        'admin.py': f'''"""
File: apps/{app_name}/admin.py
Purpose: {app_name}应用的后台管理配置
"""

from django.contrib import admin
# Register your models here.
''',

        'forms.py': f'''"""
File: apps/{app_name}/forms.py
Purpose: {app_name}应用的表单定义
"""

from django import forms

# Create your forms here.
''',

        'constants.py': f'''"""
File: apps/{app_name}/constants.py
Purpose: {app_name}应用的常量定义
"""

# Application-specific constants
''',

        'exceptions.py': f'''"""
File: apps/{app_name}/exceptions.py
Purpose: {app_name}应用的自定义异常
"""

class {app_name.title()}Error(Exception):
    """Base exception for {app_name} app"""
    pass
''',

        'utils.py': f'''"""
File: apps/{app_name}/utils.py
Purpose: {app_name}应用的工具函数
"""

# Utility functions
''',

        'services/data_service.py': f'''"""
File: apps/{app_name}/services/data_service.py
Purpose: {app_name}应用的数据服务
"""

# Data service functions
''',

        'helpers/formatters.py': f'''"""
File: apps/{app_name}/helpers/formatters.py
Purpose: {app_name}应用的格式化助手函数
"""

# Formatting helper functions
''',

        'api/serializers.py': f'''"""
File: apps/{app_name}/api/serializers.py
Purpose: {app_name}应用的API序列化器
"""

from rest_framework import serializers

# API Serializers
''',

        'api/views.py': f'''"""
File: apps/{app_name}/api/views.py
Purpose: {app_name}应用的API视图
"""

from rest_framework import viewsets

# API Views
''',

        'api/urls.py': f'''"""
File: apps/{app_name}/api/urls.py
Purpose: {app_name}应用的API路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('resource', ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
''',

        'tests/test_models.py': f'''"""
File: apps/{app_name}/tests/test_models.py
Purpose: {app_name}应用的模型测试
"""

from django.test import TestCase

# Model tests
''',

        'tests/test_views.py': f'''"""
File: apps/{app_name}/tests/test_views.py
Purpose: {app_name}应用的视图测试
"""

from django.test import TestCase, Client

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get('/{app_name}/')
        self.assertEqual(response.status_code, 200)
''',

        'tests/test_services/test_data_service.py': f'''"""
File: apps/{app_name}/tests/test_services/test_data_service.py
Purpose: {app_name}应用的服务测试
"""

from django.test import TestCase

# Service tests
''',

        'management/commands/process_data.py': f'''"""
File: apps/{app_name}/management/commands/process_data.py
Purpose: {app_name}应用的示例管理命令
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '处理{app_name}数据的示例命令'

    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, help='要执行的操作')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('命令执行成功'))
''',

        f'templates/{app_name}/base.html': f'''{{% extends "base.html" %}}

{{% block title %}}{app_name.title()} - {{{{project_name}}}}{{% endblock %}}

{{% block content %}}
{{% endblock %}}
''',

        f'templates/{app_name}/index.html': f'''{{% extends "{app_name}/base.html" %}}

{{% block title %}}{{{{title}}}}{{% endblock %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-4">{{{{title}}}}</h1>
    {{% if app_name == "main" %}}<p class="text-lg">欢迎使用 {{{{project_name}}}} 系统</p>{{% endif %}}
</div>
{{% endblock %}}
''',

        f'templates/{app_name}/components/header.html': '''{% load static %}

<header class="main-header">
    <nav class="container mx-auto px-4 py-2">
        <!-- Header content -->
    </nav>
</header>
''',

        f'static/{app_name}/css/style.css': '''/* Application specific styles */
''',

        f'static/{app_name}/js/main.js': '''// Application specific JavaScript
''',
        'APP_DEVELOPMENT_GUIDE.md': get_app_development_guide(),
    }

    for file_path, content in files.items():
        create_file(app_dir / file_path, content)

    return True


def get_app_development_guide():
    """获取应用开发指南内容"""
    return '''# Django应用开发规范指南

## 1. 目录结构与职责

### 1.1 核心业务目录 (core/)
- 用途：存放所有与Django无关的业务逻辑
- 特点：可独立运行、测试和复用
- 适合内容：
  * 数据处理算法
  * 业务逻辑
  * 工具函数
  * 自定义异常
  * 数据模型（非Django ORM）

### 1.2 服务集成目录 (services/)
- 用途：连接core层和Django层
- 特点：负责数据转换和上下文处理
- 适合内容：
  * Facade服务类
  * 数据转换逻辑
  * Django特定的服务封装

### 1.3 API目录 (api/)
- 用途：REST API实现
- 适合内容：
  * 序列化器
  * API视图
  * URL路由配置

### 1.4 模板目录 (templates/)
- 用途：HTML模板
- 适合内容：
  * 页面模板
  * 可重用组件

### 1.5 静态文件目录 (static/)
- 用途：前端资源
- 适合内容：
  * CSS样式
  * JavaScript脚本
  * 图片资源

### 1.6 其他目录
- migrations/: 数据库迁移文件
- helpers/: Django相关的辅助函数
- tests/: 测试代码
- management/: 自定义管理命令

## 2. 应用开发流程示例：Excel文件上传与显示

### 开发流程示例说明
本示例展示了一个完整的Django应用开发流程，功能是上传Excel文件并显示内容。
通过这个例子说明如何：
1. 在core中开发核心功能
2. 通过服务层集成到Django
3. 提供API接口
4. 实现前端界面

### 2.1 需求描述
创建一个应用，允许用户：
1. 上传Excel文件
2. 解析并显示内容
3. 基本的数据验证

### 2.2 示例开发步骤

#### Step 1: 核心功能实现 (core/)
```python
# core/excel_processor.py
import pandas as pd
from typing import Dict, Any

class ExcelProcessor:
    """Excel处理核心类"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_excel(self) -> Dict[str, Any]:
        """读取并解析Excel文件"""
        try:
            df = pd.read_excel(self.file_path)
            return {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'row_count': len(df),
                'col_count': len(df.columns)
            }
        except Exception as e:
            raise ExcelProcessError(f"Excel处理错误: {str(e)}")

# core/exceptions.py
class ExcelProcessError(Exception):
    """Excel处理相关的异常"""
    pass
```

#### Step 2: 服务层实现 (services/)
```python
# services/excel_service.py
from django.core.files.uploadedfile import UploadedFile
from ..core.excel_processor import ExcelProcessor, ExcelProcessError

class ExcelService:
    """Excel处理服务"""
    def process_upload(self, uploaded_file: UploadedFile) -> dict:
        """处理上传的Excel文件"""
        try:
            # 保存上传文件
            file_path = self._save_file(uploaded_file)

            # 使用核心处理器
            processor = ExcelProcessor(file_path)
            result = processor.read_excel()

            return {
                'status': 'success',
                'data': result
            }
        except ExcelProcessError as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _save_file(self, file: UploadedFile) -> str:
        """保存上传的文件"""
        # 文件保存逻辑
        pass
```

#### Step 3: API实现 (api/)
```python
# api/serializers.py
from rest_framework import serializers

class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.excel_service import ExcelService

class ExcelUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        service = ExcelService()
        result = service.process_upload(file)
        return Response(result)
```

#### Step 4: URL配置 (urls.py)
```python
from django.urls import path
from .api.views import ExcelUploadView

app_name = 'excel_processor'

urlpatterns = [
    path('upload/', ExcelUploadView.as_view(), name='upload'),
]
```

#### Step 5: 前端模板 (templates/)
```html
<!-- templates/excel_processor/upload.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h2>Excel文件上传</h2>
    <form id="uploadForm">
        {% csrf_token %}
        <input type="file" name="file" accept=".xlsx,.xls">
        <button type="submit">上传</button>
    </form>
    <div id="result"></div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('uploadForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/api/excel/upload/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        // 显示结果
        displayResult(result);
    } catch (error) {
        console.error('Upload failed:', error);
    }
};
</script>
{% endblock %}
```

### 2.3 开发顺序建议

1. **先开发核心功能**
   - 在core/目录下实现基本功能
   - 可以写个简单的测试脚本验证
   - 确保功能正确且独立可用

2. **编写服务层**
   - 创建services/下的服务类
   - 处理文件上传等Django特定逻辑
   - 调用core层的功能

3. **实现API**
   - 创建序列化器
   - 实现API视图
   - 配置URL路由

4. **前端开发**
   - 创建HTML模板
   - 添加必要的JS/CSS
   - 实现用户交互

### 2.4 测试规范

1. **核心功能测试**
```python
# tests/test_core/test_excel_processor.py
import unittest
from ...core.excel_processor import ExcelProcessor

class TestExcelProcessor(unittest.TestCase):
    def test_read_excel(self):
        processor = ExcelProcessor('test.xlsx')
        result = processor.read_excel()
        self.assertIn('columns', result)
        self.assertIn('data', result)
```

2. **服务层测试**
```python
# tests/test_services/test_excel_service.py
from django.test import TestCase
from ...services.excel_service import ExcelService

class TestExcelService(TestCase):
    def test_process_upload(self):
        service = ExcelService()
        # 测试文件上传处理
```

3. **API测试**
```python
# tests/test_api.py
from django.test import TestCase
from django.urls import reverse

class TestExcelAPI(TestCase):
    def test_upload_endpoint(self):
        url = reverse('excel_processor:upload')
        # 测试API端点
```

## 3. 最佳实践建议

### 3.1 核心开发原则
1. 核心逻辑放在core/目录
2. 保持核心功能的独立性
3. 使用依赖注入而非直接依赖
4. 详细的异常处理
5. 完整的类型注解

### 3.2 服务层原则
1. 职责单一
2. 处理所有Django相关的逻辑
3. 错误转换和日志记录
4. 统一的返回格式

### 3.3 API设计原则
1. RESTful规范
2. 适当的状态码
3. 清晰的错误信息
4. 版本控制

### 3.4 文档建议
1. 清晰的注释
2. API文档
3. 部署说明
4. 环境要求

## 4. 常见问题

### 4.1 目录使用
Q: 什么代码应该放在core/目录？
A: 所有与Django无关的业务逻辑，如数据处理、算法实现等。

Q: services/和helpers/的区别？
A: services/包含业务服务类，helpers/包含工具函数。

### 4.2 开发流程
Q: 为什么要先开发core层？
A: 确保核心功能独立可用，便于测试和维护。

Q: 如何处理文件上传？
A: 文件处理逻辑放在服务层，只传递文件路径给core层。

## 5. 其他注意事项

1. 异步处理
2. 缓存策略
3. 批处理
4. 性能优化
5. 安全考虑
'''

def create_project_structure(project_name):
    """创建项目的完整目录结构和文件"""
    base_dir = Path.cwd() / project_name

    # 创建项目根目录
    if not create_directory(base_dir):
        return True

    # 切换到项目目录
    os.chdir(base_dir)

    # 创建基本目录结构
    directories = [
        'config/settings',
        'apps',
        'static/css',
        'static/js',
        'static/images',
        'templates/shared',
        'media/uploads',
        'docs',
        'utils',
        'requirements',
    ]

    # 创建目录并添加__init__.py
    for directory in directories:
        path = Path(directory)
        create_directory(path)
        if directory in ['apps', 'utils', 'config', 'config/settings']:
            create_file(path / '__init__.py',
                        f'"""\nFile: {directory}/__init__.py\nPurpose: {directory}包的初始化文件\n"""\n')

    templates_dirs = ["            BASE_DIR / 'templates'"]
    for app in INITIAL_APPS:
        templates_dirs.append(f"            BASE_DIR / 'apps' / '{app}' / 'templates'")
    templates_str = ',\n'.join(templates_dirs)

    # 创建配置文件
    settings_base = f'''"""
File: config/settings/base.py
Purpose: Django项目基础配置文件
Warning: 此文件包含关键项目配置，修改前请仔细评估影响
"""

from pathlib import Path
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加apps目录到Python路径
sys.path.append(str(BASE_DIR / 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
{templates_str}
        ],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}},
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''

    settings_local = '''"""
File: config/settings/local.py
Purpose: Django项目本地开发配置文件
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# 开发环境特定的设置
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Debug Toolbar设置
INTERNAL_IPS = [
    '127.0.0.1',
]
'''

    settings_production = '''"""
File: config/settings/production.py
Purpose: Django项目生产环境配置文件
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['your-domain.com']  # 修改为实际域名

# 安全设置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
'''

    manage_py = '''#!/usr/bin/env python
"""
File: manage.py
Purpose: Django项目管理脚本，提供命令行工具
Warning: 此文件由系统自动生成，请勿手动修改
"""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

    wsgi_py = '''"""
File: config/wsgi.py
Purpose: WSGI配置，用于生产环境部署
Warning: 此文件由系统自动生成，请谨慎修改
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()
'''

    asgi_py = '''"""
File: config/asgi.py
Purpose: ASGI配置，用于异步服务器部署
Warning: 此文件由系统自动生成，请谨慎修改
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_asgi_application()
'''

    urls_py = '''"""
File: config/urls.py
Purpose: 项目的主URL配置
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
'''

    # 动态添加URL配置
    for app in INITIAL_APPS:
        # 主应用作为根URL
        if app == 'main':
            urls_py += f"    path('', include('main.urls')),  # 主应用作为根URL\n"
        else:
            urls_py += f"    path('{app}/', include('{app}.urls')),\n"

    # 添加结尾部分
    urls_py += ''']

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass
'''

    requirements_base = '''# 基础依赖包
Django>=5.0.8
python-dotenv>=1.0.0
Pillow>=10.0.0
djangorestframework>=3.14.0
'''

    requirements_local = '''# 本地开发依赖包
-r base.txt
django-debug-toolbar>=4.2.0
django-extensions>=3.2.3
ipython>=8.12.2
'''

    requirements_production = '''# 生产环境依赖包
-r base.txt
gunicorn>=21.2.0
psycopg2-binary>=2.9.9
'''

    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
media
staticfiles/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.venv
venv/
ENV/

# Project specific
/media/
/static/
'''

    readme = f'''# {project_name}

## 项目设置

1. 创建虚拟环境:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate  # Windows
```

2. 安装依赖:
```bash
pip install -r requirements/local.txt
```

3. 初始化数据库:
```bash
python manage.py migrate
```

4. 创建超级用户:
```bash
python manage.py createsuperuser
```

5. 运行开发服务器:
```bash
python manage.py runserver
```

## 项目结构

```
{project_name}/
├── manage.py           # Django命令行工具
├── config/             # 项目配置
│   ├── settings/      # 分环境配置
│   ├── urls.py       # URL配置
│   ├── wsgi.py      # WSGI配置
│   └── asgi.py     # ASGI配置
├── apps/             # 应用目录
├── templates/        # 项目级模板
├── static/           # 静态文件
├── media/            # 上传文件
├── docs/             # 文档
└── requirements/     # 依赖管理
```

## 环境配置

1. 开发环境:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.local
```

2. 生产环境:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

## 应用说明

1. main: 系统主要功能模块
2. [其他应用说明]

## 开发指南

### 创建新应用

```bash
python manage.py startapp your_app_name apps/your_app_name
```

### 运行测试

```bash
python manage.py test
```

### 收集静态文件

```bash
python manage.py collectstatic
```

## API文档

API文档位于 `docs/api.md`

## 部署指南

详细部署说明请参考 `docs/deployment.md`

## 开发团队

[填写开发团队信息]

## 许可证

[选择适当的许可证]
'''

    env = '''# 环境变量配置
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
'''

    base_html = '''<!DOCTYPE html>
<html lang="zh-hans">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{project_name}}{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>
        {% include "shared/header.html" %}
    </header>

    <main>
        {% block content %}
        {% endblock %}
    </main>

    <footer>
        {% include "shared/footer.html" %}
    </footer>

    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'''

    shared_header = '''<header class="site-header">
    <nav>
        <ul>
            <li><a href="{% url 'admin:index' %}">管理后台</a></li>
            <!-- Add more navigation items -->
        </ul>
    </nav>
</header>
'''

    shared_footer = '''<footer class="site-footer">
    <p>&copy; {% now "Y" %} {{project_name}}. All rights reserved.</p>
</footer>
'''

    api_md = '''# API文档

## 概述

本文档描述了项目的API接口规范。

## 认证

API使用Token认证，在请求头中添加：
```
Authorization: Token your-token-here
```

## 接口列表

### 1. 示例接口

#### 请求

```
GET /api/v1/example/
```

#### 响应

```json
{
    "status": "success",
    "data": []
}
```

## 错误处理

所有错误响应采用统一格式：

```json
{
    "status": "error",
    "message": "错误描述",
    "code": "错误代码"
}
```
'''

    deployment_md = '''# 部署文档

## 系统要求

- Python 3.10+
- PostgreSQL 13+
- nginx 1.18+

## 部署步骤

1. 准备服务器
2. 配置数据库
3. 配置nginx
4. 设置环境变量
5. 收集静态文件
6. 启动应用

## 详细步骤

### 1. 准备服务器

```bash
# 安装依赖
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql
```

### 2. 配置数据库

```bash
sudo -u postgres createdb mydb
sudo -u postgres createuser myuser
```

### 3. 配置nginx

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/static/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

### 4. 设置环境变量

创建 `.env` 文件：

```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost/dbname
```

### 5. 收集静态文件

```bash
python manage.py collectstatic
```

### 6. 启动应用

使用 gunicorn:

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

## 监控和维护

### 日志

日志文件位置：
- 应用日志：`logs/app.log`
- nginx日志：`/var/log/nginx/`

### 备份

定期备份数据库：

```bash
pg_dump dbname > backup.sql
```

### 更新

更新步骤：

1. 拉取最新代码
2. 安装依赖
3. 迁移数据库
4. 收集静态文件
5. 重启服务

```bash
git pull
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart gunicorn
```

## 故障排除

常见问题及解决方案...

## 安全建议

1. 使用 HTTPS
2. 定期更新依赖
3. 启用防火墙
4. 定期备份
'''

    utils_helpers = '''"""
File: utils/helpers.py
Purpose: 项目级通用工具函数
"""

def format_datetime(datetime_obj, format_str="%Y-%m-%d %H:%M:%S"):
    """格式化日期时间"""
    return datetime_obj.strftime(format_str) if datetime_obj else ""

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def truncate_string(text, length=100, suffix='...'):
    """截断字符串"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix
'''

    # 创建配置文件
    files_to_create = {
        'config/settings/base.py': settings_base,
        'config/settings/local.py': settings_local,
        'config/settings/production.py': settings_production,
        'config/wsgi.py': wsgi_py,
        'config/asgi.py': asgi_py,
        'config/urls.py': urls_py,
        'manage.py': manage_py,
        'requirements/base.txt': requirements_base,
        'requirements/local.txt': requirements_local,
        'requirements/production.txt': requirements_production,
        '.gitignore': gitignore,
        '.env': env,
        'README.md': readme,
        'docs/api.md': api_md,
        'docs/deployment.md': deployment_md,
        'utils/helpers.py': utils_helpers,
        'templates/base.html': base_html,
        'templates/shared/header.html': shared_header,
        'templates/shared/footer.html': shared_footer,
    }

    # 创建所有配置文件
    success = True
    for file_path, content in files_to_create.items():
        try:
            # 如果文件已存在，记录但不视为错误
            if os.path.exists(Path(file_path)):
                print(f"! 文件已存在: {file_path}")
                continue

            # 创建文件，但如果失败不会立即退出
            if not create_file(Path(file_path), content):
                success = False
                print(f"× 创建文件失败: {file_path}")
        except Exception as e:
            success = False
            print(f"× 创建文件出错 {file_path}: {str(e)}")

    # 尝试设置manage.py为可执行
    try:
        os.chmod('manage.py', 0o755)
    except Exception as e:
        print(f"! 设置manage.py权限失败: {str(e)}")
        # 不将权限设置失败视为严重错误

    # 创建初始应用
    for app_name in INITIAL_APPS:
        create_app_structure(app_name, project_name, Path.cwd())
        # 将应用添加到INSTALLED_APPS
        with open('config/settings/base.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if f"'{app_name}'" not in content:
            content = content.replace(
                "INSTALLED_APPS = [",
                f"INSTALLED_APPS = [\n    '{app_name}.apps.{app_name.title()}Config',"
            )
            create_file('config/settings/base.py', content)

        # 添加URL配置
        with open('config/urls.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if f"path('{app_name}/'," not in content:
            url_pattern = f"    path('{app_name}/', include('{app_name}.urls')),"
            content = content.replace(
                "urlpatterns = [",
                f"urlpatterns = [\n{url_pattern}"
            )
            create_file('config/urls.py', content)

    print("\n? Django项目初始化完成！")
    print("\n?? 后续步骤：")
    print("1. 创建并激活虚拟环境")
    print("2. 安装依赖: pip install -r requirements/local.txt")
    print("3. 初始化数据库: python manage.py migrate")
    print("4. 创建超级用户: python manage.py createsuperuser")
    print("5. 运行开发服务器: python manage.py runserver")


def initialize_django_project(project_name):
    """初始化Django项目"""
    try:
        # 创建项目目录结构
        create_project_structure(project_name)

        # 即使某些文件已存在，也继续创建应用
        # 创建初始应用
        for app_name in INITIAL_APPS:
            create_app_structure(app_name, project_name, Path.cwd())

            # 使用新的辅助函数更新配置
            try:
                update_installed_apps(app_name)
                update_urls_config(app_name)
            except Exception as e:
                print(f"配置文件更新失败: {str(e)}")
                # 继续执行，不中断流程

        print(f"\n✓ 项目 {project_name} 创建成功!")
        return True
    except Exception as e:
        print(f"\n✗ 项目创建过程中出现错误: {str(e)}")
        return False


def generate_manual_config_guide(app_name, project_name, base_dir, auto_updated=False):
    """
    生成配置指南文件，提供详细的手动配置步骤

    参数:
        app_name (str): 应用名称
        project_name (str): 项目名称
        base_dir (Path): 项目根目录
        auto_updated (bool): 是否已执行自动更新
    """
    # 执行验证
    verification_results = verify_app_files(app_name, project_name, base_dir)

    # 检查URL导入验证结果
    url_import_valid = False
    for filename, is_valid, message in verification_results:
        if filename == 'project_urls_imports' and is_valid:
            url_import_valid = True
            break

    if auto_updated:
        guide_content = f'''# {app_name} 应用配置指南

## 1. 自动更新执行结果

### 1.1 INSTALLED_APPS 配置更新
文件位置: ./config/settings/base.py

✅ 已自动添加以下配置:
```python
INSTALLED_APPS = [
    # Django内置应用
    'django.contrib.admin',
    ...
    # 第三方应用
    'rest_framework',
    ...
    # 自定义应用
    '{app_name}.apps.{app_name.title()}Config',  # 新增应用配置
]
```

### 1.2 URL路由配置更新
文件位置: ./config/urls.py

✅ 已自动添加以下配置:
```python
urlpatterns = [
    ...
    path('{app_name}/', include('{app_name}.urls')),  # 新增URL配置
]
```

### 1.3 备份说明
- INSTALLED_APPS配置备份位置: ./config/app_append_backups/base_backups/
- URL配置备份位置: ./config/app_append_backups/urls_backups/

如需恢复之前的配置:
```python
update_base_settings('{app_name}', restore=True)  # 恢复INSTALLED_APPS配置
update_main_urls('{app_name}', restore=True)      # 恢复URL配置
```

### 1.4 应用文件自动验证结果
"""
验证结果:
"""
'''
    else:
        guide_content = f'''# {app_name} 应用配置指南

## 1. 配置文件位置及修改内容

### 1.1 添加应用到 INSTALLED_APPS
文件位置: ./config/settings/base.py

⚠️ 注意应用顺序，确保依赖项正确!
在 INSTALLED_APPS 列表中添加:
```python
INSTALLED_APPS = [
    # Django内置应用
    'django.contrib.admin',
    ...
    # 第三方应用
    'rest_framework',
    ...
    # 自定义应用
    '{app_name}.apps.{app_name.title()}Config',
]
```

### 1.2 配置URL路由
文件位置: ./config/urls.py\n'''

        if not url_import_valid:
            guide_content += '''
1️⃣ 检查导入语句(如果已存在则跳过):
```python
from django.urls import path, include
```
'''

        guide_content += f'''
2️⃣ 在 urlpatterns 列表中添加:
```python
urlpatterns = [
    ...
    path('{app_name}/', include('{app_name}.urls')),
]
```

### 1.3 应用文件自动验证结果
"""
验证结果:
"""
'''

    # 执行验证并添加结果到指南中
    for filename, is_valid, message in verification_results:
        guide_content += f'''
{filename}:
状态: {'✅' if is_valid else '❌'} {message}
路径: ./apps/{app_name}/{filename}
'''

    if auto_updated:
        guide_content += f'''

## 2. 后续步骤

请检查以下内容以确保配置正确：

✅ 验证自动更新是否成功:
   - 检查 INSTALLED_APPS 中是否正确添加了应用配置
   - 检查 urls.py 中是否正确添加了URL配置
   - 执行 python manage.py check 确认无错误

✅ 测试应用是否正常工作:
   1. 运行开发服务器: python manage.py runserver
   2. 访问应用URL: http://localhost:8000/{app_name}/
   3. 确认页面能正常访问

📋 其他可选步骤:
   - 检查和调整应用在 INSTALLED_APPS 中的顺序
   - 检查URL配置是否有潜在的路由冲突
   - 根据需要添加其他URL配置

如果需要手动修改配置，请参考以下说明。
'''
    else:
        guide_content += f'''

如果看到❌标记，请检查对应文件是否被修改过。
自动创建的文件应该保持原样，除非你明确知道要修改什么。

## 2. 检查清单

✅ 已检查应用依赖并安装必要的包
✅ 已将应用添加到 INSTALLED_APPS 并确认顺序正确
✅ 已在主 urls.py 中添加应用的 URL 配置
✅ 已确认应用的 urls.py 配置正确
✅ 已确认视图函数工作正常
✅ 已确认模板文件位置正确
✅ 已测试页面能正常访问
'''

    guide_content += f'''
## 3. 验证步骤

1. 检查项目配置:
```bash
python manage.py check {app_name}
```

2. 运行开发服务器:
```bash
python manage.py runserver
```

3. 访问应用URL:
```
http://localhost:8000/{app_name}/
```

## 4. ❗常见问题

1. 如果出现 "No module named '{app_name}'" 错误:
   - 检查 apps 目录是否在 Python 路径中
   - 检查 INSTALLED_APPS 中应用名称拼写是否正确
   - 确认 apps.py 中的 name 配置正确

2. 如果出现 URL 不匹配错误:
   - 检查主 urls.py 中的配置顺序（注意避免路由冲突）
   - 确认应用 urls.py 中的 app_name 定义正确
   - 验证 path() 第一个参数中的 URL 模式

3. 如果模板无法找到:
   - 确认模板文件位置: ./apps/{app_name}/templates/{app_name}/index.html
   - 检查 settings.py 中的 TEMPLATES 配置
   - 确保模板文件扩展名为 .html

## 5. 其他注意事项

📋 运行测试:
```bash
# 运行特定应用的测试
python manage.py test {app_name}

# 运行特定测试类
python manage.py test {app_name}.tests.test_views.ViewTests

# 运行覆盖率测试
coverage run --source='.' manage.py test {app_name}
coverage report
```

📦 数据库迁移:
```bash
# 创建迁移文件
python manage.py makemigrations {app_name}

# 查看迁移SQL
python manage.py sqlmigrate {app_name} XXXX

# 执行迁移
python manage.py migrate {app_name}
```

🔍 调试技巧:
- 使用 django-debug-toolbar 查看请求信息
- 在视图中添加 print() 或使用 logging 模块
- 检查开发服务器的控制台输出
'''

    guide_file = base_dir / 'apps' / app_name / 'CONFIG_GUIDE.md'
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"\n✓ 配置指南已生成: {guide_file}")
        if auto_updated:
            print("  配置已自动更新，请查看该文件了解更新详情")
        else:
            print("  请查看该文件了解详细的配置步骤")
    except Exception as e:
        print(f"\n✗ 配置指南生成失败: {str(e)}")

def update_installed_apps(app_name):
    """智能更新INSTALLED_APPS配置"""
    try:
        with open('config/settings/base.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查应用是否已经在INSTALLED_APPS中
        if f"'{app_name}'" not in content:
            # 更智能的插入位置：在INSTALLED_APPS的自定义应用部分
            lines = content.split('\n')
            insert_pos = -1
            for i, line in enumerate(lines):
                if 'INSTALLED_APPS = [' in line:
                    insert_pos = i + 1
                    # 跳过Django内置应用和第三方应用
                    while i < len(lines) and ('django.contrib' in lines[i] or 'rest_framework' in lines[i]):
                        i += 1
                        insert_pos = i + 1

            if insert_pos != -1:
                lines.insert(insert_pos, f"    '{app_name}.apps.{app_name.title()}Config',")
                content = '\n'.join(lines)
                create_file('config/settings/base.py', content)
                print(f"✓ 已将 {app_name} 添加到 INSTALLED_APPS")
    except Exception as e:
        print(f"! 更新INSTALLED_APPS失败: {str(e)}")


def update_urls_config(app_name):
    """更新URL配置"""
    try:
        with open('config/urls.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if f"path('{app_name}/'," not in content:
            # 主应用作为根URL
            if app_name == 'main':
                url_pattern = f"    path('', include('main.urls')),  # 主应用作为根URL\n"
            else:
                url_pattern = f"    path('{app_name}/', include('{app_name}.urls')),\n"

            # 在最后一个path之前插入
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if ']' in line and 'urlpatterns' in content[:i]:
                    lines.insert(i, url_pattern)
                    break
            new_content = '\n'.join(lines)

            # 直接写入文件而不是使用create_file
            with open('config/urls.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ 已添加 {app_name} 的URL配置")
    except Exception as e:
        print(f"! 更新URL配置失败: {str(e)}")


def get_backup_paths(project_dir='.'):
    """
    获取备份相关的目录路径

    Args:
        project_dir: 项目根目录，默认为当前目录

    Returns:
        tuple: (base_backup_dir, urls_backup_dir)
            - base_backup_dir: INSTALLED_APPS配置备份目录
            - urls_backup_dir: URLs配置备份目录
    """
    from pathlib import Path

    # 主备份目录
    backup_root = Path(project_dir) / 'config' / 'app_append_backups'

    # 子目录
    base_backup_dir = backup_root / 'base_backups'
    urls_backup_dir = backup_root / 'urls_backups'

    # 确保目录存在
    base_backup_dir.mkdir(parents=True, exist_ok=True)
    urls_backup_dir.mkdir(parents=True, exist_ok=True)

    return str(base_backup_dir), str(urls_backup_dir)

def validate_base_settings_content(content):
    """验证base settings文件的基本格式"""
    if not content.strip():
        return False, "Empty content"
    if 'INSTALLED_APPS' not in content:
        return False, "No INSTALLED_APPS found"
    return True, ""


def validate_base_settings_syntax(content):
    """验证base settings文件的Python语法"""
    try:
        compile(content, '<string>', 'exec')
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def validate_base_settings_result(new_content):
    """验证base settings文件修改后的内容"""
    try:
        # 1. 检查基本结构
        if 'INSTALLED_APPS' not in new_content:
            return False, "INSTALLED_APPS lost after modification"

        # 2. 检查语法
        compile(new_content, '<string>', 'exec')

        # 3. 检查格式
        if new_content.count('[') != new_content.count(']'):
            return False, "Bracket mismatch"

        return True, ""
    except Exception as e:
        return False, str(e)


def append_app_to_base_settings(content, app_name):
    """
    向Django base settings配置文件中添加新应用

    参数:
        content (str): 配置文件内容
        app_name (str): 要添加的应用名称

    返回:
        tuple: (更新后的内容, 是否有更新, 更新信息)
    """
    # 1. 预检查
    valid, msg = validate_base_settings_content(content)
    if not valid:
        return content, False, f"Pre-validation failed: {msg}"

    valid, msg = validate_base_settings_syntax(content)
    if not valid:
        return content, False, f"Syntax validation failed: {msg}"

    # 2. 处理文件内容
    try:
        lines = content.split('\n')

        # 2.1 定位 INSTALLED_APPS
        start_index = -1
        end_index = -1
        for i, line in enumerate(lines):
            line_content = line.strip()
            if line_content.startswith('INSTALLED_APPS') and '[' in line:
                start_index = i
            if start_index != -1 and ']' in line:
                end_index = i
                break

        if start_index == -1 or end_index == -1:
            return content, False, "INSTALLED_APPS not found or invalid format"

        # 2.2 分析现有格式
        existing_lines = lines[start_index + 1:end_index]
        indent = ''
        for line in existing_lines:
            if line.strip() and not line.strip().startswith('#'):
                indent = line[:-len(line.lstrip())]
                break

        if not indent:
            return content, False, "Cannot determine indentation"

        # 2.3 检查是否已存在
        app_patterns = [
            f"{app_name}.apps.{app_name.title()}Config",
            app_name
        ]
        for line in existing_lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            for pattern in app_patterns:
                if f"'{pattern}'" in line or f'"{pattern}"' in line:
                    return content, False, f"App {app_name} already exists in line: {line}"

        # 2.4 插入新配置
        app_config = f"{indent}'{app_name}.apps.{app_name.title()}Config',"
        lines.insert(end_index, app_config)
        new_content = '\n'.join(lines)

        # 2.5 验证结果
        valid, msg = validate_base_settings_result(new_content)
        if not valid:
            return content, False, f"Post-validation failed: {msg}"

        return new_content, True, app_config

    except Exception as e:
        return content, False, f"Error during modification: {str(e)}"


def update_base_settings(app_name, restore=False):
    """更新或恢复 Django 项目的 INSTALLED_APPS 配置

    此函数用于管理 config/settings/base.py 文件的修改，包括备份和恢复功能。
    备份文件统一存放在 config/base_backups 目录中，使用时间戳命名。

    备份策略：
        - 所有备份保存在 config/base_backups/ 目录
        - 备份文件格式：base.py.YYYYMMDD_HHMMSS.bak
        - 每次修改前自动创建新备份
        - 不自动删除历史备份

    更新算法：
        1. 文件定位：读取 config/settings/base.py 文件
        2. 内容提取：
           - 将文件按行分割为列表
           - 查找 "INSTALLED_APPS = [" 所在行
           - 向后扫描直到找到对应的结束符号 "]"
        3. 注入规则：
           - 检查是否已存在 '{app_name}.apps.{app_name.title()}Config'
           - 如果不存在，在最后一个应用配置后、结束符号"]"前插入新应用配置
           - 新应用配置格式: '    '{app_name}.apps.{app_name.title()}Config','
           - 保持4空格缩进以维持代码格式
        4. 保存机制：
           - 将修改后的行列表重新连接为字符串
           - 使用 'w' 模式写回原文件
           - 写入失败时自动回滚到备份版本

    参数：
        app_name (str): 要添加到 INSTALLED_APPS 的应用名称
        restore (bool): 是否执行恢复操作
            - True: 从最新备份恢复
            - False: 创建新备份并执行更新（默认）

    返回：
        bool: 操作成功返回 True，失败返回 False

    用法示例：
        # 添加新应用
        update_base_settings('myapp')

        # 恢复到最新备份
        update_base_settings('myapp', restore=True)
    """
    from datetime import datetime
    settings_path = 'config/settings/base.py'
    base_backup_dir, _ = get_backup_paths()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{base_backup_dir}/base.py.{timestamp}.bak'

    # 获取最新的备份文件
    def get_latest_backup():
        if os.path.exists(base_backup_dir):
            backups = sorted([f for f in os.listdir(base_backup_dir)
                              if f.startswith('base.py.') and f.endswith('.bak')],
                             reverse=True)
            return f'{base_backup_dir}/{backups[0]}' if backups else None
        return None

    # 处理恢复操作
    if restore:
        latest_backup = get_latest_backup()
        if latest_backup:
            try:
                shutil.copy2(latest_backup, settings_path)
                print(f"? 已恢复INSTALLED_APPS配置文件至备份: {latest_backup}")
                return True
            except Exception as e:
                print(f"× 恢复INSTALLED_APPS配置文件失败: {str(e)}")
                return False
        else:
            print(f"× 未找到INSTALLED_APPS配置文件备份")
            return False

    try:
        # 1. 创建新的备份
        if os.path.exists(settings_path):
            shutil.copy2(settings_path, backup_path)
            print(f"\n# 备份信息:")
            print(f"√ 已创建配置文件备份: {backup_path}")
            print(f"! 备份目录位置: {base_backup_dir}")
            print(f"  如果确认配置正确，可以手动删除备份目录: {base_backup_dir}")

        # 2. 读取文件
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 3. 处理内容
        new_content, has_update, app_config = append_app_to_base_settings(content, app_name)

        if has_update:
            print(f"\n# 更新信息:")
            print(f"→ 在INSTALLED_APPS中添加: {app_config}")

            # 4. 写入更新后的内容
            try:
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"? 更新INSTALLED_APPS成功")
                print(f"\n# 恢复说明:")
                print(f"  如需恢复，请使用: update_base_settings('{app_name}', restore=True)")
                return True
            except Exception as write_err:
                print(f"× 写入更新失败: {str(write_err)}")
                # 5. 如果写入失败，恢复备份
                shutil.copy2(backup_path, settings_path)
                print("! 已自动恢复至备份状态")
                raise write_err
        return False

    except Exception as e:
        print(f"× 更新INSTALLED_APPS失败: {str(e)}")
        # 6. 发生任何错误，确保恢复备份
        latest_backup = get_latest_backup()
        if latest_backup:
            shutil.copy2(latest_backup, settings_path)
            print("! 已自动恢复至备份状态")
        return False


def append_url_to_main_urls(content, app_name):
    """
    向Django主urls配置文件中添加新的URL配置
    """
    print("\n=== URLs更新详细信息 ===")

    # 1. 预检查
    print("\n# 1. 预验证检查")
    valid, msg = validate_main_urls_content(content)
    if not valid:
        print(f"× 内容预验证失败: {msg}")
        return content, False, f"Pre-validation failed: {msg}"
    print("√ 内容预验证通过")

    valid, msg = validate_main_urls_syntax(content)
    if not valid:
        print(f"× 语法预验证失败: {msg}")
        return content, False, f"Syntax validation failed: {msg}"
    print("√ 语法预验证通过")

    # 2. 处理文件内容
    try:
        print("\n# 2. 文件内容处理")
        lines = content.split('\n')
        print(f"→ 总行数: {len(lines)}")

        # 新增：确保必要的导入存在
        print("\n# 2.0 检查并添加必要的导入")
        has_include_import = False
        for line in lines:
            if 'from django.urls import' in line:
                if 'include' in line:
                    has_include_import = True
                    print("√ 已存在include导入")
                elif 'path' in line:
                    # 在现有的path导入中添加include
                    lines[lines.index(line)] = line.replace('import path', 'import path, include')
                    has_include_import = True
                    print("√ 在现有path导入中添加include")
                    break

        if not has_include_import:
            # 在顶部导入区域添加新的导入语句
            for i, line in enumerate(lines):
                if line.startswith('from django.') or line.startswith('from rest_framework'):
                    lines.insert(i, 'from django.urls import path, include')
                    print("√ 添加新的导入语句")
                    break

        # 2.1 定位 urlpatterns
        print("\n# 2.1 定位urlpatterns")
        start_index = -1
        end_index = -1
        for i, line in enumerate(lines):
            line_content = line.strip()
            if line_content.startswith('urlpatterns') and '[' in line:
                start_index = i
                print(f"√ 找到urlpatterns起始位置: 第{i + 1}行")
            if start_index != -1 and ']' in line and 'debug_toolbar' not in line:
                end_index = i
                print(f"√ 找到urlpatterns结束位置: 第{i + 1}行")
                break

        if start_index == -1 or end_index == -1:
            print("× 无法定位urlpatterns的完整范围")
            return content, False, "urlpatterns not found or invalid format"
        print(f"√ urlpatterns范围确定: 第{start_index + 1}行 到 第{end_index + 1}行")

        # 2.2 分析现有格式
        print("\n# 2.2 分析现有格式")
        existing_lines = lines[start_index + 1:end_index]
        print(f"→ urlpatterns中现有内容行数: {len(existing_lines)}")

        indent = ''
        for line in existing_lines:
            if line.strip() and not line.strip().startswith('#'):
                indent = line[:-len(line.lstrip())]
                print(f"√ 检测到缩进: {len(indent)}个空格")
                break

        if not indent:
            print("× 无法确定缩进格式")
            return content, False, "Cannot determine indentation"

        # 2.3 检查是否已存在
        print("\n# 2.3 检查URL配置是否已存在")
        pattern_checks = [
            f"path('{app_name}/'",  # 标准格式
            f'path("{app_name}/"',  # 双引号格式
            f"include('{app_name}.urls')",  # include 检查
            f'include("{app_name}.urls")',  # include 双引号检查
        ]
        for line in existing_lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            for pattern in pattern_checks:
                if pattern in line:
                    print(f"! 发现已存在的URL配置: {line}")
                    return content, False, f"URL pattern for {app_name} already exists in line: {line}"
        print("√ 未发现重复的URL配置")

        # 2.4 处理特殊情况：main应用
        print("\n# 2.4 生成URL配置")
        if app_name == 'main':
            url_pattern = f"{indent}path('', include('main.urls')),  # 主应用作为根URL"
            print("→ 生成main应用根URL配置")
        else:
            url_pattern = f"{indent}path('{app_name}/', include('{app_name}.urls')),"
            print("→ 生成标准应用URL配置")
        print(f"√ 生成的URL配置: {url_pattern}")

        # 2.5 插入新配置
        print("\n# 2.5 插入新配置")
        lines.insert(end_index, url_pattern)
        print(f"√ 在第{end_index + 1}行插入新配置")
        new_content = '\n'.join(lines)

        # 2.6 验证结果
        print("\n# 2.6 结果验证")
        valid, msg = validate_main_urls_result(new_content)
        if not valid:
            print(f"× 结果验证失败: {msg}")
            return content, False, f"Post-validation failed: {msg}"
        print("√ 结果验证通过")

        print("\n# 最终结果")
        print("√ URL配置更新成功")
        return new_content, True, url_pattern

    except Exception as e:
        print(f"\n× 处理过程出现异常: {str(e)}")
        return content, False, f"Error during modification: {str(e)}"


def validate_main_urls_content(content):
    """验证main urls文件的基本格式"""
    print("\n## 验证URLs内容基本格式")
    if not content.strip():
        print("× 文件内容为空")
        return False, "Empty content"
    if 'urlpatterns' not in content:
        print("× 未找到urlpatterns定义")
        return False, "No urlpatterns found"
    print("√ 基本格式验证通过")
    return True, ""


def validate_main_urls_syntax(content):
    """验证main urls文件的Python语法"""
    print("\n## 验证URLs Python语法")
    try:
        compile(content, '<string>', 'exec')
        print("√ Python语法验证通过")
        return True, ""
    except SyntaxError as e:
        print(f"× Python语法错误: {str(e)}")
        return False, str(e)


def validate_main_urls_result(new_content):
    """验证main urls文件修改后的内容"""
    print("\n## 验证URLs更新结果")
    try:
        # 1. 检查基本结构
        if 'urlpatterns' not in new_content:
            print("× urlpatterns在更新后丢失")
            return False, "urlpatterns lost after modification"
        print("√ 基本结构完整")

        # 2. 检查语法
        compile(new_content, '<string>', 'exec')
        print("√ 更新后的Python语法正确")

        # 3. 检查关键导入
        if 'from django.urls import' not in new_content:
            print("× 缺少django.urls导入")
            return False, "Missing django.urls import"

        # 更智能的导入检查
        imports_ok = False
        for line in new_content.split('\n'):
            if line.startswith('from django.urls import'):
                if 'path' in line and 'include' in line:
                    imports_ok = True
                    break

        if not imports_ok:
            print("× django.urls导入中缺少必要的组件(path或include)")
            return False, "Missing required components in django.urls import"

        print("√ 所有必要的导入语句都存在")

        # 4. 检查格式
        if new_content.count('[') != new_content.count(']'):
            print("× 方括号数量不匹配")
            return False, "Bracket mismatch"
        print("√ 代码格式正确")

        return True, ""
    except Exception as e:
        print(f"× 验证过程出现异常: {str(e)}")
        return False, str(e)


def update_main_urls(app_name, restore=False):
    """更新或恢复 Django 项目的 URL 配置"""
    from datetime import datetime
    print("\n=== URLs配置更新过程 ===")

    urls_path = 'config/urls.py'
    _, urls_backup_dir = get_backup_paths()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{urls_backup_dir}/urls.py.{timestamp}.bak'

    # 备份目录已在get_backup_paths中创建
    print(f"√ 使用备份目录: {urls_backup_dir}")

    # 获取最新的备份文件
    def get_latest_backup():
        if os.path.exists(urls_backup_dir):
            backups = sorted([f for f in os.listdir(urls_backup_dir)
                              if f.startswith('urls.py.') and f.endswith('.bak')],
                             reverse=True)
            if backups:
                latest = f'{urls_backup_dir}/{backups[0]}'
                return latest
            return None
        return None

    # 处理恢复操作
    if restore:
        latest_backup = get_latest_backup()
        if latest_backup:
            try:
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                print(f"? 已恢复URL配置文件至备份: {latest_backup}")
                return True
            except Exception as e:
                print(f"× 恢复URL配置文件失败: {str(e)}")
                return False
        else:
            print(f"× 未找到URL配置文件备份")
            return False

    try:
        print("\n# 开始更新配置")
        # 1. 创建新的备份
        if os.path.exists(urls_path):
            print(f"→ 发现现有配置文件: {urls_path}")
            try:
                with open(urls_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                print("√ 读取现有配置成功")

                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                print(f"√ 创建备份成功: {backup_path}")
            except Exception as e:
                print(f"! 备份过程出现问题: {str(e)}")
                raise e

        # 2. 读取当前配置
        print("\n# 读取当前配置")
        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("√ 读取当前配置成功")
        except Exception as e:
            print(f"× 读取配置文件失败: {str(e)}")
            raise e

        # 3. 处理内容
        print("\n# 开始处理配置内容")
        new_content, has_update, url_pattern = append_url_to_main_urls(content, app_name)

        if has_update:
            print("\n# 准备写入更新")
            print(f"→ 新的URL配置: {url_pattern}")

            # 4. 写入更新后的内容
            try:
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("√ 写入更新成功")
                return True
            except Exception as write_err:
                print(f"× 写入更新失败: {str(write_err)}")
                # 5. 如果写入失败，恢复备份
                print("! 尝试恢复备份")
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                print("√ 已恢复至备份状态")
                raise write_err
        else:
            print("\n! 内容无需更新")
            return False

    except Exception as e:
        print(f"\n× URLs配置更新失败: {str(e)}")
        # 6. 发生任何错误，确保恢复备份
        latest_backup = get_latest_backup()
        if latest_backup:
            print("! 尝试从最新备份恢复")
            try:
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                print("√ 已自动恢复至备份状态")
            except Exception as restore_err:
                print(f"× 恢复备份失败: {str(restore_err)}")
        return False

def verify_app_files(app_name, project_name, base_dir):
    """验证应用的关键配置文件内容"""
    try:
        # 定义需要验证的文件及其结构
        def verify_views_structure(content):
            """验证views.py文件的基本结构"""
            required_elements = [
                'from django.shortcuts import render',
                'def index(request):',
                'context = {',
                'return render(request,'
            ]
            return all(element in content for element in required_elements)

        # 定义需要验证的文件及其预期内容模板
        files_to_verify = {
            'urls.py': f'''"""
File: apps/{app_name}/urls.py
Purpose: {app_name}应用的URL配置
"""

from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
]
''',
            'apps.py': f'''"""
File: apps/{app_name}/apps.py
Purpose: {app_name}应用的配置类
Warning: 此文件由系统自动生成，请勿手动修改
"""

from django.apps import AppConfig

class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_name.title()}模块'
'''
        }

        verification_results = []

        # 验证项目URLs文件中的导入语句
        project_urls_path = base_dir / 'config' / 'urls.py'
        if project_urls_path.exists():
            with open(project_urls_path, 'r', encoding='utf-8') as f:
                urls_content = f.read()
                has_path_import = 'from django.urls import path' in urls_content
                has_include_import = 'include' in urls_content
                if has_path_import and has_include_import:
                    verification_results.append(('project_urls_imports', True, "URL导入语句配置正确"))
                else:
                    missing = []
                    if not has_path_import:
                        missing.append('path')
                    if not has_include_import:
                        missing.append('include')
                    verification_results.append(('project_urls_imports', False,
                                                 f"缺少必要的导入: {', '.join(missing)}"))

        for filename, expected_content in files_to_verify.items():
            file_path = base_dir / 'apps' / app_name / filename
            if not file_path.exists():
                verification_results.append((filename, False, "文件不存在"))
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
                content_matches = actual_content.strip() == expected_content.strip()
                if content_matches:
                    verification_results.append((filename, True, "内容正确"))
                else:
                    verification_results.append((filename, False, "内容不匹配期望值"))

        # 特殊处理views.py的验证
        views_path = base_dir / 'apps' / app_name / 'views.py'
        if views_path.exists():
            with open(views_path, 'r', encoding='utf-8') as f:
                views_content = f.read()
                if verify_views_structure(views_content):
                    verification_results.append(('views.py', True, "结构正确"))
                else:
                    verification_results.append(('views.py', False, "基本结构不符合要求"))
        else:
            verification_results.append(('views.py', False, "文件不存在"))

        return verification_results
    except Exception as e:
        return [(str(e), False, "验证过程出错")]


def check_app_exists(app_name, base_dir=None):
    """检查应用是否已存在

    Args:
        app_name (str): 应用名称
        base_dir (Path, optional): 项目根目录. 默认为当前目录

    Returns:
        bool: 如果应用已存在返回True，否则返回False
    """
    if base_dir is None:
        base_dir = Path.cwd()
    app_dir = base_dir / 'apps' / app_name
    return app_dir.exists()


def filter_new_apps(app_names, base_dir=None):
    """过滤出不存在的应用列表，并返回重复的应用列表

    Args:
        app_names (list): 要检查的应用名称列表
        base_dir (Path, optional): 项目根目录. 默认为当前目录

    Returns:
        tuple: (new_apps, duplicate_apps)
            - new_apps: 不存在的应用列表
            - duplicate_apps: 已存在的应用列表
    """
    new_apps = []
    duplicate_apps = []
    for app_name in app_names:
        if check_app_exists(app_name, base_dir):
            duplicate_apps.append(app_name)
        else:
            new_apps.append(app_name)
    return new_apps, duplicate_apps


def main():
    """主函数：处理参数并根据模式执行相应操作"""
    # 解析参数
    args = parse_arguments()

    # 优先处理guide参数
    if args.guide:
        guide_content = get_app_development_guide()
        output_path = Path(args.guide_output)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            print(f"\n✓ 开发指南已生成: {output_path}")
        except Exception as e:
            print(f"\n✗ 开发指南生成失败: {str(e)}")
        return

    # 优先处理restore参数
    if args.restore:
        print("\n=== 开始执行配置恢复 ===")
        if not check_project_exists(args.project):
            print(f"\n× 错误: 项目 {args.project} 不存在!")
            print("提示: 恢复配置需要在已存在的项目中执行")
            return

        # 切换到项目目录
        os.chdir(args.project)

        # 执行恢复操作 - 注意这里不需要应用名参数
        settings_restored = update_base_settings('', restore=True)
        urls_restored = update_main_urls('', restore=True)

        # 输出恢复结果
        print("\n=== 配置恢复结果 ===")
        print(f"INSTALLED_APPS配置: {'✓ 已恢复' if settings_restored else '× 恢复失败'}")
        print(f"URL配置: {'✓ 已恢复' if urls_restored else '× 恢复失败'}")
        print("\n=== 配置恢复执行完成 ===")
        return

    # 以下是原有的初始化和添加应用的逻辑
    project_name = args.project
    project_exists = check_project_exists(project_name)

    global INITIAL_APPS

    # 根据模式和项目存在状态处理
    if args.mode == MODE_INIT:
        if project_exists:
            print(f"\n× 错误: 项目 {project_name} 已存在!")
            print("提示: 如果要在现有项目中添加应用，请使用 --mode add")
            return

        # 确定应用列表
        if args.apps is not None:
            INITIAL_APPS = args.apps

        # 创建项目目录结构
        create_project_structure(project_name)

        # 切换到项目目录进行应用检测
        os.chdir(project_name)

        # 检测重复应用
        new_apps, duplicate_apps = filter_new_apps(INITIAL_APPS)

        if not new_apps:
            print("\n! 注意: 所有指定的应用都已存在，跳过处理")
            if duplicate_apps:
                print("  重复的应用:", ", ".join(duplicate_apps))
            return

        # 更新INITIAL_APPS为新应用列表
        INITIAL_APPS = new_apps

        # 显示重复应用信息
        if duplicate_apps:
            print("\n! 以下应用已存在，将跳过处理:")
            print("  ", ", ".join(duplicate_apps))

        # 显示将要执行的操作
        print(f"\n初始化项目：{project_name}")
        print(f"创建应用：{', '.join(INITIAL_APPS) if INITIAL_APPS else '无'}")
        print("(使用默认配置)" if args.mode == MODE_INIT and args.project is None and args.apps is None else "")

        # 初始化项目
        initialize_django_project(project_name)

    elif args.mode == MODE_ADD_APP:
        if not project_exists:
            print(f"\n! 项目 {project_name} 不存在，将以初始化模式创建项目")
            INITIAL_APPS = args.apps if args.apps is not None else INITIAL_APPS

            # 创建项目目录结构
            create_project_structure(project_name)


            # 检测重复应用
            new_apps, duplicate_apps = filter_new_apps(INITIAL_APPS)

            if not new_apps:
                print("\n! 注意: 所有指定的应用都已存在，跳过处理")
                if duplicate_apps:
                    print("  重复的应用:", ", ".join(duplicate_apps))
                return

            # 更新INITIAL_APPS为新应用列表
            INITIAL_APPS = new_apps

            # 显示重复应用信息
            if duplicate_apps:
                print("\n! 以下应用已存在，将跳过处理:")
                print("  ", ", ".join(duplicate_apps))

            initialize_django_project(project_name)
        else:
            if not args.apps:
                print("\n× 错误: 添加应用模式需要指定至少一个应用名称")
                return

            # 检查apps目录
            apps_dir = Path.cwd() / 'apps'
            if not apps_dir.exists():
                print("\n× 错误: apps目录不存在，请检查项目结构")
                return

            # 检测重复应用
            new_apps, duplicate_apps = filter_new_apps(args.apps)

            if not new_apps:
                print("\n! 注意: 所有指定的应用都已存在，跳过处理")
                if duplicate_apps:
                    print("  重复的应用:", ", ".join(duplicate_apps))
                return

            # 显示重复应用信息
            if duplicate_apps:
                print("\n! 以下应用已存在，将跳过处理:")
                print("  ", ", ".join(duplicate_apps))

            # 创建新应用
            for app_name in new_apps:
                create_app_structure(app_name, project_name, Path.cwd())
                print(f"\n√ 应用 {app_name} 创建成功!")

                if args.auto_update:
                    print("\n=== 开始自动更新配置 ===")
                    settings_updated = update_base_settings(app_name)
                    urls_updated = update_main_urls(app_name)

                    print("\n=== 配置更新结果 ===")
                    print(f"INSTALLED_APPS配置: {'✓ 已更新' if settings_updated else '× 更新失败'}")
                    print(f"URL配置: {'✓ 已更新' if urls_updated else '× 更新失败'}")

                    generate_manual_config_guide(app_name, project_name, Path.cwd(), auto_updated=True)
                else:
                    generate_manual_config_guide(app_name, project_name, Path.cwd(), auto_updated=False)



def execute_django_commands():
    """执行Django必要的初始化命令"""
    print("\n开始执行Django初始化命令...")
    try:
        current_dir = os.getcwd()
        print(f"→ 当前目录: {current_dir}")

        # 检查manage.py是否存在
        manage_py_path = os.path.join(current_dir, 'manage.py')
        print(f"→ 检查manage.py是否存在: {'是' if os.path.exists(manage_py_path) else '否'}")

        if not os.path.exists(manage_py_path):
            print("! 未找到manage.py文件，无法执行Django命令")
            return

        print("\n执行数据库迁移...")
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'],
                                capture_output=True,
                                text=True,
                                check=True)
        print(result.stdout)

        print("\n检查项目配置...")
        result = subprocess.run([sys.executable, 'manage.py', 'check'],
                                capture_output=True,
                                text=True,
                                check=True)
        print(result.stdout)

        print("\n✓ Django命令执行完成!")
        print("\n后续开发提示:")
        print(f"1. 请先进入项目目录: cd {os.path.basename(os.getcwd())}")
        print("2. 启动开发服务器: python manage.py runserver")
        print("\n浏览器访问指南:")
        print("1. 项目主页: http://127.0.0.1:8000")
        print("2. 后台管理: http://127.0.0.1:8000/admin")
        print("   - 需要先创建管理员账号: python manage.py createsuperuser")
        print("   - 按提示设置用户名和密码(密码输入时不显示)")
        print("   - 需要输入邮箱地址，格式必须是email格式(如abc@example.com)")
        print("   - 邮箱地址不会被验证，仅作为管理员联系方式记录")
        print("3. API浏览器: http://127.0.0.1:8000/api")
        print("4. 其他应用URL:")
        for app in INITIAL_APPS:
            if app != 'main':  # main应用已经在根URL
                print(f"   - {app.title()}模块: http://127.0.0.1:8000/{app}")

    except subprocess.CalledProcessError as e:
        print(f"\n! Django命令执行失败:")
        print(f"错误代码: {e.returncode}")
        print(f"命令输出: {e.output}")
    except Exception as e:
        print(f"\n! 执行Django命令时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == '__main__':
    print("\n=== 开始执行项目初始化 ===")
    main()
    # 只有在非恢复模式下才执行Django命令
    if not any(arg in sys.argv for arg in ['--restore']):
        print("\n=== 项目初始化完成，准备执行Django命令 ===")
        execute_django_commands()
    print("\n=== 所有操作执行完成 ===")
