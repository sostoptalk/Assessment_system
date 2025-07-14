import os
import base64
import jinja2
from datetime import time
from weasyprint import HTML
from generate_report import (  # 替换为您的报告生成模块
    read_excel_with_averages,
    prepare_report_data,
    convert_to_radar_data,
    generate_filename,
    compare_with_average
)
from radar_chart import generate_radar_chart


# 添加之前的所有依赖函数（convert_to_radar_data, sanitize_filename, generate_filename等）
# 确保所有依赖函数都包含在这个文件中或从其他模块导入
def get_dim_strengths(strengths):
    """获取所有优势维度"""
    return strengths.get("维度", [])

def get_sub_strengths(strengths):
    """获取所有优势子维度"""
    return strengths.get("子维度", [])

# 在报告中显示劣势维度的过滤器
def get_dim_weaknesses(weaknesses):
    """获取所有劣势维度"""
    return weaknesses.get("维度", [])

def get_sub_weaknesses(weaknesses):
    """获取所有劣势子维度"""
    return weaknesses.get("子维度", [])


def get_top_strength(strengths):
    """获取最显著的优势维度或子维度"""
    candidates = strengths.get("维度", []) + strengths.get("子维度", [])
    if not candidates:
        return None

    # 按差异值从大到小排序
    candidates.sort(key=lambda x: x["diff"], reverse=True)
    return candidates[0]


def get_main_weakness(weaknesses):
    """获取最显著的劣势维度或子维度"""
    candidates = weaknesses.get("维度", []) + weaknesses.get("子维度", [])
    if not candidates:
        return None

    # 按差异值从小到大排序（差异值越小说明越需要关注）
    candidates.sort(key=lambda x: x["diff"])
    return candidates[0]


def save_temp_image(report_data, base_dir):
    """将Base64图片保存为临时文件"""
    try:
        if 'chart_img' in report_data and report_data['chart_img'].startswith('data:image'):
            # 从Base64字符串中提取图像数据
            img_data = report_data['chart_img'].split(',')[1]
            decoded_img = base64.b64decode(img_data)

            # 生成临时文件路径
            temp_dir = os.path.join(base_dir, 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)
            img_path = os.path.join(temp_dir, f"chart_{int(time.time())}.png")

            # 保存图片
            with open(img_path, 'wb') as f:
                f.write(decoded_img)
            return img_path
    except Exception:
        pass
    return ""


def generate_pdf_report(report_data, output_path, base_dir):
    """
    生成PDF报告

    :param report_data: 完整的报告数据
    :param output_path: 输出PDF文件路径
    """
    # 1. 设置Jinja2环境
    template_dir = os.path.join(base_dir, 'assets')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    # 添加自定义过滤器
    env.filters.update({
        'get_dim_strengths': get_dim_strengths,
        'get_dim_weaknesses': get_dim_weaknesses,
        'get_sub_strengths': get_sub_strengths,
        'get_sub_weaknesses': get_sub_weaknesses,
        'get_top_strength': get_top_strength,
        'get_main_weakness': get_main_weakness
    })

    # 2. 加载模板
    template_path = os.path.join(template_dir, 'report_template.html')
    #print(f"正在查找模板: {template_path}")
    if os.path.exists(template_path):
        try:
            # 直接使用模板文件路径
            template = env.get_template('report_template.html')
        except Exception:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                template = env.from_string(template_content)
    else:
        raise RuntimeError(f"无法找到模板文件: {template_path}")

    # 3. 渲染HTML内容
    try:
        # 使用report_data渲染HTML内容
        html_content = template.render(**report_data)
    except Exception as e:
        #print("222222222")
        raise RuntimeError(f"模板渲染失败: {str(e)}")


    # 4. 创建PDF文件（带错误处理和日志）
    try:
        # 保存调试HTML文件
        # debug_html_path = f"debug_{os.path.basename(output_path)}.html"
        # with open(debug_html_path, 'w', encoding='utf-8') as f:
        #     f.write(html_content)
        #print(f"调试HTML已保存至: {debug_html_path}")

        # 生成PDF（带超时）
        HTML(string=html_content).write_pdf(output_path)
        #print("zheli")
    except Exception as e:
        #print("222222222333333")
        # 尝试使用文件路径替代Base64
        temp_img_path = save_temp_image(report_data, base_dir)
        if temp_img_path:
            temp_report_data = report_data.copy()
            temp_report_data['chart_img'] = f"file://{temp_img_path}"
            try:
                html_content = template.render(**temp_report_data)
                HTML(string=html_content).write_pdf(
                    output_path,
                    timeout=60
                )
            except Exception as e2:
                raise RuntimeError(f"PDF生成失败: {str(e)} 和 {str(e2)}")
        else:
            raise RuntimeError(f"PDF生成失败: {str(e)}")

