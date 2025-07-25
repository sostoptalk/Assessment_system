import React, { useState, useEffect } from 'react';
import {
    Table,
    Button,
    Modal,
    Form,
    Input,
    Space,
    Popconfirm,
    message,
    Tag,
    Card,
    Switch,
    Upload,
    Alert,
    AutoComplete,
    InputNumber
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    UploadOutlined,
    DownloadOutlined
} from '@ant-design/icons';
import { apiService } from '../../utils/api';

interface Participant {
    id: number;
    username: string;
    real_name: string;
    email?: string;
    phone?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

const ParticipantManagement: React.FC = () => {
    const [participants, setParticipants] = useState<Participant[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingParticipant, setEditingParticipant] = useState<Participant | null>(null);
    const [form] = Form.useForm();
    const [importLoading, setImportLoading] = useState(false);
    const [importResult, setImportResult] = useState<any>(null);

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
    ]

    const [filterForm] = Form.useForm();

    // 获取被试者列表，支持筛选
    const fetchParticipants = async (filters?: any) => {
        setLoading(true);
        try {
            const params: any = {};
            if (filters) {
                if (filters.position) params.position = filters.position;
                if (filters.age_min !== undefined && filters.age_min !== null) params.age_min = filters.age_min;
                if (filters.age_max !== undefined && filters.age_max !== null) params.age_max = filters.age_max;
            }
            const data = await apiService.getList('/participants', params);
            setParticipants(data);
        } catch (error) {
            message.error('网络错误');
        } finally {
            setLoading(false);
        }
    };

