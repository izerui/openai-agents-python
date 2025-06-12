import asyncio

from manager import FinancialResearchManager


# 金融机器人示例的入口点。
# 通过 `python -m examples.financial_research_agent.main` 运行此程序，
# 然后输入一个金融研究查询，例如：
# "写一份关于苹果公司最近一个季度的分析。"
async def main() -> None:
    query = input("请输入金融研究查询：")
    mgr = FinancialResearchManager()
    await mgr.run(query)


if __name__ == "__main__":
    asyncio.run(main())
