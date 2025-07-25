import { useState, useEffect } from 'react'
import { Card, Button, Table, Modal, Form, Input, Select, message, Space, Tag, Popconfirm, Upload, Spin, Checkbox, List } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, MinusCircleOutlined, DownloadOutlined } from '@ant-design/icons'
import axios from 'axios'
import RichTextEditor from '../../components/RichTextEditor'
import QuestionContentDisplay from '../../components/QuestionContentDisplay'
import 'react-quill/dist/quill.snow.css'
import { apiService } from '../../utils/api'

const { Option } = Select
const { TextArea } = Input

// 修改Question接口，添加parent_case_id和子题字段
interface Question {
    id?: number
    content: string
    type: 'single' | 'multiple' | 'indefinite' | 'case'
    options: string[]
    scores: number[]
    shuffle_options?: boolean
    parent_case_id?: number
    children?: Question[]  // 添加子题字段
    created_at?: string
    updated_at?: string
}

const defaultOption = () => ({ value: '', score: 0 })

// 编辑器配置已移至 RichTextEditor 组件

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
    const [caseModalVisible, setCaseModalVisible] = useState(false)
    const [caseForm] = Form.useForm()
    const [caseQuestions, setCaseQuestions] = useState<any[]>([])
    const [caseBackground, setCaseBackground] = useState('')

    // 获取token
    const token = localStorage.getItem('token') || ''

    // 拉取题库列表
    const fetchQuestions = async () => {
        setLoading(true)
        try {
            const res = await apiService.getList('/questions/')

            // 组织案例背景题和子题的关系
            const allQuestions = res  // apiService.getList 已经返回 data 部分
            const caseMap = new Map() // 存储案例背景题ID到题目对象的映射
            const regularQuestions: Question[] = [] // 存储非子题的普通题目

            // 第一遍遍历，找出所有案例背景题和普通题
            allQuestions.forEach((q: Question) => {
                if (q.type === 'case') {
                    q.children = [] // 初始化子题数组
                    caseMap.set(q.id, q)
                } else if (!q.parent_case_id) {
                    regularQuestions.push(q)
                }
            })

            // 第二遍遍历，将子题添加到对应的案例背景题中
            allQuestions.forEach((q: Question) => {
                if (q.parent_case_id && caseMap.has(q.parent_case_id)) {
                    const parent = caseMap.get(q.parent_case_id)
                    parent.children!.push(q)
                }
            })

            // 合并案例背景题和普通题
            const result = [...caseMap.values(), ...regularQuestions]
            setQuestions(result)
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
            render: (text: string) => <QuestionContentDisplay content={text} maxLength={100} />
        },
        {
            title: '题型',
            dataIndex: 'type',
            key: 'type',
            render: (type: string) => {
                const typeMap = {
                    single: { color: 'blue', text: '单选题' },
                    multiple: { color: 'green', text: '多选题' },
                    indefinite: { color: 'orange', text: '不定项' },
                    case: { color: 'purple', text: '案例背景题' }
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

    // 新增：添加案例背景题
    const handleAddCase = () => {
        setCaseQuestions([{ content: '', type: 'single', options: [defaultOption(), defaultOption(), defaultOption(), defaultOption()], scores: [0, 0, 0, 0], shuffle_options: false }])
        setCaseBackground('')
        setCaseModalVisible(true)
        caseForm.resetFields()
    }

    const handleEdit = (question: Question) => {
        // First reset the form to clear any previous state
        form.resetFields();
        // Then set the editing question
        setEditingQuestion(question);
        // Then set form values
        setTimeout(() => {
            form.setFieldsValue({
                content: question.content,
                type: question.type,
                shuffle_options: question.shuffle_options || false,
                options: question.options.map((v, i) => ({ value: v, score: question.scores[i] ?? 0 }))
            });
            setModalVisible(true);
        }, 0);
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
                await apiService.update('/questions', editingQuestion.id, payload)
                message.success('编辑成功')
            } else {
                await apiService.create('/questions/', payload)
                message.success('添加成功')
            }
            setModalVisible(false)
            fetchQuestions()
        } catch (e: any) {
            if (e && e.errorFields) {
                // 表单校验错误，AntD会自动高亮
            } else if (e && e.detail) {
                message.error('后端错误: ' + e.detail)
            } else {
                message.error('操作失败，请检查网络或输入')
                console.error('操作失败详情:', e)
            }
        }
    }

    // 新增：案例背景题提交
    const handleCaseModalOk = async () => {
        try {
            const values = await caseForm.validateFields()
            if (!caseBackground || caseBackground.trim() === '') {
                message.error('请输入案例背景内容')
                return
            }
            // 先保存案例背景题（主表）
            const res = await apiService.create('/questions/', {
                content: caseBackground,
                type: 'case',
                options: [],
                scores: [],
                shuffle_options: false
            })
            const caseId = res.id
            // 组装payload
            const questions = values.questions.map((q: any) => ({
                ...q,
                options: q.options.map((item: any) => item.value),
                scores: q.options.map((item: any) => Number(item.score)),
                parent_case_id: caseId
            }))
            // 再保存子题
            for (const q of questions) {
                await apiService.create('/questions/', q)
            }
            message.success('案例背景题添加成功')
            setCaseModalVisible(false)
            fetchQuestions()
        } catch (e) {
            message.error('添加失败')
        }
    }

    // 删除题目
    const handleDelete = async (id: number) => {
        try {
            // 查找当前要删除的题目
            const questionToDelete = questions.find(q => q.id === id)

            // 如果是案例背景题，提示用户会同时删除所有子题
            if (questionToDelete && questionToDelete.type === 'case' && questionToDelete.children && questionToDelete.children.length > 0) {
                Modal.confirm({
                    title: '确认删除',
                    content: `该题为案例背景题，包含 ${questionToDelete.children.length} 个子题，删除后将同时删除所有子题，是否继续？`,
                    okText: '确认',
                    cancelText: '取消',
                    onOk: async () => {
                        await apiService.delete('/questions', id)
                        message.success('删除成功')
                        fetchQuestions()
                    }
                })
            } else {
                await apiService.delete('/questions', id)
                message.success('删除成功')
                fetchQuestions()
            }
        } catch (e: any) {
            if (e && e.detail) {
                message.error(e.detail)
            } else {
                message.error('删除失败')
                console.error('删除失败详情:', e)
            }
        }
    }

    // Word导入并批量编辑
    const handleWordImport = async (file: any) => {
        setImporting(true)
        const formData = new FormData()
        formData.append('file', file)
        try {
            const res = await axios.post('/questions/import_word', formData, {
                headers: { Authorization: `Bearer ${token}` }
            })
            const wordQuestions = res.questions.map((q: any) => ({
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
                await apiService.create('/questions/', q)
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
                        apiService.delete('/questions', id)
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

    // Excel导入相关
    const handleExcelImport = async (file: any) => {
        setImporting(true);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await axios.post('/questions/import_excel', formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const excelQuestions = res.questions.map((q: any) => ({
                content: q.content,
                type: q.type,
                options: q.options.map((v: string, i: number) => ({ value: v, score: q.scores[i] ?? 0 })),
                shuffle_options: q.shuffle_options || false
            }));
            batchForm.setFieldsValue({ questions: excelQuestions });
            setBatchModalVisible(true);
        } catch (e) {
            message.error('Excel导入失败');
        } finally {
            setImporting(false);
        }
        return false;
    };

    const handleDownloadExcelTemplate = () => {
        window.open('/excel模板.xlsx');
    };
    const handleDownloadWordTemplate = () => {
        window.open('/questionnaire_template.docx');
    };

    // 批量编辑表单内的TextArea修改为RichTextEditor
    const formItemContent = (form: any, field: any, fieldPath: any[]) => (
        <Form.Item noStyle shouldUpdate>
            {() => {
                const content = form.getFieldValue([...fieldPath, field.name, 'content']) || '';
                return (
                    <RichTextEditor
                        key={`editor-${field.key}`}
                        value={content}
                        onChange={value => form.setFieldValue([...fieldPath, field.name, 'content'], value)}
                        placeholder="请输入题目内容，可以直接上传或粘贴图片"
                    />
                );
            }}
        </Form.Item>
    );

    // 修复类型映射中缺少case
    const getTypeText = (type: string): string => {
        const typeMap: Record<string, string> = {
            'single': '单选题',
            'multiple': '多选题',
            'indefinite': '不定项',
            'case': '案例背景题'
        };
        return typeMap[type] || type;
    };

    // 修改表格，添加展开功能
    const expandedRowRender = (record: Question) => {
        // 只有案例背景题且有子题时才展开显示
        if (record.type !== 'case' || !record.children || record.children.length === 0) {
            return null
        }

        return (
            <List
                dataSource={record.children}
                renderItem={(item: Question, index) => (
                    <List.Item
                        actions={[
                            <Button
                                type="link"
                                icon={<EditOutlined />}
                                onClick={() => handleEdit(item)}
                            >
                                编辑
                            </Button>,
                            <Popconfirm
                                title="确定要删除该题目吗？"
                                onConfirm={() => handleDelete(item.id!)}
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
                        ]}
                    >
                        <div style={{ paddingLeft: 24 }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                子题{index + 1}: <QuestionContentDisplay content={item.content} maxLength={100} />
                            </div>
                            <div style={{ color: '#666', fontSize: '12px' }}>
                                类型: {getTypeText(item.type)} |
                                选项数: {item.options.length} |
                                选项乱序: {item.shuffle_options ? '已启用' : '未启用'}
                            </div>
                        </div>
                    </List.Item>
                )}
            />
        )
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
                            accept=".xlsx,.xls"
                            showUploadList={false}
                            beforeUpload={handleExcelImport}
                        >
                            <Button icon={<UploadOutlined />}>导入Excel</Button>
                        </Upload>
                        <Button icon={<DownloadOutlined />} onClick={handleDownloadExcelTemplate}>
                            下载Excel模板
                        </Button>
                        <Button icon={<DownloadOutlined />} onClick={handleDownloadWordTemplate}>
                            下载Word模板
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
                        <Button type="dashed" onClick={handleAddCase} style={{ marginLeft: 8 }}>
                            添加案例背景题
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
                    expandable={{
                        expandedRowRender: expandedRowRender,
                        rowExpandable: (record: Question) => record.type === 'case' && Array.isArray(record.children) && record.children.length > 0
                    }}
                />

                {/* 单题编辑弹窗 */}
                <Modal
                    title={editingQuestion ? '编辑题目' : '添加题目'}
                    open={modalVisible}
                    onOk={handleModalOk}
                    onCancel={() => {
                        setModalVisible(false);
                        setEditingQuestion(undefined);
                        form.resetFields();
                    }}
                    width={800}
                    okText="确定"
                    cancelText="取消"
                >
                    <Form form={form} layout="vertical">
                        <Form.Item
                            name="content"
                            label="题目内容"
                            rules={[{ required: true, message: '请输入题目内容' }]}
                        >
                            <Form.Item noStyle shouldUpdate>
                                {({ getFieldValue }) => (
                                    <RichTextEditor
                                        key={`editor-${form.getFieldValue('content')}`}
                                        value={getFieldValue('content') || ''}
                                        onChange={value => form.setFieldValue('content', value)}
                                        placeholder="请输入题目内容，可以直接上传或粘贴图片"
                                    />
                                )}
                            </Form.Item>
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
                                                key={`${field.key}-value`}
                                                name={[field.name, 'value']}
                                                fieldKey={[field.fieldKey, 'value']}
                                                rules={[{ required: true, message: '请输入选项内容' }]}
                                            >
                                                <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                            </Form.Item>
                                            <Form.Item
                                                key={`${field.key}-score`}
                                                name={[field.name, 'score']}
                                                fieldKey={[field.fieldKey, 'score']}
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
                    onCancel={() => {
                        setBatchModalVisible(false);
                        batchForm.resetFields();
                    }}
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
                                                key={`${field.key}-content`}
                                                name={[field.name, 'content']}
                                                label="题目内容"
                                                fieldKey={[field.fieldKey, 'content']}
                                                rules={[{ required: true, message: '请输入题目内容' }]}
                                            >
                                                {formItemContent(batchForm, field, ['questions'])}
                                            </Form.Item>
                                            <Form.Item
                                                key={`${field.key}-type`}
                                                name={[field.name, 'type']}
                                                label="题型"
                                                fieldKey={[field.fieldKey, 'type']}
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
                                                                    key={`${opt.key}-value`}
                                                                    name={[opt.name, 'value']}
                                                                    fieldKey={[opt.fieldKey, 'value']}
                                                                    rules={[{ required: true, message: '请输入选项内容' }]}
                                                                >
                                                                    <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                                                </Form.Item>
                                                                <Form.Item
                                                                    key={`${opt.key}-score`}
                                                                    name={[opt.name, 'score']}
                                                                    fieldKey={[opt.fieldKey, 'score']}
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

                {/* 案例背景题弹窗 */}
                <Modal
                    title="添加案例背景题"
                    open={caseModalVisible}
                    onOk={handleCaseModalOk}
                    onCancel={() => {
                        setCaseModalVisible(false);
                        setCaseBackground('');
                        setCaseQuestions([]);
                        caseForm.resetFields();
                    }}
                    width={900}
                    okText="提交全部"
                >
                    <div style={{ marginBottom: 16 }}>
                        <div style={{ fontWeight: 600, marginBottom: 8 }}>案例背景（支持直接粘贴或上传图片）：</div>
                        <RichTextEditor
                            key={`editor-${caseBackground}`}
                            value={caseBackground}
                            onChange={setCaseBackground}
                            placeholder="请输入案例背景内容，可以直接上传或粘贴图片"
                        />
                    </div>
                    <Form form={caseForm} layout="vertical">
                        <Form.List name="questions" initialValue={caseQuestions}>
                            {(fields, { add, remove }) => (
                                <>
                                    {fields.map((field, qidx) => (
                                        <Card key={field.key} style={{ marginBottom: 16 }} title={`子题${qidx + 1}`}
                                            extra={fields.length > 1 ? <MinusCircleOutlined onClick={() => remove(field.name)} /> : null}>
                                            <Form.Item
                                                key={`${field.key}-content`}
                                                name={[field.name, 'content']}
                                                label="题目内容"
                                                fieldKey={[field.fieldKey, 'content']}
                                                rules={[{ required: true, message: '请输入题目内容' }]}
                                            >
                                                {formItemContent(caseForm, field, ['questions'])}
                                            </Form.Item>
                                            <Form.Item
                                                key={`${field.key}-type`}
                                                name={[field.name, 'type']}
                                                label="题型"
                                                fieldKey={[field.fieldKey, 'type']}
                                                rules={[{ required: true, message: '请选择题型' }]}
                                            >
                                                <Select style={{ width: 200 }}>
                                                    <Option value="single">单选题</Option>
                                                    <Option value="multiple">多选题</Option>
                                                    <Option value="indefinite">不定项选择题</Option>
                                                </Select>
                                            </Form.Item>
                                            <Form.Item
                                                key={`${field.key}-shuffle_options`}
                                                name={[field.name, 'shuffle_options']}
                                                label="选项乱序"
                                                fieldKey={[field.fieldKey, 'shuffle_options']}
                                                valuePropName="checked"
                                            >
                                                <Checkbox>启用选项乱序</Checkbox>
                                            </Form.Item>
                                            <Form.List name={[field.name, 'options']} initialValue={[defaultOption(), defaultOption(), defaultOption(), defaultOption()]}>
                                                {(optFields, { add: addOpt, remove: removeOpt }) => (
                                                    <>
                                                        {optFields.map((opt, idx) => (
                                                            <Space key={opt.key} align="baseline" style={{ display: 'flex', marginBottom: 8 }}>
                                                                <Form.Item
                                                                    key={`${opt.key}-value`}
                                                                    name={[opt.name, 'value']}
                                                                    fieldKey={[opt.fieldKey, 'value']}
                                                                    rules={[{ required: true, message: '请输入选项内容' }]}
                                                                >
                                                                    <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                                                </Form.Item>
                                                                <Form.Item
                                                                    key={`${opt.key}-score`}
                                                                    name={[opt.name, 'score']}
                                                                    fieldKey={[opt.fieldKey, 'score']}
                                                                    rules={[{ required: true, message: '请输入分数' }]}
                                                                >
                                                                    <Input type="number" placeholder="分数" style={{ width: 80 }} />
                                                                </Form.Item>
                                                                {optFields.length > 2 && (
                                                                    <MinusCircleOutlined onClick={() => removeOpt(opt.name)} />
                                                                )}
                                                            </Space>
                                                        ))}
                                                        <Button type="dashed" onClick={() => addOpt(defaultOption())} block icon={<PlusOutlined />}>添加选项</Button>
                                                    </>
                                                )}
                                            </Form.List>
                                        </Card>
                                    ))}
                                    <Button type="dashed" onClick={() => add({ content: '', type: 'single', options: [defaultOption(), defaultOption(), defaultOption(), defaultOption()], scores: [0, 0, 0, 0], shuffle_options: false })} block icon={<PlusOutlined />}>添加更多子题</Button>
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