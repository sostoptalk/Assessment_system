import { Card, Row, Col, Statistic, Table, Spin, message, Button, Tabs, Select } from 'antd'
import { UserOutlined, QuestionCircleOutlined, FileTextOutlined, TrophyOutlined, ReloadOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { PieChart, Pie, Cell, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import ReactECharts from 'echarts-for-react'

interface DashboardStats {
    total_participants: number
    total_questions: number
    completed_reports: number
    avg_score: number
    total_papers: number // 新增字段
}

interface RecentAssessment {
    id: number
    name: string
    score: number
    date: string
    paper_name: string
}

const { TabPane } = Tabs
const { Option } = Select

const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null)
    const [recentAssessments, setRecentAssessments] = useState<RecentAssessment[]>([])
    const [loading, setLoading] = useState(true)
    const [statsLoading, setStatsLoading] = useState(true)
    const [assessmentsLoading, setAssessmentsLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
    const [chartType, setChartType] = useState<'pie' | 'radar'>('pie')
    const [paperList, setPaperList] = useState<{ paper_id: number, paper_name: string }[]>([])
    const [selectedPaperId, setSelectedPaperId] = useState<number | null>(null)
    const [pieData, setPieData] = useState<any[]>([])
    const [radarData, setRadarData] = useState<any[]>([])
    const [pieLoading, setPieLoading] = useState(false)
    const [radarLoading, setRadarLoading] = useState(false)
    // 新增：雷达图分组数据
    const [radarGroupData, setRadarGroupData] = useState<any>(null)

    // 获取统计数据
    const fetchStats = async () => {
        try {
            setStatsLoading(true)
            const response = await fetch('http://localhost:8000/dashboard/stats', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setStats(data)
            } else {
                message.error('获取统计数据失败')
            }
        } catch (error) {
            console.error('获取统计数据错误:', error)
            message.error('获取统计数据失败')
        } finally {
            setStatsLoading(false)
        }
    }

    // 获取最近测评数据
    const fetchRecentAssessments = async () => {
        try {
            setAssessmentsLoading(true)
            const response = await fetch('http://localhost:8000/dashboard/recent-assessments?limit=10', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setRecentAssessments(data)
            } else {
                message.error('获取最近测评数据失败')
            }
        } catch (error) {
            console.error('获取最近测评数据错误:', error)
            message.error('获取最近测评数据失败')
        } finally {
            setAssessmentsLoading(false)
        }
    }

    // 获取试卷完成量（饼图数据）
    const fetchPieData = async () => {
        setPieLoading(true)
        try {
            const res = await fetch('http://localhost:8000/dashboard/paper-completion', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            })
            if (res.ok) {
                const data = await res.json()
                setPieData(data)
                setPaperList(data.map((item: any) => ({ paper_id: item.paper_id, paper_name: item.paper_name })))
                if (data.length > 0 && selectedPaperId === null) {
                    setSelectedPaperId(data[0].paper_id)
                }
            }
        } finally {
            setPieLoading(false)
        }
    }

    // 获取雷达图数据
    const fetchRadarData = async (paperId: number) => {
        setRadarLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/dashboard/paper-dimension-avg?paper_id=${paperId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            })
            if (res.ok) {
                const data = await res.json()
                setRadarData(data)
            } else {
                setRadarData([])
            }
        } finally {
            setRadarLoading(false)
        }
    }

    // 获取分组雷达图数据
    const fetchRadarGroupData = async (paperId: number) => {
        setRadarLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/dashboard/paper-dimension-avg-grouped?paper_id=${paperId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            })
            if (res.ok) {
                const data = await res.json()
                setRadarGroupData(data)
            } else {
                setRadarGroupData(null)
            }
        } finally {
            setRadarLoading(false)
        }
    }

    // 刷新所有数据
    const refreshData = async () => {
        setRefreshing(true)
        try {
            await Promise.all([fetchStats(), fetchRecentAssessments()])
            setLastUpdate(new Date())
            message.success('数据刷新成功')
        } catch (error) {
            message.error('数据刷新失败')
        } finally {
            setRefreshing(false)
        }
    }

    // 组件加载时获取数据
    useEffect(() => {
        const loadData = async () => {
            setLoading(true)
            await Promise.all([fetchStats(), fetchRecentAssessments()])
            setLastUpdate(new Date())
            setLoading(false)
        }

        loadData()

        // 设置自动刷新，每30秒刷新一次
        const interval = setInterval(() => {
            fetchStats()
            fetchRecentAssessments()
            setLastUpdate(new Date())
        }, 30000)

        // 清理定时器
        return () => clearInterval(interval)
    }, [])

    // 初始化加载饼图数据
    useEffect(() => {
        fetchPieData()
    }, [])

    // 切换试卷时加载雷达图数据
    useEffect(() => {
        if (chartType === 'radar' && selectedPaperId) {
            fetchRadarGroupData(selectedPaperId)
        }
    }, [chartType, selectedPaperId])

    // 切换Tab时自动加载雷达图
    const handleTabChange = (key: string) => {
        setChartType(key as 'pie' | 'radar')
        if (key === 'radar' && selectedPaperId) {
            fetchRadarGroupData(selectedPaperId)
        }
    }

    // 切换试卷
    const handlePaperChange = (value: number) => {
        setSelectedPaperId(value)
        if (chartType === 'radar') {
            fetchRadarGroupData(value)
        }
    }

    // 饼图颜色
    const pieColors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#bfbfbf']

    // 统计卡片数据
    const statsData = stats ? [
        { title: '总被试者数', value: stats.total_participants, icon: <UserOutlined />, color: '#1890ff' },
        { title: '题库题目数', value: stats.total_questions, icon: <QuestionCircleOutlined />, color: '#52c41a' },
        { title: '已生成报告', value: stats.completed_reports, icon: <FileTextOutlined />, color: '#faad14' },
        { title: '试卷数量', value: stats.total_papers, icon: <TrophyOutlined />, color: '#f5222d' } // 替换为试卷数量
    ] : []

    // 饼图数据处理：将每个试卷拆分为“已完成”和“未完成”两块
    const getPieChartData = () => {
        if (!selectedPaperId || !pieData.length) return []
        const paper = pieData.find((p: any) => p.paper_id === selectedPaperId)
        if (!paper) return []
        return [
            { name: '已完成', value: paper.completed_count },
            { name: '未完成', value: Math.max(0, paper.assigned_count - paper.completed_count) }
        ]
    }

    // 生成ECharts雷达图option
    const getRadarOption = () => {
        if (!radarGroupData || !radarGroupData.groups) return {}
        // 生成indicator和数据
        const indicators: any[] = []
        const data: number[] = []
        const groupColors = ['#1890ff', '#faad14', '#52c41a', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#bfbfbf']
        let colorMap: string[] = []
        let groupRanges: { start: number, end: number, color: string, name: string }[] = []
        let idx = 0
        radarGroupData.groups.forEach((group: any, gidx: number) => {
            const color = groupColors[gidx % groupColors.length]
            group.dimensions.forEach((dim: any) => {
                indicators.push({ name: dim.dimension_name, max: 10 })
                data.push(dim.avg_score)
                colorMap.push(color)
            })
            groupRanges.push({ start: idx, end: idx + group.dimensions.length - 1, color, name: group.group_name })
            idx += group.dimensions.length
        })
        // 生成分区区域色块
        const splitAreaColors = colorMap
        return {
            tooltip: { trigger: 'item' },
            radar: {
                indicator: indicators,
                splitNumber: 5,
                radius: '75%',
                axisName: { color: '#333', fontSize: 14 },
                splitArea: {
                    show: true,
                    areaStyle: {
                        color: ['#fff'] // 保持背景白色
                    }
                },
                splitLine: { lineStyle: { color: '#eee' } },
                axisLine: { lineStyle: { color: '#aaa' } }
            },
            series: [{
                type: 'radar',
                data: [
                    {
                        value: data,
                        name: '平均分',
                        symbol: 'circle',
                        symbolSize: 10,
                        lineStyle: { color: '#8884d8', width: 2 },
                        areaStyle: { color: 'rgba(136,132,216,0.2)' },
                        itemStyle: {
                            color: function (params: any) { return colorMap[params.dataIndex] }
                        },
                        label: {
                            show: true,
                            formatter: function (params: any) { return params.value },
                            color: '#222',
                            fontWeight: 'bold',
                            fontSize: 14
                        }
                    }
                ]
            }],
            // 用 graphic 绘制分组标题
            graphic: groupRanges.map((gr, i) => {
                // 计算每组中心角度
                const total = indicators.length
                const mid = (gr.start + gr.end) / 2
                const angle = (360 / total) * mid - 90
                return {
                    type: 'text',
                    left: '50%',
                    top: '50%',
                    style: {
                        text: gr.name,
                        fill: gr.color,
                        font: 'bold 16px sans-serif',
                        textAlign: 'center',
                        textVerticalAlign: 'middle'
                    },
                    rotation: angle * Math.PI / 180,
                    position: [180 * Math.cos(angle * Math.PI / 180), 180 * Math.sin(angle * Math.PI / 180)]
                }
            })
        }
    }

    const columns = [
        {
            title: '被试者',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: '试卷',
            dataIndex: 'paper_name',
            key: 'paper_name',
        },
        {
            title: '平均得分', // 修改标题
            dataIndex: 'score',
            key: 'score',
            render: (score: number) => `${score}分` // 直接显示后端score
        },
        {
            title: '测评时间',
            dataIndex: 'date',
            key: 'date',
        }
    ]

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>加载中...</div>
            </div>
        )
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h2>仪表盘</h2>
                    {lastUpdate && (
                        <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                            最后更新: {lastUpdate.toLocaleString('zh-CN')}
                        </div>
                    )}
                </div>
                <Button
                    type="primary"
                    icon={<ReloadOutlined />}
                    onClick={refreshData}
                    loading={refreshing}
                >
                    刷新数据
                </Button>
            </div>

            {/* 统计卡片 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                {statsData.map((stat, index) => (
                    <Col span={6} key={index}>
                        <Card>
                            <Statistic
                                title={stat.title}
                                value={stat.value}
                                prefix={stat.icon}
                                valueStyle={{ color: stat.color }}
                                loading={statsLoading}
                            />
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* 统计图表 */}
            <Card title="数据概览" style={{ marginBottom: 24 }}>
                <Tabs activeKey={chartType} onChange={handleTabChange}>
                    <TabPane tab="试卷完成情况" key="pie">
                        <div style={{ marginBottom: 16 }}>
                            <span>选择试卷：</span>
                            <Select
                                style={{ width: 200 }}
                                value={selectedPaperId ?? undefined}
                                onChange={handlePaperChange}
                                options={paperList.map(p => ({ value: p.paper_id, label: p.paper_name }))}
                            />
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={getPieChartData()}
                                    dataKey="value"
                                    nameKey="name"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    label={entry => `${entry.name}: ${entry.value}`}
                                    isAnimationActive
                                >
                                    {getPieChartData().map((entry, idx) => (
                                        <Cell key={`cell-${idx}`} fill={pieColors[idx % pieColors.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </TabPane>
                    <TabPane tab="各维度平均分" key="radar">
                        <div style={{ marginBottom: 16 }}>
                            <span>选择试卷：</span>
                            <Select
                                style={{ width: 200 }}
                                value={selectedPaperId ?? undefined}
                                onChange={handlePaperChange}
                                options={paperList.map(p => ({ value: p.paper_id, label: p.paper_name }))}
                            />
                        </div>
                        <div style={{ width: '100%', height: 500 }}>
                            <ReactECharts option={getRadarOption()} style={{ height: 500 }} />
                        </div>
                    </TabPane>
                </Tabs>
            </Card>

            {/* 最近测评 */}
            <Card title="最近测评">
                <Table
                    columns={columns}
                    dataSource={recentAssessments}
                    rowKey="id"
                    pagination={false}
                    size="small"
                    loading={assessmentsLoading}
                    locale={{
                        emptyText: (
                            <div style={{ padding: '40px 0', textAlign: 'center' }}>
                                <div style={{ fontSize: '16px', color: '#666', marginBottom: '8px' }}>
                                    暂无测评数据
                                </div>
                                <div style={{ fontSize: '14px', color: '#999' }}>
                                    当有被试者完成测评后，数据将显示在这里
                                </div>
                            </div>
                        )
                    }}
                />
            </Card>
        </div>
    )
}

export default Dashboard 