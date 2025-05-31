import unittest
from unittest.mock import patch, MagicMock
from agents.specialized_agents import SpecializedAgentA, SpecializedAgentB
# Assuming mcp_stubs.stub_servers will be in the python path or PYTHONPATH is set up
from mcp_stubs.stub_servers import MCPStubServerA, MCPStubServerB

class TestSpecializedAgents(unittest.TestCase):

    def test_specialized_agent_a_init(self):
        agent = SpecializedAgentA(allowed_mcp_servers=["MCPStubServerA", "AnotherServer"])
        self.assertEqual(agent.agent_name, "SpecializedAgentA")
        self.assertEqual(agent.allowed_mcp_servers, ["MCPStubServerA", "AnotherServer"])

    @patch('agents.specialized_agents.MCPStubServerA')
    def test_specialized_agent_a_perform_task_success(self, MockMCPStubServerA):
        # Configure the mock server instance and its solve method
        mock_server_instance = MockMCPStubServerA.return_value
        mock_server_instance.solve.return_value = {"success": True, "data": "ServerA processed data"}

        agent = SpecializedAgentA(allowed_mcp_servers=["MCPStubServerA"])
        task_details = {"mcp_server": "MCPStubServerA", "data": {"info": "Task for A"}}

        response = agent.perform_task(task_details)

        MockMCPStubServerA.assert_called_once_with("MCPStubServerA")
        mock_server_instance.solve.assert_called_once_with({"info": "Task for A"})
        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "ServerA processed data")

    @patch('agents.specialized_agents.MCPStubServerA')
    def test_specialized_agent_a_perform_task_mcp_failure(self, MockMCPStubServerA):
        mock_server_instance = MockMCPStubServerA.return_value
        mock_server_instance.solve.return_value = {"success": False, "error": "ServerA error"}

        agent = SpecializedAgentA(allowed_mcp_servers=["MCPStubServerA"])
        task_details = {"mcp_server": "MCPStubServerA", "data": {"info": "Task for A"}}

        response = agent.perform_task(task_details)

        MockMCPStubServerA.assert_called_once_with("MCPStubServerA")
        mock_server_instance.solve.assert_called_once_with({"info": "Task for A"})
        self.assertFalse(response["solved"])
        self.assertEqual(response["error"], "ServerA error")
        self.assertEqual(response["partial_data"], task_details)

    def test_specialized_agent_a_perform_task_server_not_allowed(self):
        agent = SpecializedAgentA(allowed_mcp_servers=["MCPStubServerX"]) # ServerA not in allowed
        task_details = {"mcp_server": "MCPStubServerA", "data": {"info": "Task for A"}}

        response = agent.perform_task(task_details)

        self.assertFalse(response["solved"])
        self.assertIn("cannot access MCPStubServerA", response["error"])
        self.assertEqual(response["partial_data"], task_details)

    # Tests for SpecializedAgentB (similar structure to SpecializedAgentA)
    def test_specialized_agent_b_init(self):
        agent = SpecializedAgentB(allowed_mcp_servers=["MCPStubServerB"])
        self.assertEqual(agent.agent_name, "SpecializedAgentB")
        self.assertEqual(agent.allowed_mcp_servers, ["MCPStubServerB"])

    @patch('agents.specialized_agents.MCPStubServerB')
    def test_specialized_agent_b_perform_task_success(self, MockMCPStubServerB):
        mock_server_instance = MockMCPStubServerB.return_value
        mock_server_instance.solve.return_value = {"success": True, "data": "ServerB processed data"}

        agent = SpecializedAgentB(allowed_mcp_servers=["MCPStubServerB"])
        task_details = {"mcp_server": "MCPStubServerB", "data": {"info": "Task for B"}}

        response = agent.perform_task(task_details)

        MockMCPStubServerB.assert_called_once_with("MCPStubServerB")
        mock_server_instance.solve.assert_called_once_with({"info": "Task for B"})
        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "ServerB processed data")

    @patch('agents.specialized_agents.MCPStubServerB')
    def test_specialized_agent_b_perform_task_mcp_failure(self, MockMCPStubServerB):
        mock_server_instance = MockMCPStubServerB.return_value
        mock_server_instance.solve.return_value = {"success": False, "error": "ServerB error"}

        agent = SpecializedAgentB(allowed_mcp_servers=["MCPStubServerB"])
        task_details = {"mcp_server": "MCPStubServerB", "data": {"info": "Task for B"}}

        response = agent.perform_task(task_details)

        MockMCPStubServerB.assert_called_once_with("MCPStubServerB")
        mock_server_instance.solve.assert_called_once_with({"info": "Task for B"})
        self.assertFalse(response["solved"])
        self.assertEqual(response["error"], "ServerB error")
        self.assertEqual(response["partial_data"], task_details)

    def test_specialized_agent_b_perform_task_server_not_allowed(self):
        agent = SpecializedAgentB(allowed_mcp_servers=["MCPStubServerY"]) # ServerB not in allowed
        task_details = {"mcp_server": "MCPStubServerB", "data": {"info": "Task for B"}}

        response = agent.perform_task(task_details)

        self.assertFalse(response["solved"])
        self.assertIn("cannot access MCPStubServerB", response["error"])
        self.assertEqual(response["partial_data"], task_details)

if __name__ == '__main__':
    unittest.main()
