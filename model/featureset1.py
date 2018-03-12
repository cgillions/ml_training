class Featureset1:

    id = None
    meanXYZ = None
    stdXYZ = None

    def __init__(self, idx, mean_x_y_z, std_x_y_z):
        self.id = idx
        self.meanXYZ = mean_x_y_z
        self.stdXYZ = std_x_y_z
