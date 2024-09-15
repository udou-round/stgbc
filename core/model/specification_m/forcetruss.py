from core.model.specification_m.force import Force
from core.model.structure_m.element import Element
from core.model.structure_m.node import Node
from math import pow, sqrt

"""
这个类为桁架梁桥力的计算
@param object_：力的作用对象
@param name：力的名字
@param magnitude：力的大小
@param direction：力的方向，传入单位向量如[0,0,1]
@param type：力的类型，如：dead_load（建规）,main_force（铁桥规）
@param applied：施加对象，whole、group、single
"""


class ForceTruss(Force):
    def __init__(self, name, magnitude, direction, object_):
        super().__init__(name, magnitude, direction, object_)
        self.type_ = 'truss'


class ForceTrussCalculator():
    def __init__(self, L, n, H, B, b, B0):
        self.L = L
        self.n = n
        self.H = H
        self.B = B
        self.b = b
        self.B0 = B0
        self.d = self.L / self.n
        self.s_theta = self.H / sqrt(pow(self.H, 2) + pow(self.d, 2))

    """
    以下为桁架静定内力计算
    """

    def chrod(self, group, type_, force=1):
        """弦杆内力计算"""
        result = []
        e: Element
        for e in group:
            p1: Node = e.get_p1()
            p2: Node = e.get_p2()
            coordinate1 = p1.get_coordinate()
            coordinate2 = p2.get_coordinate()
            l1 = (coordinate1[0] + coordinate2[0]) / 2
            l2 = self.L - l1
            omega = l1 * l2 / 2 / self.H * force
            if type_ == '上弦杆':
                omega = - omega
            result.append(omega)

        return result

    def vertical(self, group, force=1):
        """竖杆内力计算"""
        result = []
        omega = self.d * force
        for a in range(len(group)):
            result.append(omega)
        return result

    def diagonal(self, group, force=1):
        """斜杆内力计算"""
        result = []

        for a in range(len(group)):
            m = self.n - a - 1
            omega = m * m * self.d / 2 / (self.n - 1) / self.s_theta - pow(self.n - m - 1, 2) * self.d / 2 / (
                    self.n - 1) / self.s_theta

            omega = omega * force

            result.append(omega * (-1) ** (a + 1))

        return result

    def chrod_Nk(self, group, pk, qk, distances, type_):

        """
        弦杆活载内力计算
        :return: [[Nkmax, Nkmin, lkmax, lkmin], ...]
        """
        results = []
        e: Element
        for e in group:
            p1: Node = e.get_p1()
            p2: Node = e.get_p2()
            coordinate1 = p1.get_coordinate()
            coordinate2 = p2.get_coordinate()
            l1 = (coordinate1[0] + coordinate2[0]) / 2
            l2 = self.L - l1
            y = l1 * l2 / (self.H * self.L)

            # for i in range(1, len(distances)):
            #     # distances:[0.8,1.6,1.6,1.6,0.8]
            #     total_distance += distances[i - 1]
            #     x5 = l1 - total_distance
            #     y5 = get_y_triagnle(x5, l1, l2, y)
            #     x1 = x5 + distances[0]
            #     y1 = get_y_triagnle(x1, l1, l2, y)
            #     x2 = x1 + distances[1]
            #     y2 = get_y_triagnle(x2, l1, l2, y)
            #     x3 = x2 + distances[2]
            #     y3 = get_y_triagnle(x3, l1, l2, y)
            #     x4 = x3 + distances[3]
            #     y4 = get_y_triagnle(x4, l1, l2, y)
            #     x6 = x4 + distances[4]
            #     y6 = get_y_triagnle(x6, l1, l2, y)
            #     Nk = pk * (y1 + y2 + y3 + y4) + qk * (x5 * y5 / 2) + qk * (self.L - x6) * y6 / 2
            #     Nks.append(Nk)

            # 影响线计算，通过四次集中力作用于顶点 -> [Nk_max, Nk_min]，其中影响线函数计算出的仅有正值，因此不管哪个都 >=0，需要进行处理
            result = self.influence_line_triangle_cal(distances, l1, l2, pk, qk, y)
            if type_ == "上弦杆":
                result = [-x for x in result]
                result = list(reversed(result))
                result.append(0)
                result.append(self.L)

            else:
                result.append(self.L)
                result.append(0)

            results.append(result)

        return results

    def influence_line_triangle_cal(self, distances, l1, l2, pk, qk, y, max_left=None, max_right=None):
        """
        影响线计算，传入参数力的间距、左侧长度、右侧长度、pk、qk及顶点y坐标
        """
        if max_left == None:
            max_left = 0
        if max_right == None:
            max_right = 0

        Nks = []
        total_distance = 0
        L = l1 + l2
        for time, dist in enumerate(distances):
            # 只需记录四个集中力分别在三角形顶点时的情况，若循环次数超过四次，则终止循环以节约时间
            if time > 3:
                break

            Nk_total = 0
            # distances:[0.8,1.6,1.6,1.6,0.8]
            total_distance += dist
            x_n = l1 - total_distance

            if 0 > x_n > -max_left:
                y_n = get_y_triangle_allow_negative_l(x_n, l1, l2, y)
            elif L > x_n > max_right:
                y_n = get_y_triangle_allow_negative_r(x_n, l1, l2, y)
            else:
                y_n = get_y_triangle(x_n, l1, l2, y)

            Nk = qk * (x_n * y_n / 2)
            Nk_total += Nk
            for i in range(len(distances) - 1):
                x_n = x_n + distances[i]
                y_n = get_y_triangle(x_n, l1, l2, y)
                Nk_total += pk * y_n

            x_n = x_n + distances[4]
            y_n = get_y_triangle(x_n, l1, l2, y)
            Nk_total += qk * (L - x_n) * y_n / 2

            Nks.append(Nk_total)

        Nk_max = max(Nks)
        Nk_min = min(Nks)
        return [Nk_max, Nk_min]

    def diagonal_Nk(self, group, pk, qk, distances):
        """
        相比弦杆，斜杆计算的是两个三角形的影响线，只需把每个三角形的相应参数计算出来，即可传入influence_line_triangle_cal函数计算
        但要注意：get_y_triangle y为负数时返回值为0，在三角形交界处对超出边界集中力并不适用
        但在该种情况下，一般不会是最不利情况，故不予以考虑
        """
        results = []
        e: Element
        for a, e in enumerate(group):
            m = self.n - 1 - a
            x_b = m * self.d / (self.n - 1)
            x_a = self.d - x_b
            l1 = a * self.d
            l2 = m * self.d
            y1 = a / (self.n * self.s_theta)
            y2 = m / (self.n * self.s_theta)

            result1 = self.influence_line_triangle_cal(distances, l1, x_a, pk, qk, y1, max_right=x_a)
            result2 = self.influence_line_triangle_cal(distances, x_b, l2, pk, qk, y2, max_left=x_b)

            if (-1) ** a == -1:
                result1 = [i * -1 for i in result1]
                Nk_min = result1[0]
                Nk_max = result2[0]
                lk_min = l1 + x_a
                lk_max = l2 + x_b
            else:
                result2 = [i * -1 for i in result2]
                Nk_min = result2[0]
                Nk_max = result1[0]
                lk_min = l2 + x_b
                lk_max = l1 + x_a

            results.append([Nk_max, Nk_min, lk_max, lk_min])

        return results

    def vertical_Nk(self, group, pk, qk, distances):
        """竖杆活载内力计算"""
        results = []
        l1 = self.d
        l2 = self.d
        y = 1

        # 影响线计算，通过四次集中力作用于顶点 -> [Nk_max, Nk_min]
        result = self.influence_line_triangle_cal(distances, l1, l2, pk, qk, y)
        result.append(self.d * 2)
        result.append(0)
        for i in range(len(group)):
            results.append(result)

        return results

    def lateral_sway_force(self, group, S, c1, c2, type_):
        """分别传入计算组，横向摇摆力，上平纵联分配系数，下平纵联分配系数"""
        result = []

        if type_ == "上弦杆":
            S = c1 * S
            L = self.L - 2 * self.d
        elif type_ == "下弦杆":
            S = c2 * S
            L = self.L
        else:
            return 0

        e: Element
        for n in range(len(group)):
            l1 = (2 * n + 1.5) * self.d
            l2 = L - l1
            y1 = l1 * l2 / self.B / L

            l1 = (2 * n + 0.5) * self.d
            l2 = L - l1
            y2 = l1 * l2 / self.B / L

            y = max(y1, y2)
            Ns = S * y
            if type_ == "上弦杆":
                result.append(-Ns)
            if type_ == "下弦杆":
                result.append(Ns)
        return result

    def wind_force(self, group, w, type_):

        result = []

        if type_ == "上弦杆":
            L = self.L - 2 * self.d
        elif type_ == "下弦杆":
            L = self.L
        else:
            return 0

        e: Element
        for n in range(len(group)):
            l1 = (2 * n + 1.5) * self.d
            l2 = L - l1
            omega_1 = l1 * l2 / self.B / 2

            l1 = (2 * n + 0.5) * self.d
            l2 = L - l1
            omega_2 = l1 * l2 / self.B / 2

            y = max(omega_1, omega_2)
            Nw = w * y
            if type_ == "上弦杆":
                result.append(-Nw)
            if type_ == "下弦杆":
                result.append(Nw)
        return result

    def portal_frame_effect(self, w_up, c, h_cross):
        # h_cross：衡量高度
        Hw = 1 / 2 * (self.L - 2 * self.d) * w_up
        l = sqrt(pow(self.d, 2) + pow(self.H, 2))
        l0 = c * (c + 2 * l) / (2 * (2 * c + l))
        V = Hw * (l - l0) / self.B  # 端斜杆轴力
        cos_theta = self.d / l
        Nw2 = V * cos_theta  # 端斜杆轴力在下弦杆分力
        Me = Hw * (c - l0) / 2  # 端斜杆中部附加弯矩
        Mk = Hw / 2 * (l0 - h_cross / 2)  # 端斜杆端部（横梁高度1.29m的一半处附加弯矩

        return [-V, Nw2, Me, Mk]

    def vertical_static_live_load(self, pk, qk, distances):
        return qk * (self.L - sum(distances)) + 4 * pk

    def NT(self, T):
        return T / 2

    def MT(self, h, NT):
        # h:下弦杆中线至支座下摆顶点的距离
        M = NT * h  # 端节点处产生偏心弯矩
        M1 = 0.4 * M  # 下弦杆弯矩
        M2 = 0.7 * M  # 端斜杆弯矩
        return [M1, M2]

    def calculation_combination(self, main_force, coefficient_main, name_with_force, coefficient, main_name="主力"):
        # main_force: 主力, name_with_force中传入元组列表[(force_name, force),...]
        # :return: {"combination_name":"value"}, Nc_max_str, Nc_max
        # @attention: 可能出现bug -> 主力为正值但是由于附加力而可能承受压力，程序未考虑此种情况
        result_dict = {}
        Nc_max = main_force / coefficient_main
        Nc_max_str = main_name

        # 计算每种组合的内力值并比较
        for i, (force_name, additional_force) in enumerate(name_with_force):
            # 计算组合内力值
            force_value = main_force + additional_force
            # 更新最大内力值及其对应的组合描述
            result_dict[f"{main_name} + {force_name}"] = force_value

            # 得到计算内力
            force_value = force_value / coefficient
            if abs(force_value) > abs(Nc_max):
                Nc_max = force_value
                Nc_max_str = f"{main_name} + {force_name}"

        return result_dict, Nc_max_str, Nc_max

    def combinaion(self, *args):
        sum = 0
        for i in args:
            sum += i

        return sum


