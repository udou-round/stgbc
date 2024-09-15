"""
这个类中定义了材料
@param name: 材料名称
@param sigma_List: [axial_stress, bending_stress, shearing_stress]
@E
"""


class Material():
    def __init__(self, name, sigma_list=None, E=None, sepecification=None):
        self.name = name
        self.sigma_list = sigma_list
        self.E = E
        self.sepecification = sepecification

    def get_sigma_axial(self):
        return self.sigma_list[0]

    def get_sigma_bending(self):
        return self.sigma_list[1]

    def get_sigma_shearing(self):
        return self.sigma_list[2]

    def get_name(self):
        return self.name

    def get_E(self):
        return self.E

    def set_E(self, E):
        self.E = E
