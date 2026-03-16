# Jira 任务修改流程 Skill

**版本**: 2.1.0
**更新时间**: 2026-03-16 18:18
**作者**: 皮皮虾

---

## 🎯 功能概览

### 核心功能

#### 1. 任务创建
- ✅ **智能任务创建** - 支持自然语言解析、相对日期
- ✅ **高级用户搜索** - 多方式查找、用户映射、智能缓存
- ✅ **任务模板系统** - Bug 报告、功能请求、技术预研

#### 2. 任务修改 ⭐
- ✅ **字段更新** - 支持摘要、描述、备注等字段
- ✅ **状态更新** - 通过 Transitions API 更新任务状态
- ✅ **批量更新** - 同时更新多个任务
- ✅ **我的任务列表** - 获取当前用户的任务列表

---

## 📋 API 函数列表

### 任务创建
```python
def create_issue(summary, description=None, project_key=None,
                issue_type_name=None, priority=None, assignee=None,
                due_date=None):
    """创建 Jira Issue"""
```

### 任务搜索
```python
def search_issues(jql_query, fields=None, max_results=50):
    """搜索 Jira Issues"""
```

### 用户搜索
```python
def search_user(query, project_key=None):
    """搜索用户（便捷函数）"""
```

### 字段更新 ⭐ 新功能
```python
def update_issue_fields(issue_key, **fields):
    """更新 Issue 字段（通用函数）

    支持更新多个字段，包括：
    - summary: 摘要
    - description: 描述
    - priority: 优先级
    - assignee: 责任人
    - reporter: 报告人
    - duedate: 到期时间
    - timetracking: 已工作时长（timetracking.remainingEstimate, timetracking.timeSpent）
    - customfield_xxx: 自定义字段

    Args:
        issue_key: Issue Key（如 ERP-123）
        **fields: 要更新的字段（关键字参数）

    Returns:
        dict: 包含 success, error, updated_fields 等信息
    """

def bulk_update_issue_fields(issue_keys, **fields):
    """批量更新多个 Issue 的字段

    Args:
        issue_keys: Issue Key 列表
        **fields: 要更新的字段（关键字参数）

    Returns:
        list: 每个任务的更新结果
    """

def get_issue_details(issue_key, fields=None):
    """获取 Issue 详细信息

    Args:
        issue_key: Issue Key（如 ERP-123）
        fields: 要返回的字段列表（None=返回所有字段）

    Returns:
        dict: 包含 success, issue_data 等信息
    """
```

### 状态转换管理
```python
def get_issue_transitions(issue_key):
    """获取 Issue 的可用状态转换"""

def transition_issue(issue_key, transition_id):
    """执行 Issue 状态转换"""

def update_issue_status(issue_key, target_status):
    """更新 Issue 状态（便捷函数）"""

def bulk_transition_issues(issue_keys, target_status):
    """批量更新多个 Issue 状态"""

def get_my_issues(status_filter=None, project_key=None, max_results=50):
    """获取我的 Issue 列表（便捷函数）"""
```

---

## 🔧 使用示例

### 1. 更新任务摘要
```python
from jira_task_creator import update_issue_fields

result = update_issue_fields(
    issue_key="WK-766",
    summary="更新后的任务摘要"
)

if result["success"]:
    print(f"摘要已更新: {result['updated_fields']}")
else:
    print(f"更新失败: {result['error']}")
```

### 2. 更新任务描述
```python
result = update_issue_fields(
    issue_key="WK-766",
    description="## 详细描述\n\n任务的具体内容和要求..."
)
```

### 3. 更新责任人
```python
result = update_issue_fields(
    issue_key="WK-766",
    assignee="Cloud"  # 可以是用户名、邮箱或 open_id
)
```

### 4. 更新到期时间
```python
result = update_issue_fields(
    issue_key="WK-766",
    duedate="明天"  # 支持相对日期
)
```

### 5. 更新优先级
```python
result = update_issue_fields(
    issue_key="WK-766",
    priority="高"  # 支持 "最高", "高", "中等", "低"
)
```

### 6. 更新多个字段
```python
result = update_issue_fields(
    issue_key="WK-766",
    summary="更新后的任务摘要",
    description="新的描述内容",
    priority="高",
    assignee="Cloud",
    duedate="下周"
)
```

### 7. 更新工作时长
```python
result = update_issue_fields(
    issue_key="WK-766",
    timetracking={
        "timeSpent": "3600",  # 已用时间（秒）
        "remainingEstimate": "7200"  # 剩余时间（秒）
    }
)
```

### 8. 批量更新字段
```python
from jira_task_creator import bulk_update_issue_fields

issue_keys = ["WK-766", "WK-767", "WK-768"]
results = bulk_update_issue_fields(
    issue_keys,
    priority="高",
    duedate="下周"
)

for result in results:
    issue_key = result["issue_key"]
    if result["result"]["success"]:
        print(f"✅ {issue_key} 已更新")
    else:
        print(f"❌ {issue_key} 失败: {result['result']['error']}")
```

