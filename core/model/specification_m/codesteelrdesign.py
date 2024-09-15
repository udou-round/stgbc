"""
这是铁路钢结构
"""
from math import pi

from core.model.specification_m.code import Code


class CodeSteelRDesign(Code):
    def __init__(self):
        super().__init__()
        self.name = '铁路桥梁钢结构设计规范'
        self.number = 'TB 10091 - 2017'
        self.date = '2017-01-02'

    def __str__(self):
        return super().__str__()

    def get_load(self, load_name):
        # 铁路荷载，返回 [pk, qk]
        match load_name:
            case 'ZK':
                return [200, 64]
            case 'ZC':
                return [150, 48]
            case 'ZKH':
                return [250, 85]
            case 'ZH':
                pass
        """待补充"""

    def get_load_distance(self):
        return [0.8, 1.6, 1.6, 1.6, 0.8]

    @staticmethod
    def get_basic_allowable_stress(material_name):
        # 基础容许应力，返回 [axial_stress, bending_stress, shearing_stress]
        match material_name:
            case 'Q235qD':
                return [135, 140, 80]
            case 'Q345qD' | 'Q345qE':
                return [200, 210, 120]
            case 'Q370QD' | 'Q370qE':
                return [210, 220, 125]
        """p9待补充"""

    @staticmethod
    def get_fatigue_sigma_allowed(case_):
        match case_:
            case 1:
                return 149.5
            case 2:
                return 130.7
            case 3:
                return 121.7
            case 4:
                return 114.0
            case 5:
                return 110.3
            case 6:
                return 109.6
            case 7:
                return 99.9
            case 8:
                return 91.1
            case 9:
                return 80.6

    def get_increasing_factor_allowable_stress(self, case_):  # 3.2.8
        match case_:
            case 1:
                return 1  # 主力
            case 2:
                return 1.3  # 主力 + 附加力
            case 3:
                return 1.2  # 主力 + 面内次应力（或面外次应力）
            case 4:
                return 1.4  # 主力 + 面内次应力 + 面外次应力
            case 5:
                return 1.45
            case 6:
                return 1.5
            case 7:
                return 1.2
            case 8:
                return 1.4
            case 9:
                return 1.5

    @staticmethod
    def get_varphi1_H_flange(lambda_, material):
        # 焊接H形杆件，检算翼缘板平面内整体稳定时
        match material:
            case 'Q235qD':
                if 0 < lambda_ < 30:
                    return 0.9
                if 30 <= lambda_ < 40:
                    return 0.9 - (lambda_ - 40) * (0.9 - 0.864) / 10
                """p11待补充"""

            case 'Q345qD' | 'Q370qD':
                if 0 < lambda_ < 30:
                    return 0.9
                if 30 <= lambda_ < 40:
                    return 0.9 - (lambda_ - 30) * (0.9 - 0.823) / 10
                if 40 <= lambda_ < 50:
                    return 0.823 - (lambda_ - 40) * (0.823 - 0.747) / 10
                if 50 <= lambda_ < 60:
                    return 0.747 - (lambda_ - 50) * (0.747 - 0.677) / 10
                if 60 <= lambda_ < 70:
                    return 0.677 - (lambda_ - 60) * (0.677 - 0.609) / 10
                if 70 <= lambda_ < 80:
                    return 0.609 - (lambda_ - 70) * (0.609 - 0.544) / 10
                if 80 <= lambda_ < 90:
                    return 0.544 - (lambda_ - 80) * (0.544 - 0.483) / 10
                if 90 <= lambda_ < 100:
                    return 0.483 - (lambda_ - 90) * (0.483 - 0.424) / 10
                if 100 <= lambda_ < 110:
                    return 0.424 - (lambda_ - 100) * (0.424 - 0.371) / 10
                if 110 <= lambda_ < 120:
                    return 0.371 - (lambda_ - 110) * (0.371 - 0.327) / 10
                if 120 <= lambda_ < 130:
                    return 0.327 - (lambda_ - 120) * (0.327 - 0.287) / 10
                if 130 <= lambda_ < 140:
                    return 0.287 - (lambda_ - 130) * (0.287 - 0.249) / 10
                if 140 <= lambda_ < 150:
                    return 0.249 - (lambda_ - 140) * (0.249 - 0.212) / 10

    def get_fatigue_allowable_stress(self, case_):
        # 疲劳容许应力
        match case_:
            case 1:
                return 149.5
            case 2:
                return 130.7
            case 3:
                return 121.7
            case 4:
                return 114.0
            case 5:
                return 110.3
            case 6:
                return 109.6
            case 7:
                return 99.9
            case 8:
                return 91.1
            case 9:
                return 80.6
            case 10:
                return 72.9
            case 11:
                return 71.9
            case 12:
                return 60.2
            case 13:
                return 60.2
            case 14:
                return 45.0

    """unit 4"""

    """
    以下为应力计算，对应规范4.2.1条
    """

    @staticmethod
    def central_tension(N, A):
        """中心受拉构件"""
        sigma = N / A
        return sigma

    @staticmethod
    def bend(M, W):
        """在一个主平面内受弯"""
        sigma = M / W

    @staticmethod
    def central_tension_bend(N, A, M, W):
        """拉弯"""
        sigma = N / A + M / W

    @staticmethod
    def stability_get_lambda_e(l0, rx, ry, h):  # 4.2.2 - 4
        """默认为焊接，不考虑铆接"""
        if True:
            a = 1.8
        # else:
        #     a = 2.0

        lambda_e = a * l0 * rx / h / ry
        return lambda_e

    @staticmethod
    def stability_get_mu_1(E, N, Am, phi1, lambda_, sigma_allowed, case_):
        n1 = None
        N = abs(N)
        match case_:
            case 1:
                n1 = 1.7  # 主力组合时，压杆容许应力安全系数
            case 2:
                n1 = 1.4  # 主力 + 附加力组合时，压杆容许应力安全系数

        if N / Am <= 0.15 * phi1 * sigma_allowed:
            mu1 = 1.0
        else:
            mu1 = 1 - n1 * N * pow(lambda_, 2) / pow(pi, 2) / E / Am * 1000

        return mu1

    """4.3"""

    @staticmethod
    def get_mu_f_plus1(L):  # 4.3.1
        return 1 + 18 / (40 + L)

    @staticmethod
    def get_gamma_d(n_line, delta1=None, delta=None):  # 4.3.2
        if n_line == 1:
            return 1
        else:
            pass

    @staticmethod
    def gamma_t(t, case_=False):  # 4.3.6
        if case_:
            return 1

        if t <= 25:
            return 1
        else:
            return pow(25 / t, 1 / 4)

    @staticmethod
    def get_gamma_n(l, type_load="ZKH"):  # 4.3.6
        if l >= 20:
            return 1.00
        elif l >= 16:
            return 1.10 - (l - 16) / 4 * (1.10 - 1.00)
        else:
            pass

    @staticmethod
    def get_gamma_n_(a, l, type_load="ZKH"):  # 4.3.6
        if l >= 20:
            return 1.00
        elif l >= 16:
            pass

    def get_gamma_rho(self, rho, type_="True"):
        # 若未焊接结果，则为True
        if type_:
            if rho <= -4.5:
                return 0.21
            elif rho <= -4.0:
                return 0.21 + (rho + 4.5) * (0.23 - 0.21) / (4.5 - 4.0)
            elif rho <= -3.5:
                return 0.23 + (rho + 4.0) * (0.25 - 0.23) / (4.0 - 3.5)
            elif rho <= -3.0:
                return 0.25 + (rho + 3.5) * (0.28 - 0.25) / (3.5 - 3.0)
            elif rho <= -2.0:
                return 0.28 + (rho + 3.0) * (0.36 - 0.28) / (3.0 - 2.0)
            elif rho <= -1.8:
                return 0.36 + (rho + 2.0) * (0.38 - 0.36) / (2.0 - 1.8)
            elif rho <= -1.6:
                return 0.38 + (rho + 1.8) * (0.41 - 0.38) / (1.8 - 1.6)
            elif rho <= -1.4:
                return 0.41 + (rho + 1.6) * (0.43 - 0.41) / (1.6 - 1.4)
            elif rho <= -1.2:
                return 0.43 + (rho + 1.4) * (0.46 - 0.43) / (1.4 - 1.2)
            else:
                return 0.46
        else:
            pass
            return 0

    """unit 5"""

    @staticmethod
    def get_l_in_code(l0, case_):  # 5.1.1
        match case_:
            case 1:  # 主弦杆
                return l0
            case 2:  # 端斜杆、端立杆、连续梁中间支点处立柱或斜杆作为桥门架时：面内
                return 0.9 * l0
            case 3:  # 端斜杆、端立杆、连续梁中间支点处立柱或斜杆作为桥门架时：面外
                return l0
            case 4:
                return 0.8 * l0
            case 5:
                return l0

    @staticmethod
    def get_lambda_allowed(case_, L=None, n_line=None):  # 5.2.1
        match case_:
            # 主桁杆件
            case 1:
                return 100
            case 2:
                return 150
            case 3:
                if L == None:
                    pass
                elif L <= 16:
                    return 180
                else:
                    return 150
            # 联结系杆件
            case 4:
                pass

    @staticmethod
    def get_H_detail_require(case_, delta):
        match case_:
            case 1:  # 铆接杆件
                pass
            case 2:  # 焊接杆件
                if delta >= 24:
                    return 0.5
                else:
                    return 0.6

    """Attention: 例如除Q345qD外也包含Q345QC... 材料未写全"""

    @staticmethod
    def get_max_width_thickness_ratios(case_, material, lambda_, element_type=""):  # 5.3.3
        match case_:
            case 1:  # H形截面中的腹板
                match material:
                    case "Q235q":
                        if lambda_ < 60:
                            return 34
                        else:
                            return 0.4 * lambda_ + 10
                    case "Q345qD" | "Q370qD":
                        if lambda_ < 50:
                            return 30
                        else:
                            return 0.4 * lambda_ + 10
                    case "":
                        pass

            case 2:  # 箱形截面中无加劲肋的两边支承板
                match material:
                    case "Q235q":
                        if lambda_ < 33:
                            return 34
                        else:
                            return 0.3 * lambda_ + 15
                    case "Q345qD" | "Q370qD":
                        if lambda_ < 50:
                            return 30
                        else:
                            return 0.3 * lambda_ + 15
                    case "":
                        pass

            case 3:  # H形或T形无加劲肋的伸出肢
                """因本设计未用到铆接杆，因此未补充"""
                match material:
                    case "Q235q":
                        if lambda_ < 60:
                            return 13.5
                        else:
                            return 0.15 * lambda_ + 4.5
                    case "Q345qD" | "Q370qD":
                        if lambda_ < 50:
                            return 12
                        else:
                            return 0.14 * lambda_ + 5
                    case "":
                        pass

            case 4:
                pass
            case 5:
                pass

    """unit 7"""

    @staticmethod
    def get_partition_coefficient(case_):  # 7.2.4
        if case_ == 1:  # 主桁风力
            return [0.5, 0.5]
        if case_ == 2:  # 桥面系风力、列车风力、车辆摇摆力、离心力
            return [1.0, 0.2]

    """unit 9"""

    @staticmethod
    def get_eta(a_max, a):  # 9.0.6
        return 1 + (a_max - a) / 6
