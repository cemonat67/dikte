from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Set
import os
import psycopg


@dataclass(slots=True)
class MetricDefinition:
    metric_type: str
    canonical_unit: str
    min_value: float | None = None
    max_value: float | None = None


def load_registered_metrics(db_url: str) -> Set[str]:
    sql = """
    select metric_type
    from public.metric_definitions
    """
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return {str(r[0]).strip() for r in rows if r and r[0]}


class MetricRegistry:
    def __init__(self, db_url: Optional[str] = None) -> None:
        self.db_url = db_url or os.getenv("DATABASE_URL")

    def get_metric_definition(self, metric_type: str) -> Optional[Dict[str, str]]:
        if not self.db_url:
            return None

        sql = """
        select metric_type, canonical_unit
        from public.metric_definitions
        where metric_type = %s
        limit 1
        """
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (metric_type,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d[0] for d in cur.description]
                return dict(zip(cols, row))
