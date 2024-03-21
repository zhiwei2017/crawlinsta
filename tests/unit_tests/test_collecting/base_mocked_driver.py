class BaseMockedDriver:
    def __init__(self):
        self.requests = []

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        pass

    def find_elements(self, by, value):
        pass

    def find_element(self, by, value):
        pass

    def execute(self, *args, **kwargs):
        pass

    def execute_script(self, *args, **kwargs):
        pass
