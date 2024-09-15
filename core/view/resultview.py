import time

from core.model.specification_m.verifyresult import VerifyResult
from core.model.structure_m.element import Element


class ResultView:
    def __init__(self, elements=None):
        self.elements = elements

    def create_html(self):
        html_start = self.get_html_start()
        table_start = self.get_html_table_start()
        body = self.create_body()
        html_end = self.get_html_end()

        html_output = html_start + table_start + body + html_end

        with open('table.html', 'w', encoding='utf-8') as file:
            file.write(html_output)

    def create_body(self):
        n_top_chrod = 0
        line_top_chrod = 0
        body_top_chrod = ""
        n_lower_chrod = 0
        line_lower_chrod = 0
        body_lower_chrod = ""
        n_diagonal = 0
        line_diagonal = 0
        body_diagonal = ""

        body_vertical = ""

        for group in self.elements:
            e: Element
            for e in group:
                type_ = e.get_type()
                only_N = e.whether_only_N()
                if type_ == "上弦杆":
                    if n_top_chrod != 0:
                        body_top_chrod += self.get_tr()
                    if only_N:
                        line_top_chrod += 2
                        body_top_chrod += self.generate_html_body_col2(e)
                    else:
                        line_top_chrod += 3
                        body_top_chrod += self.generate_html_body_col3(e)

                    n_top_chrod += 1

                if type_ == "下弦杆":
                    if n_lower_chrod != 0:
                        body_lower_chrod += self.get_tr()
                    if only_N:
                        line_lower_chrod += 2
                        body_lower_chrod += self.generate_html_body_col2(e)
                    else:
                        line_lower_chrod += 3
                        body_lower_chrod += self.generate_html_body_col3(e)

                    n_lower_chrod += 1

                if type_ == "斜杆":
                    if n_diagonal != 0:
                        body_diagonal += self.get_tr()
                    if only_N:
                        line_diagonal += 2
                        body_diagonal += self.generate_html_body_col2(e)
                    else:
                        line_diagonal += 3
                        body_diagonal += self.generate_html_body_col3(e)

                    n_diagonal += 1

                if type_ == "竖杆" and body_vertical == "":
                    body_vertical = self.generate_html_body_col2(e)

        body_top_chrod = self.generate_html_body_title(line_top_chrod, "上弦杆") + body_top_chrod
        body_lower_chrod = self.generate_html_body_title(line_lower_chrod, "下弦杆") + body_lower_chrod
        body_diagonal = self.generate_html_body_title(line_diagonal, "斜杆") + body_diagonal
        body_vertical = self.generate_html_body_title(2, "竖杆") + body_vertical

        return body_top_chrod + body_lower_chrod + body_diagonal + body_vertical

    @staticmethod
    def get_time():
        time_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return time_

    def get_html_start(self):
        time_ = self.get_time()
        html_start = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="utf-8">
            <title>截面验算表</title>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
            <link rel="stylesheet" href="./tablestyle.css">
        </head>
        <body>
            <div class="container">
                <h1 class="title font-center">截面验算表</h1>
                <div class="time">{time_}</div>
            </div>
        """
        return html_start

    def get_html_table_start(self):
        html_table_start = """
        <table border="0" cellspacing="1" cellpadding="4" class="tablemain" align="center">
            <tr>
                <th width="6%" colspan="2" class="header font-center header-f" rowspan="2">杆件名称</th>
                <th width="10%" class="header font-center header-f" rowspan="2">截面组合</th>
                <th width="4%" class="header font-center header-f" rowspan="2">\(A_m\)</th>
                <th width="4%" class="header font-center header-f" rowspan="2">\(A_j\)</th>
                <th width="10%" class="header font-center header-f" rowspan="2">\(I_x/I_y\)</th>
                <th width="4%" class="header font-center header-f" rowspan="2">\(r_x/r_y\)</th>
                <th width="10%" class="header font-center header-f" rowspan="2">\(l_x/l_y\)</th>
                <th width="4%" class="header font-center header-f" rowspan="2">\(\lambda_x/\lambda_y\)</th>
                <th width="4%" class="header font-center header-f" rowspan="2">构造</th>
                <th width="8%" colspan="2" class="header font-center header-f">局部稳定</th>
                <th width="10%" colspan="3" class="header font-center header-f">总体稳定</th>
                <th width="16%" colspan="2" class="header font-center header-f">疲劳验算</th>
                <th width="10%" colspan="2" class="header font-center header-f">拉力强度</th>
        
            </tr>
            <tr>
                <th class="header font-center">翼缘</th>
                <th class="header font-center">腹板</th>
                <th class="header font-center">\(\sigma_m\)</th>
                <th class="header font-center">\( \\varphi_1\)</th>
                <th class="header font-center">\([\sigma_m]\)</th>
                <th class="header font-center sfont">\( \gamma_d \gamma_n(\sigma_{max}-\sigma_{min})/\)<br> \(\gamma_d
                    \gamma_n'\sigma_{max}\)
                </th>
                <th class="header font-center sfont">\( \gamma_t [\sigma_0]/\)<br> \(\gamma_t \gamma_\rho[\sigma_0] \)</th>
                <th class="header font-center">\(\sigma_j\)</th>
                <th class="header font-center">\(\gamma[\sigma]\)</th>
            </tr>
            <tr>
                <th colspan="2" class="header font-center header-f">项次</th>
                <th class="header-f2 font-center">1</th>
                <th class="header-f2 font-center">2</th>
                <th class="header-f2 font-center">3</th>
                <th class="header-f2 font-center">4</th>
                <th class="header-f2 font-center">5</th>
                <th class="header-f2 font-center">6</th>
                <th class="header-f2 font-center">7</th>
                <th class="header-f2 font-center">8</th>
                <th class="header-f2 font-center">9</th>
                <th class="header-f2 font-center">10</th>
                <th class="header-f2 font-center">11</th>
                <th class="header-f2 font-center">12</th>
                <th class="header-f2 font-center">13</th>
                <th class="header-f2 font-center">14</th>
                <th class="header-f2 font-center">15</th>
                <th class="header-f2 font-center">16</th>
                <th class="header-f2 font-center">17</th>
            </tr>
            <tr>
                <th colspan="2" class="header font-center header-f">单位</th>
                <th class="header-f2 font-center"> \(mm\\times mm\)</th>
                <th class="header-f2 font-center">\(cm^2\)</th>
                <th class="header-f2 font-center">\(cm^2\)</th>
                <th class="header-f2 font-center">\(cm^4\)</th>
                <th class="header-f2 font-center">\(cm\)</th>
                <th class="header-f2 font-center">\(cm\)</th>
                <th class="header-f2 font-center">&nbsp;</th>
                <th class="header-f2 font-center">&nbsp;</th>
                <th class="header-f2 font-center">&nbsp;</th>
                <th class="header-f2 font-center">&nbsp;</th>
                <th class="header-f2 font-center">\(MPa\)</th>
                <th class="header-f2 font-center">&nbsp;</th>
                <th class="header-f2 font-center">\(MPa\)</th>
                <th class="header-f2 font-center">\(MPa\)</th>
                <th class="header-f2 font-center">\(MPa\)</th>
                <th class="header-f2 font-center">\(MPa\)</th>
                <th class="header-f2 font-center">\(MPa\)</th>
            </tr>
        """
        return html_table_start

    def get_html_end(self):
        html_end = """
        </table>
        </body>
        </html>
        """
        return html_end

    def generate_html_body_title(self, n_line, type_):
        title = f"""
            <tr>
                <th rowspan="{n_line}" class="header-f2 font-center">{type_}</th>
        """
        return title

    @staticmethod
    def get_tr():
        return """
            <tr>
        """

    def generate_html_body_col2(self, element):

        element_id = element.get_id()
        height = element.get_height()
        t = element.get_t1()
        hw = element.get_hw()
        tw = element.get_tw()
        Am = element.get_Am() / 100  # mm^2 -> cm^2
        Aj = element.get_Aj() / 100
        Ix = element.get_Ix() / 10000  # mm^4 -> cm^4
        Iy = element.get_Iy() / 10000
        verify_result = element.get_verify_result()
        results = verify_result.get_results()
        errors = verify_result.get_errors()

        rx = ry = lambda_x = lambda_y = lx = ly = ""
        ratio_web = allowed_web = ratio_flange = allowed_flange = ""
        detail_cal = detail_required = ""
        sigma_m = phi_1 = sigma_m_allowed = ""
        sigma_fatigue = sigma_fatigue_allowed = ""
        sigma_tensile = sigma_tensile_allowed = ""

        warn_rigidity = warn_local_bucking = warn_detail = warn_stability = warn_fatigue = warn_tensile = ""

        for k, v in results.items():
            match k:
                case "rigidity":
                    rx = round(v.get("rx", 0) / 10, 2) if v.get("rx") is not None else ""
                    ry = round(v.get("ry", 0) / 10, 2) if v.get("ry") is not None else ""
                    lambda_x = round(v.get("lambda_x", 0), 2) if v.get("lambda_x") is not None else ""
                    lambda_y = round(v.get("lambda_y", 0), 2) if v.get("lambda_y") is not None else ""
                    lx = round(v.get("lx", 0) / 10, 2) if v.get("lx") is not None else ""
                    ly = round(v.get("ly", 0) / 10, 2) if v.get("ly") is not None else ""

                case "local_bucking":
                    ratio_flange = round(v.get("ratio_flange", 0), 2) if v.get("ratio_flange") is not None else ""
                    ratio_web = round(v.get("ratio_web", 0), 2) if v.get("ratio_web") is not None else ""
                    allowed_flange = round(v.get("allowed_flange", 0), 2) if v.get("allowed_flange") is not None else ""
                    allowed_web = round(v.get("allowed_web", 0), 2) if v.get("allowed_web") is not None else ""

                case "detail":
                    detail_cal = round(v.get("detail_cal", 0), 2)
                    detail_required = round(v.get("detail_required", 0), 2)

                case "stability" | "stability_Mw" | "stability_MT":
                    sigma_m = round(v.get("sigma_cm", 0), 2) if v.get("sigma_cm") is not None else ""
                    phi_1 = round(v.get("phi1", 0), 2) if v.get("phi1") is not None else ""
                    sigma_m_allowed = round(v.get("sigma_allowed", 0), 2) if v.get("sigma_allowed") is not None else ""

                case "fatigue_tensile" | "fatigue_compressive":
                    sigma_fatigue = round(v.get("sigma_verify", 0), 2) if v.get("sigma_verify") is not None else ""
                    sigma_fatigue_allowed = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

                case "tensile_strength" | "bending_strength_MT" | "bending_strength_Mw":
                    sigma_tensile = round(v.get("sigma", 0), 2) if v.get("sigma") is not None else ""
                    sigma_tensile_allowed = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

        for error in errors:
            result_key = error.get("result_key")
            match result_key:
                case "rigidity":
                    warn_rigidity = "warn-font"
                case "local_bucking":
                    warn_local_bucking = "warn-font"
                case "detail":
                    warn_detail = "warn-font"
                case "stability" | "stability_Mw" | "stability_MT":
                    warn_stability = "warn-font"
                case "fatigue_tensile" | "fatigue_compressive":
                    warn_fatigue = "warn-font"
                case "tensile_strength" | "bending_strength_MT" | "bending_strength_Mw":
                    warn_tensile = "warn-font"

        html_body = f"""
                <th class="header-f2 font-center" rowspan="2">{element_id}</th>
                <td class="font-n font-center">\\(2-{height} \\times{t}\\)</td>
                <td class="font-n font-center" rowspan="2">{Am:.2f}</td>
                <td class="font-n font-center" rowspan="2">{Aj:.2f}</td>
                <td class="font-n font-center">{Ix:.2e}</td>
                <td class="font-n font-center">{rx:.1f}</td>
                <td class="font-n font-center">{lx:.1f}</td>
                <td class="font-n font-center {warn_rigidity}">{lambda_x:.1f}</td>
                <td class="font-n font-center {warn_detail}">{detail_cal}</td>
                <td class="font-n font-center {warn_local_bucking}">{ratio_flange}</td>
                <td class="font-n font-center {warn_local_bucking}">{ratio_web}</td>
                <td class="font-n font-center" rowspan="2" {warn_stability}>{sigma_m}</td>
                <td class="font-n font-center" rowspan="2" {warn_stability}>{phi_1}</td>
                <td class="font-n font-center" rowspan="2" {warn_stability}>{sigma_m_allowed}</td>
                <td class="font-n font-center" rowspan="2 {warn_fatigue}">{sigma_fatigue}</td>
                <td class="font-n font-center" rowspan="2 {warn_fatigue}">{sigma_fatigue_allowed}</td>
                <td class="font-n font-center" rowspan="2 {warn_tensile}">{sigma_tensile}</td>
                <td class="font-n font-center" rowspan="2 {warn_tensile}">{sigma_tensile_allowed}</td>
            </tr>
            <tr>
                <td class="font-n font-center">\\(1-{hw} \\times{tw}\\)</td>
                <td class="font-n font-center">{Iy:.2e}</td>
                <td class="font-n font-center">{ry:.1f}</td>
                <td class="font-n font-center">{ly:.1f}</td>
                <td class="font-n font-center {warn_rigidity}">{lambda_y:.1f}</td>
                <td class="font-n font-center {warn_detail}">{detail_required}</td>
                <td class="font-n font-center {warn_local_bucking}">{allowed_flange}</td>
                <td class="font-n font-center {warn_local_bucking}">{allowed_web}</td>
            </tr>
        """

        return html_body

    def generate_html_body_col3(self, element):

        element_id = element.get_id()
        height = element.get_height()
        t = element.get_t1()
        hw = element.get_hw()
        tw = element.get_tw()
        Am = element.get_Am() / 100  # mm^2 -> cm^2
        Aj = element.get_Aj() / 100
        Ix = element.get_Ix() / 10000  # mm^4 -> cm^4
        Iy = element.get_Iy() / 10000
        verify_result = element.get_verify_result()
        results = verify_result.get_results()
        errors = verify_result.get_errors()

        rx = ry = lambda_x = lambda_y = lx = ly = ""
        ratio_web = allowed_web = ratio_flange = allowed_flange = ""
        detail_cal = detail_required = ""
        sigma_m = phi_1 = sigma_m_allowed = ""
        sigma_fatigue = sigma_fatigue_allowed = ""
        sigma_tensile = sigma_tensile_allowed = ""
        sigma_m_w = phi_1_w = sigma_m_allowed_w = ""
        sigma_m_T = phi_1_T = sigma_m_allowed_T = ""

        warn_rigidity = warn_local_bucking = warn_detail = warn_stability = warn_fatigue = warn_tensile = ""

        for k, v in results.items():
            match k:
                case "rigidity":
                    rx = round(v.get("rx", 0) / 10, 2) if v.get("rx") is not None else ""
                    ry = round(v.get("ry", 0) / 10, 2) if v.get("ry") is not None else ""
                    lambda_x = round(v.get("lambda_x", 0), 2) if v.get("lambda_x") is not None else ""
                    lambda_y = round(v.get("lambda_y", 0), 2) if v.get("lambda_y") is not None else ""
                    lx = round(v.get("lx", 0) / 10, 2) if v.get("lx") is not None else ""
                    ly = round(v.get("ly", 0) / 10, 2) if v.get("ly") is not None else ""

                case "local_bucking":
                    ratio_flange = round(v.get("ratio_flange", 0), 2) if v.get("ratio_flange") is not None else ""
                    ratio_web = round(v.get("ratio_web", 0), 2) if v.get("ratio_web") is not None else ""
                    allowed_flange = round(v.get("allowed_flange", 0), 2) if v.get("allowed_flange") is not None else ""
                    allowed_web = round(v.get("allowed_web", 0), 2) if v.get("allowed_web") is not None else ""

                case "detail":
                    detail_cal = round(v.get("detail_cal", 0), 2)
                    detail_required = round(v.get("detail_required", 0), 2)

                case "stability":
                    sigma_m = round(v.get("sigma_cm", 0), 2) if v.get("sigma_cm") is not None else ""
                    phi_1 = round(v.get("phi1", 0), 2) if v.get("phi1") is not None else ""
                    sigma_m_allowed = round(v.get("sigma_allowed", 0), 2) if v.get("sigma_allowed") is not None else ""

                case "stability_Mw":
                    sigma_m_w = round(v.get("sigma_cm", 0), 2) if v.get("sigma_cm") is not None else ""
                    phi_1_w = round(v.get("phi1", 0), 2) if v.get("phi1") is not None else ""
                    sigma_m_allowed_w = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

                case "stability_MT":
                    sigma_m_T = round(v.get("sigma_cm", 0), 2) if v.get("sigma_cm") is not None else ""
                    phi_1_T = round(v.get("phi1", 0), 2) if v.get("phi1") is not None else ""
                    sigma_m_allowed_T = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

                case "fatigue_tensile" | "fatigue_compressive":
                    sigma_fatigue = round(v.get("sigma_verify", 0), 2) if v.get("sigma_verify") is not None else ""
                    sigma_fatigue_allowed = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

                case "tensile_strength":  # | "bending_tensile_MT" | "bending_tensile_Mw"
                    sigma_tensile = round(v.get("sigma", 0), 2) if v.get("sigma") is not None else ""
                    sigma_tensile_allowed = round(v.get("sigma_allowed", 0), 2) if v.get(
                        "sigma_allowed") is not None else ""

        for error in errors:
            result_key = error.get("result_key")
            match result_key:
                case "rigidity":
                    warn_rigidity = "warn-font"
                case "local_bucking":
                    warn_local_bucking = "warn-font"
                case "detail":
                    warn_detail = "warn-font"
                case "stability" | "stability_Mw" | "stability_MT":
                    warn_stability = "warn-font"
                case "fatigue_tensile" | "fatigue_compressive":
                    warn_fatigue = "warn-font"
                case "tensile_strength" | "bending_strength_MT" | "bending_strength_Mw":
                    warn_tensile = "warn-font"

        html_body = f"""
                <th class="header-f2 font-center" rowspan="3">{element_id}</th>
                <td class="font-n font-center">\\(2-{height} \\times{t}\\)</td>
                <td class="font-n font-center" rowspan="3">{Am:.2f}</td>
                <td class="font-n font-center" rowspan="3">{Aj:.2f}</td>
                <td class="font-n font-center">{Ix:.2e}</td>
                <td class="font-n font-center">{rx:.1f}</td>
                <td class="font-n font-center">{lx:.1f}</td>
                <td class="font-n font-center {warn_rigidity}">{lambda_x:.1f}</td>
                <td class="font-n font-center {warn_detail}">{detail_cal}</td>
                <td class="font-n font-center {warn_local_bucking}">{ratio_flange}</td>
                <td class="font-n font-center {warn_local_bucking}">{ratio_web}</td>
                <td class="font-n font-center" rowspan="1" {warn_stability}>{sigma_m}</td>
                <td class="font-n font-center" rowspan="1" {warn_stability}>{phi_1}</td>
                <td class="font-n font-center" rowspan="1" {warn_stability}>{sigma_m_allowed}</td>
                <td class="font-n font-center" rowspan="3 {warn_fatigue}">{sigma_fatigue}</td>
                <td class="font-n font-center" rowspan="3 {warn_fatigue}">{sigma_fatigue_allowed}</td>
                <td class="font-n font-center" rowspan="3 {warn_tensile}">{sigma_tensile}</td>
                <td class="font-n font-center" rowspan="3 {warn_tensile}">{sigma_tensile_allowed}</td>
            </tr>
            <tr>
                <td class="font-n font-center">\\(1-{hw} \\times{tw}\\)</td>
                <td class="font-n font-center"  rowspan="2">{Iy:.2e}</td>
                <td class="font-n font-center"  rowspan="2">{ry:.1f}</td>
                <td class="font-n font-center"  rowspan="2">{ly:.1f}</td>
                <td class="font-n font-center {warn_rigidity}"  rowspan="2">{lambda_y:.1f}</td>
                <td class="font-n font-center"  rowspan="2" {warn_detail}>{detail_required}</td>
                <td class="font-n font-center"  rowspan="2" {warn_local_bucking}>{allowed_flange}</td>
                <td class="font-n font-center"  rowspan="2" {warn_local_bucking}>{allowed_web}</td>\
                <td class="font-n font-center {warn_stability}">{sigma_m_w}</td>
                <td class="font-n font-center {warn_stability}">{phi_1_w}</td>
                <td class="font-n font-center {warn_stability}">{sigma_m_allowed_w}</td>
            </tr>
            <tr>
                <td class="font-n font-center">&nbsp;</td>
                <td class="font-n font-center {warn_stability}">{sigma_m_T}</td>
                <td class="font-n font-center {warn_stability}">{phi_1_T}</td>
                <td class="font-n font-center {warn_stability}">{sigma_m_allowed_T}</td>
            </tr>
        """

        return html_body
