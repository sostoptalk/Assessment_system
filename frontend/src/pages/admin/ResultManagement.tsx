import React, { useEffect, useState } from 'react';
import { Card, Tabs, Select, Table, Spin, message, Button, Space } from 'antd';
import type { TabsProps } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import * as XLSX from 'xlsx';

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

    // 获取token
    const token = localStorage.getItem('token') || '';

    // 获取试卷列表
    useEffect(() => {
        axios.get('/api/papers', {
            headers: { Authorization: `Bearer ${token}` }
        }).then(res => {
            console.log('试卷列表:', res.data);
            setPaperOptions(res.data.map((p: any) => ({ label: p.name, value: p.id })));
        }).catch(err => {
            console.error('获取试卷列表失败:', err);
            message.error('获取试卷列表失败');
        });

        axios.get('/api/users', {
            headers: { Authorization: `Bearer ${token}` }
        }).then(res => {
            console.log('用户列表:', res.data);
            const participants = res.data.filter((u: any) => u.role === 'participant');
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

    // 按试卷查
    const fetchByPaper = (paperId: number) => {
        console.log('fetchByPaper 调用，paperId:', paperId, typeof paperId);
        setLoading(true);
        axios.get('/api/results/by-paper', {
            params: { paper_id: paperId },
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => {
                console.log('按试卷查询结果:', res.data);
                setByPaperData(res.data);
            })
            .catch((err) => {
                console.error('按试卷查询失败:', err);
                message.error(`获取数据失败: ${err.response?.data?.detail || err.message}`);
            })
            .finally(() => setLoading(false));
    };

    // 按被试者查
    const fetchByUser = (userId: number) => {
        console.log('fetchByUser 调用，userId:', userId, typeof userId);
        // 确保 userId 是数字类型
        const numericUserId = Number(userId);
        if (isNaN(numericUserId)) {
            console.error('userId 不是有效数字:', userId);
            message.error('用户ID无效');
            return;
        }

        setLoading(true);
        const url = '/api/results/by-user';
        const params = { user_id: numericUserId };
        console.log('请求URL:', url, '参数:', params);

        axios.get(url, {
            params: params,
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => {
                console.log('按被试者查询结果:', res.data);
                setByUserData(res.data);
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