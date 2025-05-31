from .specialized_agent_base import SpecializedAgentBase
from mcp_stubs.stub_servers import MCPStubServerA, MCPStubServerB, MCPStubServerC

class SpecializedAgentA(SpecializedAgentBase):
    def __init__(self, allowed_mcp_servers: list[str]):
        super().__init__(agent_name="SpecializedAgentA", allowed_mcp_servers=allowed_mcp_servers)

    def perform_task(self, task_details: dict) -> dict:
        print(f"{self.agent_name}: Received task for {task_details.get('mcp_server')}")
        target_mcp_server = task_details.get('mcp_server')

        if target_mcp_server not in self.allowed_mcp_servers:
            print(f"{self.agent_name}: Access denied to {target_mcp_server}")
            return {"solved": False, "error": f"{self.agent_name} cannot access {target_mcp_server}.", "partial_data": task_details}

        print(f"{self.agent_name}: Attempting to solve with {target_mcp_server}")
        if target_mcp_server == "MCPStubServerA":
            server_instance = MCPStubServerA(target_mcp_server)
        else:
            # This case should ideally not be reached
            print(f"{self.agent_name}: Incorrect server configuration for {target_mcp_server}")
            return {"solved": False, "error": f"Incorrect server configuration for {self.agent_name}.", "partial_data": task_details}

        server_response = server_instance.solve(task_details.get('data'))

        if server_response.get("success"):
            print(f"{self.agent_name}: Task solved successfully by {target_mcp_server}")
            return {"solved": True, "result": server_response['data']}
        else:
            print(f"{self.agent_name}: MCP interaction failed for {target_mcp_server}")
            return {"solved": False, "error": server_response.get('error'), "partial_data": task_details}

class SpecializedAgentB(SpecializedAgentBase):
    def __init__(self, allowed_mcp_servers: list[str]):
        super().__init__(agent_name="SpecializedAgentB", allowed_mcp_servers=allowed_mcp_servers)

    def perform_task(self, task_details: dict) -> dict:
        print(f"{self.agent_name}: Received task for {task_details.get('mcp_server')}")
        target_mcp_server = task_details.get('mcp_server')

        if target_mcp_server not in self.allowed_mcp_servers:
            print(f"{self.agent_name}: Access denied to {target_mcp_server}")
            return {"solved": False, "error": f"{self.agent_name} cannot access {target_mcp_server}.", "partial_data": task_details}

        print(f"{self.agent_name}: Attempting to solve with {target_mcp_server}")
        if target_mcp_server == "MCPStubServerB":
            server_instance = MCPStubServerB(target_mcp_server)
        else:
            # This case should ideally not be reached
            print(f"{self.agent_name}: Incorrect server configuration for {target_mcp_server}")
            return {"solved": False, "error": f"Incorrect server configuration for {self.agent_name}.", "partial_data": task_details}

        server_response = server_instance.solve(task_details.get('data'))

        if server_response.get("success"):
            print(f"{self.agent_name}: Task solved successfully by {target_mcp_server}")
            return {"solved": True, "result": server_response['data']}
        else:
            print(f"{self.agent_name}: MCP interaction failed for {target_mcp_server}")
            return {"solved": False, "error": server_response.get('error'), "partial_data": task_details}
