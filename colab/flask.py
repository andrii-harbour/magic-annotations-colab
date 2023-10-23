import logging


class DummyFlaskApp:
    def __init__(self):
        self.logger = logging.getLogger()


current_app = DummyFlaskApp()