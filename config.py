"""
Configuration file for the AI Agent System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
SERPER_API_KEY = "f7c85cc629b2d2a20bd478075a402a3e158677b4"
OPENROUTER_API_KEY = "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"

# OpenRouter Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"

# Serper Configuration
SERPER_BASE_URL = "https://google.serper.dev"

# System Configuration
LOG_LEVEL = "INFO"
MAX_RESEARCH_ITERATIONS = 3
RESEARCH_TIMEOUT = 300

# CRM Tools to Research
CRM_TOOLS = ["HubSpot", "Zoho", "Salesforce"]

# Research Focus Areas
RESEARCH_AREAS = [
    "pricing",
    "features", 
    "integrations",
    "limitations"
]

# Assignment Query
ASSIGNMENT_QUERY = "We're evaluating CRM tools. Give me a summarized comparison between HubSpot, Zoho, and Salesforce for small to mid-size B2B businesses. Focus on pricing, features, integrations, and limitations."
