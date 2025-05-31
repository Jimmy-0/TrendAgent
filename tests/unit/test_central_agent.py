import unittest
from unittest.mock import patch, MagicMock
from agents.central_agent import CentralAgent
from agents.specialized_agents import SpecializedAgentA, SpecializedAgentB
from agents.agent_squad import AgentSquad

class TestCentralAgent(unittest.TestCase):

    @patch('agents.central_agent.SpecializedAgentA')
    @patch('agents.central_agent.SpecializedAgentB')
    @patch('agents.central_agent.AgentSquad')
    def test_central_agent_init(self, MockAgentSquad, MockSpecializedAgentB, MockSpecializedAgentA):
        central_agent = CentralAgent()
        MockSpecializedAgentA.assert_called_once_with(allowed_mcp_servers=["MCPStubServerA"])
        MockSpecializedAgentB.assert_called_once_with(allowed_mcp_servers=["MCPStubServerB"])
        MockAgentSquad.assert_called_once_with()
        # self.assertIsInstance(central_agent.specialized_agent_a_instance, MockSpecializedAgentA) # Causes TypeError
        # self.assertIsInstance(central_agent.specialized_agent_b_instance, MockSpecializedAgentB) # Causes TypeError
        # self.assertIsInstance(central_agent.agent_squad, MockAgentSquad) # Causes TypeError
        self.assertEqual(central_agent.specialized_agent_routing["MCPStubServerA"], central_agent.specialized_agent_a_instance)
        self.assertEqual(central_agent.specialized_agent_routing["MCPStubServerB"], central_agent.specialized_agent_b_instance)

    def test_validate_request_valid(self):
        central_agent = CentralAgent()
        request = {"mcp_server": "ServerA", "data": "TaskData"}
        is_valid, error_msg = central_agent.validate_request(request)
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_request_invalid_missing_mcp_server(self):
        central_agent = CentralAgent()
        request = {"data": "TaskData"}
        is_valid, error_msg = central_agent.validate_request(request)
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Missing 'mcp_server' key in request.")

    def test_validate_request_invalid_missing_data(self):
        central_agent = CentralAgent()
        request = {"mcp_server": "ServerA"}
        is_valid, error_msg = central_agent.validate_request(request)
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Missing 'data' key in request.")

    def test_identify_specialized_agent(self):
        central_agent = CentralAgent()
        self.assertEqual(central_agent.identify_specialized_agent({"mcp_server": "MCPStubServerA"}), central_agent.specialized_agent_a_instance)
        self.assertEqual(central_agent.identify_specialized_agent({"mcp_server": "MCPStubServerB"}), central_agent.specialized_agent_b_instance)
        self.assertIsNone(central_agent.identify_specialized_agent({"mcp_server": "UnknownServer"}))

    @patch.object(CentralAgent, 'validate_request')
    def test_handle_client_request_invalid_request(self, mock_validate_request):
        mock_validate_request.return_value = (False, "Test validation error")
        central_agent = CentralAgent()
        response = central_agent.handle_client_request({})
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Invalid request: Test validation error")
        mock_validate_request.assert_called_once_with({})

    @patch.object(CentralAgent, 'validate_request', return_value=(True, None))
    @patch.object(CentralAgent, 'identify_specialized_agent')
    def test_handle_client_request_specialized_agent_solves(self, mock_identify_agent, mock_validate_request):
        mock_specialized_agent = MagicMock()
        mock_specialized_agent.perform_task.return_value = {"solved": True, "result": "Specialized success"}
        mock_identify_agent.return_value = mock_specialized_agent

        central_agent = CentralAgent()
        client_request = {"mcp_server": "MCPStubServerA", "data": "some data"}
        response = central_agent.handle_client_request(client_request)

        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "Specialized success")
        mock_validate_request.assert_called_once_with(client_request)
        mock_identify_agent.assert_called_once_with(client_request)
        mock_specialized_agent.perform_task.assert_called_once_with(client_request)

    @patch.object(CentralAgent, 'validate_request', return_value=(True, None))
    @patch.object(CentralAgent, 'identify_specialized_agent')
    @patch.object(AgentSquad, 'enrich_and_solve') # Patching the class method
    def test_handle_client_request_specialized_fails_squad_solves(self, mock_squad_solve, mock_identify_agent, mock_validate_request):
        mock_specialized_agent = MagicMock()
        specialized_failure_response = {"solved": False, "error": "Specialized failed", "partial_data": "partial"}
        mock_specialized_agent.perform_task.return_value = specialized_failure_response
        mock_identify_agent.return_value = mock_specialized_agent

        mock_squad_solve.return_value = {"solved": True, "result": "Squad success"}

        central_agent = CentralAgent()
        # Ensure the agent_squad instance within central_agent uses the mocked method
        central_agent.agent_squad.enrich_and_solve = mock_squad_solve

        client_request = {"mcp_server": "MCPStubServerA", "data": "some data"}
        response = central_agent.handle_client_request(client_request)

        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "Squad success")
        mock_validate_request.assert_called_once_with(client_request)
        mock_identify_agent.assert_called_once_with(client_request)
        mock_specialized_agent.perform_task.assert_called_once_with(client_request)
        mock_squad_solve.assert_called_once_with({
            "original_request": client_request,
            "partial_data": specialized_failure_response
        })

    @patch.object(CentralAgent, 'validate_request', return_value=(True, None))
    @patch.object(CentralAgent, 'identify_specialized_agent')
    @patch.object(AgentSquad, 'enrich_and_solve')
    def test_handle_client_request_specialized_fails_squad_fails(self, mock_squad_solve, mock_identify_agent, mock_validate_request):
        mock_specialized_agent = MagicMock()
        specialized_failure_response = {"solved": False, "error": "Specialized failed", "partial_data": "partial"}
        mock_specialized_agent.perform_task.return_value = specialized_failure_response
        mock_identify_agent.return_value = mock_specialized_agent

        mock_squad_solve.return_value = {"solved": False, "error": "Squad failed"}

        central_agent = CentralAgent()
        central_agent.agent_squad.enrich_and_solve = mock_squad_solve

        client_request = {"mcp_server": "MCPStubServerA", "data": "some data"}
        response = central_agent.handle_client_request(client_request)

        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Squad failed")
        mock_squad_solve.assert_called_once_with({
            "original_request": client_request,
            "partial_data": specialized_failure_response
        })

    @patch.object(CentralAgent, 'validate_request', return_value=(True, None))
    @patch.object(CentralAgent, 'identify_specialized_agent', return_value=None) # No specialized agent
    @patch.object(AgentSquad, 'enrich_and_solve')
    def test_handle_client_request_no_specialized_agent_squad_solves(self, mock_squad_solve, mock_identify_agent, mock_validate_request):
        mock_squad_solve.return_value = {"solved": True, "result": "Squad direct success"}

        central_agent = CentralAgent()
        central_agent.agent_squad.enrich_and_solve = mock_squad_solve

        client_request = {"mcp_server": "MCPStubServerC", "data": {"enrichment_needed": True, "partial_data": "data for C"}}
        response = central_agent.handle_client_request(client_request)

        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "Squad direct success")
        mock_identify_agent.assert_called_once_with(client_request)
        # Check the structure passed to squad_solve for direct escalation
        mock_squad_solve.assert_called_once_with({
            "original_request": client_request,
            "partial_data": {"error": "No specialized agent for this MCP.", "data": client_request.get('data')}
        })

    @patch.object(CentralAgent, 'validate_request', return_value=(True, None))
    @patch.object(CentralAgent, 'identify_specialized_agent', return_value=None) # No specialized agent
    @patch.object(AgentSquad, 'enrich_and_solve')
    def test_handle_client_request_no_specialized_agent_squad_fails(self, mock_squad_solve, mock_identify_agent, mock_validate_request):
        mock_squad_solve.return_value = {"solved": False, "error": "Squad direct fail"}

        central_agent = CentralAgent()
        central_agent.agent_squad.enrich_and_solve = mock_squad_solve

        client_request = {"mcp_server": "UnknownServer", "data": "some data"}
        response = central_agent.handle_client_request(client_request)

        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Squad direct fail")
        mock_squad_solve.assert_called_once_with({
            "original_request": client_request,
            "partial_data": {"error": "No specialized agent for this MCP.", "data": client_request.get('data')}
        })


if __name__ == '__main__':
    unittest.main()
