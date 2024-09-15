"""
这个类中定义了杆件的各个参数
@param section 为截面类型，具体见Section类
@param material 为材料类型，具体见Material类

@param p1, p2 为杆件两端坐标
@param id 为杆件的编号，从1开始
@param type 属于哪种杆件类型
@param type_end True/False 判定是否为端部杆件
@param Np 恒载
@oaram Ns 横向摇摆力
@param Nw 横向附加风力 - 平纵联
@param Nw_2 桥门架风力
@param NT 制动力造成的附加内力
@param main_force main_force_with_Nw main_force_with_NT
@param Ncmax Ncmin Ncmax_str, Ncmin_str 计算内力
@param Nn_max Nn_min 疲劳计算内力
@param lk_max, lk_min 影响线加载长度
@param MT 制动力弯矩
@param Mw 风弯矩
@param Nk_max Nk_min 活载，其中Nk_max>=0，Nk_min<=0
@param a_max a_min 恒活比
@param bolt_dict {d:n,...} 螺栓规格从中间向两边排列, n必须为偶数
@param bolt_dist [d1,d2...] 螺栓距离中心距离
@param Aj 净截面面积
@param l 杆件长度（节点间）
@param verify_result 验算结果
"""
from math import sqrt, pi

from core.model.structure_m.material import Material
from core.model.structure_m.node import Node


