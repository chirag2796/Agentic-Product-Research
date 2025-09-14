# AI Agent Team for CRM Research

An autonomous agent system that researches and compares CRM tools (HubSpot, Zoho, Salesforce) for small to mid-size B2B businesses.

## 🤖 Agent Architecture

The system consists of 5 specialized agents that work collaboratively:

1. **Research Coordinator** - Orchestrates the research process and delegates tasks
2. **Web Research Specialist** - Gathers real-time data from web sources
3. **Data Analysis Specialist** - Processes and structures research data
4. **Validation Specialist** - Cross-checks findings and ensures accuracy
5. **Report Generation Specialist** - Creates comprehensive comparison reports

## 🚀 Features

- **Autonomous Operation**: Agents work independently and make decisions based on context
- **Dynamic Communication**: Agents can trigger each other, request re-research, and validate findings
- **Real-time Research**: Uses web search APIs to gather current information
- **Structured Output**: Generates both JSON and markdown comparison reports
- **Quality Assurance**: Built-in validation and cross-checking mechanisms

## 📋 Requirements

- Python 3.8+
- API keys for:
  - OpenRouter (for LLM access)
  - Serper.dev (for web search)

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys in `config.py`:
   - Add your OpenRouter API key
   - Add your Serper.dev API key

## 🎯 Usage

Run the main application:

```bash
python main.py
```

The system will:
1. Initialize all agents
2. Create a research plan
3. Conduct web research on each CRM tool
4. Analyze and structure the data
5. Validate findings
6. Generate a comprehensive comparison report

## 📊 Output

The system generates:
- **Structured JSON comparison** with pricing, features, integrations, and limitations
- **Markdown table** for easy side-by-side comparison
- **Detailed analysis** with recommendations for small to mid-size B2B businesses

## 🔧 Configuration

Key configuration options in `config.py`:
- CRM tools to research
- Research focus areas
- API endpoints and models
- System timeouts and limits

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coordinator   │────│  Web Research   │────│ Data Analysis   │
│     Agent       │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Validation     │    │    Report       │    │   Web Search    │
│     Agent       │    │   Generation    │    │      Tool       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔍 Research Areas

For each CRM tool, the system researches:
- **Pricing**: Free tiers, paid plans, enterprise pricing
- **Features**: Core functionality, advanced capabilities, unique features
- **Integrations**: Popular business tools, API access, marketplace
- **Limitations**: User complaints, missing features, technical constraints

## 📝 Notes

- The system uses CrewAI for agent orchestration
- Agents communicate through hierarchical delegation
- Research is conducted in real-time using web search APIs
- All findings are validated through cross-referencing multiple sources
