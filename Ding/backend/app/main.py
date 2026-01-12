"""
FastAPI MVP API for 定额估算。
提供项目、模板、估算及导出 CSV 的基础接口。
当前实现为 MVP，使用内存存储，便于快速迭代；未来可替换为数据库。
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import csv

from .storage import seed_sample_data, projects, templates, estimates
from .schemas import Template, Project, CreateEstimation, Estimation, EstimationLine

app = FastAPI(title="定额估算 MVP")

# 允许跨域（开发阶段读取方便，生产环境请限制域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时注入示例数据，确保 API 可用
seed_sample_data()

# Projects
@app.post("/projects", response_model=Project)
def create_project(project: Project):
    """创建一个新项目。若 ID 已存在，返回 400。"""
    if project.id in projects:
        raise HTTPException(status_code=400, detail="Project with this ID already exists")
    projects[project.id] = project
    return project

@app.get("/projects", response_model=list[Project])
def list_projects():
    """列出所有项目。"""
    return list(projects.values())

# Templates
@app.post("/templates", response_model=Template)
def create_template(tpl: Template):
    """创建一个模板。ID 不能重复。"""
    if tpl.id in templates:
        raise HTTPException(status_code=400, detail="Template with this ID already exists")
    templates[tpl.id] = tpl
    return tpl

@app.get("/templates", response_model=list[Template])
def list_templates():
    """列出所有模板。"""
    return list(templates.values())

@app.get("/templates/{template_id}", response_model=Template)
def get_template(template_id: str):
    """获取指定模板详情。"""
    tpl = templates.get(template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tpl

# Estimations
@app.post("/estimates", response_model=Estimation)
def create_estimation(req: CreateEstimation):
    """基于项目、模板及选定条目生成估算。"""
    # Validate project
    proj = projects.get(req.project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    # Validate template
    tpl = templates.get(req.template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    # Build lines
    lines = []
    subtotal = 0.0
    for item_req in req.items:
        # locate item in template
        found = None
        for sec in tpl.sections:
            for it in sec.items:
                if it.code == item_req.item_code:
                    found = it
                    break
            if found:
                break
        if not found:
            raise HTTPException(status_code=404, detail=f"Item code {item_req.item_code} not found in template")
        line = EstimationLine(
            item_code=found.code,
            item_name=found.name,
            unit=found.unit,
            quantity=float(item_req.quantity),
            unit_price=float(found.unit_price),
        )
        lines.append(line)
        subtotal += line.quantity * line.unit_price

    tax = subtotal * proj.tax_rate
    total = subtotal + tax

    est_id = f"E-{len(estimates) + 1:03d}"
    estimation = Estimation(
        id=est_id,
        project_id=req.project_id,
        template_id=req.template_id,
        lines=lines,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )
    estimates[est_id] = estimation.dict()
    return estimation

@app.get("/estimates", response_model=list[Estimation])
def list_estimations():
    """列出所有估算记录。"""
    return [Estimation(**e) for e in estimates.values()]

@app.get("/estimates/{estimation_id}", response_model=Estimation)
def get_estimation(estimation_id: str):
    """获取指定估算的详细信息。"""
    data = estimates.get(estimation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Estimation not found")
    return Estimation(**data)

@app.get("/estimates/{estimation_id}/export.csv")
def export_estimation_csv(estimation_id: str):
    """将指定估算导出为 CSV 文件。"""
    data = estimates.get(estimation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Estimation not found")

    est: Estimation = Estimation(**data)
    # create CSV in memory
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Code", "Name", "Unit", "Quantity", "UnitPrice", "LineTotal"])
    for l in est.lines:
        line_total = l.quantity * l.unit_price
        writer.writerow([l.item_code, l.item_name, l.unit, l.quantity, l.unit_price, line_total])
    writer.writerow([])
    writer.writerow(["Subtotal", est.subtotal])
    writer.writerow(["Tax", est.tax])
    writer.writerow(["Total", est.total])

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=estimation_{estimation_id}.csv"})
