import { useState, useEffect } from 'react'
import { Card, Table, Button, Tag, message } from 'antd'
import { DownloadOutlined, EyeOutlined } from '@ant-design/icons'

interface ReportData {
    id: number
    title: string
    status: 'pending' | 'generated' | 'failed'
    created_at: string
    score?: number
}

const Report = () => {
    const [reports, setReports] = useState<ReportData[]>([])

    // 模拟数据
    useEffect(() => {
        setReports([
            {
                id: 1,
                title: '商业推理能力测评报告',
                status: 'generated',
                created_at: '2024-01-15 10:30:00',
                score: 85
            },
            {
                id: 2,
                title: '管理能力测评报告',
                status: 'pending',
                created_at: '2024-01-16 14:20:00'
            }
        ])
    }, [])

    const columns = [
        {
            title: '报告标题',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    pending: { color: 'orange', text: '生成中' },
                    generated: { color: 'green', text: '已完成' },
                    failed: { color: 'red', text: '生成失败' }
                }
                const { color, text } = statusMap[status as keyof typeof statusMap]
                return <Tag color={color}>{text}</Tag>
            }
        },
        {
            title: '得分',
            dataIndex: 'score',
            key: 'score',
            render: (score?: number) => score ? `${score}分` : '-'
        },
        {
            title: '生成时间',
            dataIndex: 'created_at',
            key: 'created_at',
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: ReportData) => (
                <div>
                    {record.status === 'generated' && (
                        <>
                            <Button
                                type="link"
                                icon={<EyeOutlined />}
                                onClick={() => handlePreview(record)}
                            >
                                预览
                            </Button>
                            <Button
                                type="link"
                                icon={<DownloadOutlined />}
                                onClick={() => handleDownload(record)}
                            >
                                下载
                            </Button>
                        </>
                    )}
                    {record.status === 'failed' && (
                        <Button
                            type="link"
                            onClick={() => handleRegenerate(record)}
                        >
                            重新生成
                        </Button>
                    )}
                </div>
            )
        }
    ]

    const handlePreview = (report: ReportData) => {
        message.info('预览功能待实现')
    }

    const handleDownload = (report: ReportData) => {
        message.info('下载功能待实现')
    }

    const handleRegenerate = (report: ReportData) => {
        message.info('重新生成功能待实现')
    }

    return (
        <Card title="我的报告">
            <Table
                columns={columns}
                dataSource={reports}
                rowKey="id"
                pagination={false}
            />
        </Card>
    )
}

export default Report 