def get_y_triangle(x, l1, l2, y):
    if x <= 0:
        return 0
    elif 0 < x <= l1:
        return (x / l1) * y
    elif l1 < x <= l1 + l2:
        return (l1 + l2 - x) / l2 * y
    else:
        return 0


def get_y_triangle_allow_negative(x, l1, l2, y):
    if x <= l1:
        return (x / l1) * y
    else:
        return (l1 + l2 - x) / l2 * y


def get_y_triangle_allow_negative_l(x, l1, l2, y):
    if x <= l1:
        return (x / l1) * y
    elif l1 < x <= l1 + l2:
        return (l1 + l2 - x) / l2 * y
    else:
        return 0


def get_y_triangle_allow_negative_r(x, l1, l2, y):
    if x <= 0:
        return 0
    elif 0 < x <= l1:
        return (x / l1) * y
    elif l1 < x:
        return (l1 + l2 - x) / l2 * y


def ensure_non_negative(value):
    return max(0, value)


class VerifyTrussCalculator(object):
    def __init__(self):
        pass

    @staticmethod
    def rigidity_verify(lambda_allowed, Am, lx, ly, Ix, Iy):
        ry = sqrt(Iy / Am)
        lambda_y = ly / ry
        rx = sqrt(Ix / Am)
        lambda_x = lx / rx

        if lambda_x <= lambda_allowed and lambda_y <= lambda_allowed:
            verify_result = True
        else:
            verify_result = False

        return verify_result, rx, ry, lambda_x, lambda_y

    @staticmethod
    def tensile_strength_N(sigama_allowed, N, Aj):
        """仅轴力杆件验算强度"""
        sigma_cj = N / Aj * 1000
        verify_result = sigma_cj < sigama_allowed
        return verify_result, sigma_cj

    @staticmethod
    def tensile_strength_M(sigma_allowed, N, Aj, M, Wj, increasing_factor):
        """含M杆件验算强度"""
        M = abs(M)
        sigma_cj = N / Aj * 1000
        sigma_II = sigma_cj + M / Wj * 1000 * 1000
        sigma_allowed = sigma_allowed * increasing_factor
        verify_result = sigma_II < sigma_allowed
        return verify_result, sigma_II, sigma_cj, sigma_allowed

    @staticmethod
    def detail_H(t, tw, detail_required):
        detail_cal = tw / t
        verify_result = detail_cal >= detail_required
        return verify_result, detail_cal

    @staticmethod
    def overall_statbility_N(N, Am, phi1, sigma_allowed):
        """仅轴力杆件验算总体稳定"""
        N = abs(N)
        sigma_cm = N / Am * 1000
        sigma_allowed = phi1 * sigma_allowed
        verify_result = sigma_cm <= sigma_allowed
        return verify_result, sigma_cm, sigma_allowed

    @staticmethod
    def overall_statbility_M(N, Am, M, Wm, mu1, phi1, phi2, increasing_factor, sigma_allowed):
        """压弯杆件验算总体稳定"""
        N = abs(N)
        M = abs(M)
        sigma_cm = N / Am * 1000 + phi1 / mu1 / phi2 * M / Wm * 1000 * 1000

        sigma_allowed = increasing_factor * phi1 * sigma_allowed
        verify_result = sigma_cm <= sigma_allowed
        return verify_result, sigma_cm, sigma_allowed

    @staticmethod
    def width_thickness_ratios(b, delta, allowed):
        """验算局部稳定"""
        ratio = b / delta
        verify_result = ratio <= allowed
        return verify_result, ratio

    @staticmethod
    def fatigue_verify_tensile(gamma_d, gamma_n, gamma_t, simga_0, sigma_max, sigma_min):
        """焊接结构以拉为主构件 拉拉构件"""
        sigma_allow = simga_0 * gamma_t

        sigma_verify = gamma_d * gamma_n * (sigma_max - sigma_min)
        verify_result = sigma_verify <= sigma_allow
        return verify_result, sigma_verify, sigma_allow

    @staticmethod
    def fatigue_verify_compressed(gamma_d, gamma_n_, gamma_t, gamma_rho, simga_0, sigma_max):
        sigma_allow = simga_0 * gamma_t * gamma_rho

        sigma_verify = gamma_d * gamma_n_ * sigma_max
        verify_result = sigma_verify <= sigma_allow
        return verify_result, sigma_verify, sigma_allow

    @staticmethod
    def fatige_get_sigma(Nn_max, Nn_min, Aj):
        sigma_max = Nn_max / Aj * 1000
        sigma_min = Nn_min / Aj * 1000
        return sigma_max, sigma_min
