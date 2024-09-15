from core.model.specification_m.code import Code


class CodeSteelR(Code):
    def __init__(self):
        super().__init__()
        self.name = '铁路桥涵设计规范'
        self.number = 'TB 10002 - 2017'
        self.date = '2017-01-02'

    def __str__(self):
        return super().__str__()

    @staticmethod
    def get_mu_plus1(L, load):  # 4.3.6
        if load == "ZKH":
            return 1 + 28 / (40 + L)
        else:
            pass

    def get_braking_force(self, case, static_live_load, n_line):  # 4.3.10
        if n_line >= 3:  # 三线或三线以上的桥梁按双线
            m = 2
        else:
            m = 1

        if case == 1:
            return 0.1 * static_live_load * m
        elif case == 2:  # 当与离心力或列车竖向动力作用同时计算时
            return 0.07 * static_live_load * m
        else:
            pass

    def get_lateral_sway_force(self, load):  # 4.3.11
        if load == "ZKH":
            return 100
        else:
            pass

    def get_wind_pressure(self, K1, K2, K3, W0):  # 4.4.1
        return K1 * K2 * K3 * W0

    def get_wind_pressure_standard(self, K1, K2):  # 4.4.8
        W1 = min(K1 * K2 * 800, 1250)  # 有车时
        W2 = K1 * K2 * 1400  # 无车时
        return [W1, W2]
