import matplotlib.pyplot as plt
import numpy as np


def generate_radar_chart(data, output_path="assets/radar_chart.png"):
    """生成雷达图并保存为文件"""
    try:
        # 确保输出目录存在
        from pathlib import Path
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 设置全局字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
        plt.rcParams['axes.unicode_minus'] = False

        # 创建白色背景
        fig = plt.figure(figsize=(10, 10), facecolor='white')
        fig.patch.set_alpha(1.0)  # 确保背景不透明

        ax = plt.subplot(111, polar=True, facecolor='white')
        ax.set_theta_direction(-1)  # 顺时针
        ax.set_theta_zero_location('N')  # 0度在上方
        ax.set_xticks([])
        ax.set_ylim(0, 18)  # 扩大范围以容纳更大的元素



        ax = plt.subplot(111, polar=True, facecolor='white')
        ax.set_theta_direction(-1)  # 顺时针
        ax.set_theta_zero_location('N')  # 0度在上方
        ax.set_xticks([])
        ax.set_ylim(0, 18)  # 扩大范围以容纳更大的元素

        # 数据预处理
        angles, scores, labels, colors = [], [], [], []
        for group in data:
            for dim in group["dims"]:
                angles.append(np.deg2rad(dim["angle"]))
                scores.append(dim["score"])
                labels.append(dim["name"])
                colors.append(group["color"])

        # 按角度排序
        sorted_indices = np.argsort(angles)
        angles = np.array(angles)[sorted_indices].tolist()
        scores = np.array(scores)[sorted_indices].tolist()
        labels = np.array(labels)[sorted_indices].tolist()
        colors = np.array(colors)[sorted_indices].tolist()

        # 蜘蛛网格线
        radii = np.arange(0, 11, 2)
        for r in radii:
            ax.plot(np.linspace(0, 2 * np.pi, 361), [r] * 361,
                    color="#DDDDDD", lw=0.8, zorder=1)

        # 添加维度点标记和虚线 ======================================
        for i in range(len(angles)):
            # 获取当前点的角度和分数
            angle = angles[i]
            score = scores[i]
            color = colors[i]

            # 绘制从中心到点的虚线
            ax.plot([0, angle], [0, 10],
                    linestyle='--',
                    color='#CCCCCC',
                    linewidth=1.0,
                    alpha=0.7,
                    zorder=1)

            # 在点上添加标记
            ax.plot(angle, score, 'o',
                    markersize=8,
                    markerfacecolor=color,
                    markeredgecolor='white',
                    markeredgewidth=1.5,
                    zorder=3)
        # =====================================================

        # 雷达图主体
        angles += angles[:1]
        scores += scores[:1]
        ax.plot(angles, scores, color='#8000FF', linewidth=2.5, zorder=5)  # 深紫色线条
        ax.fill(angles, scores, color='#8000FF', alpha=0.15, zorder=4)

        # 维度标签与分数显示
        for angle, score, label, color in zip(angles[:-1], scores[:-1], labels, colors):
            # 维度名称（移到外圈）
            text_radius = 13.5
            ax.text(angle, text_radius, label,
                    ha='center', va='center',
                    fontsize=12, color='#333333',
                    fontweight='bold', zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2",
                              ec=color,
                              fc='white',
                              alpha=0.8))

            # 分数标记
            marker_radius = 15.5
            ax.plot(angle, marker_radius, 'o',
                    markersize=32,
                    markerfacecolor=color,
                    markeredgecolor='white',
                    markeredgewidth=2.5,
                    zorder=7)

            ax.text(angle, marker_radius, f"{score:.1f}",
                    ha='center', va='center',
                    fontsize=16,
                    color='white',
                    fontweight='bold', zorder=8)

        # 象限背景色填充
        quadrant_params = [
            (0, 90, "#00CC0060"),  # 深绿色
            (90, 180, "#9900FF60"),  # 深紫色
            (180, 270, "#0066FF60"),  # 深蓝色
            (270, 360, "#FF333360")  # 深红色
        ]
        for start, end, color in quadrant_params:
            theta = np.linspace(np.deg2rad(start), np.deg2rad(end), 100)
            ax.fill_between(theta, 10.5, 16.5,  # 填充范围稍作调整
                            color=color, zorder=3)

        # 增强外部圆形轮廓
        ax.plot(np.linspace(0, 2 * np.pi, 361), [10] * 361,
                color="#666666", lw=1.5, zorder=2)

        # 圆弧文字函数
        def circular_text(ax, deg, radius, text, color, fontsize=16):
            rad = np.deg2rad(deg)
            if deg > 180:
                rotation = rad - np.pi / 2
                ha = 'right'
            else:
                rotation = rad + np.pi / 2
                ha = 'left'

            # 沿弧线排列文字
            ax.text(rad, radius, text,
                    fontsize=fontsize,
                    color=color,
                    fontweight='bold',
                    ha=ha,
                    va='center',
                    rotation_mode='anchor',
                    rotation=np.rad2deg(rotation),
                    zorder=8)

        # 象限标题（沿圆形排列，紧贴外圈）
        group_labels = [
            (45, "自我成长与发展", "#00CC00"),  # 深绿色
            (135, "管理动力", "#9900FF"),  # 深紫色
            (225, "管理事务", "#0066FF"),  # 深蓝色
            (315, "管理他人", "#FF3333")  # 深红色
        ]

        # 在雷达图最外圈圆形线外侧添加背景色环
        for deg in range(0, 360, 90):
            theta = np.linspace(np.deg2rad(deg), np.deg2rad(deg + 90), 100)
            # 确定当前象限对应的颜色
            quadrant_color = "#CCCCCC"
            if deg == 0:
                quadrant_color = "#00CC0020"
            elif deg == 90:
                quadrant_color = "#9900FF20"
            elif deg == 180:
                quadrant_color = "#0066FF20"
            elif deg == 270:
                quadrant_color = "#FF333320"

            ax.fill_between(theta, 10.0, 11.0,  # 紧贴10分圆圈的背景环
                            color=quadrant_color, zorder=3)

        # 标题文字位置
        title_radius = 18.8
        for deg, text, color in group_labels:
            # 添加轻微文字阴影增强可读性
            ax.text(np.deg2rad(deg), title_radius - 0.05, text,
                    fontsize=20,
                    color='white',
                    fontweight='bold',
                    ha='center',
                    va='center',
                    zorder=7,
                    alpha=0.5)

            # 添加主文字
            ax.text(np.deg2rad(deg), title_radius, text,
                    fontsize=20,
                    color=color,
                    fontweight='bold',
                    ha='center',
                    va='center',
                    zorder=8)

        # 刻度标签
        ax.set_yticks(radii)
        ax.set_yticklabels([str(int(x)) for x in radii],
                           color='#333333', fontsize=12)
        ax.tick_params(axis='y', pad=22)  # 刻度外移更多

        # 保存图像
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return output_path

    except Exception as e:
        print(f"生成雷达图时出错: {str(e)}")
        return None