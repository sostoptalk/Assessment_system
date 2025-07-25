import React, { useState, useEffect } from 'react';
import {
    Card,
    Select,
    Table,
    Button,
    Space,
    message,
    Checkbox,
    Spin,
    Modal,
    Progress,
    Tag,
    Pagination,
    Input,
    DatePicker,
    Row,
    Col,
    Popconfirm,
    Tooltip,
    AutoComplete,
    InputNumber,
    Form
} from 'antd';
import {
    DownloadOutlined,
    FileTextOutlined,
    CheckOutlined,
    CloseOutlined,
    DeleteOutlined,
    SearchOutlined,
    ReloadOutlined,
    EyeOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';
import { apiService } from '../../utils/api';

interface PaperOption {
    label: string;
    value: number;
}

interface UserOption {
    label: string;
    value: number;
    user_name: string;
}

interface ReportTask {
    id: string;
    user_id: number;
    user_name: string;
    paper_id: number;
    paper_name: string;
    status: 'pending' | 'generating' | 'completed' | 'failed';
    progress: number;
    file_path?: string;
    error_message?: string;
    report_id?: number;
}

interface StoredReport {
    id: number;
    user_id: number;
    user_name: string;
    paper_id: number;
    paper_name: string;
    file_path: string;
    file_name: string;
    file_size?: number;
    status: string;
    error_message?: string;
    created_at: string;
}

// 岗位列表（可根据实际岗位补充）
const positionOptions = [
    '生产力促进部副总监',
    '经营管理主管',
    '副总裁兼广州分公司总经理',
    '董事长兼总裁',
    '咨询师',
    '招采项目经理',
    '见习咨询师',
    '数字化总监',
    '项目主管',
    '项目经理',
    '项目专员',
    '法务经理',
    '管培生',
    '审计专员',
    '财务主管',
    '运作支持主管',
    '新咨询发展研究院执行院长',
    '研发赋能专员',
    '法务专员',
    '双碳项目区域负责人',
    '组织发展主管',
    '法务主管',
    '数字化主管',
    '研发赋能主管',
    '总经理助理',
    '合约专员',
    '会计主管',
    '合约主管',
    '询价副经理',
    '品牌专员',
    'IT主管',
    '制度流程主管',
    '品牌经理',
    '招聘专员',
    '档案管理员',
    '会计',
    '办公室主任',
    'IT专员',
    '品牌主管',
    '薪酬绩效主管',
    '综合事务专员',
    '询价专员',
    '合同专员',
    '综合事务主管',
    '人力资源主管',
    '招聘主管',
    '培训主管',
    '文员',
    '司机',
    '资料员',
    '项目资料员',
    '行政专员',
    '行政主管',
    '人力资源部总监',
    '人力行政部经理',
    '人力资源专员',
    '人力行政主管',
    '人力资源部经理',
    '出纳',
    '财务经理',
    '财务专员',
    '保洁',
    '人力行政专员',
    '人力资源副经理',
    '市场部经理',
    '投标专员',
    '投标主管',
    '助理客户经理',
    '高级客户经理',
    '客户经理',
    '商务主管',
    '商务经理',
    '商务专员',
    '市场合约部经理',
    '质控专员',
    '质控副主任兼造价纠纷与法律服务部经理',
    '总工程师兼质控主任',
    '质控主任',
    '质控副主任',
    '质控主管',
    '部门主管',
    'BIM项目经理',
    'BIM工程师',
    '招采专员',
    '招采主管',
    '招采业务部经理',
    '高级造价主管',
    '造价纠纷调解经理',
    '鉴定经理',
    '副经理',
    '经理',
    '部门经理',
    '造价业务部经理',
    '实习生',
    '鉴定主管',
    '鉴定专员',
    '专业经理',
    '造价员',
    '造价主管',
    '数字化与AI创新总监',
    '承包商事业部总监',
    '副总裁兼政企决策与前期咨询事业中心总经理',
    '副总裁兼市场与营销中心总经理',
    '营销中心副总经理兼海南分公司营销负责人',
    '新咨询发展研究院副院长',
    '数字化事业部总监',
    '生产力促进中心副总监',
    '政企决策与前期咨询事业中心副总监',
    '技术总监',
    '（储备）副总经理',
    '成本顾问中心总经理',
    '副总裁',
    '全过程工程咨询事业部副总监',
    '数字化专业技术委员会主任',
    '东莞分公司总经理兼广州分公司常务副总经理',
    '人力资源部副总监',
    '造价纠纷与法律服务中心副总监',
    '副总经理兼东莞分公司常务副总经理（兼质控主任）',
    '常务副总经理',
    '商务总经理',
    '市场部总监',
    '法律咨询业务部总监',
    '造价纠纷与法律服务中心总经理',
    '运营管理中心总经理',
    '造价纠纷业务部总监',
    '政府决策与前期咨询事业中心总经理',
    '运营管理中心副总经理',
    '总监',
    '副总经理',
    '总经理',
    '总裁',
    '董事长',
    '常务副总裁',
    '副董事长',
    '城市公司发展和管理部副总监',
    '总工程师',
    '财务部总监',
];

const ReportManagement: React.FC = () => {
    const [paperOptions, setPaperOptions] = useState<PaperOption[]>([]);
    const [userOptions, setUserOptions] = useState<UserOption[]>([]);
    const [selectedPaper, setSelectedPaper] = useState<number | undefined>();
    const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
    const [allSelected, setAllSelected] = useState(false);
    const [reportTasks, setReportTasks] = useState<ReportTask[]>([]);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [showProgress, setShowProgress] = useState(false);

    // 报告存储相关状态
    const [storedReports, setStoredReports] = useState<StoredReport[]>([]);
    const [reportsLoading, setReportsLoading] = useState(false);
    const [selectedReports, setSelectedReports] = useState<number[]>([]);
    const [reportsPagination, setReportsPagination] = useState({
        current: 1,
        pageSize: 10,
        total: 0
    });
    const [searchParams, setSearchParams] = useState({
        user_id: undefined as number | undefined,
        paper_id: undefined as number | undefined,
        status: undefined as string | undefined
    });

    const [reportFilterForm] = Form.useForm();

    const token = localStorage.getItem('token') || '';

    // 获取试卷列表
    useEffect(() => {
        apiService.getList('/papers')
            .then(res => {
                setPaperOptions(res.map((p: any) => ({ label: p.name, value: p.id })));
            }).catch(err => {
                console.error('获取试卷列表失败:', err);
                message.error('获取试卷列表失败');
            });
    }, []);

    // 获取被试者列表
    useEffect(() => {
        apiService.getList('/users')
            .then(res => {
                const participants = res.filter((u: any) => u.role === 'participant');
                setUserOptions(participants.map((u: any) => ({
                    label: u.real_name || u.username,
                    value: u.id,
                    user_name: u.real_name || u.username
                })));
            }).catch(err => {
                console.error('获取用户列表失败:', err);
                message.error('获取用户列表失败');
            });
    }, []);

    // 当试卷改变时，获取该试卷的被试者
    useEffect(() => {
        if (selectedPaper) {
            setLoading(true);
            axios.get(`/api/papers/${selectedPaper}/list-assignment`, {
                headers: { Authorization: `Bearer ${token}` }
            }).then(res => {
                const completedUsers = res.data
                    .filter((assignment: any) => assignment.status === 'completed')
                    .map((assignment: any) => assignment.user_id);

                // 过滤出已完成该试卷的被试者
                const availableUsers = userOptions.filter(user =>
                    completedUsers.includes(user.value)
                );
                setUserOptions(availableUsers);
                setSelectedUsers([]);
                setAllSelected(false);
            }).catch(err => {
                console.error('获取试卷分配失败:', err);
                message.error('获取试卷分配失败');
            }).finally(() => setLoading(false));
        }
    }, [selectedPaper, token]);

    // 获取报告列表，支持筛选
    const fetchStoredReports = async (page = 1, pageSize = 10, filters?: any) => {
        setReportsLoading(true);
        try {
            const params: any = {
                page,
                page_size: pageSize,
                ...searchParams
            };
            if (filters) {
                if (filters.position) params.position = filters.position;
                if (filters.age_min !== undefined && filters.age_min !== null) params.age_min = filters.age_min;
                if (filters.age_max !== undefined && filters.age_max !== null) params.age_max = filters.age_max;
            }
            const response = await apiService.getList('/reports', params);
            setStoredReports(response.reports);
            setReportsPagination({
                current: response.page,
                pageSize: response.page_size,
                total: response.total
            });
        } catch (error) {
            console.error('获取报告列表失败:', error);
            message.error('获取报告列表失败');
        } finally {
            setReportsLoading(false);
        }
    };

    // 初始加载报告列表
    useEffect(() => {
        fetchStoredReports();
    }, [searchParams]);

    // 全选/取消全选
    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            setSelectedUsers(userOptions.map(u => u.value));
            setAllSelected(true);
        } else {
            setSelectedUsers([]);
            setAllSelected(false);
        }
    };

    // 单个选择
    const handleSelectUser = (userId: number, checked: boolean) => {
        if (checked) {
            setSelectedUsers([...selectedUsers, userId]);
        } else {
            setSelectedUsers(selectedUsers.filter(id => id !== userId));
        }
    };

    // 批量生成报告
    const handleBatchGenerate = async () => {
        if (!selectedPaper || selectedUsers.length === 0) {
            message.warning('请选择试卷和被试者');
            return;
        }

        const paperName = paperOptions.find(p => p.value === selectedPaper)?.label || '试卷';

        setShowProgress(true);
        setGenerating(true);

        try {
            // 调用后端API批量生成报告
            const response = await axios.post('/api/reports/batch-generate', {
                paper_id: selectedPaper,
                user_ids: selectedUsers
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.data.success) {
                message.success('报告生成任务已提交');

                // 使用后端返回的task_ids创建任务
                const backendTaskIds = response.data.task_ids;
                const tasks: ReportTask[] = backendTaskIds.map((taskId: string, index: number) => {
                    const userId = selectedUsers[index];
                    const user = userOptions.find(u => u.value === userId);
                    return {
                        id: taskId,
                        user_id: userId,
                        user_name: user?.user_name || '',
                        paper_id: selectedPaper,
                        paper_name: paperName,
                        status: 'pending',
                        progress: 0
                    };
                });

                setReportTasks(tasks);
                // 开始轮询任务状态
                pollReportStatus(tasks);
            } else {
                message.error(response.data.message || '报告生成失败');
                setGenerating(false);
            }
        } catch (error) {
            console.error('批量生成报告失败:', error);
            message.error('批量生成报告失败');
            setGenerating(false);
        }
    };

    // 轮询报告状态
    const pollReportStatus = (tasks: ReportTask[]) => {
        const interval = setInterval(async () => {
            try {
                console.log('轮询任务状态:', tasks.map(t => t.id));
                const response = await axios.get('/api/reports/status', {
                    params: { 'task_ids[]': tasks.map(t => t.id) },
                    headers: { Authorization: `Bearer ${token}` }
                });

                console.log('轮询响应:', response.data);
                const updatedTasks = tasks.map(task => {
                    const status = response.data[task.id];
                    if (status) {
                        return { ...task, ...status };
                    }
                    return task;
                });

                setReportTasks(updatedTasks);

                // 检查是否所有任务都完成
                const allCompleted = updatedTasks.every(task =>
                    task.status === 'completed' || task.status === 'failed'
                );

                if (allCompleted) {
                    clearInterval(interval);
                    setGenerating(false);
                    message.success('所有报告生成完成');
                    // 刷新报告列表
                    fetchStoredReports();
                }
            } catch (error) {
                console.error('获取报告状态失败:', error);
            }
        }, 2000); // 每2秒轮询一次
    };

    // 下载单个报告
    const handleDownloadReport = async (task: ReportTask) => {
        if (task.status !== 'completed' || !task.file_path) {
            message.warning('报告尚未生成完成');
            return;
        }

        try {
            const response = await axios.get(`/api/reports/download/${task.id}`, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${task.user_name}_${task.paper_name}_报告.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            message.success('报告下载成功');
        } catch (error) {
            console.error('下载报告失败:', error);
            message.error('下载报告失败');
        }
    };

    // 批量下载
    const handleBatchDownload = () => {
        const completedTasks = reportTasks.filter(task => task.status === 'completed');
        if (completedTasks.length === 0) {
            message.warning('没有可下载的报告');
            return;
        }

        completedTasks.forEach(task => {
            handleDownloadReport(task);
        });
    };

    // 下载存储的报告
    const handleDownloadStoredReport = async (report: StoredReport) => {
        try {
            const response = await axios.get(`/api/reports/${report.id}/download`, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', report.file_name);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            message.success('报告下载成功');
        } catch (error) {
            console.error('下载报告失败:', error);
            message.error('下载报告失败');
        }
    };

    // 删除单个报告
    const handleDeleteReport = async (reportId: number) => {
        try {
            await axios.delete(`/api/reports/${reportId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            message.success('报告删除成功');
            fetchStoredReports();
        } catch (error) {
            console.error('删除报告失败:', error);
            message.error('删除报告失败');
        }
    };

    // 批量删除报告
    const handleBatchDeleteReports = async () => {
        if (selectedReports.length === 0) {
            message.warning('请选择要删除的报告');
            return;
        }

        try {
            await axios.delete('/api/reports/batch', {
                data: { report_ids: selectedReports },
                headers: { Authorization: `Bearer ${token}` }
            });
            message.success('批量删除成功');
            setSelectedReports([]);
            fetchStoredReports();
        } catch (error) {
            console.error('批量删除失败:', error);
            message.error('批量删除失败');
        }
    };

    // 批量下载存储的报告
    const handleBatchDownloadStoredReports = async () => {
        if (selectedReports.length === 0) {
            message.warning('请选择要下载的报告');
            return;
        }

        try {
            const response = await axios.post('/api/reports/batch/download', selectedReports, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // 逐个下载报告
            for (const link of response.data.download_links) {
                const report = storedReports.find(r => r.id === link.report_id);
                if (report) {
                    handleDownloadStoredReport(report);
                }
            }

            message.success('批量下载已开始');
        } catch (error) {
            console.error('批量下载失败:', error);
            message.error('批量下载失败');
        }
    };

    // 筛选表单提交
    const handleReportFilter = (values: any) => {
        fetchStoredReports(1, reportsPagination.pageSize, values);
    };

    // 报告任务表格列
    const taskColumns = [
        {
            title: '被试者',
            dataIndex: 'user_name',
            key: 'user_name',
        },
        {
            title: '试卷',
            dataIndex: 'paper_name',
            key: 'paper_name',
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string, record: ReportTask) => {
                const statusMap = {
                    pending: { color: 'orange', text: '等待中' },
                    generating: { color: 'blue', text: '生成中' },
                    completed: { color: 'green', text: '已完成' },
                    failed: { color: 'red', text: '生成失败' }
                };
                const { color, text } = statusMap[status as keyof typeof statusMap];
                return <Tag color={color}>{text}</Tag>;
            }
        },
        {
            title: '进度',
            dataIndex: 'progress',
            key: 'progress',
            render: (progress: number, record: ReportTask) => {
                if (record.status === 'generating') {
                    return <Progress percent={progress} size="small" />;
                }
                return progress > 0 ? `${progress}%` : '-';
            }
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: ReportTask) => (
                <Space>
                    {record.status === 'completed' && (
                        <Button
                            type="link"
                            icon={<DownloadOutlined />}
                            onClick={() => handleDownloadReport(record)}
                        >
                            下载
                        </Button>
                    )}
                    {record.status === 'failed' && (
                        <span style={{ color: '#ff4d4f' }}>
                            {record.error_message || '生成失败'}
                        </span>
                    )}
                </Space>
            )
        }
    ];

    // 存储报告表格列
    const storedReportColumns = [
        {
            title: '选择',
            key: 'select',
            width: 60,
            render: (record: StoredReport) => (
                <Checkbox
                    checked={selectedReports.includes(record.id)}
                    onChange={(e) => {
                        if (e.target.checked) {
                            setSelectedReports([...selectedReports, record.id]);
                        } else {
                            setSelectedReports(selectedReports.filter(id => id !== record.id));
                        }
                    }}
                />
            )
        },
        {
            title: '被试者',
            dataIndex: 'user_name',
            key: 'user_name',
        },
        {
            title: '试卷',
            dataIndex: 'paper_name',
            key: 'paper_name',
        },
        {
            title: '文件名',
            dataIndex: 'file_name',
            key: 'file_name',
            ellipsis: true,
        },
        {
            title: '文件大小',
            dataIndex: 'file_size',
            key: 'file_size',
            render: (size: number) => {
                if (!size) return '-';
                const kb = size / 1024;
                const mb = kb / 1024;
                return mb > 1 ? `${mb.toFixed(1)}MB` : `${kb.toFixed(1)}KB`;
            }
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    completed: { color: 'green', text: '已完成' },
                    failed: { color: 'red', text: '生成失败' }
                };
                const { color, text } = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
                return <Tag color={color}>{text}</Tag>;
            }
        },
        {
            title: '生成时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
        },
        {
            title: '操作',
            key: 'action',
            width: 200,
            render: (record: StoredReport) => (
                <Space>
                    <Button
                        type="link"
                        icon={<DownloadOutlined />}
                        onClick={() => handleDownloadStoredReport(record)}
                        disabled={record.status !== 'completed'}
                    >
                        下载
                    </Button>
                    <Popconfirm
                        title="确定要删除这个报告吗？"
                        onConfirm={() => handleDeleteReport(record.id)}
                        okText="确定"
                        cancelText="取消"
                    >
                        <Button
                            type="link"
                            danger
                            icon={<DeleteOutlined />}
                        >
                            删除
                        </Button>
                    </Popconfirm>
                </Space>
            )
        }
    ];

    return (
        <div>
            <h2 style={{ marginBottom: 24 }}>报告管理</h2>

            {/* 试卷和被试者选择 */}
            <Card title="选择试卷和被试者" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                        <span style={{ marginRight: 8 }}>选择试卷：</span>
                        <Select
                            showSearch
                            allowClear
                            style={{ width: 300 }}
                            placeholder="请选择试卷"
                            options={paperOptions}
                            value={selectedPaper}
                            onChange={setSelectedPaper}
                            loading={loading}
                        />
                    </div>

                    {selectedPaper && (
                        <div>
                            <div style={{ marginBottom: 8 }}>
                                <Checkbox
                                    checked={allSelected}
                                    onChange={(e) => handleSelectAll(e.target.checked)}
                                    disabled={userOptions.length === 0}
                                >
                                    全选被试者 ({userOptions.length}人)
                                </Checkbox>
                            </div>
                            <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid #d9d9d9', padding: 8 }}>
                                {userOptions.map(user => (
                                    <div key={user.value} style={{ marginBottom: 4 }}>
                                        <Checkbox
                                            checked={selectedUsers.includes(user.value)}
                                            onChange={(e) => handleSelectUser(user.value, e.target.checked)}
                                        >
                                            {user.label}
                                        </Checkbox>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {selectedPaper && selectedUsers.length > 0 && (
                        <div>
                            <Button
                                type="primary"
                                icon={<FileTextOutlined />}
                                onClick={handleBatchGenerate}
                                loading={generating}
                            >
                                批量生成报告 ({selectedUsers.length}份)
                            </Button>
                        </div>
                    )}
                </Space>
            </Card>

            {/* 报告生成进度 */}
            {showProgress && (
                <Card title="报告生成进度" style={{ marginBottom: 16 }}>
                    <Table
                        columns={taskColumns}
                        dataSource={reportTasks}
                        rowKey="id"
                        pagination={false}
                        size="small"
                    />
                    {!generating && reportTasks.length > 0 && (
                        <div style={{ marginTop: 16 }}>
                            <Space>
                                <Button
                                    type="primary"
                                    icon={<DownloadOutlined />}
                                    onClick={handleBatchDownload}
                                >
                                    批量下载
                                </Button>
                                <Button onClick={() => setShowProgress(false)}>
                                    关闭
                                </Button>
                            </Space>
                        </div>
                    )}
                </Card>
            )}

            {/* 存储的报告列表 */}
            <Card
                title="已生成的报告"
                extra={
                    <Space>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={() => fetchStoredReports()}
                            loading={reportsLoading}
                        >
                            刷新
                        </Button>
                        <Button
                            type="primary"
                            icon={<DownloadOutlined />}
                            onClick={handleBatchDownloadStoredReports}
                            disabled={selectedReports.length === 0}
                        >
                            批量下载 ({selectedReports.length})
                        </Button>
                        <Popconfirm
                            title={`确定要删除选中的 ${selectedReports.length} 个报告吗？`}
                            onConfirm={handleBatchDeleteReports}
                            disabled={selectedReports.length === 0}
                            okText="确定"
                            cancelText="取消"
                        >
                            <Button
                                danger
                                icon={<DeleteOutlined />}
                                disabled={selectedReports.length === 0}
                            >
                                批量删除 ({selectedReports.length})
                            </Button>
                        </Popconfirm>
                    </Space>
                }
            >
                {/* 筛选条件 */}
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={6}>
                        <Select
                            placeholder="选择试卷"
                            allowClear
                            style={{ width: '100%' }}
                            options={paperOptions}
                            value={searchParams.paper_id}
                            onChange={(value) => setSearchParams({ ...searchParams, paper_id: value })}
                        />
                    </Col>
                    <Col span={6}>
                        <Select
                            placeholder="选择状态"
                            allowClear
                            style={{ width: '100%' }}
                            options={[
                                { label: '已完成', value: 'completed' },
                                { label: '生成失败', value: 'failed' }
                            ]}
                            value={searchParams.status}
                            onChange={(value) => setSearchParams({ ...searchParams, status: value })}
                        />
                    </Col>
                    <Col span={6}>
                        <Button
                            icon={<SearchOutlined />}
                            onClick={() => fetchStoredReports(1)}
                        >
                            搜索
                        </Button>
                    </Col>
                </Row>

                {/* 新增：岗位、年龄筛选表单 */}
                <Form
                    form={reportFilterForm}
                    layout="inline"
                    onFinish={handleReportFilter}
                    style={{ marginBottom: 16 }}
                >
                    <Form.Item label="岗位" name="position">
                        <AutoComplete
                            options={positionOptions.map(pos => ({ value: pos }))}
                            placeholder="请输入或选择岗位"
                            filterOption={(inputValue, option) =>
                                option!.value.toLowerCase().indexOf(inputValue.toLowerCase()) !== -1
                            }
                            allowClear
                            style={{ width: 180 }}
                        />
                    </Form.Item>
                    <Form.Item label="年龄" name="age_min">
                        <InputNumber min={0} max={120} placeholder="最小年龄" style={{ width: 100 }} />
                    </Form.Item>
                    <Form.Item label="-" colon={false} name="age_max">
                        <InputNumber min={0} max={120} placeholder="最大年龄" style={{ width: 100 }} />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit">筛选</Button>
                    </Form.Item>
                    <Form.Item>
                        <Button onClick={() => { reportFilterForm.resetFields(); fetchStoredReports(1, reportsPagination.pageSize); }}>重置</Button>
                    </Form.Item>
                </Form>

                <Table
                    columns={storedReportColumns}
                    dataSource={storedReports}
                    rowKey="id"
                    loading={reportsLoading}
                    pagination={{
                        current: reportsPagination.current,
                        pageSize: reportsPagination.pageSize,
                        total: reportsPagination.total,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                        onChange: (page, pageSize) => fetchStoredReports(page, pageSize)
                    }}
                />
            </Card>
        </div>
    );
};

export default ReportManagement; 