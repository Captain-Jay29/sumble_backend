import asyncpg
from typing import List, Dict, Any
import os


class Database:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv('PGHOST', 'localhost'),
            port=int(os.getenv('PGPORT', 5432)),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', 'supersecretpassword'),
            database=os.getenv('PGDATABASE', 'sumble_data'),
            min_size=10,
            max_size=20
        )
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]


# Global database instance
db = Database()