# def generate_pdf_report(report_data, output_path, base_dir, chart_path):
#     """
#     生成PDF报告
#
#     :param report_data: 完整的报告数据
#     :param output_path: 输出PDF文件路径
#     """
#
#     template_path = os.path.join(base_dir, 'assets', 'report_template.html')
#
#     # 1. 设置Jinja2环境
#     template_dir = os.path.join(base_dir, 'assets')
#     env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
#
#     env.filters['get_dim_strengths'] = get_dim_strengths
#     env.filters['get_dim_weaknesses'] = get_dim_weaknesses
#     env.filters['get_sub_strengths'] = get_sub_strengths
#     env.filters['get_sub_weaknesses'] = get_sub_weaknesses
#     env.filters['get_top_strength'] = get_top_strength
#     env.filters['get_main_weakness'] = get_main_weakness
#
#
#     # 2. 加载模板
#     try:
#         template = env.get_template('report_template.html')
#     except jinja2.exceptions.TemplateNotFound:
#         # 尝试使用绝对路径加载模板
#         if os.path.exists(template_path):
#             with open(template_path, 'r', encoding='utf-8') as f:
#                 template_content = f.read()
#                 template = env.from_string(template_content)
#         else:
#             raise RuntimeError(f"无法找到模板文件: {template_path}")
#
#     # 3. 渲染HTML内容
#     try:
#         html_content = template.render(**report_data,chart_img=chart_path)
#
#         # 调试：保存HTML文件以便验证
#         debug_html_path = output_path.replace('.pdf', '.html')
#         with open(debug_html_path, 'w', encoding='utf-8') as f:
#             f.write(html_content)
#
#     except Exception as e:
#         raise RuntimeError(f"模板渲染失败: {str(e)}")
#
#     # 4. 创建PDF文件
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             HTML(string=html_content).write_pdf(output_path)
#             break  # 成功则退出循环
#         except Exception as e:
#             if attempt < max_retries - 1:
#                 time.sleep(1)  # 等待1秒后重试
#             else:
#                 # 将Base64图片保存为临时文件，再尝试生成PDF
#                 temp_img_path = save_temp_image(report_data, base_dir)
#                 html_content = template.render(**report_data)
#                 HTML(string=html_content).write_pdf(output_path)


