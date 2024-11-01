# Django补充开发规范

## 一、Forms规范

### 1.1 基础表单结构
```python
from django import forms
from django.utils.translation import gettext_lazy as _

class BaseForm(forms.Form):
    """表单基类"""
    
    def clean(self):
        """通用清理方法"""
        cleaned_data = super().clean()
        self._validate_business_rules(cleaned_data)
        return cleaned_data
    
    def _validate_business_rules(self, cleaned_data):
        """业务规则验证"""
        pass

class BaseModelForm(forms.ModelForm):
    """模型表单基类"""
    
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_fields()
    
    def _configure_fields(self):
        """配置字段属性"""
        pass
```

### 1.2 表单验证
```python
class UserProfileForm(BaseModelForm):
    """用户资料表单示例"""
    
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password']
        
    def clean_password_confirm(self):
        """自定义字段验证"""
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_("Passwords don't match"))
        
        return password_confirm
```

## 二、URL配置规范

### 2.1 URL组织
```python
# urls/
# ├── __init__.py
# ├── base.py
# ├── api.py
# └── admin.py

# base.py
from django.urls import path, include

app_name = 'myapp'

urlpatterns = [
    path('', include('myapp.urls.web')),
    path('api/', include('myapp.urls.api')),
    path('admin/', include('myapp.urls.admin')),
]
```

### 2.2 URL命名规范
```python
# web.py
urlpatterns = [
    # 列表页面: {model_name}_list
    path('users/', views.UserListView.as_view(), name='user_list'),
    
    # 详情页面: {model_name}_detail
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # 创建页面: {model_name}_create
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    
    # 更新页面: {model_name}_update
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    
    # 删除页面: {model_name}_delete
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]
```

## 三、Admin配置规范

### 3.1 Admin基类
```python
from django.contrib import admin

class BaseModelAdmin(admin.ModelAdmin):
    """Admin基类"""
    
    list_per_page = 20
    save_on_top = True
    
    def get_readonly_fields(self, request, obj=None):
        """获取只读字段"""
        if obj:  # 编辑时
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """保存时的额外处理"""
        if not change:  # 创建时
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
```

### 3.2 Admin定制
```python
@admin.register(User)
class UserAdmin(BaseModelAdmin):
    list_display = ['username', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'groups']
    search_fields = ['username', 'email']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('username', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'groups'),
            'classes': ('collapse',)
        }),
    )
```

## 四、Middleware规范

### 4.1 中间件结构
```python
from django.utils.deprecation import MiddlewareMixin

class BaseMiddleware(MiddlewareMixin):
    """中间件基类"""
    
    def process_request(self, request):
        """请求处理"""
        pass
    
    def process_response(self, request, response):
        """响应处理"""
        return response
    
    def process_exception(self, request, exception):
        """异常处理"""
        pass
```

### 4.2 自定义中间件
```python
class AuditMiddleware(BaseMiddleware):
    """审计中间件"""
    
    def process_request(self, request):
        request.audit_data = {
            'start_time': timezone.now(),
            'user': request.user if request.user.is_authenticated else None,
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    
    def process_response(self, request, response):
        if hasattr(request, 'audit_data'):
            AuditLog.objects.create(
                user=request.audit_data['user'],
                action=request.method,
                ip_address=request.audit_data['ip_address'],
                url=request.path,
                execution_time=timezone.now() - request.audit_data['start_time'],
                response_code=response.status_code
            )
        return response
```

## 五、Settings配置规范

### 5.1 设置分层
```
config/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   └── test.py
├── urls.py
└── wsgi.py
```

### 5.2 设置组织
```python
# base.py
from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Core settings
DEBUG = False
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    # ...
    'myapp.apps.MyAppConfig',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

# development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Add development specific settings
```

## 六、Signals规范

### 6.1 信号定义
```python
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

# 自定义信号
user_registered = Signal()  # providing_args=['user', 'request']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时创建资料"""
    if created:
        Profile.objects.create(user=instance)
```

### 6.2 信号注册
```python
# apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'
    
    def ready(self):
        """注册信号"""
        import myapp.signals
```

## 七、Management Commands规范

