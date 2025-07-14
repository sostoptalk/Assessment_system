import { useState, useEffect } from 'react'
import { Card, Button, Table, Modal, Form, Input, Select, message, Space, Tag, Popconfirm, Upload, Spin, Checkbox } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, MinusCircleOutlined } from '@ant-design/icons'
import axios from 'axios'

const { Option } = Select
const { TextArea } = Input

interface Question {
    id?: number
    content: string
    type: 'single' | 'multiple' | 'indefinite'
    options: string[]
    scores: number[]
    shuffle_options?: boolean
    created_at?: string
    updated_at?: string
}

const defaultOption = () => ({ value: '', score: 0 })

const QuestionManagement = () => {
    const [questions, setQuestions] = useState<Question[]>([])
    const [modalVisible, setModalVisible] = useState(false)
    const [editingQuestion, setEditingQuestion] = useState<Question | null>(null)
    const [form] = Form.useForm()
    const [loading, setLoading] = useState(false)
    const [batchModalVisible, setBatchModalVisible] = useState(false)
    const [batchForm] = Form.useForm()
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
    const [importing, setImporting] = useState(false)
    const [batchSubmitting, setBatchSubmitting] = useState(false)
    const [pagination, setPagination] = useState({ current: 1, pageSize: 10 })

    // 获取token
    const token = localStorage.getItem('token') || ''

    // 拉取题库列表
    const fetchQuestions = async () => {
        setLoading(true)
        try {
            const res = await axios.get('/api/questions/', {
                headers: { Authorization: `Bearer ${token}` }
            })
            setQuestions(res.data)
        } catch (e) {
            message.error('获取题库失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchQuestions()
        // eslint-disable-next-line
    }, [])

    useEffect(() => {
        setPagination((p) => ({ ...p, current: 1 }))
    }, [questions])

    const columns = [
        {
            title: '题目内容',
            dataIndex: 'content',
            key: 'content',
            width: '40%',
            render: (text: string) => <div style={{ maxWidth: 300 }}>{text}</div>
        },
        {
            title: '题型',
            dataIndex: 'type',
            key: 'type',
            render: (type: string) => {
                const typeMap = {
                    single: { color: 'blue', text: '单选题' },
                    multiple: { color: 'green', text: '多选题' },
                    indefinite: { color: 'orange', text: '不定项' }
                }
                const { color, text } = typeMap[type as keyof typeof typeMap]
                return <Tag color={color}>{text}</Tag>
            }
        },
        {
            title: '选项数',
            key: 'options_count',
            render: (_: any, record: Question) => record.options.length
        },
        {
            title: '选项乱序',
            key: 'shuffle_options',
            render: (shuffle_options: boolean) => (
                <Tag color={shuffle_options ? 'green' : 'default'}>
                    {shuffle_options ? '已启用' : '未启用'}
                </Tag>
            )
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: Question) => (
                <Space>
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                    >
                        编辑
                    </Button>
                    <Popconfirm
                        title="确定要删除该题目吗？"
                        onConfirm={() => handleDelete(record.id!)}
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
    ]

    const handleAdd = () => {
        setEditingQuestion(null)
        form.resetFields()
        setModalVisible(true)
    }

    const handleEdit = (question: Question) => {
        setEditingQuestion(question)
        form.setFieldsValue({
            content: question.content,
            type: question.type,
            shuffle_options: question.shuffle_options || false,
            options: question.options.map((v, i) => ({ value: v, score: question.scores[i] ?? 0 }))
        })
        setModalVisible(true)
    }

    // 新增或编辑题目
    const handleModalOk = async () => {
        try {
            const values = await form.validateFields()
            const options = values.options.map((item: any) => item.value)
            const scores = values.options.map((item: any) => Number(item.score))
            if (options.length !== scores.length) {
                message.error('选项数和分数数必须一致')
                return
            }
            const payload = {
                content: values.content,
                type: values.type,
                options,
                scores,
                shuffle_options: values.shuffle_options || false
            }
            if (editingQuestion) {
                await axios.put(`/api/questions/${editingQuestion.id}`, payload, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                message.success('编辑成功')
            } else {
                await axios.post('/api/questions/', payload, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                message.success('添加成功')
            }
            setModalVisible(false)
            fetchQuestions()
        } catch (e: any) {
            if (e && e.errorFields) {
                // 表单校验错误，AntD会自动高亮
            } else if (e && e.response && e.response.data && e.response.data.detail) {
                message.error('后端错误: ' + e.response.data.detail)
            } else {
                message.error('操作失败，请检查网络或输入')
            }
        }
    }

    // 删除题目
    const handleDelete = async (id: number) => {
        try {
            await axios.delete(`/api/questions/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            message.success('删除成功')
            fetchQuestions()
        } catch (e) {
            message.error('删除失败')
        }
    }

    // Word导入并批量编辑
    const handleWordImport = async (file: any) => {
        setImporting(true)
        const formData = new FormData()
        formData.append('file', file)
        try {
            const res = await axios.post('/api/questions/import_word', formData, {
                headers: { Authorization: `Bearer ${token}` }
            })
            const wordQuestions = res.data.questions.map((q: any) => ({
                content: q.content,
                type: q.type,
                options: q.options.map((v: string, i: number) => ({ value: v, score: q.scores[i] ?? 0 }))
            }))
            batchForm.setFieldsValue({ questions: wordQuestions })
            setBatchModalVisible(true)
        } catch (e) {
            message.error('Word导入失败')
        } finally {
            setImporting(false)
        }
        return false
    }

    // 批量提交
    const handleBatchOk = async () => {
        setBatchSubmitting(true)
        try {
            const values = await batchForm.validateFields()
            const payload = values.questions.map((q: any) => ({
                content: q.content,
                type: q.type,
                options: q.options.map((item: any) => item.value),
                scores: q.options.map((item: any) => Number(item.score))
            }))
            for (const q of payload) {
                await axios.post('/api/questions/', q, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            }
            message.success('批量添加成功')
            setBatchModalVisible(false)
            fetchQuestions()
        } catch (e) {
            message.error('批量添加失败')
        } finally {
            setBatchSubmitting(false)
        }
    }

    // 批量删除
    const handleBatchDelete = async () => {
        if (selectedRowKeys.length === 0) {
            message.warning('请先选择要删除的题目')
            return
        }
        Modal.confirm({
            title: `确定要删除选中的${selectedRowKeys.length}道题目吗？`,
            okText: '确定',
            cancelText: '取消',
            onOk: async () => {
                try {
                    await Promise.all(selectedRowKeys.map(id =>
                        axios.delete(`/api/questions/${id}`, {
                            headers: { Authorization: `Bearer ${token}` }
                        })
                    ))
                    message.success('批量删除成功')
                    setSelectedRowKeys([])
                    fetchQuestions()
                } catch (e) {
                    message.error('批量删除失败')
                }
            }
        })
    }

    return (
        <div style={{ position: 'relative', minHeight: 600 }}>
            {(importing || batchSubmitting) && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    background: 'rgba(255,255,255,0.5)',
                    zIndex: 2000,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}>
                    <Spin
                        spinning={true}
                        tip={importing ? '正在解析Word...' : batchSubmitting ? '正在批量提交...' : ''}
                        size="large"
                    />
                </div>
            )}
            <Card
                title="题库管理"
                extra={
                    <Space>
                        <Button danger disabled={selectedRowKeys.length === 0} onClick={handleBatchDelete}>
                            批量删除
                        </Button>
                        <Upload
                            accept=".doc,.docx"
                            beforeUpload={handleWordImport}
                            showUploadList={false}
                        >
                            <Button icon={<UploadOutlined />}>导入Word</Button>
                        </Upload>
                        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                            添加题目
                        </Button>
                    </Space>
                }
            >
                <Table
                    columns={columns}
                    dataSource={questions.slice(
                        (pagination.current - 1) * pagination.pageSize,
                        pagination.current * pagination.pageSize
                    )}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        current: pagination.current,
                        pageSize: pagination.pageSize,
                        showSizeChanger: true,
                        pageSizeOptions: ['5', '10', '20', '50'],
                        showTotal: (total) => `共 ${total} 条`,
                        total: questions.length,
                        onChange: (page, pageSize) => setPagination({ current: page, pageSize })
                    }}
                    rowSelection={{
                        selectedRowKeys,
                        onChange: setSelectedRowKeys
                    }}
                />

                {/* 单题编辑弹窗 */}
                <Modal
                    title={editingQuestion ? '编辑题目' : '添加题目'}
                    open={modalVisible}
                    onOk={handleModalOk}
                    onCancel={() => setModalVisible(false)}
                    width={800}
                >
                    <Form form={form} layout="vertical">
                        <Form.Item
                            name="content"
                            label="题目内容"
                            rules={[{ required: true, message: '请输入题目内容' }]}
                        >
                            <TextArea rows={4} />
                        </Form.Item>

                        <Form.Item
                            name="type"
                            label="题型"
                            rules={[{ required: true, message: '请选择题型' }]}
                        >
                            <Select>
                                <Option value="single">单选题</Option>
                                <Option value="multiple">多选题</Option>
                                <Option value="indefinite">不定项选择题</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="shuffle_options"
                            label="选项乱序"
                            valuePropName="checked"
                        >
                            <Checkbox>启用选项乱序（被试者答题时选项顺序随机化）</Checkbox>
                        </Form.Item>

                        <Form.List name="options" initialValue={[defaultOption(), defaultOption(), defaultOption(), defaultOption()]}>
                            {(fields, { add, remove }) => (
                                <>
                                    {fields.map((field, idx) => (
                                        <Space key={field.key} align="baseline" style={{ display: 'flex', marginBottom: 8 }}>
                                            <Form.Item
                                                {...field}
                                                name={[field.name, 'value']}
                                                rules={[{ required: true, message: '请输入选项内容' }]}
                                            >
                                                <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                            </Form.Item>
                                            <Form.Item
                                                {...field}
                                                name={[field.name, 'score']}
                                                rules={[{ required: true, message: '请输入分数' }]}
                                            >
                                                <Input type="number" placeholder="分数" style={{ width: 80 }} />
                                            </Form.Item>
                                            {fields.length > 2 && (
                                                <MinusCircleOutlined onClick={() => remove(field.name)} />
                                            )}
                                        </Space>
                                    ))}
                                    <Button type="dashed" onClick={() => add(defaultOption())} block icon={<PlusOutlined />}>添加选项</Button>
                                </>
                            )}
                        </Form.List>
                    </Form>
                </Modal>

                {/* 批量编辑弹窗 */}
                <Modal
                    title="批量导入题目"
                    open={batchModalVisible}
                    onOk={handleBatchOk}
                    onCancel={() => setBatchModalVisible(false)}
                    width={900}
                    okText="全部提交"
                >
                    <Form form={batchForm} layout="vertical">
                        <Form.List name="questions">
                            {(fields) => (
                                <>
                                    {fields.map((field, qidx) => (
                                        <Card key={field.key} style={{ marginBottom: 16 }} title={`题目${qidx + 1}`}>
                                            <Form.Item
                                                {...field}
                                                name={[field.name, 'content']}
                                                label="题目内容"
                                                rules={[{ required: true, message: '请输入题目内容' }]}
                                            >
                                                <TextArea rows={2} />
                                            </Form.Item>
                                            <Form.Item
                                                {...field}
                                                name={[field.name, 'type']}
                                                label="题型"
                                                rules={[{ required: true, message: '请选择题型' }]}
                                            >
                                                <Select style={{ width: 200 }}>
                                                    <Option value="single">单选题</Option>
                                                    <Option value="multiple">多选题</Option>
                                                    <Option value="indefinite">不定项选择题</Option>
                                                </Select>
                                            </Form.Item>
                                            <Form.List name={[field.name, 'options']}>
                                                {(optFields, { add, remove }) => (
                                                    <>
                                                        {optFields.map((opt, idx) => (
                                                            <Space key={opt.key} align="baseline" style={{ display: 'flex', marginBottom: 8 }}>
                                                                <Form.Item
                                                                    {...opt}
                                                                    name={[opt.name, 'value']}
                                                                    rules={[{ required: true, message: '请输入选项内容' }]}
                                                                >
                                                                    <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                                                </Form.Item>
                                                                <Form.Item
                                                                    {...opt}
                                                                    name={[opt.name, 'score']}
                                                                    rules={[{ required: true, message: '请输入分数' }]}
                                                                >
                                                                    <Input type="number" placeholder="分数" style={{ width: 80 }} />
                                                                </Form.Item>
                                                                {optFields.length > 2 && (
                                                                    <MinusCircleOutlined onClick={() => remove(opt.name)} />
                                                                )}
                                                            </Space>
                                                        ))}
                                                        <Button type="dashed" onClick={() => add(defaultOption())} block icon={<PlusOutlined />}>添加选项</Button>
                                                    </>
                                                )}
                                            </Form.List>
                                        </Card>
                                    ))}
                                </>
                            )}
                        </Form.List>
                    </Form>
                </Modal>
            </Card>
        </div>
    )
}

export default QuestionManagement 