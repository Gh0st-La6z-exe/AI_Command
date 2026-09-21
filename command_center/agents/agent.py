from command_center.task import TaskStatus
from command_center.events.event import Event


class Agent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

    def run(self, step, context, tool):
        
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
        result = tool(step.input)       

        self.report_result(result, context, step)

        return result

    def report_result(self, result, context, step):
        print(
            f"Goal: {context.goal} "
            f"Agent {self.name} executed "
            f"action '{step.action}' "
            f"with input '{step.input}'"
        )

        print(result.describe())