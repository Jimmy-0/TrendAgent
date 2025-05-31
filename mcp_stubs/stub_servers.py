class MCPStubServerA:
    def __init__(self, server_name):
        self.server_name = server_name

    def solve(self, task_data):
        # task_data is the actual data payload, e.g. {"info": "some_info"} or {"payload": "...", "error": True}
        if isinstance(task_data, dict) and task_data.get("error"):
            return {"success": False, "error": f"Simulated processing error in {self.server_name}"}
        return {"success": True, "data": f"Processed data from {self.server_name}: {task_data}"}

    def enrich_and_solve(self, partial_data):
        raise NotImplementedError(f"{self.server_name} does not implement enrich_and_solve")

class MCPStubServerB:
    def __init__(self, server_name):
        self.server_name = server_name

    def solve(self, task_data):
        # task_data is the actual data payload
        if isinstance(task_data, dict) and task_data.get("error"):
            return {"success": False, "error": f"Simulated processing error in {self.server_name}"}
        return {"success": True, "data": f"Processed data from {self.server_name}: {task_data}"}

    def enrich_and_solve(self, partial_data):
        raise NotImplementedError(f"{self.server_name} does not implement enrich_and_solve")

class MCPStubServerC:
    def __init__(self, server_name):
        self.server_name = server_name

    def solve(self, task_data):
        if task_data.get("enrichment_needed"):
            return {"success": True, "data": f"Enriched data by {self.server_name}: {task_data.get('partial_data')} with new details"}
        return {"success": False, "error": f"{self.server_name} requires enrichment_needed to be true."}

    def enrich_and_solve(self, partial_data):
        return {"success": True, "data": f"Enriched and solved by {self.server_name}: {partial_data} with comprehensive analysis"}
