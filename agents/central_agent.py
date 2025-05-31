from .specialized_agents import SpecializedAgentA, SpecializedAgentB
from .agent_squad import AgentSquad

class CentralAgent:
    def __init__(self):
        agent_configs = {
            "SpecializedAgentA": {
                "mcp_servers": ["MCPStubServerA"],
                "target_mcp_routing": ["MCPStubServerA"] # MCPs this agent is primarily responsible for
            },
            "SpecializedAgentB": {
                "mcp_servers": ["MCPStubServerB"],
                "target_mcp_routing": ["MCPStubServerB"]
            }
            # New agents could be added here
        }

        self.specialized_agent_a_instance = SpecializedAgentA(
            allowed_mcp_servers=agent_configs["SpecializedAgentA"]["mcp_servers"]
        )
        self.specialized_agent_b_instance = SpecializedAgentB(
            allowed_mcp_servers=agent_configs["SpecializedAgentB"]["mcp_servers"]
        )
        self.agent_squad = AgentSquad()

        self.specialized_agent_routing = {}
        if self.specialized_agent_a_instance: # Check if instance exists
            for mcp_target in agent_configs["SpecializedAgentA"]["target_mcp_routing"]:
                self.specialized_agent_routing[mcp_target] = self.specialized_agent_a_instance
        if self.specialized_agent_b_instance:
            for mcp_target in agent_configs["SpecializedAgentB"]["target_mcp_routing"]:
                self.specialized_agent_routing[mcp_target] = self.specialized_agent_b_instance

    def validate_request(self, request: dict) -> tuple[bool, str | None]:
        # Logging for request validation can be added here if desired,
        # but the prompt focuses on handle_client_request
        if 'mcp_server' not in request:
            return False, "Missing 'mcp_server' key in request."
        if 'data' not in request:
            return False, "Missing 'data' key in request."
        return True, None

    def identify_specialized_agent(self, validated_request: dict):
        target_mcp_server = validated_request.get('mcp_server')
        return self.specialized_agent_routing.get(target_mcp_server)

    def handle_client_request(self, client_request: dict) -> dict:
        is_valid, error_msg = self.validate_request(client_request)
        if not is_valid:
            # No print here as per prompt, but one could be added for invalid requests.
            return {"success": False, "error": f"Invalid request: {error_msg}"}

        print(f"CentralAgent: Validated request for {client_request.get('mcp_server')}")

        specialized_agent = self.identify_specialized_agent(client_request)

        if specialized_agent:
            print(f"CentralAgent: Routing to {type(specialized_agent).__name__} for {client_request.get('mcp_server')}")
            response = specialized_agent.perform_task(client_request)
            if response.get('solved'):
                print(f"CentralAgent: {type(specialized_agent).__name__} solved the task.")
                return {"success": True, "data": response['result']}
            else:
                print(f"CentralAgent: {type(specialized_agent).__name__} failed, escalating to AgentSquad.")
                squad_response = self.agent_squad.enrich_and_solve({
                    "original_request": client_request,
                    "partial_data": response
                })
                if squad_response.get('solved'):
                    print("CentralAgent: AgentSquad solved the task.")
                    return {"success": True, "data": squad_response['result']}
                else:
                    print("CentralAgent: AgentSquad failed to solve the task.")
                    return {"success": False, "error": squad_response.get('error', 'Task could not be resolved by AgentSquad')}
        else:
            print(f"CentralAgent: No specialized agent for {client_request.get('mcp_server')}, routing to AgentSquad.")
            squad_response = self.agent_squad.enrich_and_solve({
                "original_request": client_request,
                "partial_data": {"error": "No specialized agent for this MCP.", "data": client_request.get('data')}
            })

            if squad_response.get('solved'):
                print("CentralAgent: AgentSquad solved the task.")
                return {"success": True, "data": squad_response['result']}
            else:
                print("CentralAgent: AgentSquad failed to solve the task.")
                return {"success": False, "error": squad_response.get('error', 'Task could not be resolved by AgentSquad after direct escalation')}
