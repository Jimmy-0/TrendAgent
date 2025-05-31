import unittest
from agents.central_agent import CentralAgent
# We use the real stub servers for integration tests
from mcp_stubs.stub_servers import MCPStubServerA, MCPStubServerB, MCPStubServerC

class TestAgentFlows(unittest.TestCase):

    def setUp(self):
        """Set up a CentralAgent instance before each test."""
        self.central_agent = CentralAgent()

    def test_scenario_1_specialized_agent_a_success(self):
        client_request = {"mcp_server": "MCPStubServerA", "data": {"info": "task for A"}}
        response = self.central_agent.handle_client_request(client_request)
        expected_response = {
            "success": True,
            "data": "Processed data from MCPStubServerA: {'info': 'task for A'}"
        }
        self.assertEqual(response, expected_response)

    def test_scenario_2_specialized_agent_b_success(self):
        client_request = {"mcp_server": "MCPStubServerB", "data": {"info": "task for B"}}
        response = self.central_agent.handle_client_request(client_request)
        expected_response = {
            "success": True,
            "data": "Processed data from MCPStubServerB: {'info': 'task for B'}"
        }
        self.assertEqual(response, expected_response)

    def test_scenario_3_revised_agent_a_fails_squad_solves(self):
        # MCPStubServerA's solve method will return an error if task_data contains {"error": True}
        client_request = {
            "mcp_server": "MCPStubServerA",
            "data": {"payload": "complex task for A", "error": True} # This will make MCPStubServerA fail
        }

        # Expected behavior:
        # 1. CentralAgent routes to SpecializedAgentA.
        # 2. SpecializedAgentA calls MCPStubServerA.solve with client_request['data'].
        # 3. MCPStubServerA.solve returns {"success": False, "error": "Simulated processing error in MCPStubServerA"}.
        # 4. SpecializedAgentA returns this failure to CentralAgent.
        # 5. CentralAgent escalates to AgentSquad.
        #    - escalation_details to AgentSquad.enrich_and_solve:
        #      {
        #          "original_request": client_request,
        #          "partial_data": {  // This is the response from SpecializedAgentA
        #              "solved": False,
        #              "error": "Simulated processing error in MCPStubServerA",
        #              "partial_data": client_request // SpecializedAgentA puts original task_details here
        #          }
        #      }
        # 6. AgentSquad.enrich_and_solve extracts data. Based on the updated logic in AgentSquad:
        #    - It will check escalation_details['partial_data']['data'], which is client_request['data']
        #      i.e., {"payload": "complex task for A", "error": True}
        #    - This dictionary is passed to MCPStubServerC.enrich_and_solve.
        # 7. MCPStubServerC.enrich_and_solve returns:
        #    {"success": True, "data": "Enriched and solved by MCPStubServerC: {'payload': 'complex task for A', 'error': True} with comprehensive analysis"}

        response = self.central_agent.handle_client_request(client_request)

        expected_final_data_from_squad = "Enriched and solved by MCPStubServerC: {'payload': 'complex task for A', 'error': True} with comprehensive analysis"
        expected_response = {
            "success": True,
            "data": expected_final_data_from_squad
        }
        self.assertEqual(response, expected_response)

    def test_scenario_4_unknown_server_direct_to_squad(self):
        client_request = {
            "mcp_server": "MCPStubServerUnknown", # This server is not in CentralAgent's routing
            "data": {"info": "direct task for squad"}
        }

        # Expected behavior:
        # 1. CentralAgent.identify_specialized_agent returns None.
        # 2. CentralAgent directly calls AgentSquad.enrich_and_solve.
        #    - escalation_details to AgentSquad.enrich_and_solve:
        #      {
        #          "original_request": client_request,
        #          "partial_data": {
        #              "error": "No specialized agent for this MCP.",
        #              "data": client_request.get('data')
        #              # which is {"info": "direct task for squad"}
        #          }
        #      }
        # 3. AgentSquad.enrich_and_solve extracts data. Based on updated AgentSquad logic:
        #    - It will check escalation_details['partial_data']['data'], which is client_request['data']
        #      i.e., {"info": "direct task for squad"}
        #    - This dictionary is passed to MCPStubServerC.enrich_and_solve.
        # 4. MCPStubServerC.enrich_and_solve returns:
        #    {"success": True, "data": "Enriched and solved by MCPStubServerC: {'info': 'direct task for squad'} with comprehensive analysis"}

        response = self.central_agent.handle_client_request(client_request)

        expected_final_data_from_squad = "Enriched and solved by MCPStubServerC: {'info': 'direct task for squad'} with comprehensive analysis"
        expected_response = {
            "success": True,
            "data": expected_final_data_from_squad
        }
        self.assertEqual(response, expected_response)

    def test_scenario_4b_server_c_direct_to_squad(self):
        # This is similar to UnknownServer, but explicitly targeting MCPStubServerC
        # which also isn't in specialized_agent_routing
        client_request = {
            "mcp_server": "MCPStubServerC",
            "data": {"info": "direct task for Server C via squad"}
        }
        response = self.central_agent.handle_client_request(client_request)
        expected_final_data_from_squad = "Enriched and solved by MCPStubServerC: {'info': 'direct task for Server C via squad'} with comprehensive analysis"
        expected_response = {
            "success": True,
            "data": expected_final_data_from_squad
        }
        self.assertEqual(response, expected_response)


    def test_scenario_5_invalid_request_missing_mcp_server(self):
        client_request = {"data": "some data but no mcp_server"} # Missing 'mcp_server'
        response = self.central_agent.handle_client_request(client_request)
        expected_response = {
            "success": False,
            "error": "Invalid request: Missing 'mcp_server' key in request."
        }
        self.assertEqual(response, expected_response)

    def test_scenario_5b_invalid_request_missing_data(self):
        client_request = {"mcp_server": "MCPStubServerA"} # Missing 'data'
        response = self.central_agent.handle_client_request(client_request)
        expected_response = {
            "success": False,
            "error": "Invalid request: Missing 'data' key in request."
        }
        self.assertEqual(response, expected_response)

if __name__ == '__main__':
    unittest.main()