### 9. 获取任务详细信息
```python
from jira_task_creator import get_issue_details

result = get_issue_details(
    issue_key="WK-766",
    fields=["key", "summary", "status", "assignee", "duedate", "priority"]
)

if result["success"]:
    issue = result["issue_data"]
    print(f"摘要: {issue['fields']['summary']}")
    print(f"状态: {issue['fields']['status']['name']}")
    print(f"负责人: {issue['fields']['assignee']['name']}")
```

---

## 📊 支持的字段

### 标准字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `summary` | string | 任务摘要 | `"修复登录bug"` |
| `description` | string | 任务描述 | `"## 详细说明\n\n..."` |
| `priority` | string | 优先级 | `"高"`, `"Medium"` |
| `assignee` | string | 责任人 | `"Cloud"`, `"user@example.com"` |
| `reporter` | string | 报告人 | `"Cloud"` |
| `duedate` | string | 到期时间 | `"明天"`, `"2026-03-20"` |
| `timetracking` | dict | 工作时长 | `{"timeSpent": "3600", "remainingEstimate": "7200"}` |

### 自定义字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| `customfield_10000` | 自定义文本字段 | `"自定义值"` |
| `customfield_10001` | 自定义数字字段 | `123` |
| `customfield_10002` | 自定义日期字段 | `"2026-03-20"` |

**注意**: 自定义字段 ID 需要根据具体的 Jira 实例确定。

---

## 💡 最佳实践

### 1. 字段更新
- **使用通用函数**: `update_issue_fields()` 支持所有字段
- **字段验证**: 系统会自动验证字段有效性
- **错误处理**: 提供清晰的错误信息和更新详情

### 2. 用户搜索
- **多方式支持**: 支持用户名、邮箱、open_id
- **智能缓存**: 5分钟缓存，减少 API 调用
- **自动映射**: 自动将查询结果转换为 Jira 用户对象

### 3. 批量操作
- **逐个处理**: 批量更新时逐个处理每个任务
- **错误收集**: 收集所有成功和失败的更新
- **进度报告**: 提供批量操作的进度和结果汇总

---

## 🔍 技术细节

### 字段更新机制

#### PUT /rest/api/latest/issue/{issueKey}

```python
# 更新字段
PUT /rest/api/latest/issue/WK-766
{
  "fields": {
    "summary": "新的摘要",
    "description": "新的描述",
    "priority": {"name": "High"},
    "assignee": {"name": "Cloud"},
    "duedate": "2026-03-20T00:00:00.000+08:00"
  }
}
```

#### 工作时长更新

```python
# 工作时长是一个复杂对象
{
  "fields": {
    "timetracking": {
      "timeSpent": "3600",
      "remainingEstimate": "7200"
    }
  }
}
```

#### 自定义字段

```python
# 自定义字段直接使用字段名
{
  "fields": {
    "customfield_10000": "自定义值",
    "customfield_10001": 123
  }
}
```

---

## 🚀 未来计划

### v2.2.0 计划
- [ ] 支持添加评论
- [ ] 支持附件上传
- [ ] 支持子任务管理
- [ ] 支持组件和版本管理

### v2.3.0 计划
- [ ] Web UI 界面
- [ ] 飞书集成
- [ ] 邮件通知系统
- [ ] 定时任务提醒

---

## 📊 函数签名总结

| 函数名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `create_issue` | summary, description, project_key, issue_type_name, priority, assignee, due_date | dict | 创建新任务 |
| `search_issues` | jql_query, fields, max_results | dict | 搜索任务 |
| `search_user` | query, project_key | dict 或 None | 搜索用户 |
| `update_issue_fields` | issue_key, **fields | dict | 更新字段 |
| `bulk_update_issue_fields` | issue_keys, **fields | list | 批量更新字段 |
| `get_issue_details` | issue_key, fields | dict | 获取详细信息 |
| `get_issue_transitions` | issue_key | dict | 获取状态转换 |
| `transition_issue` | issue_key, transition_id | dict | 执行状态转换 |
| `update_issue_status` | issue_key, target_status | dict | 更新状态（便捷）|
| `bulk_transition_issues` | issue_keys, target_status | list | 批量更新状态 |
| `get_my_issues` | status_filter, project_key, max_results | dict | 获取我的任务 |

---

## 📝 版本历史

### v2.1.0 (2026-03-16) ⭐ 最新
- ✅ 添加通用字段更新函数
- ✅ 支持摘要、描述、优先级、责任人、报告人、到期时间、工作时长
- ✅ 支持批量字段更新
- ✅ 添加任务详细信息获取
- ✅ 改进用户搜索集成

### v2.0.0 (2026-03-16)
- ✅ 添加状态转换管理功能
- ✅ 添加批量状态更新功能
- ✅ 添加我的任务列表功能
- ✅ 改进 API 错误处理

### v1.0.0 (2026-03-16)
- ✅ 初始版本
- ✅ 任务创建功能
- ✅ 用户搜索功能
- ✅ 自然语言解析

---

**作者**: 皮皮虾
**许可**: MIT License
**仓库**: https://github.com/Mycheers/jira-task-creator
