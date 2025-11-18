from pydantic import BaseModel, Field
from typing import Union, List, Literal, Optional
from enum import Enum


class FieldType(str, Enum):
    TECHNOLOGY = "technology"
    JOB_FUNCTION = "job_function"
    ORGANIZATION = "organization"


class Condition(BaseModel):
    field: FieldType
    value: str


class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class QueryNode(BaseModel):
    type: Literal["condition", "operator"]
    operator: Optional[LogicalOperator] = None
    condition: Optional[Condition] = None
    children: Optional[List['QueryNode']] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "operator",
                "operator": "AND",
                "children": [
                    {
                        "type": "condition",
                        "condition": {
                            "field": "organization",
                            "value": "apple"
                        }
                    },
                    {
                        "type": "condition",
                        "condition": {
                            "field": "technology",
                            "value": ".net"
                        }
                    }
                ]
            }
        }


# Required for self-referential models
QueryNode.model_rebuild()

