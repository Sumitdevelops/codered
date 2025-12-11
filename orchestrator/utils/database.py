"""
Database utilities for task logging and history
"""

import aiosqlite
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class Database:
    """SQLite database for task history and logging"""
    
    def __init__(self, db_path: str = "orchestrator.db"):
        """Initialize database connection"""
        self.db_path = db_path
    
    async def initialize(self) -> None:
        """Create tables if they don't exist"""
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    priority INTEGER,
                    latency_requirement INTEGER,
                    requires_gpu BOOLEAN,
                    chosen_node TEXT NOT NULL,
                    confidence REAL,
                    execution_time REAL,
                    cost REAL,
                    status TEXT,
                    explanation TEXT,
                    timestamp TEXT NOT NULL,
                    payload TEXT
                )
            """)
            await db.commit()
        
        print(f"Database initialized at {self.db_path}")
    
    async def log_task(
        self,
        task_id: str,
        task_metadata: Dict[str, Any],
        decision: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> None:
        """Log task execution to database"""
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO task_history (
                    task_id, task_type, priority, latency_requirement,
                    requires_gpu, chosen_node, confidence, execution_time,
                    cost, status, explanation, timestamp, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                task_metadata.get('taskType', 'unknown'),
                task_metadata.get('priority', 5),
                task_metadata.get('latency', 5),
                task_metadata.get('requiresGPU', False),
                decision['best_node'],
                decision['confidence'],
                execution_result.get('execution_time', 0.0),
                execution_result.get('cost', 0.0),
                execution_result.get('status', 'unknown'),
                decision['explanation'],
                datetime.utcnow().isoformat(),
                json.dumps(task_metadata.get('payload', {}))
            ))
            await db.commit()
    
    async def get_task_history(
        self,
        limit: int = 100,
        node: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve task history from database"""
        
        query = "SELECT * FROM task_history"
        params = []
        
        if node:
            query += " WHERE chosen_node = ?"
            params.append(node)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                
                return [
                    {
                        "task_id": row['task_id'],
                        "task_type": row['task_type'],
                        "priority": row['priority'],
                        "latency_requirement": row['latency_requirement'],
                        "requires_gpu": bool(row['requires_gpu']),
                        "chosen_node": row['chosen_node'],
                        "confidence": row['confidence'],
                        "execution_time": row['execution_time'],
                        "cost": row['cost'],
                        "status": row['status'],
                        "explanation": row['explanation'],
                        "timestamp": row['timestamp']
                    }
                    for row in rows
                ]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        
        async with aiosqlite.connect(self.db_path) as db:
            # Total tasks per node
            async with db.execute("""
                SELECT chosen_node, COUNT(*) as count, 
                       AVG(execution_time) as avg_time,
                       SUM(cost) as total_cost
                FROM task_history
                GROUP BY chosen_node
            """) as cursor:
                node_stats = await cursor.fetchall()
            
            # Recent success rate
            async with db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful
                FROM task_history
            """) as cursor:
                success_stats = await cursor.fetchone()
            
            return {
                "node_statistics": [
                    {
                        "node": row[0],
                        "task_count": row[1],
                        "avg_execution_time": round(row[2], 3) if row[2] else 0,
                        "total_cost": round(row[3], 4) if row[3] else 0
                    }
                    for row in node_stats
                ],
                "overall": {
                    "total_tasks": success_stats[0],
                    "successful_tasks": success_stats[1],
                    "success_rate": round(success_stats[1] / success_stats[0], 3) if success_stats[0] > 0 else 0
                }
            }


# Singleton instance
_database = None


async def get_database() -> Database:
    """Get or create singleton database instance"""
    
    global _database
    
    if _database is None:
        _database = Database()
        await _database.initialize()
    
    return _database
