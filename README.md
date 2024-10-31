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
- ⚡ 开发环境自动配置
- 📚 完整的文档生成

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

3. 创建项目并指定应用：
```bash
python django_project_init.py -p myproject -a user blog admin
```

### 在现有项目中添加应用

1. 手动配置模式：
```bash
python django_project_init.py --mode add -p myproject -a newapp
```

2. 自动配置模式：
```bash
python django_project_init.py --mode add -p myproject -a newapp --auto-update
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
├── docs/              # 文档
├── utils/            # 工具函数
├── .env             # 环境变量
└── README.md        # 项目说明
```

### 应用目录结构

```
app_name/
├── migrations/           # 数据库迁移
├── templates/           # 应用模板
│   └── app_name/       # 应用特定模板
│       └── components/ # 组件模板
├── static/             # 应用静态文件
│   └── app_name/      # 应用特定静态文件
│       ├── css/       # 样式文件
│       ├── js/        # JavaScript文件
│       └── images/    # 图片资源
├── api/                # REST API
│   ├── serializers.py # API序列化器
│   ├── views.py       # API视图
│   └── urls.py        # API路由配置
├── services/          # 业务服务层
│   └── data_service.py
├── helpers/           # 辅助函数
│   └── formatters.py
├── tests/            # 测试文件
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services/
├── management/       # 管理命令
│   └── commands/
│       └── process_data.py
├── models.py         # 数据模型
├── views.py         # 视图
├── urls.py          # URL配置
├── forms.py         # 表单
├── apps.py         # 应用配置
├── admin.py       # 管理接口
├── constants.py   # 常量定义
├── exceptions.py  # 自定义异常
└── utils.py      # 工具函数
```

## 详细使用说明

### 运行模式

脚本支持三种运行模式：

1. **初始化模式（init）**
   - 创建新的Django项目
   - 生成完整的目录结构
   - 配置基础设置

2. **添加应用模式（add）**
   - 在现有项目中创建新应用
   - 可选择自动更新配置
   - 生成配置指南

3. **恢复模式（restore）**
   - 恢复配置文件到最近的备份
   - 支持增量恢复

### 命令行参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| --mode | 运行模式 | init | --mode init |
| -p, --project | 项目名称 | 当前目录名 | -p myproject |
| -a, --apps | 要创建的应用列表 | ['main'] | -a user blog |
| --auto-update | 自动更新配置（add模式可用） | False | --auto-update |
| --restore | 还原配置到最新备份 | False | --restore |

### 文件影响说明

#### add模式（不带--auto-update）:
- ✅ 完全不修改任何现有文件
- ℹ️ 只在apps目录下创建新的应用
- 📝 生成配置指南文件（CONFIG_GUIDE.md）

#### add模式（带--auto-update）:
- 🔄 修改两个配置文件：
  - `config/settings/base.py`：添加新应用
  - `config/urls.py`：添加URL配置
- ⚡ 自动备份修改的文件到：
  - `config/app_append_backups/base_backups/`
  - `config/app_append_backups/urls_backups/`

#### restore模式:
- 🔄 只恢复配置文件
- ⚠️ 不影响已创建的应用文件
- 🛡️ 提供安全的配置回滚机制

## 后续步骤

### 1. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装开发环境依赖
pip install -r requirements/local.txt
```

### 3. 初始化数据库
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户
```bash
python manage.py createsuperuser
```

### 5. 运行开发服务器
```bash
python manage.py runserver
```

## 常见问题

### 1. 权限问题
```bash
# Linux/Mac下赋予执行权限
chmod +x django_project_init.py
```

### 2. 编码问题
```bash
# Windows下可能需要设置
set PYTHONIOENCODING=utf-8
```

### 3. 路径问题
```bash
# 确保在正确的目录运行脚本
cd target_directory
python path/to/django_project_init.py
```

### 4. ModuleNotFoundError
如果遇到"No module named 'xxx'"错误：
- 检查虚拟环境是否激活
- 验证依赖是否正确安装
- 确认apps目录在Python路径中

### 5. 配置问题
如果配置更新失败：
- 检查备份目录中的文件
- 使用--restore参数恢复
- 查看CONFIG_GUIDE.md获取手动配置指导

## 开发建议

### 1. 版本控制
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"
```

### 2. 测试实践
```bash
# 运行测试
python manage.py test

# 运行覆盖率测试
coverage run --source='.' manage.py test
coverage report
```

### 3. 代码质量
```bash
# 运行代码检查
flake8
black .
isort .
```

## 部署建议

1. 使用环境变量管理敏感配置
2. 在生产环境中：
   - 使用 production.py 设置
   - 配置 proper ALLOWED_HOSTS
   - 禁用 DEBUG 模式
   - 使用安全的 SECRET_KEY

## 安全说明

1. 自动备份机制
   - 所有配置修改都会创建备份
   - 备份文件使用时间戳命名
   - 支持配置回滚

2. 文件处理策略
   - 新增：只添加不覆盖
   - 修改：自动创建备份
   - 恢复：支持选择性恢复

## 项目贡献

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 致谢

- Django 项目组
- Python 社区
- 所有贡献者

## 维护者

- [@your-username](https://github.com/your-username)
- [@another-maintainer](https://github.com/another-maintainer)

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
