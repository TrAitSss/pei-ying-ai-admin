"""
自动初始化种子数据模块
在生产环境首次启动时自动运行（AUTO_SEED=true 时触发）
也可手动调用：python -m app.seed
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal, Base, engine
from app.models import User, Supplier, InventoryItem, Template
from app.routers.auth import get_password_hash


async def auto_seed():
    """如果数据库为空，自动初始化种子数据"""
    # 确保表已创建
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 检查是否已有种子数据（以供应商为判断依据）
        result = await db.execute(select(Supplier))
        if result.scalars().first():
            print("[seed] 数据库已有种子数据，跳过初始化")
            return

        # 1. 创建用户（如果不存在）
        result = await db.execute(select(User).where(User.username == "steven"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                username="steven",
                email="steven@peiying.edu.hk",
                full_name="Steven",
                hashed_password=get_password_hash("steven123"),
                department="校务处",
            )
            db.add(user)
            await db.flush()

        # 2. 创建标书/报价单模板
        templates = [
            Template(
                name="采购标书模板",
                template_type="tender",
                description="适用于学校物资采购的标书",
                content="""{{ school_name }} 采购标书

项目名称：{{ project_name }}
标书编号：{{ tender_no }}
日期：{{ date }}

一、项目概述
{{ description }}

二、采购清单
{% for item in items %}{{ loop.index }}. {{ item.name }} - 数量: {{ item.quantity }} - 预算: HK${{ item.budget }}
{% endfor %}
三、合计预算：HK${{ total_budget }}

四、投标要求
1. 供应商须为香港注册公司
2. 交货期不超过 {{ delivery_days }} 个工作日
3. 质保期不少于 {{ warranty_months }} 个月

联系人：Steven
电话：(852) XXXX XXXX""",
                variables=[
                    {"name": "school_name", "label": "学校名称", "default": "香港培英中学"},
                    {"name": "project_name", "label": "项目名称"},
                    {"name": "tender_no", "label": "标书编号"},
                    {"name": "date", "label": "日期"},
                    {"name": "description", "label": "项目描述"},
                    {"name": "items", "label": "采购清单"},
                    {"name": "total_budget", "label": "合计预算"},
                    {"name": "delivery_days", "label": "交货天数", "default": "14"},
                    {"name": "warranty_months", "label": "质保月数", "default": "12"},
                ],
                created_by=user.id,
            ),
            Template(
                name="报价单模板",
                template_type="quotation",
                description="适用于向供应商询价的报价单",
                content="""报价单 (Quotation)

致：{{ supplier_name }}
报价日期：{{ date }}
报价编号：QT-{{ date }}-{{ seq }}

| 序号 | 项目 | 规格 | 数量 | 单价(HK$) | 总价(HK$) |
|------|------|------|------|-----------|-----------|
{% for item in items %}| {{ loop.index }} | {{ item.name }} | {{ item.spec }} | {{ item.qty }} | {{ item.unit_price }} | {{ item.total }} |
{% endfor %}

|      |      |      | 合计 |            | {{ grand_total }} |

有效期：{{ valid_days }} 天
联系人：Steven""",
                variables=[
                    {"name": "supplier_name", "label": "供应商名称"},
                    {"name": "date", "label": "日期"},
                    {"name": "seq", "label": "序号"},
                    {"name": "items", "label": "报价项目"},
                    {"name": "grand_total", "label": "合计金额"},
                    {"name": "valid_days", "label": "有效天数", "default": "30"},
                ],
                created_by=user.id,
            ),
            Template(
                name="维修服务报价模板",
                template_type="quotation",
                description="适用于维修/保养服务的报价",
                content="""维修服务报价单

服务对象：{{ client_name }}
日期：{{ date }}
报价编号：MS-{{ date }}-001

一、服务内容
{{ service_description }}

二、费用明细
| 项目 | 费用(HK$) |
|------|-----------|
{% for fee in fees %}| {{ fee.name }} | {{ fee.amount }} |
{% endfor %}
| 合计 | {{ total_amount }} |

