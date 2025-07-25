import React, { useEffect, useState } from 'react';
import { Card, Tabs, Select, Table, Spin, message, Button, Space, AutoComplete, InputNumber, Form } from 'antd';
import type { TabsProps } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import * as XLSX from 'xlsx';
import { apiService } from '../../utils/api';

interface ScoreDetail {
    name: string;
    score: number;
    sub_dimensions?: ScoreDetail[];
}

interface UserResult {
    user_id: number;
    user_name: string;
    total_score: number;
    big_dimensions: ScoreDetail[];
}

interface PaperResult {
    paper_id: number;
    paper_name: string;
    total_score: number;
    big_dimensions: ScoreDetail[];
}

interface PaperOption {
    label: string;
    value: number;
}

interface UserOption {
    label: string;
    value: number;
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

const ResultManagement: React.FC = () => {
    // 试卷/被试者下拉
    const [paperOptions, setPaperOptions] = useState<PaperOption[]>([]);
    const [userOptions, setUserOptions] = useState<UserOption[]>([]);
    // 当前选择
    const [selectedPaper, setSelectedPaper] = useState<number | undefined>();
    const [selectedUser, setSelectedUser] = useState<number | undefined>();
    // 数据
    const [byPaperData, setByPaperData] = useState<UserResult[]>([]);
    const [byUserData, setByUserData] = useState<PaperResult[]>([]);
    // 加载状态
    const [loading, setLoading] = useState(false);
    const [byPaperFilterForm] = Form.useForm();
    const [byUserFilterForm] = Form.useForm();

    // 获取token
    const token = localStorage.getItem('token') || '';

    // 获取试卷列表
    useEffect(() => {
        apiService.getList('/papers')
            .then(res => {
                console.log('试卷列表:', res);
                setPaperOptions(res.map((p: any) => ({ label: p.name, value: p.id })));
            }).catch(err => {
                console.error('获取试卷列表失败:', err);
                message.error('获取试卷列表失败');
            });

        apiService.getList('/users')
            .then(res => {
                console.log('用户列表:', res);
                const participants = res.filter((u: any) => u.role === 'participant');
                console.log('被试者列表:', participants);
                setUserOptions(participants.map((u: any) => ({
                    label: u.real_name || u.username,
                    value: u.id
                })));
            }).catch(err => {
                console.error('获取用户列表失败:', err);
                message.error('获取用户列表失败');
            });
    }, [token]);

    // 按试卷筛选
    const handleByPaperFilter = (values: any) => {
        if (selectedPaper) {
            fetchByPaper(selectedPaper, values);
        }
    };
    // 按被试者筛选
    const handleByUserFilter = (values: any) => {
        if (selectedUser) {
            fetchByUser(selectedUser, values);
        }
    };

    // 按试卷查
    const fetchByPaper = (paperId: number, filters?: any) => {
        console.log('fetchByPaper 调用，paperId:', paperId, typeof paperId);
        setLoading(true);
        const params: any = { paper_id: paperId };
        if (filters) {
            if (filters.position) params.position = filters.position;
            if (filters.age_min !== undefined && filters.age_min !== null) params.age_min = filters.age_min;
            if (filters.age_max !== undefined && filters.age_max !== null) params.age_max = filters.age_max;
        }
        apiService.getList('/results/by-paper', params)
            .then(res => {
                console.log('按试卷查询结果:', res);
                setByPaperData(res);
            })
            .catch((err) => {
                console.error('按试卷查询失败:', err);
                message.error(`获取数据失败: ${err.response?.data?.detail || err.message}`);
            })
            .finally(() => setLoading(false));
    };

    // 按被试者查
    const fetchByUser = (userId: number, filters?: any) => {
        console.log('fetchByUser 调用，userId:', userId, typeof userId);
        // 确保 userId 是数字类型
        const numericUserId = Number(userId);
        if (isNaN(numericUserId)) {
            console.error('userId 不是有效数字:', userId);
            message.error('用户ID无效');
            return;
        }

        setLoading(true);
        const params: any = { user_id: numericUserId };
        if (filters) {
            if (filters.position) params.position = filters.position;
            if (filters.age_min !== undefined && filters.age_min !== null) params.age_min = filters.age_min;
            if (filters.age_max !== undefined && filters.age_max !== null) params.age_max = filters.age_max;
        }
        const url = '/results/by-user';
        console.log('请求URL:', url, '参数:', params);

        apiService.getList(url, params)
            .then(res => {
                console.log('按被试者查询结果:', res);
                setByUserData(res);
            })
            .catch((err) => {
                console.error('按被试者查询失败:', err);
                console.error('错误详情:', err.response?.data);
                message.error(`获取数据失败: ${err.response?.data?.detail || err.message}`);
            })
            .finally(() => setLoading(false));
    };

    // 维度分数表格生成
    const renderDimensionColumns = (bigDimensions: ScoreDetail[]) => {
        // 动态生成所有大/小维度列
        const columns: any[] = [
            { title: '姓名', dataIndex: 'user_name', fixed: 'left', width: 120 },
            { title: '总分', dataIndex: 'total_score', width: 80 }
        ];
        bigDimensions.forEach(big => {
            if (big.sub_dimensions && big.sub_dimensions.length > 0) {
                big.sub_dimensions.forEach(sub => {
                    columns.push({
                        title: `${big.name} - ${sub.name}`,
                        dataIndex: `${big.name}_${sub.name}`,
                        width: 120
                    });
                });
                columns.push({
                    title: `${big.name}平均分`,
                    dataIndex: `${big.name}_avg`,
                    width: 100
                });
            } else {
                columns.push({ title: big.name, dataIndex: big.name, width: 120 });
            }
        });
        return columns;
    };

    // 按试卷表格数据
    const getByPaperTableData = () => {
        if (!byPaperData.length) return [];
        return byPaperData.map(user => {
            const row: any = {
                user_name: user.user_name,
                total_score: user.total_score
            };
            user.big_dimensions.forEach(big => {
                if (big.sub_dimensions && big.sub_dimensions.length > 0) {
                    big.sub_dimensions.forEach(sub => {
                        row[`${big.name}_${sub.name}`] = sub.score;
                    });
                    row[`${big.name}_avg`] = big.score;
                } else {
                    row[big.name] = big.score;
                }
            });
            return row;
        });
    };

    // 按被试者表格数据
    const getByUserTableData = () => {
        if (!byUserData.length) return [];
        return byUserData.map(paper => {
            const row: any = {
                paper_name: paper.paper_name,
                total_score: paper.total_score
            };
            paper.big_dimensions.forEach(big => {
                if (big.sub_dimensions && big.sub_dimensions.length > 0) {
                    big.sub_dimensions.forEach(sub => {
                        row[`${big.name}_${sub.name}`] = sub.score;
                    });
                    row[`${big.name}_avg`] = big.score;
                } else {
                    row[big.name] = big.score;
                }
            });
            return row;
        });
    };

    // 按被试者表格列
    const renderUserColumns = (bigDimensions: ScoreDetail[]) => {
        const columns: any[] = [
            { title: '试卷', dataIndex: 'paper_name', fixed: 'left', width: 120 },
            { title: '总分', dataIndex: 'total_score', width: 80 }
        ];
        bigDimensions.forEach(big => {
            if (big.sub_dimensions && big.sub_dimensions.length > 0) {
                big.sub_dimensions.forEach(sub => {
                    columns.push({
                        title: `${big.name} - ${sub.name}`,
                        dataIndex: `${big.name}_${sub.name}`,
                        width: 120
                    });
                });
                columns.push({
                    title: `${big.name}平均分`,
                    dataIndex: `${big.name}_avg`,
                    width: 100
                });
            } else {
                columns.push({ title: big.name, dataIndex: big.name, width: 120 });
            }
        });
        return columns;
    };

    // 导出Excel功能
    const exportToExcel = (data: any[], filename: string) => {
        try {
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
            XLSX.writeFile(wb, `${filename}.xlsx`);
            message.success('Excel文件导出成功');
        } catch (error) {
            console.error('导出Excel失败:', error);
            message.error('导出Excel失败');
        }
    };

    // 导出按试卷数据
    const handleExportByPaper = () => {
        if (!byPaperData.length) {
            message.warning('没有数据可导出');
            return;
        }

        const exportData = getByPaperTableData();
        const paperName = paperOptions.find(p => p.value === selectedPaper)?.label || '试卷';
        exportToExcel(exportData, `${paperName}_测试结果`);
    };

    // 导出按被试者数据
    const handleExportByUser = () => {
        if (!byUserData.length) {
            message.warning('没有数据可导出');
            return;
        }

        const exportData = getByUserTableData();
        const userName = userOptions.find(u => u.value === selectedUser)?.label || '被试者';
        exportToExcel(exportData, `${userName}_测试结果`);
    };

    const items: TabsProps['items'] = [
        {
            key: 'by-paper',
            label: '按试卷查看',
            children: (
                <Card>
                    {/* 新增：岗位、年龄筛选表单 */}
                    <Form
                        form={byPaperFilterForm}
                        layout="inline"
                        onFinish={handleByPaperFilter}
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
                            <Button onClick={() => { byPaperFilterForm.resetFields(); if (selectedPaper) fetchByPaper(selectedPaper); }}>重置</Button>
                        </Form.Item>
                    </Form>
                    <div style={{ marginBottom: 16 }}>
                        <Space>
                            <Select
                                showSearch
                                allowClear
                                style={{ width: 300 }}
                                placeholder="请选择试卷"
                                options={paperOptions}
                                value={selectedPaper}
                                onChange={v => {
                                    console.log('Paper Select onChange, value:', v, typeof v);
                                    setSelectedPaper(v);
                                    if (v !== undefined && v !== null) {
                                        fetchByPaper(v);
                                    }
                                    setByPaperData([]);
                                }}
                            />
                            {byPaperData.length > 0 && (
                                <Button
                                    type="primary"
                                    icon={<DownloadOutlined />}
                                    onClick={handleExportByPaper}
                                >
                                    导出Excel
                                </Button>
                            )}
                        </Space>
                    </div>
                    <Spin spinning={loading}>
                        {byPaperData.length > 0 ? (
                            <Table
                                columns={renderDimensionColumns(byPaperData[0].big_dimensions)}
                                dataSource={getByPaperTableData()}
                                rowKey={(_, idx) => idx?.toString() || ''}
                                scroll={{ x: 1200 }}
                                bordered
                            />
                        ) : <div>请选择试卷后查看结果</div>}
                    </Spin>
                </Card>
            )
        },
        {
            key: 'by-user',
            label: '按被试者查看',
            children: (
                <Card>
                    {/* 新增：岗位、年龄筛选表单 */}
                    <Form
                        form={byUserFilterForm}
                        layout="inline"
                        onFinish={handleByUserFilter}
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
                            <Button onClick={() => { byUserFilterForm.resetFields(); if (selectedUser) fetchByUser(selectedUser); }}>重置</Button>
                        </Form.Item>
                    </Form>
                    <div style={{ marginBottom: 16 }}>
                        <Space>
                            <Select
                                showSearch
                                allowClear
                                style={{ width: 300 }}
                                placeholder="请选择被试者"
                                options={userOptions}
                                value={selectedUser}
                                onChange={v => {
                                    console.log('Select onChange, value:', v, typeof v);
                                    setSelectedUser(v);
                                    if (v !== undefined && v !== null) {
                                        fetchByUser(v);
                                    }
                                    setByUserData([]);
                                }}
                            />
                            {byUserData.length > 0 && (
                                <Button
                                    type="primary"
                                    icon={<DownloadOutlined />}
                                    onClick={handleExportByUser}
                                >
                                    导出Excel
                                </Button>
                            )}
                        </Space>
                    </div>
                    <Spin spinning={loading}>
                        {byUserData.length > 0 ? (
                            <Table
                                columns={renderUserColumns(byUserData[0].big_dimensions)}
                                dataSource={getByUserTableData()}
                                rowKey={(_, idx) => idx?.toString() || ''}
                                scroll={{ x: 1200 }}
                                bordered
                            />
                        ) : <div>请选择被试者后查看结果</div>}
                    </Spin>
                </Card>
            )
        }
    ];

    return (
        <div>
            <h2 style={{ marginBottom: 24 }}>测试结果</h2>
            <Tabs items={items} />
        </div>
    );
};

export default ResultManagement; 