def batch_generate_reports(excel_path, output_dir, progress_callback, log_callback,
                           assets_dir_name="assets", base_dir=None):
    """
    批量生成报告的包装函数，支持进度和日志回调
    """
    if base_dir is None:
        # 获取应用程序基础目录
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 创建资源目录
    assets_dir = os.path.join(output_dir, assets_dir_name)
    os.makedirs(assets_dir, exist_ok=True)

    # 1. 读取Excel数据
    if not progress_callback(5, "读取Excel数据..."):
        return
    log_callback("读取Excel数据和平均分...")

    try:
        # 使用之前定义的函数读取Excel
        report_data_list, average_scores = read_excel_with_averages(excel_path)
        total_reports = len(report_data_list)
        log_callback(f"发现 {total_reports} 份报告需要生成")
    except Exception as e:
        log_callback(f"读取Excel失败: {str(e)}")
        raise

    # 2. 批量生成报告
    successful_reports = 0
    failed_users = []

    for i, report_data in enumerate(report_data_list):
        user_name = report_data['user_info']['name']
        report_num = i + 1

        # 检查是否被取消
        if not progress_callback(10 + i * 75 // total_reports,
                                 f"处理用户 {report_num}/{total_reports}: {user_name}"):
            return

        log_callback(f"\n>> 开始处理: {user_name} ({report_num}/{total_reports})")

        try:
            # 2.1 准备报告数据
            log_callback("准备报告数据...")

            report_data = prepare_report_data(report_data)
            report_data = compare_with_average(report_data, average_scores)

            report_data = prepare_report_data(report_data)

            # 2.2 转换为雷达图数据
            log_callback("生成雷达图数据...")
            radar_data = convert_to_radar_data(report_data['dimensions'])

            # 2.3 生成雷达图
            log_callback("创建雷达图...")
            chart_filename = generate_filename("radar_chart", user_name)
            chart_path = os.path.join(assets_dir, chart_filename)

            # 假设您的雷达图生成函数是 generate_radar_chart
            generated_path = generate_radar_chart(radar_data, chart_path)
            log_callback(f"雷达图已保存: {generated_path}")
            #print("111111111")
            #(generated_path)
            # 嵌入图片为Base64
            with open(generated_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            #print(encoded_string)
            # 将图片存储在report_data中
            report_data['chart_img'] = f"data:image/png;base64,{encoded_string}"
            #print(report_data['chart_img'])
            # 2.4 生成PDF报告
            log_callback("生成PDF报告...")
            report_filename = generate_filename("2025年5月管培生管理潜质测评", user_name, extension="pdf",
                                                with_timestamp=False)
            report_path = os.path.join(output_dir, report_filename)
            #print("111111111111111")
            # 调用PDF生成函数 - 只传入base_dir
            generate_pdf_report(report_data, report_path, base_dir)
            #print("111111111111111")
            log_callback(f"报告已生成: {report_path}")

            successful_reports += 1

        except Exception as e:
            error_msg = f"生成 {user_name} 的报告时出错: {str(e)}"
            log_callback(error_msg)
            failed_users.append(user_name)

    # 完成所有报告
    completion_message = f"报告生成完成: {successful_reports}份成功"
    if failed_users:
        completion_message += f", {len(failed_users)}份失败 ({', '.join(failed_users)})"

    progress_callback(100, completion_message)
    log_callback(f"\n{completion_message}")


# def batch_generate_reports(excel_path, output_dir, progress_callback, log_callback,
#                           assets_dir_name="assets", base_dir=None):
#     """
#     批量生成报告的包装函数，支持进度和日志回调
#
#     :param excel_path: Excel文件路径
#     :param output_dir: 输出目录
#     :param progress_callback: 进度回调函数
#     :param log_callback: 日志回调函数
#     :param assets_dir_name: 资源文件目录名
#     """
#
#     if base_dir is None:
#         # 获取应用程序基础目录
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#
#     # 创建资源目录
#     assets_dir = os.path.join(output_dir, assets_dir_name)
#     os.makedirs(assets_dir, exist_ok=True)
#
#     # 1. 读取Excel数据
#     if not progress_callback(5, "读取Excel数据..."):
#         return
#     log_callback("读取Excel数据和平均分...")
#
#     try:
#         # 使用之前定义的函数读取Excel
#         report_data_list, average_scores = read_excel_with_averages(excel_path)
#         total_reports = len(report_data_list)
#         log_callback(f"发现 {total_reports} 份报告需要生成")
#     except Exception as e:
#         log_callback(f"读取Excel失败: {str(e)}")
#         raise
#
#     # 2. 批量生成报告
#     successful_reports = 0
#     failed_users = []
#
#     for i, report_data in enumerate(report_data_list):
#         user_name = report_data['user_info']['name']
#         report_num = i + 1
#
#         # 检查是否被取消
#         if not progress_callback(10 + i * 75 // total_reports,
#                                  f"处理用户 {report_num}/{total_reports}: {user_name}"):
#             return
#
#         log_callback(f"\n>> 开始处理: {user_name} ({report_num}/{total_reports})")
#
#         try:
#             # 2.1 准备报告数据
#             log_callback("准备报告数据...")
#             report_data = prepare_report_data(report_data)
#
#             # 2.2 转换为雷达图数据
#             log_callback("生成雷达图数据...")
#             radar_data = convert_to_radar_data(report_data['dimensions'])
#
#             # 2.3 生成雷达图
#             log_callback("创建雷达图...")
#             chart_filename = generate_filename("radar_chart", user_name)
#             chart_path = os.path.join(assets_dir, chart_filename)
#
#             # 假设您的雷达图生成函数是 generate_radar_chart
#             generated_path = generate_radar_chart(radar_data, chart_path)
#             log_callback(f"雷达图已保存: {generated_path}")
#
#             # 嵌入图片为Base64
#             with open(generated_path, "rb") as image_file:
#                 encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#             chart_base64 = f"data:image/png;base64,{encoded_string}"
#
#
#             # 2.5 生成PDF报告
#             log_callback("生成PDF报告...")
#             report_filename = generate_filename("2025年5月管培生管理潜质测评", user_name, extension="pdf",
#                                                 with_timestamp=False)
#             report_path = os.path.join(output_dir, report_filename)
#             # 调用PDF生成函数 - 传入base_dir
#             generate_pdf_report(report_data, report_path, base_dir, chart_base64)
#             log_callback(f"报告已生成: {report_path}")
#
#             successful_reports += 1
#
#         except Exception as e:
#             error_msg = f"生成 {user_name} 的报告时出错: {str(e)}"
#             log_callback(error_msg)
#             failed_users.append(user_name)
#
#     # 完成所有报告
#     completion_message = f"报告生成完成: {successful_reports}份成功"
#     if failed_users:
#         completion_message += f", {len(failed_users)}份失败 ({', '.join(failed_users)})"
#
#     progress_callback(100, completion_message)
#     log_callback(f"\n{completion_message}")