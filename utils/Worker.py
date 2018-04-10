import enum from Enum


class State(enum):
    INACTIVE = 0
    ACTIVE = 1


class Worker(object):
    def __init__(self):
        self.state = State.INACTIVE

    def assign_job(self, job):
        pass

    def on_finished_job(self, code):
        pass
