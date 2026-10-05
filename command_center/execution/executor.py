import time

from command_center.tools.result import ToolResult
from command_center.tools.registry import get_capability
from command_center.task import ExecutionRecord


class Executor:
    def __init__(self, agent, tool_registry, capability_registry=get_capability):
        self.agent = agent
        self.tool_registry = tool_registry
        self.capability_registry = capability_registry

    def execute_step(self, step, context):
        # Executor is the deterministic gate for every plan step.
        # Before anything gets executed, it makes sure the step actually
        # contains an action and input. Bad instructions stop here instead
        # of propagating further into the execution pipeline.
        if not step.action:
            raise ValueError("Plan step is missing an action.")

        if not step.input:
            raise ValueError("Plan step is missing input.")

        try:
            capability = self.capability_registry(step.action)
        except KeyError:
            raise ValueError(f"Unknown action: {step.action}")

        capability.validate_input(step.input)

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

        def validator(result):
            # Validator closes over the capability to ensure the tool's return
            # type explicitly matches the registry's documented contract.
            if not isinstance(result, ToolResult) or not isinstance(
                result, capability.result_type
            ):
                raise TypeError(
                    f"Action '{step.action}' returned an invalid result type."
                )

        start_time = time.time()

        try:
            result = self.agent.run(step, context, tool, validator=validator)
            elapsed_ms = (time.time() - start_time) * 1000.0

            # Because validation passed, the result is now securely at the end of the list.
            result_index = len(context.task.results) - 1

            record = ExecutionRecord(
                step_id=step.id,
                action=step.action,
                input_reference=step.input,
                elapsed_ms=elapsed_ms,
                success=True,
                result_index=result_index,
                result_type=capability.result_type.__name__
            )
            context.task.records.append(record)

            return result

        except Exception as error:
            elapsed_ms = (time.time() - start_time) * 1000.0
            record = ExecutionRecord(
                step_id=step.id,
                action=step.action,
                input_reference=step.input,
                elapsed_ms=elapsed_ms,
                success=False,
                error=str(error)
            )
            context.task.records.append(record)
            raise

    def execute_plan(self, plan, context):
        results = []

        for step in plan.steps:
            result = self.execute_step(step, context)
            results.append(result)

        return results