    // 创建或更新被试者
    const handleSubmit = async (values: any) => {
        try {
            if (editingParticipant) {
                // 更新被试者
                await apiService.update('/participants', editingParticipant.id, values);
                message.success('被试者更新成功');
                setModalVisible(false);
                setEditingParticipant(null);
                form.resetFields();
                fetchParticipants();
            } else {
                // 创建被试者
                await apiService.create('/participants', values);
                message.success('被试者创建成功');
                setModalVisible(false);
                form.resetFields();
                fetchParticipants();
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 删除被试者
    const handleDelete = async (id: number) => {
        try {
            await apiService.delete('/participants', id);
            message.success('删除成功');
            fetchParticipants();
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 从Excel导入被试者
    const handleImportFromExcel = async (file: File) => {
        setImportLoading(true);
        setImportResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/participants/import_excel', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                setImportResult(result);
                message.success(result.msg);
                fetchParticipants();
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '导入失败');
            }
        } catch (error) {
            message.error('网络错误');
        } finally {
            setImportLoading(false);
        }
    };

    // 下载Excel模板
    const downloadTemplate = () => {
        const template = [
            {
                username: 'user001',
                password: 'password123',
                real_name: '张三',
                email: 'zhangsan@example.com',
                phone: '13800138001',
                is_active: true
            },
            {
                username: 'user002',
                password: 'password123',
                real_name: '李四',
                email: 'lisi@example.com',
                phone: '13800138002',
                is_active: true
            }
        ];

        const csvContent = [
            'username,password,real_name,email,phone,is_active',
            ...template.map(row =>
                `${row.username},${row.password},${row.real_name},${row.email || ''},${row.phone || ''},${row.is_active}`
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', '被试者导入模板.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // 筛选表单提交
    const handleFilter = (values: any) => {
        fetchParticipants(values);
    };

    useEffect(() => {
        fetchParticipants();
    }, []);

    const columns = [
        {
            title: '用户名',
            dataIndex: 'username',
            key: 'username',
        },
        {
            title: '真实姓名',
            dataIndex: 'real_name',
            key: 'real_name',
        },
        {
            title: '邮箱',
            dataIndex: 'email',
            key: 'email',
            render: (email: string) => email || '-',
        },
        {
            title: '电话',
            dataIndex: 'phone',
            key: 'phone',
            render: (phone: string) => phone || '-',
        },
        {
            title: '状态',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (isActive: boolean) => (
                <Tag color={isActive ? 'success' : 'error'}>
                    {isActive ? '激活' : '禁用'}
                </Tag>
            ),
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => new Date(date).toLocaleString(),
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: Participant) => (
                <Space size="middle">
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => {
                            setEditingParticipant(record);
                            form.setFieldsValue({
                                username: record.username,
                                real_name: record.real_name,
                                email: record.email,
                                phone: record.phone,
                                is_active: record.is_active
                            });
                            setModalVisible(true);
                        }}
                    >
                        编辑
                    </Button>
                    <Popconfirm
                        title="确定要删除这个被试者吗？"
                        onConfirm={() => handleDelete(record.id)}
                        okText="确定"
                        cancelText="取消"
                    >
                        <Button type="link" danger icon={<DeleteOutlined />}>
                            删除
                        </Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <Card title="被试者管理" extra={
                <Space>
                    <Button
                        icon={<DownloadOutlined />}
                        onClick={downloadTemplate}
                    >
                        下载模板
                    </Button>
                    <Upload
                        accept=".xlsx,.xls,.csv"
                        showUploadList={false}
                        beforeUpload={(file) => {
                            handleImportFromExcel(file);
                            return false;
                        }}
                    >
                        <Button
                            icon={<UploadOutlined />}
                            loading={importLoading}
                        >
                            批量导入
                        </Button>
                    </Upload>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => {
                            setEditingParticipant(null);
                            form.resetFields();
                            setModalVisible(true);
                        }}
                    >
                        添加被试者
                    </Button>
                </Space>
            }>
                {/* 新增：筛选表单 */}
                <Form
                    form={filterForm}
                    layout="inline"
                    onFinish={handleFilter}
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
                        <Button onClick={() => { filterForm.resetFields(); fetchParticipants(); }}>重置</Button>
                    </Form.Item>
                </Form>
                {/* 导入结果提示 */}
                {importResult && (
                    <Alert
                        message={`导入结果: ${importResult.msg}`}
                        description={
                            <div>
                                <p>成功导入: {importResult.success_count} 个</p>
                                <p>失败: {importResult.error_count} 个</p>
                                {importResult.errors && importResult.errors.length > 0 && (
                                    <div>
                                        <p>错误详情:</p>
                                        <ul>
                                            {importResult.errors.map((error: string, index: number) => (
                                                <li key={index}>{error}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        }
                        type={importResult.error_count > 0 ? 'warning' : 'success'}
                        showIcon
                        style={{ marginBottom: '16px' }}
                        closable
                        onClose={() => setImportResult(null)}
                    />
                )}

                <Table
                    columns={columns}
                    dataSource={participants}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                />
            </Card>

            {/* 创建/编辑被试者模态框 */}
            <Modal
                title={editingParticipant ? '编辑被试者' : '添加被试者'}
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false);
                    setEditingParticipant(null);
                    form.resetFields();
                }}
                footer={null}
                width={600}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                >
                    <Form.Item
                        name="username"
                        label="用户名"
                        rules={[{ required: true, message: '请输入用户名' }]}
                    >
                        <Input placeholder="请输入用户名" disabled={!!editingParticipant} />
                    </Form.Item>
                    {!editingParticipant && (
                        <Form.Item
                            name="password"
                            label="密码"
                            rules={[{ required: true, message: '请输入密码' }]}
                        >
                            <Input.Password placeholder="请输入密码" />
                        </Form.Item>
                    )}
                    <Form.Item
                        name="real_name"
                        label="真实姓名"
                        rules={[{ required: true, message: '请输入真实姓名' }]}
                    >
                        <Input placeholder="请输入真实姓名" />
                    </Form.Item>
                    <Form.Item
                        name="email"
                        label="邮箱"
                        rules={[
                            { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                    >
                        <Input placeholder="请输入邮箱" />
                    </Form.Item>
                    <Form.Item
                        name="phone"
                        label="电话"
                    >
                        <Input placeholder="请输入电话" />
                    </Form.Item>
                    <Form.Item
                        name="is_active"
                        label="激活状态"
                        valuePropName="checked"
                    >
                        <Switch checkedChildren="激活" unCheckedChildren="禁用" />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                {editingParticipant ? '更新' : '创建'}
                            </Button>
                            <Button onClick={() => {
                                setModalVisible(false);
                                setEditingParticipant(null);
                                form.resetFields();
                            }}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default ParticipantManagement; 