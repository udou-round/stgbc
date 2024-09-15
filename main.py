from core.controller.calcontroller import CalService
from core.model.specification_m.codesteelrdesign import CodeSteelRDesign
from core.model.structure_m.element import Element
from core.model.structure_m.material import Material
from core.view.resultview import ResultView


def set_elements_section(group, input_controller, section_list, material):
    for i, element in enumerate(group):
        list_ = section_list[i]
        bolt_dict = {list_[6]: list_[5]}
        bolt_dist = list_[7]
        input_controller.set_section(element, list_[0], list_[1], list_[2], list_[3], list_[4], bolt_dict,
                                     bolt_dist)
        input_controller.set_material(element, material)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    input_controller: CalService
    input_controller = CalService(89.8, 10, 12.35, 5.75, 2, 5.3)
    input_controller.auto_create()
    input_controller.auto_calculate_Np(18)
    input_controller.auto_calculate_Nk()
    input_controller.cal_force_in_code()
    input_controller.auto_calculate_sway()
    input_controller.auto_calculate_wind(1, 1, 1, 1.25, 1.69, 8.04)
    input_controller.braking_additional_force(0.37)
    input_controller.combination()
    input_controller.fatigue_internal_force()

    axial_sigma, bending_sigma, shearing_sigma = CodeSteelRDesign.get_basic_allowable_stress("Q345qD")
    sigma_list = [axial_sigma, bending_sigma, shearing_sigma]
    material = Material("Q345qD", sigma_list)
    material.set_E(210000)

    groups = Element.current_group
    groups_sorted = []

    # 下弦杆
    group = Element.current_group[0]
    half_length = (len(group) + 1) // 2
    groups_sorted.append(group[:half_length])
    # [[height, width, tw, t1, t2, n_bolt,d_bolt]]
    section_list = [
        [460, 460, 12, 16, 16, 4, 23, [90, 170]],
        [460, 460, 24, 32, 32, 4, 23, [90, 170]],
        [460, 460, 32, 40, 40, 4, 23, [90, 170]],
        [460, 460, 24, 32, 32, 4, 23, [90, 170]],
        [460, 460, 12, 16, 16, 4, 23, [90, 170]]]

    element: Element
    set_elements_section(group, input_controller, section_list, material)

    group = Element.current_group[1]
    set_elements_section(group, input_controller, section_list, material)

    # 上弦杆
    group = Element.current_group[8]
    half_length = (len(group) + 1) // 2
    groups_sorted.append(group[:half_length])
    section_list = [
        [460, 460, 16, 32, 32, 4, 23, [90, 170]],
        [460, 460, 32, 56, 56, 4, 23, [90, 170]],
        [460, 460, 32, 56, 56, 4, 23, [90, 170]],
        [460, 460, 16, 32, 32, 4, 23, [90, 170]]]

    set_elements_section(group, input_controller, section_list, material)
    group = Element.current_group[9]
    set_elements_section(group, input_controller, section_list, material)

    # 斜杆
    group1 = groups[4]
    group2 = groups[6]
    group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
    half_length = (len(group) + 1) // 2
    groups_sorted.append(group[:half_length])
    section_list = [
        [600, 460, 20, 26, 26, 6, 23, [90, 170, 250]],
        [520, 460, 12, 16, 16, 6, 23, [90, 170, 250]],
        [520, 460, 20, 20, 20, 4, 23, [90, 170]],
        [520, 460, 12, 16, 16, 4, 23, [90, 170]],
        [520, 460, 10, 16, 16, 4, 23, [90, 170]],
        [520, 460, 10, 16, 16, 4, 23, [90, 170]],
        [520, 460, 12, 16, 16, 4, 23, [90, 170]],
        [520, 460, 20, 20, 20, 4, 23, [90, 170]],
        [520, 460, 12, 16, 16, 6, 23, [90, 170, 250]],
        [600, 460, 20, 26, 26, 6, 23, [90, 170, 250]],
    ]
    set_elements_section(group, input_controller, section_list, material)

    group1 = groups[5]
    group2 = groups[7]
    group = sorted(group1 + group2, key=lambda e: e.min_coordinate_x())
    set_elements_section(group, input_controller, section_list, material)

    # 竖杆
    group = Element.current_group[2]
    groups_sorted.append(group)
    section_list = [
        [360, 460, 10, 14, 14, 2, 23, [120]],
        [360, 460, 10, 14, 14, 2, 23, [120]],
        [360, 460, 10, 14, 14, 2, 23, [120]],
        [360, 460, 10, 14, 14, 2, 23, [120]],
        [360, 460, 10, 14, 14, 2, 23, [120]]]
    set_elements_section(group, input_controller, section_list, material)
    group = Element.current_group[3]
    set_elements_section(group, input_controller, section_list, material)
    input_controller.verify_pass_element()
    # for group in Element.current_group:
    #     print("--------------------------------")
    #     e: Element
    #     for e in group:
    #         print(
    #             f"ID, {e.id}, type: {e.type_}, Nkmax: {e.Nk_max:.2f}, Nkmin: {e.Nk_min:.2f}"
    #             f", Ix: {e.get_Ix():.3e}, Iy: {e.get_Iy():.3e}"
    #             f", MT: {e.get_MT():.3e}, Mw: {e.get_Mw():.3e}"
    #             f", material: {e.get_material_name()}, sigma_axial: {e.get_sigma_axial()}")

    for group in Element.current_group:
        # print("--------------------------------")
        e: Element
        for e in group:
            # print(
            #     f"ID, {e.id}, type: {e.type_}"
            #     f"result: {e.verify_result}")
            print(e.verify_result)
            print(
                f"ID, {e.id}, type: {e.type_},Np:{e.Np:.2f}, Nkmax: {e.Nk_max:.2f}, Nkmin: {e.Nk_min:.2f}"
                f", Ncmax: {e.Nc_max:.2f} - {e.Nc_max_str}, Ncmin: {e.Nc_min:.2f} - {e.Nc_min_str}"
                f", Nnmax: {e.Nn_max:.2f}, Nnmin: {e.Nn_min:.2f}, mu_f+1: {e.mu_f_plus1:.2f}"
                f", Mw:{e.get_Mw():.2f}, MT:{e.get_MT():.2f}, Nw:{e.get_Nw():.2f}, NT:{e.get_NT():.2f}, l:{e.get_l():.2f}")


    result_view = ResultView(groups_sorted)
    result_view.create_html()
