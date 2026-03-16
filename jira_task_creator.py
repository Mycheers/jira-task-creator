import requests
import json
from datetime import datetime, timedelta
import calendar
import re
import os

class NaturalLanguageParser:
    """自然语言解析器 - 解析日期、优先级等"""

    def __init__(self):
        self.today = datetime.now()

    def parse_date(self, date_str):
        """解析相对日期字符串"""
        if not date_str:
            return None

        date_str = date_str.strip().lower()

        # 相对日期映射
        date_map = {
            "今天": self.today,
            "tomorrow": self.today + timedelta(days=1),
            "明天": self.today + timedelta(days=1),
            "后天": self.today + timedelta(days=2),
            "后天": self.today + timedelta(days=2),
            "next week": self.today + timedelta(weeks=1),
            "下周": self.today + timedelta(weeks=1),
            "this week": self.today + timedelta(days=7),
            "本周": self.today + timedelta(days=7),
            "end of month": self.today.replace(day=calendar.monthrange(self.today.year, self.today.month)[1]),
            "月底": self.today.replace(day=calendar.monthrange(self.today.year, self.today.month)[1]),
            "next month end": (self.today + timedelta(days=32)).replace(day=1) - timedelta(days=1),
            "下月底": (self.today + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        }

        if date_str in date_map:
            return date_map[date_str]

        # 匹配 "X天" 或 "X周"
        days_match = re.match(r'(\d+)\s*[天日]', date_str)
        if days_match:
            days = int(days_match.group(1))
            return self.today + timedelta(days=days)

        weeks_match = re.match(r'(\d+)\s*[周星期]', date_str)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return self.today + timedelta(weeks=weeks)

        return None

    def parse_priority(self, priority_str):
        """解析优先级字符串"""
        if not priority_str:
            return None

        priority_str = priority_str.strip().lower()

        priority_map = {
            "highest": "Highest",
            "highest": "Highest",
            "最高": "Highest",
            "high": "High",
            "high": "High",
            "高": "High",
            "medium": "Medium",
            "medium": "Medium",
            "中等": "Medium",
            "low": "Low",
            "low": "Low",
            "低": "Low"
        }

        return priority_map.get(priority_str, "Medium")


class UserSearcher:
    """用户搜索器 - 多方式查找用户"""

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.user_mapping = {}

    def search_user(self, query, project_key=None):
        """搜索用户"""
        if not query:
            return None

        query = query.strip()

        # 检查缓存
        cache_key = f"{query}_{project_key}"
        if cache_key in self.cache:
            cached_user, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                return cached_user

        # 多方式搜索
        user = self._search_by_name(query, project_key)
        if not user:
            user = self._search_by_email(query, project_key)
        if not user:
            user = self._search_by_display_name(query, project_key)

        # 缓存结果
        if user:
            self.cache[cache_key] = (user, datetime.now())

        return user

    def _search_by_name(self, name, project_key=None):
        """通过用户名搜索"""
        endpoint = "/rest/api/3/user/assignable/search"
        params = {"query": name}
        if project_key:
            params["projectKey"] = project_key

        return self._make_request(endpoint, params)

    def _search_by_email(self, email, project_key=None):
        """通过邮箱搜索"""
        endpoint = "/rest/api/3/user/search"
        params = {"query": email}
        if project_key:
            params["projectKey"] = project_key

        return self._make_request(endpoint, params)

    def _search_by_display_name(self, display_name, project_key=None):
        """通过显示名称搜索"""
        endpoint = "/rest/api/3/user/assignable/search"
        params = {"query": display_name}
        if project_key:
            params["projectKey"] = project_key

        return self._make_request(endpoint, params)

    def _make_request(self, endpoint, params):
        """发送 HTTP 请求"""
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                users = response.json()
                if users and len(users) > 0:
                    return users[0]
            return None
        except Exception as e:
            print(f"[ERROR] User search failed: {str(e)}")
            return None


def create_issue(summary, description=None, project_key=None, issue_type_name=None,
                priority=None, assignee=None, due_date=None):
    """创建 Jira Issue"""

    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    # 默认值
    if not project_key:
        project_key = os.getenv("JIRA_DEFAULT_PROJECT")
    if not assignee:
        assignee = os.getenv("JIRA_DEFAULT_ASSIGNEE")

    # 构建 issue 数据
    issue_data = {
        "fields": {
            "summary": summary,
            "project": {"key": project_key} if project_key else None,
            "issuetype": {"name": issue_type_name} if issue_type_name else None,
        }
    }

    # 添加可选字段
    if description:
        issue_data["fields"]["description"] = description

    if priority:
        parser = NaturalLanguageParser()
        priority = parser.parse_priority(priority)
        issue_data["fields"]["priority"] = {"name": priority}

    if assignee:
        issue_data["fields"]["assignee"] = {"name": assignee}

    if due_date:
        parser = NaturalLanguageParser()
        due_date = parser.parse_date(due_date)
        if due_date:
            issue_data["fields"]["duedate"] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")

    # 发送请求
    url = f"{base_url.rstrip('/')}/rest/api/latest/issue"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=issue_data, timeout=30)
        print(f"[INFO] Status code: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            return {
                "success": True,
                "issue_key": result["key"],
                "issue_id": result["id"],
                "self": result["self"]
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_user(query, project_key=None):
    """搜索用户（便捷函数）"""
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return None

    searcher = UserSearcher(base_url, token)
    return searcher.search_user(query, project_key)


def search_issues(jql_query, fields=None, max_results=50):
    """搜索 Jira Issues"""
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    url = f"{base_url.rstrip('/')}/rest/api/latest/search"

    # 构建查询参数
    params = {
        "jql": jql_query,
        "fields": fields if fields else ["key", "summary", "status", "assignee", "created", "updated"],
        "maxResults": max_results
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"[INFO] Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "total": result.get("total", 0),
                "issues": result.get("issues", [])
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_issue_transitions(issue_key):
    """获取 Issue 的可用状态转换"""
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    url = f"{base_url.rstrip('/')}/rest/api/latest/issue/{issue_key}/transitions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"[INFO] Transitions Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "transitions": result.get("transitions", [])
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def transition_issue(issue_key, transition_id):
    """执行 Issue 状态转换"""
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    url = f"{base_url.rstrip('/')}/rest/api/latest/issue/{issue_key}/transitions"

    # 构建转换数据
    transition_data = {
        "transition": {
            "id": transition_id
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=transition_data, timeout=30)
        print(f"[INFO] Transition Status code: {response.status_code}")

        if response.status_code in [200, 204]:
            return {
                "success": True,
                "issue_key": issue_key
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def update_issue_status(issue_key, target_status):
    """更新 Issue 状态（便捷函数）

    这是高层封装函数，自动查找并执行状态转换。

    Args:
        issue_key: Issue Key（如 ERP-123）
        target_status: 目标状态名称（如 "处理中"）

    Returns:
        dict: 包含 success, error, transition_name 等信息
    """
    # 获取可用的状态转换
    transitions_result = get_issue_transitions(issue_key)

    if not transitions_result["success"]:
        return {
            "success": False,
            "error": transitions_result["error"],
            "issue_key": issue_key
        }

    transitions = transitions_result["transitions"]

    # 查找目标状态的转换
    target_transition = None
    for transition in transitions:
        if transition.get("to", {}).get("name") == target_status:
            target_transition = transition
            print(f"[INFO] 找到转换: {transition['name']} -> {transition['to']['name']}")
            break

    if not target_transition:
        return {
            "success": False,
            "error": f"未找到状态 '{target_status}' 的转换",
            "issue_key": issue_key,
            "available_transitions": [t["to"]["name"] for t in transitions]
        }

    # 执行状态转换
    transition_result = transition_issue(issue_key, target_transition["id"])

    return {
        "success": transition_result["success"],
        "error": transition_result.get("error"),
        "issue_key": issue_key,
        "transition_name": target_transition["name"],
        "from_status": transitions[0]["from"]["name"] if transitions else "未知",
        "to_status": target_status
    }


def bulk_transition_issues(issue_keys, target_status):
    """批量更新多个 Issue 状态"""
    results = []

    for issue_key in issue_keys:
        result = update_issue_status(issue_key, target_status)
        results.append({
            "issue_key": issue_key,
            "result": result
        })

    return results


def get_my_issues(status_filter=None, project_key=None, max_results=50):
    """获取我的 Issue 列表（便捷函数）

    Args:
        status_filter: 状态过滤（None=全部, "Done"=已完成）
        project_key: 项目 Key（None=默认项目）
        max_results: 最大返回数量

    Returns:
        dict: 包含 success, total, issues 等信息
    """
    # 构建 JQL 查询
    jql_parts = []

    if status_filter:
        jql_parts.append(f"status = '{status_filter}'")

    if project_key:
        jql_parts.append(f"project = '{project_key}'")

    # 添加 assignee 过滤（获取当前用户的任务）
    jql_parts.append("assignee = currentUser()")

    jql_query = " AND ".join(jql_parts)

    # 搜索
    return search_issues(jql_query, max_results=max_results)


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
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    url = f"{base_url.rstrip('/')}/rest/api/latest/issue/{issue_key}"

    # 构建更新数据
    update_data = {"fields": {}}

    # 处理每个字段
    for field_name, field_value in fields.items():
        if field_value is None:
            continue

        # 字段映射
        if field_name == "summary":
            update_data["fields"]["summary"] = field_value

        elif field_name == "description":
            update_data["fields"]["description"] = field_value

        elif field_name == "priority":
            parser = NaturalLanguageParser()
            priority = parser.parse_priority(field_value)
            update_data["fields"]["priority"] = {"name": priority}

        elif field_name == "assignee":
            # 支持用户名、邮箱、open_id
            assignee_search = UserSearcher(base_url, token)
            assignee = assignee_search.search_user(field_value)
            if assignee:
                update_data["fields"]["assignee"] = {
                    "name": assignee.get("name"),
                    "accountId": assignee.get("accountId")
                }
            else:
                # 如果找不到用户，直接使用提供的值
                update_data["fields"]["assignee"] = {"name": field_value}

        elif field_name == "reporter":
            reporter_search = UserSearcher(base_url, token)
            reporter = reporter_search.search_user(field_value)
            if reporter:
                update_data["fields"]["reporter"] = {
                    "name": reporter.get("name"),
                    "accountId": reporter.get("accountId")
                }
            else:
                update_data["fields"]["reporter"] = {"name": field_value}

        elif field_name == "duedate":
            parser = NaturalLanguageParser()
            due_date = parser.parse_date(field_value)
            if due_date:
                update_data["fields"]["duedate"] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
            else:
                update_data["fields"]["duedate"] = field_value

        elif field_name == "timetracking":
            # timetracking 是一个复杂对象
            timetracking_value = {}
            if isinstance(field_value, dict):
                if "remainingEstimate" in field_value:
                    timetracking_value["remainingEstimate"] = field_value["remainingEstimate"]
                if "timeSpent" in field_value:
                    timetracking_value["timeSpent"] = field_value["timeSpent"]
            else:
                timetracking_value["timeSpent"] = field_value

            if timetracking_value:
                update_data["fields"]["timetracking"] = timetracking_value

        elif field_name.startswith("customfield_"):
            # 自定义字段，直接使用
            update_data["fields"][field_name] = field_value

        else:
            # 其他字段，直接使用
            update_data["fields"][field_name] = field_value

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, headers=headers, json=update_data, timeout=30)
        print(f"[INFO] Update Status code: {response.status_code}")

        if response.status_code in [200, 204]:
            return {
                "success": True,
                "issue_key": issue_key,
                "updated_fields": list(fields.keys()),
                "update_data": update_data
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def bulk_update_issue_fields(issue_keys, **fields):
    """批量更新多个 Issue 的字段

    Args:
        issue_keys: Issue Key 列表
        **fields: 要更新的字段（关键字参数）

    Returns:
        list: 每个任务的更新结果
    """
    results = []

    for issue_key in issue_keys:
        result = update_issue_fields(issue_key, **fields)
        results.append({
            "issue_key": issue_key,
            "result": result
        })

    return results


def get_issue_details(issue_key, fields=None):
    """获取 Issue 详细信息

    Args:
        issue_key: Issue Key（如 ERP-123）
        fields: 要返回的字段列表（None=返回所有字段）

    Returns:
        dict: 包含 success, issue_data 等信息
    """
    base_url = os.getenv("JIRA_BASE_URL")
    token = os.getenv("JIRA_BEARER_TOKEN")

    if not base_url or not token:
        return {
            "success": False,
            "error": "JIRA_BASE_URL and JIRA_BEARER_TOKEN environment variables required"
        }

    url = f"{base_url.rstrip('/')}/rest/api/latest/issue/{issue_key}"

    # 构建参数
    params = {}
    if fields:
        params["fields"] = ",".join(fields)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"[INFO] Get Details Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "issue_key": issue_key,
                "issue_data": result
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
