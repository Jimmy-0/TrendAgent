import unittest
from unittest.mock import patch, MagicMock
from agents.agent_squad import AgentSquad
from mcp_stubs.stub_servers import MCPStubServerC # Used by AgentSquad

class TestAgentSquad(unittest.TestCase):

    def test_agent_squad_init(self):
        squad = AgentSquad(squad_name="TestSquad")
        self.assertEqual(squad.squad_name, "TestSquad")
        self.assertIsInstance(squad.mcp_server_c, MCPStubServerC)
        self.assertEqual(squad.mcp_server_c.server_name, "MCPStubServerC")

    @patch('agents.agent_squad.MCPStubServerC')
    def test_enrich_and_solve_success(self, MockMCPStubServerC):
        # Configure the mock MCPStubServerC instance and its enrich_and_solve method
        mock_server_c_instance = MockMCPStubServerC.return_value
        mock_server_c_instance.enrich_and_solve.return_value = {
            "success": True,
            "data": "Squad successfully enriched and solved"
        }

        # Instantiate AgentSquad (which will use the mocked MCPStubServerC)
        # We need to re-patch the instance used by AgentSquad or pass the mock
        squad = AgentSquad(squad_name="TestSquad")
        squad.mcp_server_c = mock_server_c_instance # Ensure squad uses our mock

        escalation_details = {
            "original_request": {"data": "Original task data"},
            "partial_data": {"error": "Specialized failed", "data": {"original_data_key": "Original task data"}}
        }

        response = squad.enrich_and_solve(escalation_details)

        # Check that MCPStubServerC's enrich_and_solve was called correctly
        # The logic in AgentSquad tries to find 'data', let's trace that
        # It will look into partial_data['data']['original_data_key']
        # or original_request['data']
        # Based on current AgentSquad logic, it will first check partial_data['data']
        # then original_request['data']
        # then partial_data['data']['data'] (if nested)
        # then the whole partial_data_dict.
        # In this test case, partial_data['data'] is {"original_data_key": "Original task data"}
        # So, this dict is passed to enrich_and_solve.
        mock_server_c_instance.enrich_and_solve.assert_called_once_with(
            {"original_data_key": "Original task data"}
        )

        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "Squad successfully enriched and solved")

    @patch('agents.agent_squad.MCPStubServerC')
    def test_enrich_and_solve_success_original_request_data(self, MockMCPStubServerC):
        mock_server_c_instance = MockMCPStubServerC.return_value
        mock_server_c_instance.enrich_and_solve.return_value = {
            "success": True,
            "data": "Squad used original_request data"
        }
        squad = AgentSquad(squad_name="TestSquad")
        squad.mcp_server_c = mock_server_c_instance

        escalation_details = {
            "original_request": {"data": "Data from original request"},
            "partial_data": {"error": "Specialized failed", "data": None} # No data here
        }
        response = squad.enrich_and_solve(escalation_details)
        mock_server_c_instance.enrich_and_solve.assert_called_once_with("Data from original request")
        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "Squad used original_request data")


    @patch('agents.agent_squad.MCPStubServerC')
    def test_enrich_and_solve_success_nested_partial_data(self, MockMCPStubServerC):
        mock_server_c_instance = MockMCPStubServerC.return_value
        mock_server_c_instance.enrich_and_solve.return_value = {
            "success": True,
            "data": "Squad used nested partial data"
        }
        squad = AgentSquad(squad_name="TestSquad")
        squad.mcp_server_c = mock_server_c_instance

        escalation_details = {
            "original_request": {"data": "Original"},
            # This structure matches partial_data['data']['data']
            "partial_data": {"error": "Specialized failed", "data": {"data": "Nested data to use"}}
        }
        response = squad.enrich_and_solve(escalation_details)
        # partial_data['data'] is {"data": "Nested data to use"}
        # then partial_data['data']['data'] is "Nested data to use"
        mock_server_c_instance.enrich_and_solve.assert_called_once_with("Nested data to use")
        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "Squad used nested partial data")

    @patch('agents.agent_squad.MCPStubServerC')
    def test_enrich_and_solve_success_fallback_partial_data_dict(self, MockMCPStubServerC):
        mock_server_c_instance = MockMCPStubServerC.return_value
        mock_server_c_instance.enrich_and_solve.return_value = {
            "success": True,
            "data": "Squad used fallback partial_data_dict"
        }
        squad = AgentSquad(squad_name="TestSquad")
        squad.mcp_server_c = mock_server_c_instance

        # Neither partial_data['data'], original_request['data'], nor partial_data['data']['data'] are present/valid
        escalation_details = {
            "original_request": {"info": "No data key"}, # No 'data' key
            "partial_data": {"error": "Specialized failed", "details": "Some other details"} # No 'data' key
        }
        response = squad.enrich_and_solve(escalation_details)
        # Fallback: passes the whole partial_data dict
        mock_server_c_instance.enrich_and_solve.assert_called_once_with(
            {"error": "Specialized failed", "details": "Some other details"}
        )
        self.assertTrue(response["solved"])
        self.assertEqual(response["result"], "Squad used fallback partial_data_dict")


    @patch('agents.agent_squad.MCPStubServerC')
    def test_enrich_and_solve_mcp_failure(self, MockMCPStubServerC):
        mock_server_c_instance = MockMCPStubServerC.return_value
        mock_server_c_instance.enrich_and_solve.return_value = {
            "success": False,
            "error": "MCPStubServerC enrichment failed"
        }

        squad = AgentSquad(squad_name="TestSquad")
        squad.mcp_server_c = mock_server_c_instance

        escalation_details = {
             "original_request": {"data": "Original task data"},
            "partial_data": {"error": "Specialized failed", "data": {"info": "Some info"}}
        }

        response = squad.enrich_and_solve(escalation_details)

        mock_server_c_instance.enrich_and_solve.assert_called_once_with({"info": "Some info"})
        self.assertFalse(response["solved"])
        self.assertEqual(response["error"], "MCPStubServerC enrichment failed")

if __name__ == '__main__':
    unittest.main()
