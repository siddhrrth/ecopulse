import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk import Context
from google.adk.events import RequestInput
from google.adk.tools import AgentTool, MCPToolset
from google.adk.workflow import Workflow, START, Edge, node
from google.genai import types
from mcp import StdioServerParameters

from app.config import config

# 1. State Schema for Workflow
class WorkflowState(BaseModel):
    user_query: str = ""
    air_quality_data: str = ""
    suggestions: str = ""
    personal_actions: str = ""
    community_actions: str = ""
    security_checked: bool = False
    revision_feedback: str = ""
    approved: bool = False
    audit_log: list[dict] = []

# 2. Define MCP Toolset
mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["-m", "app.mcp_server"],
    )
)

# 3. Define Specialized Sub-Agents
air_quality_analyst = Agent(
    name="air_quality_analyst",
    model=Gemini(model=config.model),
    instruction=(
        "You are the Air Quality Analyst. Analyze the provided environmental reports, air quality levels, or emissions data.\n"
        "Use your MCP tools to fetch the actual air quality index and environmental reports for the user's location.\n"
        "Explain key metrics like AQI, PM2.5, PM10, CO2, etc., and identify any unhealthy ranges or environmental concerns."
    ),
    tools=[mcp_toolset],
)

eco_action_planner = Agent(
    name="eco_action_planner",
    model=Gemini(model=config.model),
    instruction=(
        "You are the Eco Action Planner. Based on the air quality analysis, suggest:\n"
        "- Actionable personal health/protective measures.\n"
        "- Actionable community environmental steps.\n"
        "Use your MCP tools to check local climate policies and calculate the emissions impact of your suggested actions."
    ),
    tools=[mcp_toolset],
)

# 3. Define Orchestrator Agent
orchestrator = Agent(
    name="orchestrator",
    model=Gemini(model=config.model),
    instruction=(
        "You are the EcoPulse Orchestrator. Your goal is to analyze local environmental reports or user queries about air quality/emissions, "
        "and suggest actionable personal and community action items.\n"
        "You have access to specialized sub-agents: `air_quality_analyst` and `eco_action_planner` via tools.\n"
        "Always call `air_quality_analyst` first to get detailed air quality analysis, and then call `eco_action_planner` to get action items.\n"
        "Synthesize their outputs into a cohesive response containing:\n"
        "1. Air Quality Analysis\n"
        "2. Recommended Personal Action Items\n"
        "3. Recommended Community Action Items\n"
        "If there is revision feedback from the user, incorporate that feedback to revise the suggestions."
    ),
    tools=[
        AgentTool(air_quality_analyst),
        AgentTool(eco_action_planner),
    ],
)

