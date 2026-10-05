from command_center.tools.result import ToolResult


class Executor:
    def __init__(self, agent, tool_registry):
        self.agent = agent
        self.tool_registry = tool_registry

    def execute_step(self, step, context):
        # Executor is the deterministic gate for every plan step.
        # Before anything gets executed, it makes sure the step actually
        # contains an action and input. Bad instructions stop here instead
        # of propagating further into the execution pipeline.
        if not step.action:
            raise ValueError("Plan step is missing an action.")

        if not step.input:
            raise ValueError("Plan step is missing input.")

        # The Planner decides WHAT action should happen.
        # Executor decides WHICH registered tool is actually allowed to
        # perform that action. The Agent does not get to choose the tool;
        # it receives the exact callable Executor resolved here.
        try:
            tool = self.tool_registry(step.action)
        except KeyError:
            raise ValueError(
                f"Unknown action: {step.action}"
            )

        result = self.agent.run(step, context, tool)

        # Agent performed the operation; Executor verifies what came back.
        # This keeps deterministic result validation out of the Agent and
        # gives the execution layer ownership of the tool/result contract.
        assert isinstance(result, ToolResult)

        return result

    def execute_plan(self, plan, context):
        results = []

        for step in plan.steps:
            result = self.execute_step(step, context)
            results.append(result)

        return results