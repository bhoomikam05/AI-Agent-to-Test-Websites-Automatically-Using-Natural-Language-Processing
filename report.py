class TestReport:
    def __init__(self):
        self.steps = []
        self.status = "PASS"
        self.screenshot = None
        self.execution_time = 0

    def add_step(self, step, status):
        self.steps.append({
            "step": step,
            "status": status
        })

    def set_status(self, status):
        self.status = status

    def set_screenshot(self, path):
        self.screenshot = path

    def set_execution_time(self, t):
        self.execution_time = t

    def generate(self):
        return {
            "status": self.status,
            "steps": self.steps,
            "total_steps": len(self.steps),
            "execution_time": self.execution_time,
            "screenshot": self.screenshot
        }