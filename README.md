# Jira Task Creator
Jira 任务创建和管理技能，支持自然语言解析、批量操作和智能搜索。

## 功能特性

- 🎯 **智能任务创建**: 支持自然语言解析、相对日期、批量操作
- 🔍 **高级用户搜索**: 多方式查找、用户映射、智能缓存
- 📊 **任务统计分析**: 多维度统计、过期识别、工作负载分析
- 📋 **任务模板系统**: Bug 报告、功能请求、技术预研
- ⏰ **智能提醒系统**: 到期提醒、过期警告、批量汇总

## 快速开始

```bash
# 安装依赖
pip install requests python-dateutil

# 配置环境变量
export JIRA_BASE_URL="http://pm.ulanzi.cn:8020/"
export JIRA_BEARER_TOKEN="your-token-here"

# 使用示例
python -c "from jira_task_creator import create_issue; print(create_issue('测试任务', '任务描述'))"
```

## 核心功能

### 1. 自然语言任务创建
```python
from jira_task_creator import create_issue_natural

result = create_issue_natural(
    "下周三完成贾小丽负责的API开发任务，高优先级"
)
```

### 2. 智能用户搜索
```python
from jira_task_creator import search_user

user = search_user("贾小丽", "ERP")
print(f"用户名: {user['name']}")
print(f"显示名称: {user['displayName']}")
```

### 3. 批量任务创建
```python
from batch_creator import BatchTaskCreator

creator = BatchTaskCreator(base_url, token)
results = creator.create_from_csv("tasks.csv")
```

### 4. 任务统计分析
```python
from task_analyzer import TaskAnalyzer

analyzer = TaskAnalyzer()
analysis = analyzer.analyze_tasks(tasks)
report = analyzer.generate_report(analysis)
print(report)
```

## 文档

- [SKILL.md](SKILL.md) - 完整技能说明
- [README.md](README.md) - 使用指南和 API 参考

## 许可证

MIT License
