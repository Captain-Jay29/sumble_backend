from typing import Tuple, List, Any, Set
from app.models import QueryNode, LogicalOperator, FieldType


class QueryBuilder:
    def build_query(self, node: QueryNode, limit: int = 10) -> Tuple[str, List[Any]]:
        """
        Build complete SQL query with JOINs and WHERE clause
        """
        # Collect all field types needed for JOINs
        required_joins = self._collect_required_fields(node)
        
        # Build base query with necessary JOINs
        base_query = self._build_base_query(required_joins)
        
        # Build WHERE clause with proper parameter tracking
        where_clause, params, _ = self._build_where_clause(node)
        
        # Combine into final query
        query = f"{base_query} WHERE {where_clause} LIMIT {limit}"
        
        return query, params
    
    def _collect_required_fields(self, node: QueryNode) -> Set[FieldType]:
        """Recursively collect all field types that need JOINs"""
        fields = set()
        
        if node.type == "condition":
            fields.add(node.condition.field)
        elif node.type == "operator" and node.children:
            for child in node.children:
                fields.update(self._collect_required_fields(child))
        
        return fields
    
    def _build_base_query(self, required_fields: Set[FieldType]) -> str:
        """Build SELECT with necessary JOINs based on required fields"""
        query_parts = [
            "SELECT DISTINCT jp.id, jp.datetime_pulled",
            "FROM job_posts jp"
        ]
        
        if FieldType.ORGANIZATION in required_fields:
            query_parts.append("INNER JOIN organizations o ON jp.organization_id = o.id")
        
        if FieldType.TECHNOLOGY in required_fields:
            query_parts.append("INNER JOIN job_posts_tech jpt ON jp.id = jpt.job_post_id")
            query_parts.append("INNER JOIN tech t ON jpt.tech_id = t.id")
        
        if FieldType.JOB_FUNCTION in required_fields:
            query_parts.append("INNER JOIN job_posts_job_functions jpjf ON jp.id = jpjf.job_post_id")
            query_parts.append("INNER JOIN job_functions jf ON jpjf.job_function_id = jf.id")
        
        return " ".join(query_parts)
    
    def _build_where_clause(self, node: QueryNode, param_offset: int = 0) -> Tuple[str, List[Any], int]:
        """Recursively build WHERE clause from query tree. Returns (clause, params, next_offset)"""
        if node.type == "condition":
            return self._build_condition(node.condition, param_offset)
        elif node.type == "operator":
            return self._build_operator(node, param_offset)
        else:
            raise ValueError(f"Unknown node type: {node.type}")
    
    def _build_condition(self, condition, param_offset: int) -> Tuple[str, List[Any], int]:
        """Build SQL condition for a single field"""
        # Map fields to actual database columns
        field_mapping = {
            FieldType.TECHNOLOGY: "t.name",
            FieldType.JOB_FUNCTION: "jf.name", 
            FieldType.ORGANIZATION: "o.name"
        }
        
        column = field_mapping[condition.field]
        # Use ILIKE for case-insensitive search with proper param numbering
        return f"{column} ILIKE ${param_offset + 1}", [f"%{condition.value}%"], param_offset + 1
    
    def _build_operator(self, node: QueryNode, param_offset: int) -> Tuple[str, List[Any], int]:
        """Build SQL for logical operators with proper parameter tracking"""
        if node.operator == LogicalOperator.NOT:
            sub_clause, params, next_offset = self._build_where_clause(node.children[0], param_offset)
            return f"NOT ({sub_clause})", params, next_offset
        
        # For AND/OR operators
        clauses = []
        all_params = []
        current_offset = param_offset
        
        for child in node.children:
            sub_clause, params, current_offset = self._build_where_clause(child, current_offset)
            clauses.append(f"({sub_clause})")
            all_params.extend(params)
        
        operator = " AND " if node.operator == LogicalOperator.AND else " OR "
        return operator.join(clauses), all_params, current_offset

