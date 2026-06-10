"""Monitoring Workflow Definitions."""

from app.agents.monitoring_agent import MonitoringAgent


async def monitoring_workflow(customer_id: str, customer_data: dict):
    """Execute complete monitoring workflow."""
    agent = MonitoringAgent()
    result = await agent.monitor_customer(customer_id, customer_data)
    return result