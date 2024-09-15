import itertools

from core.model.specification_m.codesteelr import CodeSteelR as CodeSR
from core.model.specification_m.forcetruss import ForceTrussCalculator, VerifyTrussCalculator
from core.model.specification_m.codesteelrdesign import CodeSteelRDesign as CodeSRD
from core.model.specification_m.verifyerror import VerifyError
from core.model.specification_m.verifyresult import VerifyResult
from core.model.structure_m.element import Element
from core.model.structure_m.material import Material
from core.model.structure_m.node import Node
from core.model.structure_m.section_H import Section_H

"""
这个类为计算控制器，传入数据后将数据传递向模型
@param L:计算跨度
@param n：节间数量
@param d：节间长度
@param H：主桁高度
@param B：主桁中心距
@param b：纵梁中心距
@param B0：纵联计算宽度
@param n_piece：主桁片数
@param result_dict: 杆件验算结果{ID:[error1,error2...]}
"""


class CalService:
    def __init__(self, L, n, H, B, b, B0, n_piece=2, load="ZKH"):
        self.n_piece = n_piece
        self.L, self.n, self.H, self.B, self.b, self.B0, self.load = L, n, H, B, b, B0, load
        self.d = L / n

        # 引入规范类，从规范中提取所需规范值
        self.code_srd = CodeSRD()
        self.code_sr = CodeSR()
        [self.pk, self.qk] = self.code_srd.get_load(self.load)
        self.distance = self.code_srd.get_load_distance()
        # 引入计算类，用于计算受力
        self.ft = ForceTrussCalculator(L, n, H, B, b, B0)
        # 引入验证类，用于验证截面
        self.ftv = VerifyTrussCalculator()
        # 杆件验算结果
        self.result_dict = {}

    def auto_create(self):
        """
        自动生成节点与杆件，仅适用于单线，且仅适用于程序无创建节点情况下
        """

        # 生成主桁杆件节点
        x1 = [i * (self.L / self.n) for i in range(self.n + 1)]  # x1中存的是所有下弦杆端点x坐标，x2则为所有上弦杆端点x坐标

        # print(x1)

        y1 = [0, self.B]  # y1存的是弦杆y坐标，而y2为纵联y坐标
        y2 = [(self.B - self.b) / 2, self.B - self.b / 2]
        z = [0, self.H]

        # 高度为0的点的创建
        all_coordinates = list(itertools.product(x1, y1, [z[0]]))
        sorted_coordinates = sorted(all_coordinates)
        self.from_list_create_nodes(sorted_coordinates)

        #  高度为H的点的创建
        x1.pop(0)
        x1.pop()
        all_coordinates = list(itertools.product(x1, y1, [z[1]]))
        sorted_coordinates = sorted(all_coordinates)
        self.from_list_create_nodes(sorted_coordinates)

        # 杆件创建
        self.__auto_set_elements()

    def __auto_set_elements(self):
        try:
            n_max = 6 + 4 * (self.n / 2 - 1)
            self.__auto_set_single_element(1, n_max, 4, 4, "下弦杆")
            self.__auto_set_single_element(2, n_max, 4, 4, "下弦杆")
            self.__auto_set_single_element(3, n_max, 4, 20, "竖杆")
            self.__auto_set_single_element(4, n_max, 4, 20, "竖杆")

            self.__auto_set_single_element(1, n_max, 4, 22, "斜杆")
            self.__auto_set_single_element(2, n_max, 4, 22, "斜杆")

            n_max = 6 + 4 * (self.n / 2 - 1) + 2
            self.__auto_set_single_element(5, n_max, 4, 18, "斜杆")
            self.__auto_set_single_element(6, n_max, 4, 18, "斜杆")

            n_max = 2 * (6 + 4 * (self.n / 2 - 1)) - 4
            self.__auto_set_single_element(23, n_max, 4, 4, "上弦杆")
            self.__auto_set_single_element(24, n_max, 4, 4, "上弦杆")
        except:
            print("创建节点失败，节点详情如下")
            for k, v in Node.node_dict.items():
                print(f"{k}={v}")
            print("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
            raise Exception

    def __auto_set_single_element(self, n_start, n_max, n_add, n_dist, type_=None):
        """
        自动生成时，节点将进行排序，则可根据特定规律生成杆件，并进行分组
        该函数将在传入区间、间隔、类型后自动实例化杆件
        n_add：1、3节点相隔的距离
        n_dist：1、2节点相隔的距离
        """
        dict_ = Node.node_dict
        i = n_start
        group = []
        while i < n_max - 1:
            e = Element(dict_[i], dict_[i + n_dist], type_=type_)
            group.append(e)
            i += n_add

        Element.auto_group(group)

    def auto_calculate_Np(self, p):
        """
        自动生成节点后，可自动计算各个杆件的力
        """
        groups = Element.current_group
        # 调用桁架力计算

        # 下弦杆
        group = Element.current_group[0]
        result_lower_chrod = self.ft.chrod(group, "下弦杆", p)
        self.__set_Np(group, result_lower_chrod)
        group = Element.current_group[1]
        self.__set_Np(group, result_lower_chrod)

        # 上弦杆
        group = Element.current_group[8]
        result_upper_chrod = self.ft.chrod(group, "上弦杆", p)
        self.__set_Np(group, result_upper_chrod)
        group = Element.current_group[9]
        self.__set_Np(group, result_upper_chrod)

        # 斜杆
        group1 = groups[4]
        group2 = groups[6]
        group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
        group[-1].set_type_end(True)  # 后续需要根据是否为端部杆件而进行取值，现在先进行设定
        group[0].set_type_end(True)
        result_diagonal = self.ft.diagonal(group, p)
        self.__set_Np(group, result_diagonal)

        group1 = groups[5]
        group2 = groups[7]
        group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
        group[-1].set_type_end(True)
        group[0].set_type_end(True)
        self.__set_Np(group, result_diagonal)

        # 竖杆
        group = Element.current_group[2]
        result_vertical = self.ft.vertical(group, p)
        self.__set_Np(group, result_vertical)
        group = Element.current_group[3]
        self.__set_Np(group, result_vertical)

    def auto_calculate_Nk(self):
        """
        自动生成节点后，可自动计算各个杆件的力
        """
        groups = Element.current_group
        # 调用桁架力计算
        pk = self.pk / self.n_piece
        qk = self.qk / self.n_piece

        # 下弦杆
        group = Element.current_group[0]
        result_lower_chrod = self.ft.chrod_Nk(group, pk, qk, self.distance, "下弦杆")
        self.__set_Nk(group, result_lower_chrod)
        group = Element.current_group[1]
        self.__set_Nk(group, result_lower_chrod)

        # 上弦杆
        group = Element.current_group[8]
        result_upper_chrod = self.ft.chrod_Nk(group, pk, qk, self.distance, "上弦杆")
        self.__set_Nk(group, result_upper_chrod)
        group = Element.current_group[9]
        self.__set_Nk(group, result_upper_chrod)

        # 斜杆
        group1 = groups[4]
        group2 = groups[6]
        group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
        result_diaganol = self.ft.diagonal_Nk(group, pk, qk, self.distance)
        self.__set_Nk(group, result_diaganol)

        group1 = groups[5]
        group2 = groups[7]
        group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
        self.__set_Nk(group, result_diaganol)

        # 竖杆
        group = Element.current_group[2]
        result_vertical = self.ft.vertical_Nk(group, pk, qk, self.distance)
        self.__set_Nk(group, result_vertical)
        group = Element.current_group[3]
        self.__set_Nk(group, result_vertical)

    def __set_Np(self, group, result):
        # 通过传入Element列表与结果数组，设置Element的静力
        i = 0
        for e in group:
            e: Element
            e.set_Np(result[i])
            i += 1

    def __set_Nk(self, group, result):
        # 通过传入Element列表与结果数组，设置Element的动力
        i = 0
        for e in group:
            e: Element
            e.set_Nk_lk_with_list(result[i])
            i += 1

    def from_list_create_nodes(self, list_):
        for a, b, c in list_:
            # print(a, b, c)
            Node(a, b, c)

    def cal_force(self, p1, p2, p3, p4, p5, p6, p7):
        # 每片主桁受力
        p = (p1 + p2 + p3 + p4 + p5 + p6 + p7) / self.n_piece
        return p

    def cal_force_in_code(self):
        # 计算(1+\mu)\eta Nk
        mu_plus1_a = self.code_sr.get_mu_plus1(self.L, self.load)
        mu_plus1_b = self.code_sr.get_mu_plus1(2 * self.d, self.load)
        elements = Element.element_dict.values()
        e: Element
        for e in elements:
            if e.type_ != "竖杆":
                e.set_mu_plus1(mu_plus1_a)
            else:
                e.set_mu_plus1(mu_plus1_b)
            e.self_set_a()

        # 得到a_max，借此计算eta
        a_max = Element.get_max_a()
        for e in elements:
            if e.a_positive != 0:
                eta = self.code_srd.get_eta(a_max, e.a_positive)
                e.set_eta_positive(eta)

            if e.a_negative != 0:
                eta = self.code_srd.get_eta(a_max, e.a_negative)
                e.set_eta_negative(eta)

    def auto_calculate_sway(self):
        """
        计算横向摇摆力
        """
        sway_force = self.code_sr.get_lateral_sway_force(self.load)
        [c2, c1] = self.code_srd.get_partition_coefficient(case_=2)

        # 下弦杆
        group = Element.current_group[0]
        result_lower_chrod = self.ft.lateral_sway_force(group, sway_force, c1, c2, "下弦杆")
        self.__set_Ns(group, result_lower_chrod)
        group = Element.current_group[1]
        self.__set_Ns(group, result_lower_chrod)

        # 上弦杆
        group = Element.current_group[8]
        result_upper_chrod = self.ft.lateral_sway_force(group, sway_force, c1, c2, "上弦杆")
        self.__set_Ns(group, result_upper_chrod)
        group = Element.current_group[9]
        self.__set_Ns(group, result_upper_chrod)

    def auto_calculate_wind(self, K1, K2, K3, W0, h_cross, c):
        """
        计算风力，注意该函数中涉及计算内容，实际上不应该出现，后续应当修改！！！
        """
        # 平纵联效应
        W = self.code_sr.get_wind_pressure(K1, K2, K3, W0)
        W2 = 0.8 * W  # 有车时
        w_up = (0.5 * 0.4 * self.H + 0.2 * (h_cross + 3) * (1 - 0.4)) * W2
        w_down = (0.5 * 0.4 * self.H + (h_cross + 3) * (1 - 0.4)) * W2
        # print(w_down)
        # print(w_up)

        # 下弦杆
        group = Element.current_group[0]
        result_lower_chrod = self.ft.wind_force(group, w_down, "下弦杆")
        self.__set_Nw(group, result_lower_chrod)
        group = Element.current_group[1]
        self.__set_Nw(group, result_lower_chrod)

        # 上弦杆
        group = Element.current_group[8]
        result_upper_chrod = self.ft.wind_force(group, w_up, "上弦杆")
        self.__set_Nw(group, result_upper_chrod)
        group = Element.current_group[9]
        self.__set_Nw(group, result_upper_chrod)

        # 桥门架效应
        [V, Nw2, Me, Mk] = self.ft.portal_frame_effect(w_up, c, h_cross)
        group = Element.current_group[4]
        group[0].set_Nw2(V)
        group[0].set_Mw(Me)
        group = Element.current_group[5]
        group[0].set_Nw2(V)
        group[0].set_Mw(Me)
        group = Element.current_group[6]
        group[-1].set_Nw2(V)
        group[-1].set_Mw(Me)
        group = Element.current_group[7]
        group[-1].set_Nw2(V)
        group[-1].set_Mw(Me)

        group = Element.current_group[8]
        group[0].set_Nw2(Nw2)
        group[-1].set_Nw2(Nw2)
        group = Element.current_group[9]
        group[0].set_Nw2(Nw2)
        group[-1].set_Nw2(Nw2)

    def braking_additional_force(self, h):
        # 求静活载
        static_live_load = self.ft.vertical_static_live_load(self.pk, self.qk, self.distance)
        T = self.code_sr.get_braking_force(2, static_live_load, 2)  # 制动力
        NT = self.ft.NT(T)  # 受制动力作用下的附加内力
        [M1, M2] = self.ft.MT(NT, h)
        group = Element.current_group[0]
        self.__set_NT(group, NT)
        group[0].set_MT(M1)
        group[-1].set_MT(M1)
        group = Element.current_group[1]
        group[-1].set_MT(M1)
        group[0].set_MT(M1)
        self.__set_NT(group, NT)

        group = Element.current_group[4]
        group[0].set_MT(M2)
        group = Element.current_group[6]
        group[-1].set_MT(M2)
        group = Element.current_group[5]
        group[0].set_MT(M2)
        group = Element.current_group[7]
        group[-1].set_MT(M2)

    def combination(self):
        groups = Element.current_group
        # 获取主力与对应系数
        coefficient_main = self.code_srd.get_increasing_factor_allowable_stress(1)
        coefficient = self.code_srd.get_increasing_factor_allowable_stress(2)

        for groups in groups:
            element: Element
            for element in groups:
                # 判断弯矩为0
                name_with_force = []
                # 获取力与对应系数集合，准备传入函数 -> 计算内力
                additional_forces = element.get_additional_forces()
                for f_name, f in additional_forces.items():
                    name_with_force.append((f_name, f))

                if element.Nk_max > 0:
                    main_posi = element.get_main_load_positive()
                    positive_dict, Nc_max_str, Nc_max = self.ft.calculation_combination(main_posi, coefficient_main,
                                                                                        name_with_force,
                                                                                        coefficient)
                    element.set_combination_positive(positive_dict)
                    # if element.MT == 0 and element.Mw == 0:
                    # Nc为仅有轴力杆件的计算内力
                    element.set_Nc_max([Nc_max_str, Nc_max])

                if element.Nk_min < 0:
                    main_nega = element.get_main_load_negative()
                    negative_dict, Nc_min_str, Nc_min = self.ft.calculation_combination(main_nega, coefficient_main,
                                                                                        name_with_force,
                                                                                        coefficient)
                    element.set_combination_nagative(negative_dict)
                    # if element.MT == 0 and element.Mw == 0:
                    element.set_Nc_min([Nc_min_str, Nc_min])

    def fatigue_internal_force(self):
        # 获得运营动力系数
        mu_f_plus1_a = self.code_srd.get_mu_f_plus1(self.L)
        mu_f_plus1_b = self.code_srd.get_mu_f_plus1(2 * self.d)  # 竖杆
        elements = Element.element_dict.values()
        e: Element
        for e in elements:
            if e.type_ != "竖杆":
                e.set_mu_f_plus1(mu_f_plus1_a)
            else:
                e.set_mu_f_plus1(mu_f_plus1_b)
            # 计算疲劳计算内力
            e.self_set_Nn()

    def __set_Ns(self, group, result):
        # 通过传入Element列表与结果数组，设置Element的动力
        i = 0
        for e in group:
            e: Element
            e.set_Ns(result[i])
            i += 1

    def __set_Nw(self, group, result):
        # 通过传入Element列表与结果数组，设置Element的动力
        i = 0
        for e in group:
            e: Element
            e.set_Nw(result[i])
            i += 1

    def __set_NT(self, group, result_single):
        # 通过传入Element列表与结果数组，设置Element的动力
        i = 0
        for e in group:
            e: Element
            e.set_NT(result_single)
            i += 1

    @staticmethod
    def get_nodes():
        return Node.node_dict

    @staticmethod
    def get_elements():
        return Element.element_dict

    @staticmethod
    def get_groups():
        return Element.current_group

    """以下为检算部分"""

    def set_section(self, element, height, width, tw, t1, t2, bolt_dict=None, bolt_dist=None):
        if bolt_dict is None:
            bolt_dict = {}

        if bolt_dist is None:
            bolt_dist = []

        section = Section_H(height, width, tw, t1, t2)
        element.set_section(section)
        element.set_bolt_dict(bolt_dict)
        element.set_bolt_dist(bolt_dist)
        element.cal_Aj()  # 计算净截面面积

    def set_material(self, element, material):
        element.set_material(material)

    def verify_pass_element(self):
        groups = Element.current_group

        for group in groups:
            element: Element
            for element in group:
                if 1 == 1:
                    # 仅有轴力作用的杆件
                    self.verify_cal(element)

    # 验算仅有轴力作用的杆件
    def verify_cal(self, element):
        [lk_max, lk_min] = element.get_lks()  # 加载长度
        [Nc_max, Nc_min] = element.get_Ncs()  # 计算内力
        [Nn_max, Nn_min] = element.get_Nns()  # 疲劳计算内力

        lx = self.get_l_in_code(element, "x")
        ly = self.get_l_in_code(element, "y")
        material = element.get_material_name()
        Am = element.get_Am()
        Ix = element.get_Ix()
        Iy = element.get_Iy()
        Aj = element.get_Aj()
        Wx = element.get_Wx()
        t1 = element.get_section().get_t1()
        width = element.get_section().get_width()
        section_type = element.get_section_type()
        sigma_allowed = element.get_sigma_axial()  # 容许轴向应力
        MT = element.get_MT()
        Mw = element.get_Mw()
        E = element.get_E()  # 弹性模量

        only_N = element.whether_only_N()

        # 储存验算结果
        result = VerifyResult()

        # 抗拉强度检算
        if Nc_max > 0:
            self.verify_tensile_strength(result, Aj, Nc_max, sigma_allowed)

        if not only_N:
            Wyj = element.get_Wyj()
            self.verify_bending_tensile_strength(result, Aj, MT, Mw, Nc_max, Wyj, sigma_allowed)

        # 刚度检算
        lambda_x, lambda_y, rx, ry = self.verify_rigidity(result, Am, Ix, Iy, element, lx, ly)

        lambda_max = max(lambda_x, lambda_y)

        # 构造检算
        self.verify_detail(result, element)

        if Nc_min != 0:
            if only_N:
                # 总体稳定检算
                self.verify_stability(result, Am, Nc_min, lambda_max, material, sigma_allowed)
            else:
                (self.verify_stability_M
                 (result, element, width, Am, Wx, Nc_min, MT, Mw, lambda_max, lambda_x, lambda_y, rx, ry, lx, ly,
                  material,
                  sigma_allowed,
                  E))

            # 局部稳定检算
            self.verify_local_bucking(result, element, lambda_max, material)

        if Nc_max != 0:  # 存在拉力时需要检算疲劳
            self.verify_fatigue(result, Aj, Nn_max, Nn_min, element, lk_max, lk_min, t1)

        element.set_verify_result(result)

    def verify_tensile_strength(self, result, Aj, Nc_max, sigma_allowed):
        result_tensile_strength, sigma_cj = self.ftv.tensile_strength_N(sigma_allowed, Nc_max, Aj)
        result.add_result("tensile_strength", {"sigma": sigma_cj, "sigma_allowed": sigma_allowed})
        if not result_tensile_strength:
            result.add_error("StructuralError", "A001", "tensile_strength")

    def verify_bending_tensile_strength(self, result, Aj, MT, Mw, Nc_max, Wyj, sigma_allowed):
        if MT != 0:
            increasing_factor = self.code_srd.get_increasing_factor_allowable_stress(2)  # 主力 + 附加力

            result_MT_tensile_strength, sigma_II, sigma_cj, sigma_allowed_MT = (
                self.ftv.tensile_strength_M(sigma_allowed, Nc_max, Aj, MT, Wyj, increasing_factor))

            result.add_result("bending_tensile_MT", {"sigma": sigma_II, "sigma_allowed": sigma_allowed_MT})
            if not result_MT_tensile_strength:
                result.add_error("StructuralError", "A001", "bending_tensile_MT")

        if Mw != 0:
            increasing_factor = self.code_srd.get_increasing_factor_allowable_stress(2)  # 主力 + 附加力

            result_Mw_tensile_strength, sigma_II, sigma_cj, sigma_allowed_Mw = (
                self.ftv.tensile_strength_M(sigma_allowed, Nc_max, Aj, MT, Wyj, increasing_factor))
            result.add_result("bending_tensile_Mw", {"sigma": sigma_II, "sigma_allowed": sigma_allowed_Mw})
            if not result_Mw_tensile_strength:
                result.add_error("StructuralError", "A001", "bending_tensile_Mw")

    def verify_rigidity(self, result, Am, Ix, Iy, element, lx, ly):
        lambda_allowed = self.get_lambda_allowed(element)
        result_rigidity, rx, ry, lambda_x, lambda_y = (
            self.ftv.rigidity_verify(lambda_allowed, Am, lx, ly, Ix, Iy))

        result.add_result("rigidity",
                          {"rx": rx, "ry": ry, "lambda_x": lambda_x, "lambda_y": lambda_y, "lx": lx, "ly": ly})
        if not result_rigidity:
            result.add_error("StructuralError", "B001", "rigidity")
        return lambda_x, lambda_y, rx, ry

    def verify_detail(self, result, element):
        tw = element.get_tw()
        t = element.get_t1()
        detail_required = self.code_srd.get_H_detail_require(2, t)

        result_detail, detail_cal = self.ftv.detail_H(t, tw, detail_required)

        result.add_result("detail", {"detail_cal": detail_cal, "detail_required": detail_required})
        if not result_detail:
            result.add_error("DesignError", "A001", "detail")

    def verify_stability(self, result, Am, Nc_min, lambda_max, material, sigma_allowed):
        phi1 = self.code_srd.get_varphi1_H_flange(lambda_max, material)

        result_stability, sigma_cm, sigma_cm_allowed = (
            self.ftv.overall_statbility_N(Nc_min, Am, phi1, sigma_allowed))
        result.add_result("stability", {"sigma_cm": sigma_cm, "phi1": phi1, "sigma_allowed": sigma_cm_allowed})
        if not result_stability:
            result.add_error("StructuralError", "B002", "stability")

        return phi1

    def verify_stability_M(self, result, element, width, Am, Wm, Nc_min, MT, Mw, lambda_max, lambda_x, lambda_y, rx, ry,
                           lx, ly,
                           material, sigma_allowed, E,
                           ):

        # 主力作用 - 总体稳定验算
        main_force = element.get_main_load_negative()
        phi1 = self.verify_stability(result, Am, main_force, lambda_max, material, sigma_allowed)

        # 横向风力 - 失稳平面与弯矩作用平面不一致
        if Mw != 0:
            Nw = element.get_Nw()
            Nw2 = element.get_Nw2()
            force = main_force + Nw + Nw2
            """Attention: Nw Nw2 与 force可能不同号，此处不考虑"""

            lambda_e = self.code_srd.stability_get_lambda_e(lx, rx, ry, width)
            phi2 = self.code_srd.get_varphi1_H_flange(lambda_e, material)
            increasing_factor = self.code_srd.get_increasing_factor_allowable_stress(2)  # 主力 + 附加力
            mu1 = self.code_srd.stability_get_mu_1(E, force, Am, phi1, lambda_x, sigma_allowed, 2)
            result_stability, sigma_cm, sigma_cm_allowed = (
                self.ftv.overall_statbility_M(force, Am, Mw, Wm, mu1, phi1, phi2, increasing_factor, sigma_allowed))
            result.add_result("stability_Mw", {"sigma_cm": sigma_cm, "phi1": phi1, "sigma_allowed": sigma_cm_allowed})

            if not result_stability:
                result.add_error("StructuralError", "B002", "stability_Mw")

        # 制动力 - 失稳平面与弯矩作用平面一致
        if MT != 0:
            NT = element.get_NT()
            force = main_force + NT
            """Attention: NT 与 force可能不同号，此处不考虑"""

            phi2 = 1.0
            increasing_factor = self.code_srd.get_increasing_factor_allowable_stress(2)  # 主力 + 附加力
            mu1 = self.code_srd.stability_get_mu_1(E, force, Am, phi1, lambda_y, sigma_allowed, 2)
            result_stability, sigma_cm, sigma_cm_allowed = (
                self.ftv.overall_statbility_M(force, Am, Mw, Wm, mu1, phi1, phi2, increasing_factor, sigma_allowed))
            result.add_result("stability_MT", {"sigma_cm": sigma_cm, "phi1": phi1, "sigma_allowed": sigma_cm_allowed})

            if not result_stability:
                result.add_error("StructuralError", "B002", "stability_MT")

    def verify_local_bucking(self, result, element, lambda_max, material):
        """验算局部稳定"""
        b1 = element.section.get_hw()
        delta1 = element.section.get_tw()
        b2 = (element.section.get_height() - delta1) / 2
        delta2 = element.section.get_t2()
        bd_allowed_web = self.code_srd.get_max_width_thickness_ratios(1, material, lambda_max)  # 腹板
        bd_allowed_flange = self.code_srd.get_max_width_thickness_ratios(3, material, lambda_max)  # 翼缘板
        result_ratio_web, ratio_web = self.ftv.width_thickness_ratios(b1, delta1, bd_allowed_web)
        result_ratio_flange, ratio_flange = self.ftv.width_thickness_ratios(b2, delta2, bd_allowed_flange)

        result.add_result("local_bucking",
                          {"ratio_web": ratio_web, "allowed_web": bd_allowed_web, "ratio_flange": ratio_flange,
                           "allowed_flange": bd_allowed_flange})

        if not result_ratio_web or not result_ratio_flange:
            result.add_error("StructuralError", "B003", "local_bucking")

    def verify_fatigue(self, result, Aj, Nn_max, Nn_min, element, lk_max, lk_min, t1):
        sigma_max, sigma_min = self.ftv.fatige_get_sigma(Nn_max, Nn_min, Aj)
        rho = sigma_min / sigma_max
        # 以拉为主的 拉压杆件 疲劳强度检算
        if rho >= -1:
            self.verify_fatigue_tensile(lk_max, lk_min, result, sigma_max, sigma_min, t1)
        # 以压为主的 拉压杆件 疲劳强度检算
        elif rho < -1:
            self.verify_fatigue_compressive(Aj, Nn_max, Nn_min, element, lk_max, lk_min, result, rho, t1)

    def verify_fatigue_tensile(self, lk_max, lk_min, result, sigma_max, sigma_min, t1):
        gamma_d = self.code_srd.get_gamma_d(1)
        gamma_n = self.code_srd.get_gamma_n(lk_max + lk_min)
        gamma_t = self.code_srd.gamma_t(t1)
        sigma_allowed_f = self.code_srd.get_fatigue_sigma_allowed(2)
        result_fatigue, sigma_verify, sigma_allow = (
            self.ftv.fatigue_verify_tensile(gamma_d, gamma_n, gamma_t, sigma_allowed_f, sigma_max, sigma_min))

        result.add_result("fatigue_tensile", {"sigma_verify": sigma_verify, "sigma_allowed": sigma_allow})
        if not result_fatigue:
            result.add_error("StructuralError", "A002", "fatigue_tensile")

    def verify_fatigue_compressive(self, Aj, Nn_max, Nn_min, element, lk_max, lk_min, result, rho, t1):
        a = element.get_a_positive()
        gamma_d = self.code_srd.get_gamma_d(1)
        gamma_n_ = self.code_srd.get_gamma_n_(a, lk_max + lk_min)
        gamma_rho = self.code_srd.get_gamma_rho(rho)
        gamma_t = self.code_srd.gamma_t(t1)
        sigma_allowed_f = self.code_srd.get_fatigue_sigma_allowed(2)
        sigma_max, sigma_min = self.ftv.fatige_get_sigma(Nn_max, Nn_min, Aj)
        result_fatigue, sigma_verify, sigma_allow = (
            self.ftv.fatigue_verify_compressed(gamma_d, gamma_n_, gamma_t, gamma_rho, sigma_allowed_f, sigma_max))

        result.add_result("fatigue_compressive", {"sigma_verify": sigma_verify, "sigma_allowed": sigma_allow})
        if not result_fatigue:
            result.add_error("StructuralError", "A002", "fatigue_compressive")

    def get_lambda_allowed(self, element):
        type_ = element.get_type()
        [Nk_max, Nk_min] = element.get_Nks()
        [Nn_max, Nn_min] = element.get_Nns()
        [Nc_max, Nc_min] = element.get_Ncs()
        if type_ == "上弦杆" or type_ == "下弦杆":
            # 弦杆
            return self.code_srd.get_lambda_allowed(1)
        elif Nc_min < 0:
            # 受压或受反复应力的杆件
            return self.code_srd.get_lambda_allowed(1)
        elif type_ == "斜杆" or type_ == "竖杆":
            if Nc_max >= 0 and Nc_min >= 0:
                l = element.get_l()
                return self.code_srd.get_lambda_allowed(3, l)
            elif Nk_min == 0 and Nk_max == 0:
                # 不受活载的腹杆
                return self.code_srd.get_lambda_allowed(2)
            pass

    def get_l_in_code(self, element, direction):
        type_ = element.get_type()
        type_end = element.get_type_end()
        l0 = element.get_l()
        if type_ == "上弦杆" or type_ == "下弦杆":
            l = self.code_srd.get_l_in_code(l0, 1) / 2 * 1000
        elif type_ == "斜杆" or type_ == "竖杆":
            if type_end:  # 如若为端斜杆
                if direction == "x":  # 面内
                    l = self.code_srd.get_l_in_code(l0, 3) * 1000
                elif direction == "y":  # 面外
                    l = self.code_srd.get_l_in_code(l0, 2) * 1000
                else:
                    raise Exception

            else:
                if direction == "x":
                    l = self.code_srd.get_l_in_code(l0, 5) * 1000
                elif direction == "y":
                    l = self.code_srd.get_l_in_code(l0, 4) * 1000
                else:
                    raise Exception
        else:
            return l0 * 1000

        return l
