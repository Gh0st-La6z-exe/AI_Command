from command_center.task import TaskStatus

class Executor:
    def __init__(self, agent, tool_registry):
        self.agent = agent
        self.tool_registry = tool_registry

    def execute_step(self, step, context):
        #The Executor owns deterministic validation of a plan step.
        if not step.action:
            raise ValueError("Plan step is missing an action.")
        
        if not step.input:
            raise ValueError("Plan step is missing input.")

        #Verify that the requested action is actually registered,
        #before allowing the agent to execute it
        try:            
            tool = self.tool_registry(step.action)
        except KeyError:
            raise ValueError(
                f"Unknown Action: {step.action}"
            )
                
        result = self.agent.run(step, context, tool)

        return result

        assert isinstance(result, ToolResult)

    def execute_plan(self, plan, context):
        context.task.status = TaskStatus.RUNNING

        results = []

        try:
            for step in plan.steps:
                result = self.execute_step(step, context)
                results.append(result)

            context.task.status = TaskStatus.COMPLETED
            return results

        except Exception:
            context.task.status = TaskStatus.FAILED
            raise
        