# 4. Workflow Function Nodes
@node
async def security_checkpoint(ctx: Context, node_input: Any):
    import re
    import json
    
    query = ""
    if isinstance(node_input, types.Content):
        parts = node_input.parts or []
        query = "".join(part.text for part in parts if part.text)
    elif isinstance(node_input, str):
        query = node_input
    
    # 1. PII Scrubbing (Emails and Phone numbers)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    scrubbed_query = query
    scrubbed_query, email_count = re.subn(email_pattern, "[EMAIL_REDACTED]", scrubbed_query)
    scrubbed_query, phone_count = re.subn(phone_pattern, "[PHONE_REDACTED]", scrubbed_query)
    
    ctx.state["user_query"] = scrubbed_query
    
    # 2. Prompt Injection Detection
    injection_keywords = [
        "ignore previous instructions", 
        "system prompt", 
        "override instructions", 
        "you are now a", 
        "ignore instructions",
        "act as a",
        "forget your instructions"
    ]
    is_injection = any(kw in query.lower() for kw in injection_keywords)
    
    # 3. Domain-Specific Rule: Content Filter
    # Check if the query contains environment-related keywords. If it is completely unrelated, block it.
    environmental_keywords = [
        "air", "quality", "pollution", "emission", "carbon", "environment", 
        "aqi", "climate", "eco", "green", "sustainability", "wildfire",
        "pm2.5", "pm10", "co2", "ozone", "weather", "temp", "forest", 
        "recycle", "waste", "compost", "solar", "energy", "clean", "report",
        "sf", "beijing", "china", "california", "san francisco", "city"
    ]
    
    # Check if the query is a simple greeting or general help request
    is_general_or_greeting = query.lower().strip() in [
        "hi", "hello", "hey", "help", "good morning", "good afternoon", "good evening", "test"
    ] or len(query.strip()) < 4
    
    has_environmental_context = any(kw in query.lower() for kw in environmental_keywords)
    is_domain_violation = not (has_environmental_context or is_general_or_greeting)
    
    # 4. Structured JSON Audit Logging
    audit_event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "severity": "INFO",
        "event_type": "security_scan",
        "checks": {
            "pii_redacted": {
                "emails_removed": email_count,
                "phones_removed": phone_count
            },
            "prompt_injection": {
                "detected": is_injection
            },
            "domain_validation": {
                "passed": not is_domain_violation
            }
        }
    }
    
    if is_injection:
        audit_event["severity"] = "CRITICAL"
        audit_event["event_type"] = "prompt_injection_violation"
        audit_event["description"] = "Input matches prompt injection attack patterns."
        logs = list(ctx.state.get("audit_log") or [])
        logs.append(audit_event)
        ctx.state["audit_log"] = logs
        print(json.dumps(audit_event, indent=2))
        ctx.route = "security_event"
        return "Security Violation: Prompt injection attempt detected."
        
    if is_domain_violation:
        audit_event["severity"] = "WARNING"
        audit_event["event_type"] = "domain_content_violation"
        audit_event["description"] = "Input is unrelated to environmental or air quality topics."
        logs = list(ctx.state.get("audit_log") or [])
        logs.append(audit_event)
        ctx.state["audit_log"] = logs
        print(json.dumps(audit_event, indent=2))
        ctx.route = "security_event"
        return "Security Violation: Queries must be related to environmental quality, air pollution, or sustainability."
        
    # Safe to proceed
    audit_event["event_type"] = "security_check_passed"
    logs = list(ctx.state.get("audit_log") or [])
    logs.append(audit_event)
    ctx.state["audit_log"] = logs
    print(json.dumps(audit_event, indent=2))
    
    ctx.route = "secure"
    return scrubbed_query

@node
async def security_event_node(ctx: Context, node_input: Any):
    return f"Access Denied: {node_input}"

@node(rerun_on_resume=True)
async def human_approval(ctx: Context, node_input: Any):
    if "user_decision" in ctx.resume_inputs:
        decision = ctx.resume_inputs["user_decision"]
        feedback = ctx.resume_inputs.get("user_feedback", "")
        
        if decision.lower() == "yes":
            ctx.state["approved"] = True
            ctx.route = "approved"
            return node_input
        else:
            ctx.state["revision_feedback"] = feedback
            ctx.route = "request_revision"
            return f"User requested revision with feedback: {feedback}"
            
    ctx.state["suggestions"] = str(node_input)
    
    return RequestInput(
        interrupt_id="user_decision",
        message="Do you approve the suggested actions? Reply 'yes' to approve, or 'no' with feedback to request revision.",
        response_schema=None
    )

@node
async def finalize_plan(ctx: Context, node_input: Any):
    return f"### EcoPulse Final Approved Plan\n\n{node_input}"

# 5. Define Workflow Graph and Edges
workflow = Workflow(
    name="ecopulse_workflow",
    description="EcoPulse Workflow for analyzing air quality and suggesting actions",
    edges=[
        Edge(from_node=START, to_node=security_checkpoint),
        Edge(from_node=security_checkpoint, to_node=orchestrator, route="secure"),
        Edge(from_node=security_checkpoint, to_node=security_event_node, route="security_event"),
        Edge(from_node=orchestrator, to_node=human_approval),
        Edge(from_node=human_approval, to_node=finalize_plan, route="approved"),
        Edge(from_node=human_approval, to_node=orchestrator, route="request_revision"),
    ],
    state_schema=WorkflowState,
)

# Export the app using the workflow as the root agent
app = App(
    root_agent=workflow,
    name="app",
)

root_agent = workflow
