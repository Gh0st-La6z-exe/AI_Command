class Context:
    def __init__(self, task, goal, repository_path):
        # Context carries the information needed across the planning and
        # execution pipeline without forcing each component to pass every
        # piece of information independently.
        self.task = task
        self.goal = goal
        self.repository_path = repository_path