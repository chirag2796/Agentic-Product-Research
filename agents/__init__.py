"""
Agents package for the AI Agent System
"""
from .langgraph_agents import CRMResearchOrchestrator, AgentState
from .generic_agents import GenericResearchOrchestrator, GenericAgentState

__all__ = ['CRMResearchOrchestrator', 'AgentState', 'GenericResearchOrchestrator', 'GenericAgentState']