三、服务承诺
- 响应时间：{{ response_time }}
- 服务期限：{{ service_period }}
- 质保：{{ warranty }}""",
                variables=[
                    {"name": "client_name", "label": "客户名称", "default": "培英中学"},
                    {"name": "date", "label": "日期"},
                    {"name": "service_description", "label": "服务描述"},
                    {"name": "fees", "label": "费用明细"},
                    {"name": "total_amount", "label": "合计金额"},
                    {"name": "response_time", "label": "响应时间", "default": "24小时内"},
                    {"name": "service_period", "label": "服务期限"},
                    {"name": "warranty", "label": "质保条款", "default": "维修后30天"},
                ],
                created_by=user.id,
            ),
        ]
        for t in templates:
            db.add(t)

        # 3. 创建示例供应商
        suppliers = [
            Supplier(
                name="恒达办公用品有限公司",
                contact_person="陳志明",
                phone="2345-6789",
                email="info@hingdat.com.hk",
                address="香港九龍觀塘工業區XX大廈5樓",
                category="辦公用品",
                tags=["辦公用品", "紙張", "文具", "打印耗材"],
                quotation_history=[
                    {"date": "2025-09-15", "item": "A4复印纸", "price": 85, "qty": 50},
                    {"date": "2026-01-10", "item": "打印墨盒", "price": 320, "qty": 10},
                    {"date": "2026-04-20", "item": "文件夹套装", "price": 45, "qty": 30},
                ],
            ),
            Supplier(
                name="華聯電子科技有限公司",
                contact_person="李偉強",
                phone="2789-0123",
                email="sales@wahlian.com.hk",
                address="香港新界沙田XX中心18樓",
                category="電子設備",
                tags=["電子設備", "音響", "投影儀", "電腦", "網絡設備"],
                quotation_history=[
                    {"date": "2025-11-20", "item": "投影仪 EPSON EB-X51", "price": 8500, "qty": 2},
                    {"date": "2026-03-05", "item": "无线麦克风套装", "price": 2800, "qty": 3},
                ],
            ),
            Supplier(
                name="明輝清潔服務公司",
                contact_person="張美玲",
                phone="2567-8901",
                email="mingfai@mfc.com.hk",
                address="香港港島東區XX商業大廈3樓",
                category="清潔服務",
                tags=["清潔服務", "消毒", "滅蟲", "環保清潔"],
                quotation_history=[
                    {"date": "2026-01-05", "item": "全校清洁月费", "price": 18000, "qty": 1},
                    {"date": "2026-06-01", "item": "暑期深度清洁", "price": 35000, "qty": 1},
                ],
            ),
            Supplier(
                name="金鑫印刷有限公司",
                contact_person="王大衛",
                phone="2345-1234",
                email="quote@goldenprint.com.hk",
                address="香港九龍深水埗XX街12號地下",
                category="印刷服務",
                tags=["印刷", "影印", "裝訂", "橫幅"],
                quotation_history=[
                    {"date": "2025-12-10", "item": "校刊印刷 500份", "price": 4500, "qty": 1},
                    {"date": "2026-02-28", "item": "考试成绩单印刷", "price": 1200, "qty": 1},
                ],
            ),
            Supplier(
                name="安達家具工程有限公司",
                contact_person="劉國華",
                phone="2987-6543",
                email="sales@anda-furniture.com.hk",
                address="香港新界葵涌XX工業大廈8樓",
                category="傢俱設備",
                tags=["傢俱", "桌椅", "儲物柜", "教學設備"],
                quotation_history=[
                    {"date": "2025-10-15", "item": "学生桌椅套装 x30", "price": 45000, "qty": 1},
                    {"date": "2026-05-20", "item": "教师办公椅 x10", "price": 15000, "qty": 1},
                ],
            ),
        ]
        for s in suppliers:
            db.add(s)

        # 4. 创建示例库存物品
        inventory_items = [
            InventoryItem(name="A4 复印纸 (5包/箱)", category="紙張", location="校务处储物间", current_quantity=8, min_quantity=10, unit="箱", unit_price=85.0),
            InventoryItem(name="打印墨盒 (黑色)", category="打印耗材", location="校务处储物间", current_quantity=3, min_quantity=5, unit="个", unit_price=320.0),
            InventoryItem(name="打印墨盒 (彩色)", category="打印耗材", location="校务处储物间", current_quantity=2, min_quantity=3, unit="个", unit_price=450.0),
            InventoryItem(name="文件夹 (A4)", category="文具", location="校务处储物间", current_quantity=50, min_quantity=20, unit="个", unit_price=3.5),
            InventoryItem(name="白板笔 (红/蓝/黑)", category="文具", location="各教室储物柜", current_quantity=15, min_quantity=30, unit="支", unit_price=8.0),
            InventoryItem(name="胶带 (透明)", category="文具", location="校务处储物间", current_quantity=12, min_quantity=10, unit="卷", unit_price=5.0),
            InventoryItem(name="信封 (A4大小)", category="文具", location="校务处储物间", current_quantity=5, min_quantity=15, unit="包", unit_price=12.0),
            InventoryItem(name="修正带", category="文具", location="校务处储物间", current_quantity=20, min_quantity=10, unit="个", unit_price=6.0),
            InventoryItem(name="洗手液", category="清潔用品", location="各楼层清洁柜", current_quantity=4, min_quantity=8, unit="瓶", unit_price=15.0),
            InventoryItem(name="厕纸 (大卷)", category="清潔用品", location="各楼层清洁柜", current_quantity=30, min_quantity=40, unit="卷", unit_price=4.5),
        ]
        for item in inventory_items:
            db.add(item)

        await db.commit()
        print("[seed] 种子数据初始化完成！")
        print("[seed] - 用户: steven / steven123")
        print("[seed] - 模板: 3 个")
        print("[seed] - 供应商: 5 个")
        print("[seed] - 库存物品: 10 个")


if __name__ == "__main__":
    asyncio.run(auto_seed())
