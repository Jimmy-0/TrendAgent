import unittest
from mcp_stubs.stub_servers import MCPStubServerA, MCPStubServerB, MCPStubServerC

class TestMCPStubServers(unittest.TestCase):

    def test_mcp_stub_server_a_init(self):
        server = MCPStubServerA(server_name="TestServerA")
        self.assertEqual(server.server_name, "TestServerA")

    def test_mcp_stub_server_a_solve_success(self):
        server = MCPStubServerA(server_name="TestServerA")
        task_data = {"data": "Sample task data"}
        response = server.solve(task_data)
        self.assertTrue(response["success"])
        self.assertIn("Processed data from TestServerA", response["data"])
        self.assertIn("Sample task data", response["data"])

    def test_mcp_stub_server_a_solve_error(self):
        server = MCPStubServerA(server_name="TestServerA")
        task_data = {"error": True, "data": "Sample task data"}
        response = server.solve(task_data)
        self.assertFalse(response["success"])
        self.assertIn("Simulated processing error in TestServerA", response["error"])

    def test_mcp_stub_server_a_enrich_and_solve(self):
        server = MCPStubServerA(server_name="TestServerA")
        with self.assertRaises(NotImplementedError):
            server.enrich_and_solve("Partial data")

    def test_mcp_stub_server_b_init(self):
        server = MCPStubServerB(server_name="TestServerB")
        self.assertEqual(server.server_name, "TestServerB")

    def test_mcp_stub_server_b_solve_success(self):
        server = MCPStubServerB(server_name="TestServerB")
        task_data = {"data": "Sample task data for B"}
        response = server.solve(task_data)
        self.assertTrue(response["success"])
        self.assertIn("Processed data from TestServerB", response["data"])
        self.assertIn("Sample task data for B", response["data"])

    def test_mcp_stub_server_b_solve_error(self):
        server = MCPStubServerB(server_name="TestServerB")
        task_data = {"error": True, "data": "Sample task data for B"}
        response = server.solve(task_data)
        self.assertFalse(response["success"])
        self.assertIn("Simulated processing error in TestServerB", response["error"])

    def test_mcp_stub_server_b_enrich_and_solve(self):
        server = MCPStubServerB(server_name="TestServerB")
        with self.assertRaises(NotImplementedError):
            server.enrich_and_solve("Partial data for B")

    def test_mcp_stub_server_c_init(self):
        server = MCPStubServerC(server_name="TestServerC")
        self.assertEqual(server.server_name, "TestServerC")

    def test_mcp_stub_server_c_solve_success_enrichment_needed(self):
        server = MCPStubServerC(server_name="TestServerC")
        task_data = {"enrichment_needed": True, "partial_data": "Data needing enrichment"}
        response = server.solve(task_data)
        self.assertTrue(response["success"])
        self.assertIn("Enriched data by TestServerC", response["data"])
        self.assertIn("Data needing enrichment with new details", response["data"])

    def test_mcp_stub_server_c_solve_failure_enrichment_not_needed(self):
        server = MCPStubServerC(server_name="TestServerC")
        task_data = {"enrichment_needed": False, "partial_data": "Data"}
        response = server.solve(task_data)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "TestServerC requires enrichment_needed to be true.")

    def test_mcp_stub_server_c_solve_failure_missing_enrichment_flag(self):
        server = MCPStubServerC(server_name="TestServerC")
        task_data = {"partial_data": "Data"} # Missing enrichment_needed
        response = server.solve(task_data)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "TestServerC requires enrichment_needed to be true.")

    def test_mcp_stub_server_c_enrich_and_solve_success(self):
        server = MCPStubServerC(server_name="TestServerC")
        partial_data = "Initial data for comprehensive analysis"
        response = server.enrich_and_solve(partial_data)
        self.assertTrue(response["success"])
        self.assertIn("Enriched and solved by TestServerC", response["data"])
        self.assertIn("Initial data for comprehensive analysis with comprehensive analysis", response["data"])

if __name__ == '__main__':
    unittest.main()
