"""
数据模型定义：用于 MVP 的定额/估算应用
说明：
- Item：定额条目，包含编码、名称、单位与单价
- Section：模板中的一个分组，包含若干条目
- Template：定额模板，由若干 Section 组成
- Project：工程项目信息，包含币种与税率
- EstimationLine：估算单条目，包含 item_code、名称、单位、数量、单价
- Estimation：一个完整的估算结果，包含若干 EstimationLine，以及小计、税、总额
- EstimationLineRequest/CreateEstimation：用于创建 Estimation 的输入结构
"""
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    code: str
    name: str
    unit: str
    unit_price: float  # 单价，至少在模板中作为默认值

class Section(BaseModel):
    code: str
    name: str
    items: List[Item]

class Template(BaseModel):
    id: str
    name: str
    version: str
    sections: List[Section]

class Project(BaseModel):
    id: str
    name: str
    currency: str
    tax_rate: float  # e.g., 0.13 for 13%

class EstimationLine(BaseModel):
    item_code: str
    item_name: str
    unit: str
    quantity: float
    unit_price: float

class Estimation(BaseModel):
    id: str
    project_id: str
    template_id: str
    lines: List[EstimationLine]
    subtotal: float
    tax: float
    total: float

class EstimationLineRequest(BaseModel):
    item_code: str
    quantity: float

class CreateEstimation(BaseModel):
    project_id: str
    template_id: str
    items: List[EstimationLineRequest]
