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
    Alert
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    UploadOutlined,
    DownloadOutlined
} from '@ant-design/icons';

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

    // 获取被试者列表
    const fetchParticipants = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/participants');
            if (response.ok) {
                const data = await response.json();
                setParticipants(data);
            } else {
                message.error('获取被试者列表失败');
            }
        } catch (error) {
            message.error('网络错误');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchParticipants();
    }, []);

    // 创建或更新被试者
    const handleSubmit = async (values: any) => {
        try {
            if (editingParticipant) {
                // 更新被试者
                const response = await fetch(`/api/participants/${editingParticipant.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values),
                });
                if (response.ok) {
                    message.success('被试者更新成功');
                    setModalVisible(false);
                    setEditingParticipant(null);
                    form.resetFields();
                    fetchParticipants();
                } else {
                    const errorData = await response.json();
                    message.error(errorData.detail || '更新失败');
                }
            } else {
                // 创建被试者
                const response = await fetch('/api/participants', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values),
                });
                if (response.ok) {
                    message.success('被试者创建成功');
                    setModalVisible(false);
                    form.resetFields();
                    fetchParticipants();
                } else {
                    const errorData = await response.json();
                    message.error(errorData.detail || '创建失败');
                }
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 删除被试者
    const handleDelete = async (id: number) => {
        try {
            const response = await fetch(`/api/participants/${id}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                message.success('删除成功');
                fetchParticipants();
            } else {
                message.error('删除失败');
            }
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