### 7.1 命令结构
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Command description'
    
    def add_arguments(self, parser):
        """添加命令参数"""
        parser.add_argument('--days', type=int, default=7)
    
    def handle(self, *args, **options):
        """命令处理逻辑"""
        try:
            # 执行命令逻辑
            self.stdout.write(self.style.SUCCESS('Command executed successfully'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
```

### 7.2 命令组织
```
management/
├── __init__.py
└── commands/
    ├── __init__.py
    ├── cleanup_data.py
    ├── generate_report.py
    └── sync_external.py
```

## 八、Cache规范

### 8.1 缓存配置
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 缓存中间件
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# 缓存设置
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ''
```

### 8.2 缓存使用
```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存15分钟
def view_function(request):
    pass

class CachedView:
    def get_data(self, key):
        """获取缓存数据"""
        data = cache.get(key)
        if data is None:
            data = self.compute_data()
            cache.set(key, data, timeout=3600)
        return data
```

## 九、Celery任务规范

### 9.1 任务定义
```python
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def process_data_task(self, data_id):
    """处理数据的异步任务"""
    try:
        # 任务逻辑
        logger.info(f"Processing data {data_id}")
    except Exception as exc:
        logger.error(f"Error processing data {data_id}: {exc}")
        self.retry(exc=exc, countdown=60)
```

### 9.2 Celery配置
```python
# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# 任务配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

## 十、测试规范

### 10.1 测试组织
```
tests/
├── __init__.py
├── conftest.py
├── factories/
│   ├── __init__.py
│   └── user.py
├── integration/
│   ├── __init__.py
│   └── test_views.py
└── unit/
    ├── __init__.py
    ├── test_models.py
    └── test_services.py
```

### 10.2 测试用例
```python
import pytest
from django.test import TestCase
from django.urls import reverse

class TestUserViews(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.client.login(username=self.user.username, password='password')
    
    def test_user_list_view(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_list.html')
```

## 十一、日志规范

### 11.1 日志配置
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'myapp': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 11.2 日志使用
```python
import logging

logger = logging.getLogger(__name__)

class UserService:
    def create_user(self, data):
        try:
            user = User.objects.create(**data)
            logger.info(f"User created: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
```

## 十二、API规范

### 12.1 序列化器
```python
from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    """序列化器基类"""
    
    def validate(self, attrs):
        """通用验证"""
        attrs = super().validate(attrs)
        self._validate_business_rules(attrs)
        return attrs
    
    def _validate_business_rules(self, attrs):
        """业务规则验证"""
        pass

class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['created_at']
```

### 12.2 API视图
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet基类"""
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """创建时的额外处理"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """更新时的额外处理"""
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)

class UserViewSet(BaseViewSet):
    """用户API示例"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
```

## 十三、静态文件规范

### 13.1 静态文件组织
```
static/
├── css/
│   ├── base/
│   │   ├── _variables.scss
│   │   └── _mixins.scss
│   ├── components/
│   │   └── _buttons.scss
│   └── main.scss
├── js/
│   ├── utils/
│   │   └── api.js
│   ├── components/
│   │   └── modal.js
│   └── main.js
└── images/
    ├── logos/
    └── icons/
```

### 13.2 静态文件配置
```python
# settings/base.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# 文件压缩
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

## 十四、媒体文件规范

### 14.1 媒体文件配置
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 文件上传配置
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# 最大上传大小
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### 14.2 文件处理
```python
class MediaFileService:
    """媒体文件处理服务"""
    
    def save_file(self, file_obj, path=None):
        """保存文件"""
        if path is None:
            path = default_storage.generate_filename(file_obj.name)
        
        path = default_storage.save(path, file_obj)
        return path
    
    def delete_file(self, path):
        """删除文件"""
        if default_storage.exists(path):
            default_storage.delete(path)
```

## 十五、国际化规范

### 15.1 国际化配置
```python
# settings/base.py
from django.utils.translation import gettext_lazy as _

USE_I18N = True
USE_L10N = True

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', _('English')),
    ('zh-hans', _('Simplified Chinese')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    # ...
]
```

### 15.2 翻译使用
```python
# models.py
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Category name')
    )
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
```

## 十六、安全规范

### 16.1 安全设置
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session安全
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# 安全头部
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 16.2 密码处理
```python
from django.contrib.auth.hashers import make_password, check_password

class UserService:
    def set_password(self, user, password):
        """设置用户密码"""
        user.password = make_password(password)
        user.save(update_fields=['password'])
    
    def check_password(self, user, password):
        """验证用户密码"""
        return check_password(password, user.password)
```

## 十七、部署规范

### 17.1 WSGI配置
```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
```

### 17.2 ASGI配置
```python
# asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
```

## 十八、Docker配置规范

### 18.1 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE config.settings.production

# 创建工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 复制项目文件
COPY . /app/

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 18.2 Docker Compose
```yaml
# docker-compose.yml
version: '3'

services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env
  
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
  
  redis:
    image: redis:6

volumes:
  postgres_data:
```

## 十九、监控规范

### 19.1 健康检查
```python
from django.http import JsonResponse
from django.db import connections
from redis import Redis
from django.core.cache import cache

def health_check(request):
    """系统健康检查"""
    checks = {
        'database': _check_database(),
        'cache': _check_cache(),
        'redis': _check_redis(),
    }
    
    status = 'healthy' if all(c['status'] == 'ok' for c in checks.values()) else 'unhealthy'
    
    return JsonResponse({
        'status': status,
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    })

def _check_database():
    try:
        connections['default'].cursor()
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

### 19.2 性能监控
```python
from django.db import connection
from django.conf import settings
import time

class PerformanceMiddleware:
    """性能监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # 清除之前的查询
        connection.queries_log.clear()
        
        response = self.get_response(request)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 在调试模式下记录性能数据
        if settings.DEBUG:
            response['X-Execution-Time'] = f"{execution_time:.2f}s"
            response['X-Query-Count'] = str(len(connection.queries))
        
        return response
```

## 二十、文档生成规范

### 20.1 API文档
```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
```

### 20.2 代码文档
```python
from django.utils.safestring import mark_safe
import docutils.core

def generate_docs(app_name):
    """生成应用文档"""
    app_path = apps.get_app_config(app_name).path
    docs = []
    
    for model in apps.get_app_config(app_name).get_models():
        # 收集模型文档
        model_doc = {
            'name': model.__name__,
            'description': model.__doc__,
            'fields': _get_model_fields(model),
            'methods': _get_model_methods(model),
        }
        docs.append(model_doc)
    
    return docs

def _get_model_fields(model):
    """获取模型字段文档"""
    return [
        {
            'name': field.name,
            'type': field.get_internal_type(),
            'help_text': field.help_text,
        }
        for field in model._meta.fields
    ]
```