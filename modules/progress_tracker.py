"""
进度追踪模块 - 跟踪申请、任务等进度
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, db_path: str = "./data/progress.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # 任务/阶段表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                due_date TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # 时间线/日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                task_id INTEGER,
                event_type TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _now(self) -> str:
        return datetime.now().isoformat()
    
    # ===== 项目管理 =====
    
    def create_project(self, 
                       name: str, 
                       project_type: str,
                       description: str = "") -> int:
        """
        创建项目
        project_type: offer申请, 签证申请, 项目管理, 自定义
        返回: 项目ID
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = self._now()
        cursor.execute('''
            INSERT INTO projects (name, type, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, project_type, description, now, now))
        
        project_id = cursor.lastrowid
        
        # 添加创建日志
        cursor.execute('''
            INSERT INTO timeline (project_id, event_type, content, created_at)
            VALUES (?, 'created', ?, ?)
        ''', (project_id, f"创建项目: {name}", now))
        
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_projects(self, 
                     status: Optional[str] = None,
                     project_type: Optional[str] = None) -> List[Dict]:
        """获取项目列表"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if project_type:
            query += " AND type = ?"
            params.append(project_type)
        
        query += " ORDER BY updated_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """获取单个项目详情"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        project = dict(row)
        
        # 获取任务
        cursor.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY priority DESC, created_at", (project_id,))
        project['tasks'] = [dict(r) for r in cursor.fetchall()]
        
        # 获取时间线
        cursor.execute("SELECT * FROM timeline WHERE project_id = ? ORDER BY created_at DESC LIMIT 20", (project_id,))
        project['timeline'] = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return project
    
    def update_project_status(self, project_id: int, status: str) -> bool:
        """更新项目状态"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = self._now()
        cursor.execute('''
            UPDATE projects SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, now, project_id))
        
        cursor.execute('''
            INSERT INTO timeline (project_id, event_type, content, created_at)
            VALUES (?, 'status_change', ?, ?)
        ''', (project_id, f"状态更新为: {status}", now))
        
        conn.commit()
        conn.close()
        return True
    
    # ===== 任务管理 =====
    
    def add_task(self,
                 project_id: int,
                 name: str,
                 due_date: Optional[str] = None,
                 priority: int = 0,
                 notes: str = "") -> int:
        """添加任务"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = self._now()
        cursor.execute('''
            INSERT INTO tasks (project_id, name, due_date, priority, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, name, due_date, priority, notes, now, now))
        
        task_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO timeline (project_id, task_id, event_type, content, created_at)
            VALUES (?, ?, 'task_added', ?, ?)
        ''', (project_id, task_id, f"添加任务: {name}", now))
        
        # 更新项目时间
        cursor.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        
        conn.commit()
        conn.close()
        return task_id
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        更新任务状态
        status: pending, in_progress, completed, cancelled
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = self._now()
        completed_at = now if status == 'completed' else None
        
        cursor.execute('''
            UPDATE tasks SET status = ?, updated_at = ?, completed_at = ? WHERE id = ?
        ''', (status, now, completed_at, task_id))
        
        # 获取项目ID
        cursor.execute("SELECT project_id, name FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            project_id, task_name = row
            cursor.execute('''
                INSERT INTO timeline (project_id, task_id, event_type, content, created_at)
                VALUES (?, ?, 'task_status', ?, ?)
            ''', (project_id, task_id, f"任务 '{task_name}' 状态更新为: {status}", now))
            
            cursor.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        
        conn.commit()
        conn.close()
        return True
    
    def add_note(self, project_id: int, content: str, task_id: Optional[int] = None):
        """添加备注/日志"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = self._now()
        cursor.execute('''
            INSERT INTO timeline (project_id, task_id, event_type, content, created_at)
            VALUES (?, ?, 'note', ?, ?)
        ''', (project_id, task_id, content, now))
        
        cursor.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        
        conn.commit()
        conn.close()
    
    # ===== 报表 =====
    
    def generate_report(self, project_id: Optional[int] = None) -> pd.DataFrame:
        """生成进度报表"""
        conn = sqlite3.connect(str(self.db_path))
        
        if project_id:
            query = '''
                SELECT 
                    p.name as 项目名称,
                    p.type as 类型,
                    p.status as 项目状态,
                    t.name as 任务,
                    t.status as 任务状态,
                    t.due_date as 截止日期,
                    t.completed_at as 完成时间
                FROM projects p
                LEFT JOIN tasks t ON p.id = t.project_id
                WHERE p.id = ?
                ORDER BY t.priority DESC, t.created_at
            '''
            df = pd.read_sql_query(query, conn, params=(project_id,))
        else:
            query = '''
                SELECT 
                    p.name as 项目名称,
                    p.type as 类型,
                    p.status as 项目状态,
                    COUNT(t.id) as 总任务数,
                    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as 已完成,
                    SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as 进行中,
                    SUM(CASE WHEN t.status = 'pending' THEN 1 ELSE 0 END) as 待处理,
                    p.updated_at as 最后更新
                FROM projects p
                LEFT JOIN tasks t ON p.id = t.project_id
                GROUP BY p.id
                ORDER BY p.updated_at DESC
            '''
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def export_to_excel(self, output_path: str, project_id: Optional[int] = None) -> str:
        """导出到Excel"""
        df = self.generate_report(project_id)
        df.to_excel(output_path, index=False)
        return output_path


# ===== 预设项目模板 =====

def create_offer_application(tracker: ProgressTracker, company: str, position: str) -> int:
    """创建Offer申请项目模板"""
    project_id = tracker.create_project(
        name=f"{company} - {position}",
        project_type="offer申请",
        description=f"申请 {company} 的 {position} 职位"
    )
    
    # 添加标准任务
    tasks = [
        ("准备简历", 1),
        ("撰写求职信", 1),
        ("投递申请", 2),
        ("等待反馈", 0),
        ("笔试/测评", 0),
        ("一面", 0),
        ("二面", 0),
        ("HR面", 0),
        ("Offer谈判", 0),
    ]
    
    for task_name, priority in tasks:
        tracker.add_task(project_id, task_name, priority=priority)
    
    return project_id


def create_visa_application(tracker: ProgressTracker, visa_type: str, country: str) -> int:
    """创建签证申请项目模板"""
    project_id = tracker.create_project(
        name=f"{country} {visa_type}签证",
        project_type="签证申请",
        description=f"申请{country}的{visa_type}签证"
    )
    
    # 添加标准任务
    tasks = [
        ("准备护照", 2),
        ("填写申请表", 2),
        ("准备照片", 1),
        ("准备财务证明", 1),
        ("准备工作证明/在读证明", 1),
        ("预约面签", 1),
        ("面签", 0),
        ("等待结果", 0),
        ("领取护照", 0),
    ]
    
    for task_name, priority in tasks:
        tracker.add_task(project_id, task_name, priority=priority)
    
    return project_id
