import abc

class SpecializedAgentBase(abc.ABC):
    def __init__(self, agent_name: str, allowed_mcp_servers: list[str]):
        self.agent_name = agent_name
        self.allowed_mcp_servers = allowed_mcp_servers

    @abc.abstractmethod
    def perform_task(self, task_details: dict) -> dict:
        pass
