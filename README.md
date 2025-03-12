# WeChat Robot

一个灵活、易维护、易扩展的微信机器人项目，用于连接微信公众号和企业微信与各种AI服务提供商。

## 项目结构

```
WeChatRobot
├── app/
│   ├── adapters/                # 适配器 - 连接不同来源和服务
│   │   ├── source_adapters/     # 消息来源适配器 (微信公众号、企业微信)
│   │   │   ├── base_adapter.py  # 基础适配器接口
│   │   │   ├── wechat_adapter.py # 微信公众号适配器
│   │   │   └── wecom_adapter.py  # 企业微信适配器
│   ├── config/                  # 配置
│   │   └── config.py            # 配置类
│   ├── core/                    # 核心功能
│   │   ├── router.py            # 主路由 - 处理URL路径参数
│   │   └── source_processor.py  # 消息来源处理
│   ├── handlers/                # 消息处理
│   ├── models/                  # 数据模型
│   ├── services/                # 服务层
│   │   ├── provider_services/   # AI提供商服务
│   │   │   ├── base_service.py  # 基础服务接口
│   │   │   ├── groq_service.py  # Groq服务实现
│   │   │   └── tencent_service.py # 腾讯服务实现
│   ├── utils/                   # 工具函数
│   │   └── celery_utils.py      # Celery工具
│   └── __init__.py              # 应用工厂
├── .env                         # 环境变量
├── celery_worker.py             # Celery Worker入口
└── run.py                       # 应用入口
```

## 功能特点

1. **灵活的路由系统**: 基于URL路径参数进行路由，可以轻松区分不同的消息来源和AI服务提供商
   - `/wechat/Groq` - 微信公众号使用Groq处理
   - `/wecom/Tencent` - 企业微信使用腾讯AI处理
   - `/wechat/Groq/DS-R1-70B` - 微信公众号使用Groq上的特定模型

2. **易扩展的适配器设计**: 
   - 消息来源适配器 - 可以轻松添加新的来源（如飞书等）
   - AI服务提供商适配器 - 可以轻松添加新的服务提供商

3. **异步处理**: 使用Celery进行异步任务处理，提供更好的用户体验

4. **配置集中化**: 所有配置都集中在一个环境变量文件中，便于管理

## 开始使用

1. 为`.env`并填写相应的配置信息

2. 安装依赖
   ```
   pip install -r requirements.txt
   ```

3. 启动Redis服务（用于Celery）

4. 启动应用
   ```
   FLASK_APP=run.py FLASK_DEBUG=1 flask run --port=xxxx
   ```

5. 在另一个终端启动Celery worker
   ```
   celery -A celery_worker.celery worker --loglevel=info
   ```

## 使用示例

### 配置微信公众号

将微信公众号的服务器URL设置为:
```
http://your-domain/source/ai-provider
```

### 配置企业微信

将企业微信的服务器URL设置为:
```
http://your-domain/source/ai-provider
```

## 扩展项目

### 添加新的消息来源

1. 在`app/adapters/source_adapters/`目录下创建新的适配器类
2. 实现`BaseSourceAdapter`接口
3. 无需修改路由设置，系统会自动处理

### 添加新的AI服务提供商

1. 在`app/services/provider_services/`目录下创建新的服务类
2. 实现`BaseProviderService`接口
3. 无需修改路由设置，系统会自动处理

## 作者

jackingoole520@gmail.com