class Config(object):
    def __init__(self):
        self.n_items = 100
        self.n_contrainers = 3
        self.n_drones = 7
        self.n_meds = 3
        self.n_types = self.n_drones + self.n_meds

        # container
        # self.L = 231
        # self.W = 92
        # self.H = 94
        # self.L = 132
        # self.W = 129
        # self.H = 149
        # self.L = 111
        # self.W = 51
        # self.H = 121
        self.L = 233
        self.W = 233
        self.H = 233
        self.V = self.L * self.W * self.H
        self.door_width  = 92
        self.door_height = 89

        self.length = {'DRONE A': 45, 'DRONE B': 30, 'DRONE C': 60, 'DRONE D': 25, 'DRONE E': 25,
                       'DRONE F': 40, 'DRONE G': 32, 'DRONE H': 65, 'MED 1': 14, 'MED 2': 5, 'MED 3': 12,
                       'BAY 1': 8, 'BAY 2': 24}
        self.width = {'DRONE A': 45, 'DRONE B': 30, 'DRONE C': 50, 'DRONE D': 20, 'DRONE E': 20,
                      'DRONE F': 40, 'DRONE G': 32, 'DRONE H': 75, 'MED 1': 7, 'MED 2': 8, 'MED 3': 7,
                      'BAY 1': 10, 'BAY 2': 20}
        self.height = {'DRONE A': 25, 'DRONE B': 22, 'DRONE C': 30, 'DRONE D': 25, 'DRONE E': 27,
                       'DRONE F': 25, 'DRONE G': 17, 'DRONE H': 41, 'MED 1': 5, 'MED 2': 5, 'MED 3': 4,
                       'BAY 1': 14, 'BAY 2': 20}
        self.weight = {'DRONE A': 3.5, 'DRONE B': 8, 'DRONE C': 14, 'DRONE D': 11, 'DRONE E': 15,
                       'DRONE F': 22, 'DRONE G': 20, 'DRONE H': 0, 'MED 1': 2, 'MED 2': 2, 'MED 3': 3,
                       'BAY 1': 8, 'BAY 2': 20}
        self.drones = ['DRONE A', 'DRONE B', 'DRONE C', 'DRONE D', 'DRONE E', 'DRONE F', 'DRONE G', 'DRONE H']
        self.meds = ['MED 1', 'MED 2', 'MED 3']
        self.bays = ['BAY 1', 'BAY 2']

config = Config()
