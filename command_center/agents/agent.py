from command_center.events.event import Event


class Agent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

    def run(self, step, context, tool):
        # Agent owns the execution lifecycle and observability for an
        # individual plan step. The Executor has already validated the
        # step and selected the tool, so Agent does not make those decisions.
        self.bus.emit(
            Event(
                type="agent.started",
                data={
                    "agent": self.name,
                    "task_id": context.task.id,
                },
            )
        )

        try:
            result = self.execute(step, context, tool)
            context.task.results.append(result)

            self.bus.emit(
                Event(
                    type="agent.completed",
                    data={
                        "agent": self.name,
                        "task_id": context.task.id,
                    },
                )
            )

            return result

        except Exception as error:
            # Failures are surfaced as events before being re-raised so
            # higher layers can observe the failure without Agent swallowing it.
            self.bus.emit(
                Event(
                    type="agent.failed",
                    data={
                        "agent": self.name,
                        "task_id": context.task.id,
                        "error": str(error),
                    },
                )
            )

            raise

    def execute(self, step, context, tool):
        # Agent receives the exact callable selected by the Executor.
        # It performs the operation but does not decide which tool is valid.
        result = tool(step.input)

        self.report_result(result, context, step)

        return result

    def report_result(self, result, context, step):
        # Reporting uses execution context to make the operation observable
        # to the developer/user. Result validation remains the Executor's
        # responsibility rather than being coupled to the Agent.
        print(
            f"Goal: {context.goal} "
            f"Agent {self.name} executed "
            f"action '{step.action}' "
            f"with input '{step.input}'"
        )

        print(result.describe())