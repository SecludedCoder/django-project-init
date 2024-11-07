# Django Project Init

一个用于快速创建和管理Django项目结构的命令行工具。它可以帮助您：
- 创建遵循最佳实践的Django项目结构
- 轻松添加新的Django应用
- 自动处理配置文件和URL路由
- 提供完整的备份和恢复机制

## 功能特点

- 📁 创建组织良好的项目目录结构
- 🔧 智能配置管理（settings分环境）
- 🚀 快速添加新应用
- 📋 自动更新配置文件
- 💾 配置文件自动备份
- 📝 集成日志系统（自动配置各应用日志）
- ⚡ 开发环境自动配置
- 📚 完整的文档生成
- 🔄 集成REST Framework和Swagger

## 系统要求

- Python 3.10+
- Django 5.0+

## 安装

1. 下载脚本文件：
```bash
curl -O https://raw.githubusercontent.com/your-username/django-project-init/main/django_project_init.py
```

2. 添加执行权限（Linux/Mac）：
```bash
chmod +x django_project_init.py
```

## 应用命名限制

⚠️ 由于与Django内置应用的命名冲突问题，以下名称不能用于创建新应用：

- `admin`（建议使用 `management` 或 `administration` 代替）
- `auth`（建议使用 `authentication` 或 `accounts` 代替）
- `contenttypes`
- `sessions`
- `messages`
- `staticfiles`（建议使用 `assets` 或 `resources` 代替）

如果尝试使用这些名称，脚本会提供错误提示并建议替代名称。

## 快速开始

### 创建新项目

1. 基本用法（使用默认设置）：
```bash
python django_project_init.py
```

2. 指定项目名称：
```bash
python django_project_init.py -p myproject
```

3. 创建项目并指定应用（注意避免使用受限名称）：
```bash
python django_project_init.py -p myproject -a accounts dashboard
```

### 在现有项目中添加应用

1. 手动配置模式：
```bash
python django_project_init.py --mode add -p myproject -a customer_service
```

2. 自动配置模式：
```bash
python django_project_init.py --mode add -p myproject -a accounts --auto-update
```

### 导出开发指南

1. 使用默认文件名：
```bash
python django_project_init.py --guide
```

2. 指定输出文件：
```bash
python django_project_init.py --guide --guide-output custom_guide.md
```

### 恢复配置文件

如果需要还原之前的配置：
```bash
python django_project_init.py -p myproject --restore
```

## 项目结构

```
project_name/
├── manage.py                # Django管理脚本
├── requirements/            # 依赖管理
│   ├── base.txt            # 基础依赖
│   ├── local.txt           # 开发环境依赖
│   └── production.txt      # 生产环境依赖
├── config/                 # 项目配置
│   ├── settings/          # 分环境配置
│   │   ├── base.py       # 基础配置
│   │   ├── local.py      # 开发环境配置
│   │   ├── logging_config.py # 日志配置
│   │   └── production.py # 生产环境配置
│   ├── urls.py            # URL配置
│   ├── asgi.py           # ASGI服务器配置
│   └── wsgi.py           # WSGI服务器配置
├── apps/                  # 应用目录
│   └── [应用名]/         # 各个应用目录
├── templates/            # 项目级模板
│   └── shared/          # 共享模板
├── static/              # 静态文件
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── images/         # 图片资源
├── media/              # 上传文件
├── logs/               # 日志文件目录
│   ├── debug_YYYYMMDD.log    # 调试日志
│   ├── info_YYYYMMDD.log     # 信息日志
│   └── error_YYYYMMDD.log    # 错误日志
├── docs/               # 文档
│   ├── api.md                                                      # API接口文档
│   ├── deployment.md                                               # 部署文档
│   ├── api_design_guide.md                                        # API设计指南(精简版)
│   └── django_rest_api_lightweight_specification_and_implementation_guide.md # API设计规范与实现指南
├── common/            # 工具函数
├── .env              # 环境变量
└── README.md         # 项目说明
```

### 应用目录结构

```
app_name/
├── migrations/           # 数据库迁移
├── core/                # 核心业务逻辑目录
│   ├── __init__.py
│   ├── services/       # 核心服务实现
│   ├── models/        # 核心数据模型（非ORM）
│   ├── utils/         # 核心工具函数
│   └── exceptions/    # 核心异常定义
├── bootstrap.py        # 应用启动器
├── models/             # [更新] Django模型目录
│   ├── __init__.py    # 导出所有模型
│   └── base.py        # 基础模型定义
├── views/             # [更新] 视图目录
│   ├── __init__.py    # 导出所有视图
│   └── base.py        # 基础视图定义
├── forms/             # [更新] 表单目录
│   ├── __init__.py    # 导出所有表单
│   └── base.py        # 基础表单定义
├── templates/          # 应用模板
│   └── app_name/      # 应用特定模板
│       └── components/ # 组件模板
├── static/            # 应用静态文件
│   └── app_name/     # 应用特定静态文件
│       ├── css/      # 样式文件
│       ├── js/       # JavaScript文件
│       └── images/   # 图片资源
├── api/               # REST API
│   ├── serializers.py # API序列化器
│   ├── views.py      # API视图
│   └── urls.py       # API路由配置
├── services/         # 业务服务层（集成层）
│   └── app_facade.py # Django集成服务
├── helpers/          # 辅助函数
│   └── formatters.py
├── tests/           # 测试文件
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services/
├── management/      # 管理命令
│   └── commands/
│       └── process_data.py
├── urls.py          # URL配置
├── apps.py         # 应用配置
├── admin.py       # 管理接口
├── constants.py   # 常量定义
├── exceptions.py  # Django相关异常
└── utils.py      # Django相关工具函数
```

## 版本历史

- 1.0.0 (2024-01-01)
  - 初始发布
  - 支持基本项目初始化
  - 添加应用功能
  - 配置备份和恢复

## 路线图

- [ ] 支持自定义模板
- [ ] Docker集成
- [ ] CI/CD配置生成
- [ ] 国际化支持
