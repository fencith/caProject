"""
In-memory MVP storage for 定额估算应用。
数据模型来自 schemas.py 的结构定义。
- projects: 以 Project 对象为值的字典，key 为 id
- templates: 以 Template 对象为值的字典，key 为 id
- estimates: 以 Estimation 的字典表示，key 为估算 id
seed_sample_data(): 初始化演示数据，包含一个示例项目与一个示例模板，方便快速验证 API。
"""

from typing import Dict
from .schemas import Template, Section, Item, Project

# In-memory storage (MVP)
projects: Dict[str, Project] = {}
templates: Dict[str, Template] = {}
estimates: Dict[str, dict] = {}


def seed_sample_data():
    """
    初始化示例数据：一个项目、一个模板，包含两个分区和若干条目。
    目的是让后端在没有数据库的情况下也能快速运行与验证。
    """
    # Seed a sample project
    p = Project(id="P-001", name="示例项目", currency="CNY", tax_rate=0.13)
    projects[p.id] = p

    # Seed a sample template with sections and items
    it1 = Item(code="I-001", name="钢材", unit="吨", unit_price=5000.0)
    it2 = Item(code="I-002", name="混凝土", unit="立方", unit_price=400.0)
    sec1 = Section(code="S1", name="基材", items=[it1, it2])

    it3 = Item(code="I-101", name="人工", unit="人时", unit_price=120.0)
    sec2 = Section(code="S2", name="人工", items=[it3])
    tmpl = Template(id="T-001", name="通用模板", version="1.0", sections=[sec1, sec2])
    templates[tmpl.id] = tmpl
