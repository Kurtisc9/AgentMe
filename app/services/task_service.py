from app.core.commander import RoutedTask, SageCommander


class TaskService:
    def __init__(self, commander: SageCommander | None = None) -> None:
        self.commander = commander or SageCommander()

    def route(self, description: str) -> RoutedTask:
        return self.commander.route_task(description)
