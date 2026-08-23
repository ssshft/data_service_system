from queue import Queue, Empty


class DataQueue:
    def __init__(self):
        self.view_data = None
        self.detail_data = None

    def add_view_data(self, data):
        self.view_data = data

    def get_view_data(self):
        return self.view_data
    
    def add_detail_data(self, data):
        self.detail_data = data

    def get_detail_data(self):
        return self.detail_data


data_queue = DataQueue()
