from core.model.structure_m.section import Section
from math import pow

"""
这个类中定义了H形截面的各个参数，并对其属性进行运算
@param height 是截面的高度（默认翼缘板高度相同）
@param width 是截面的宽度
@param tw 截面腹板的宽度
@param t1 截面左侧翼缘板的宽度
@param t2 截面右侧翼缘板的宽度
方便起见，设定的是 t1=t2
@param type_ 截面类型，即 "H"
"""


class Section_H(Section):
    h_sections = []

    def __init__(self, height, width, tw, t1, t2):
        Section_H.h_sections.append(self)
        super().__init__(height, width)
        (self.height, self.width) = (height, width)
        (self.t1, self.t2, self.tw) = (t1, t2, tw)
        self.type_ = "H"
        self.hw = width - t1 - t2
        self.Ix = self.Iy = 0
        self.Wx = self.Wy = 0
        self.A = 0
        self.calculate_Ix(), self.calculate_Iy()
        self.calculate_A()

    def calculate_A(self):
        super().calculate_A()
        self.A = self.tw * self.hw + self.t1 * self.height + self.t2 * self.height

    '''计算截面x轴惯性矩'''

    def calculate_Iy(self):
        super().calculate_Iy()
        i1 = pow(self.tw, 3) * self.hw / 12
        i2 = pow(self.height, 3) * self.t1 / 12
        i3 = pow(self.height, 3) * self.t2 / 12
        self.Iy = i1 + i2 + i3
        self.Wy = self.Iy / self.height * 2

    def calculate_Ix(self):
        super().calculate_Ix()
        i1 = self.tw * pow(self.hw, 3) / 12
        i2 = self.height * pow(self.t1, 3) / 12 + self.height * self.t1 * pow((self.t1 + self.hw) / 2, 2)
        self.Ix = i1 + i2 * 2
        self.Wx = self.Ix / self.width * 2

    def get_Ix(self):
        return self.Ix

    def get_Iy(self):
        return self.Iy

    def get_Wx(self):
        return self.Wx

    def get_Wy(self):
        return self.Wy

    def get_type(self):
        return self.type_

    def get_hw(self):
        return self.hw

    def get_tw(self):
        return self.tw

    def get_t1(self):
        return self.t1

    def get_t2(self):
        return self.t2

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width