class Element:
    element_dict = {}  # 存储编号到实例的映射
    _current_id = 1  # 当前编号
    current_group = []  # 组

    def __init__(self, p1, p2, section=None, type_=None):

        self.id = self.__class__._current_id
        # 若该编号已经存在，重新获取编号
        if self.id in self.__class__.element_dict:
            self.id = self.__class__.__get_next_id()

        Element.element_dict[self.id] = self
        Element._current_id += 1
        self.p1 = p1
        self.p2 = p2
        self.section = section
        self.type_ = type_
        self.type_end = False
        self.Np = 0
        self.Ns = 0
        self.Nw = 0
        self.Nw2 = 0
        self.Mw = 0
        self.NT = 0
        self.MT = 0
        self.Nk_max = 0
        self.Nk_min = 0
        self.lk_max = self.lk_min = 0
        self.mu_plus1 = 0
        self.mu_f_plus1 = 0
        self.a_positive = 0
        self.a_negative = 0
        self.eta_positive = 0
        self.eta_negative = 0
        self.combination_positive_dict = {}
        self.combination_negative_dict = {}
        self.Nc_max = self.Nc_min = 0
        self.Nc_max_str = self.Nc_min_str = ""
        self.Nn_max = self.Nn_min = 0
        self.l = 0
        self.cal_l()
        self.Iyj = 0
        self.Wyj = 0
        self.bolt_dict = {}
        self.Aj = 0
        material: Material
        self.materia = None
        self.verify_result = None

    def cal_l(self):
        self.p1: Node
        x1, y1, z1 = self.p1.get_coordinate()
        x2, y2, z2 = self.p2.get_coordinate()
        self.l = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    def cal_Aj(self):
        delta_A = 0
        t = self.get_t1()
        for d, n in self.bolt_dict.items():
            delta_A += 2 * n * t * d
        self.Aj = self.section.A - delta_A

    def cal_Iyj(self):
        # 计算去除螺栓后的截面净惯性矩
        cal_list = []
        i = 0
        for d, n in self.bolt_dict.items():
            for num in range(n // 2):
                cal_list.append([d, self.bolt_dist[i]])
                i += 1

        delta_Iy = 0
        t = self.section.get_t1()

        for list_ in cal_list:
            delta_Iy += list_[0] * t * 4 * pow(list_[1], 2)

        self.Iyj = self.section.get_Iy() - delta_Iy


    def get_Iyj(self):
        if self.Iyj == 0:
            self.cal_Iyj()

        return self.Iyj

    def get_Wyj(self):
        if self.Wyj == 0:
            Iyj = self.get_Iyj()
            self.Wyj = Iyj / self.section.get_width() * 2

        return self.Wyj

    def min_coordinate_x(self):
        return min(self.p1.x, self.p2.x)

    @classmethod
    def auto_group(cls, e_list):
        group = []
        for e in e_list:
            group.append(e)
        cls.current_group.append(group)

    @classmethod
    def __get_next_id(cls):
        """遍历获取下一个可用编号"""
        next_id = 1
        while True:
            if next_id not in cls.element_dict:
                cls._current_id = next_id
                return next_id
            next_id += 1

    @classmethod
    def reset_id(cls):
        """重置编号"""
        cls._current_id = 1
        cls.element_dict.clear()
        cls.current_group.clear()

    def delete(self):
        """删除节点"""
        if self.id in self.__class__.element_dict:
            del self.__class__.element_dict[self.id]
            self.__class__._current_id = 1
            self.id = 0  # 重置为0，表示已删除
            print("删除成功")

    def __lt__(self, other):
        p1: Node
        p2: Node
        return self.p1.x < self.p2.x

    def __del__(self):
        """当实例删除后，从字典中删除实例"""
        if self.id in self.__class__.element_dict:
            del self.__class__.element_dict[self.id]
            self.__class__._current_id = 1

    def __str__(self):
        return f"Element ID: {self.id}, Coordinate: {str(self.p1)},{str(self.p2)}, type: {self.type_}"

    def get_id(self):
        return self.id

    def whether_only_N(self):
        """判断是否为仅受轴力构件"""
        if self.MT == 0 and self.Mw == 0:
            return True
        else:
            return False

    def get_main_load_positive(self):
        return self.Np + self.eta_positive * self.mu_plus1 * self.Nk_max + self.Ns

    def get_main_load_negative(self):
        return self.Np + self.eta_negative * self.mu_plus1 * self.Nk_min + self.Ns

    def get_additional_forces(self):
        return {"风力": self.Nw + self.Nw2, "制动力": self.NT}

    def get_Nw(self):
        return self.Nw

    def get_Nw2(self):
        return self.Nw2

    def get_NT(self):
        return self.NT

    def set_type(self, type_):
        self.type_ = type_

    def set_type_end(self, type_end):
        self.type_end = type_end

    def get_type_end(self):
        return self.type_end

    def set_section(self, section):
        self.section = section

    def set_Np(self, Np):
        self.Np = Np

    def set_Nk_lk_with_list(self, Nks):
        self.Nk_max = max(0, Nks[0])
        self.Nk_min = min(0, Nks[1])
        if len(Nks) == 4:
            self.lk_max = Nks[2]
            self.lk_min = Nks[3]

    def self_set_a(self):
        if self.Nk_max != 0:
            self.a_positive = self.Np / (self.mu_plus1 * self.Nk_max)

        if self.Nk_min != 0:
            self.a_negative = self.Np / (self.mu_plus1 * self.Nk_min)

    def self_set_Nn(self):
        # 获得运营动力系数后可进行计算疲劳计算内力
        if self.Nk_max != 0:
            self.Nn_max = self.Np + self.mu_f_plus1 * self.Nk_max
        else:
            self.Nn_max = self.Np

        if self.Nk_min != 0:
            self.Nn_min = self.Np + self.mu_f_plus1 * self.Nk_min
        else:
            self.Nn_min = self.Np

    def set_mu_plus1(self, mu_plus1):
        self.mu_plus1 = mu_plus1

    def set_mu_f_plus1(self, mu_f_plus1):
        self.mu_f_plus1 = mu_f_plus1

    def set_eta_positive(self, eta):
        self.eta_positive = eta

    def set_eta_negative(self, eta):
        self.eta_negative = eta

    def set_Ns(self, Ns):
        self.Ns = Ns

    def set_Nw(self, Nw):
        self.Nw = Nw

    def set_Nw2(self, Nw2):
        self.Nw2 = Nw2

    def set_NT(self, NT):
        self.NT = NT

    def set_MT(self, MT):
        self.MT = MT

    def set_Mw(self, Mw):
        self.Mw = Mw

    def set_Nc_max(self, list):
        [self.Nc_max_str, self.Nc_max] = list

    def set_Nc_min(self, list):
        [self.Nc_min_str, self.Nc_min] = list

    def set_combination_positive(self, combination_positive_dict):
        self.combination_positive_dict = combination_positive_dict

    def set_combination_nagative(self, combination_negative_dict):
        self.combination_negative_dict = combination_negative_dict

    def set_bolt_dict(self, bolt_dict):
        self.bolt_dict = bolt_dict

    def set_bolt_dist(self, bolt_dist):
        self.bolt_dist = bolt_dist

    def set_verify_result(self, result):
        self.verify_result = result

    @classmethod
    def get_max_a(cls):
        """
        这个方法是对所有的element进行查询，而非根据当前组进行单独查询
        """
        a_max = 0
        for e in cls.element_dict.values():
            if e.a_positive != 0 and e.a_positive > a_max:
                a_max = e.a_positive
        return a_max

    def get_p1(self):
        return self.p1

    def get_p2(self):
        return self.p2

    def get_l(self):
        return self.l

    def get_type(self):
        return self.type_

    def get_force(self):
        return self.Np

    def get_a_positive(self):
        return self.a_positive

    def get_lks(self):
        return [self.lk_max, self.lk_min]

    def get_Nks(self):
        return [self.Nk_max, self.Nk_min]

    def get_Nns(self):
        return [self.Nn_max, self.Nn_min]

    def get_Ncs(self):
        return [self.Nc_max, self.Nc_min]

    def get_MT(self):
        return self.MT

    def get_Mw(self):
        return self.Mw

    """材料相关"""

    def set_material(self, material):
        self.materia = material

    def get_sigma_axial(self):
        return self.materia.get_sigma_axial()

    def get_sigma_bending(self):
        return self.materia.get_sigma_bending()

    def get_sigma_shearing(self):
        return self.materia.get_sigma_shearing()

    def get_material_name(self):
        return self.materia.get_name()

    def get_E(self):
        return self.materia.get_E()

    """截面相关"""

    def get_section(self):
        return self.section

    def get_Am(self):
        return self.section.A

    def get_Aj(self):
        return self.Aj

    def get_Ix(self):
        Ix = self.section.get_Ix()
        return Ix

    def get_Iy(self):
        Iy = self.section.get_Iy()
        return Iy

    def get_Wx(self):
        Wx = self.section.get_Wx()
        return Wx

    def get_t1(self):
        t1 = self.section.get_t1()
        return t1

    def get_t2(self):
        t2 = self.section.get_t2()
        return t2

    def get_width(self):
        width = self.section.get_width()
        return width

    def get_height(self):
        height = self.section.get_height()
        return height

    def get_tw(self):
        tw = self.section.get_tw()
        return tw

    def get_hw(self):
        hw = self.section.get_hw()
        return hw

    def get_section_type(self):
        return self.section.get_type()

    def get_verify_result(self):
        return self.verify_result
