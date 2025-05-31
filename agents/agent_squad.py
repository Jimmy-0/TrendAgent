from mcp_stubs.stub_servers import MCPStubServerC

class AgentSquad:
    def __init__(self, squad_name="AgentSquad"):
        self.squad_name = squad_name
        self.mcp_server_c = MCPStubServerC("MCPStubServerC")

    def enrich_and_solve(self, escalation_details: dict) -> dict:
        print(f"AgentSquad: Received escalation: {escalation_details}")
        partial_data_dict = escalation_details.get('partial_data', {})

        data_to_enrich = None
        # Try to get data from partial_data['data']
        if 'data' in partial_data_dict and partial_data_dict['data'] is not None:
            data_to_enrich = partial_data_dict['data']
            # If this data is a dictionary and itself contains a 'data' key, prefer the inner 'data'
            # This handles the nested case like partial_data: {"error": "...", "data": {"data": "actual_info"}}
            if isinstance(data_to_enrich, dict) and 'data' in data_to_enrich:
                data_to_enrich = data_to_enrich['data']

        # If not found or was None from partial_data['data'], try original_request['data']
        if data_to_enrich is None and \
           'original_request' in escalation_details and \
           'data' in escalation_details['original_request'] and \
           escalation_details['original_request']['data'] is not None:
             data_to_enrich = escalation_details['original_request']['data']

        # Fallback to the whole partial_data_dict if no specific data could be extracted or if it was explicitly None
        if data_to_enrich is None:
             data_to_enrich = partial_data_dict

        # Ensure data_to_enrich is not None (it could be if partial_data_dict was empty and no original_request data)
        # and is suitable for the server. For MCPStubServerC, enrich_and_solve expects a string or dict.
        # If data_to_enrich is a dictionary, it might need specific formatting or extraction.
        # For this stub, we'll assume it can handle a dictionary by converting it or expecting a certain structure.
        # If it's just a string, that's fine.

        # The stub's enrich_and_solve expects a single argument `partial_data`
        # Let's ensure we pass what it expects. The current stub takes `partial_data` directly.
        # If `data_to_enrich` was extracted from a nested structure, use that.
        # If we are passing the whole `partial_data_dict` because specific data wasn't found, that's also fine for the stub.

        print("AgentSquad: Attempting enrichment with MCPStubServerC")
        server_response = self.mcp_server_c.enrich_and_solve(data_to_enrich)

        if server_response.get("success"):
            print("AgentSquad: Enrichment successful.")
            return {"solved": True, "result": server_response['data']}
        else:
            print("AgentSquad: Enrichment failed.")
            return {"solved": False, "error": server_response.get('error', f'{self.squad_name} failed to enrich and solve')}
