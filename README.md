# TrendAgent

## Project Description
TrendAgent demonstrates a multi-agent setup where a `CentralAgent` coordinates work across specialized agents and an escalation `AgentSquad`. It relies on stub MCP servers to emulate external systems for testing.

## Installation
1. Create a virtual environment with Python 3.10 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Only a subset of these packages is required to run the tests, but installing everything ensures environment parity.

## Running Tests
Execute the unit and integration tests with `pytest` from the project root:
```bash
pytest -q
```

## Architecture
- **CentralAgent** – entry point for client requests. It validates each request, selects the appropriate specialized agent based on the `mcp_server` field, and escalates failures to the `AgentSquad`.
- **SpecializedAgentA** and **SpecializedAgentB** – handle requests for specific MCP servers (A and B respectively). They call their stub servers (`MCPStubServerA` and `MCPStubServerB`) to attempt a solution.
- **AgentSquad** – a cooperative agent used when specialized agents fail or when no specialized agent is available. It uses `MCPStubServerC` to enrich partial data and produce a final answer.
- **mcp_stubs** – contains the stub server classes that simulate MCP behavior for testing and development.

## Environment Variables
The repository includes `.env.example` with sample configuration values. If you extend the application to use environment variables, copy this file to `.env` and adjust the values for your environment.
