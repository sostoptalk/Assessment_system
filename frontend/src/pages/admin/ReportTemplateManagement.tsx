import React, { useState, useEffect } from 'react';
import {
    Card,
    Button,
    List,
    Form,
    Input,
    Select,
    Divider,
    Row,
    Col,
    Space,
    Tabs,
    Alert,
    Spin,
    message,
    Modal,
    Typography,
    Tag,
    Popconfirm,
    Collapse,
    Tooltip
} from 'antd';
import { MinusCircleOutlined, PlusOutlined, EyeOutlined, EditOutlined, DeleteOutlined, CopyOutlined, InfoCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import MonacoEditor from '@monaco-editor/react';
import yaml from 'js-yaml';
import TemplateDesigner from '../../components/TemplateDesigner';
import DOMPurify from 'dompurify';
import api, { apiService } from '../../utils/api';

const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { TabPane } = Tabs;

interface Paper {
    id: number;
    name: string;
}

interface Dimension {
    id: number;
    name: string;
    parent_id?: number;
    children?: Dimension[];
    defaultColor?: string; // 添加默认颜色属性
}

interface ScoreRange {
    range: string;
    comment: string;
}

interface DimensionConfig {
    scoreRanges: ScoreRange[];
}

interface ReportTemplate {
    id?: number;
    name: string;
    paper_id: number;
    paper_name?: string;
    title: string;
    introduction: string;
    conclusion: string;
    dimensions: Record<string, DimensionConfig>;
    charts: any[];
    created_at?: string;
    updated_at?: string;
    yaml_config?: string;
}

interface ComponentItem {
    id: string;
    type: string;
    name: string;
    html: string;
    content: string;
    params: Record<string, any>;
}

const ReportTemplateManagement: React.FC = () => {
    // 状态定义
    const [templates, setTemplates] = useState<ReportTemplate[]>([]);
    const [papers, setPapers] = useState<Paper[]>([]);
    const [dimensions, setDimensions] = useState<Dimension[]>([]);
    const [loading, setLoading] = useState(false);
    const [yamlLoading, setYamlLoading] = useState(false);
    const [yamlContent, setYamlContent] = useState('');
    const [previewLoading, setPreviewLoading] = useState(false);
    const [previewUrl, setPreviewUrl] = useState('');
    const [modalVisible, setModalVisible] = useState(false);
    const [currentTemplate, setCurrentTemplate] = useState<ReportTemplate | null>(null);
    const [form] = Form.useForm();
    const [activeTab, setActiveTab] = useState('basic');
    const [templateComponents, setTemplateComponents] = useState<ComponentItem[]>([]);
    const [htmlContent, setHtmlContent] = useState('');

    // 评价级别选项
    const evaluationLevels = ['high', 'medium', 'low', 'bad'];

    // 加载模板列表
    const fetchTemplates = async () => {
        setLoading(true);
        try {
            const response = await apiService.getList('/report-templates');
            setTemplates(response);
        } catch (error) {
            console.error('Failed to fetch templates:', error);
            message.error('获取模板列表失败');
        } finally {
            setLoading(false);
        }
    };

    // 加载试卷列表
    const fetchPapers = async () => {
        try {
            const response = await apiService.getList('/papers');
            setPapers(response);
        } catch (error) {
            console.error('Failed to fetch papers:', error);
            message.error('获取试卷列表失败');
        }
    };

    // 根据试卷ID加载维度
    const fetchDimensions = async (paperId: number) => {
        try {
            const response = await apiService.getList(`/dimensions/paper/${paperId}`);

            // 默认维度颜色配置
            const defaultColors = [
                "#1890ff", // 蓝色
                "#52c41a", // 绿色
                "#fa8c16", // 橙色
                "#722ed1", // 紫色
                "#eb2f96", // 粉色
                "#f5222d", // 红色
                "#13c2c2", // 青色
                "#faad14"  // 黄色
            ];

            // 为每个维度设置默认颜色
            const dimensionsWithColors = response.map((dim: any, index: number) => {
                // 为大维度设置默认颜色
                const color = defaultColors[index % defaultColors.length];
                return {
                    ...dim,
                    defaultColor: color,
                    // 为子维度设置颜色
                    children: dim.children ? dim.children.map((child: any, childIndex: number) => {
                        // 子维度颜色与父维度相近，但略有不同
                        const childColor = defaultColors[(index + childIndex + 1) % defaultColors.length];
                        return { ...child, defaultColor: childColor };
                    }) : []
                };
            });

            // 直接使用设置了默认颜色的维度树结构
            console.log("从后端获取的维度结构(带默认颜色):", dimensionsWithColors);
            setDimensions(dimensionsWithColors);
        } catch (error) {
            console.error('Failed to fetch dimensions:', error);
            message.error('获取维度列表失败');
        }
    };

    // 初始化
    useEffect(() => {
        fetchTemplates();
        fetchPapers();
    }, []);

    // 当选择的试卷变化时，获取相应的维度
    const handlePaperChange = (paperId: number) => {
        fetchDimensions(paperId);
        // 清空维度相关表单
        const currentValues = form.getFieldsValue();
        form.setFieldsValue({
            ...currentValues,
            dimensions: {}
        });
    };

    // 表单值转换为YAML
    const formToYaml = (values: any) => {
        try {
            setYamlLoading(true);

            // 处理值，确保它符合预期的格式
            const processedValues = {
                ...values,
                paper_id: Number(values.paper_id),
                score_levels: values.score_levels || [],
                dimensions: values.dimensions || {},
                dimension_evaluations: values.dimension_evaluations || {},
                template: values.template || {
                    name: "report_template.html",
                    title: values.title || "测评报告",
                    description: values.introduction || ""
                },
                charts: values.charts || []
            };

            // 转换为YAML
            const yamlStr = yaml.dump(processedValues, { indent: 2 });
            setYamlContent(yamlStr);
        } catch (error) {
            console.error('Failed to convert to YAML:', error);
            message.error('转换为YAML失败');
        } finally {
            setYamlLoading(false);
        }
    };

    // YAML转换为表单值
    const yamlToForm = () => {
        try {
            if (!yamlContent) return;

            const values = yaml.load(yamlContent) as any;

            form.setFieldsValue({
                ...values,
                template: values.template || {},
                dimensions: values.dimensions || {},
                dimension_evaluations: values.dimension_evaluations || {},
                score_levels: values.score_levels || []
            });

            // 如果有paper_id，获取相应的维度
            if (values.paper_id) {
                fetchDimensions(values.paper_id);
            }
        } catch (error) {
            console.error('Failed to parse YAML:', error);
            message.error('解析YAML失败，请检查格式');
        }
    };

    // 保存模板
    const handleSave = async () => {
        try {
            if (activeTab === 'designer') {
                // 保存设计器模式下的模板
                if (!form.getFieldValue('name') || !form.getFieldValue('paper_id')) {
                    message.error('请填写模板名称和选择关联试卷');
                    return;
                }

                const formValues = form.getFieldsValue();
                const config = {
                    ...formValues,
                    html_content: htmlContent // 设计器生成的HTML内容
                };

                const payload = {
                    name: formValues.name,
                    paper_id: formValues.paper_id,
                    config: config,
                    yaml_config: yamlContent || '# 默认YAML配置'
                };

                // 创建或更新模板
                if (currentTemplate?.id) {
                    await apiService.update('/report-templates', currentTemplate.id, payload);
                    message.success('模板更新成功');
                } else {
                    await apiService.create('/report-templates', payload);
                    message.success('模板创建成功');
                }

                setModalVisible(false);
                fetchTemplates();
                return;
            }

            // 基础模式和高级模式下的保存逻辑
            const values = await form.validateFields();

            // 确保YAML与表单同步
            if (activeTab === 'basic') {
                formToYaml(values);
            } else if (activeTab === 'advanced') {
                // 验证YAML
                try {
                    yaml.load(yamlContent);
                } catch (e) {
                    message.error('YAML格式错误，请检查');
                    return;
                }
            }

            const payload = {
                ...values,
                yaml_config: yamlContent,
                config: {
                    ...values,
                    html_content: htmlContent || '<div>默认模板内容</div>' // 添加HTML内容
                }
            };

            // 创建或更新模板
            if (currentTemplate?.id) {
                await apiService.update('/report-templates', currentTemplate.id, payload);
                message.success('模板更新成功');
            } else {
                await apiService.create('/report-templates', payload);
                message.success('模板创建成功');
            }

            setModalVisible(false);
            fetchTemplates();
        } catch (error) {
            console.error('Failed to save template:', error);
            message.error('保存模板失败');
        }
    };

    // 预览报告
    const handlePreview = async (templateId?: number) => {
        try {
            setPreviewLoading(true);

            // 默认请求数据，确保始终有config字段
            let requestData: any = {
                config: {
                    html_content: '<!DOCTYPE html><html><body><h1>模板内容</h1></body></html>'
                },
                yaml_config: '# 默认YAML配置\npaper_id: 1\npaper_name: "测试试卷"\n'
            };

            if (templateId) {
                // 使用现有模板预览
                console.log(`使用模板ID ${templateId} 预览`);

                // 获取模板详情，以确保有HTML内容
                try {
                    console.log(`正在获取模板ID ${templateId} 的详情...`);
                    const templateDetail = await apiService.getDetail('/report-templates', templateId);
                    console.log(`获取到模板: ${templateDetail?.name || '未知'}`);

                    if (templateDetail && templateDetail.config) {
                        console.log('成功获取模板配置');
                        const templateConfig = typeof templateDetail.config === 'string'
                            ? JSON.parse(templateDetail.config)
                            : templateDetail.config;

                        requestData = {
                            config: templateConfig,
                            yaml_config: templateDetail.yaml_config || ''
                        };
                    } else {
                        console.log('模板配置为空，使用模板ID作为备用');
                        requestData.template_id = templateId;
                    }
                } catch (error) {
                    console.error('获取模板详情失败:', error);
                    // 使用template_id字段，后端将尝试再次获取模板
                    requestData.template_id = templateId;
                }
            } else {
                // 使用当前编辑的模板预览
                if (activeTab === 'designer') {
                    // 设计器模式
                    console.log('使用设计器模式预览');
                    requestData = {
                        config: {
                            html_content: htmlContent || '<!DOCTYPE html><html><body><h1>模板内容</h1></body></html>'
                        },
                        yaml_config: yamlContent || '# 默认YAML配置\npaper_id: 1\npaper_name: "测试试卷"\n'
                    };
                } else {
                    try {
                        // 基础/高级模式
                        console.log('使用基础/高级模式预览');
                        const values = await form.validateFields();

                        // 确保config有正确的格式
                        let config: any = {
                            html_content: htmlContent || '<!DOCTYPE html><html><body><h1>模板内容</h1></body></html>'
                        };

                        // 添加表单中的所有字段
                        if (values) {
                            Object.keys(values).forEach(key => {
                                config[key] = values[key];
                            });
                        }

                        requestData = {
                            config: config,
                            yaml_config: yamlContent || '# 默认YAML配置\npaper_id: 1\npaper_name: "测试试卷"\n'
                        };

                        console.log('准备发送的预览请求:', JSON.stringify(requestData, null, 2));
                    } catch (formError) {
                        console.error('表单验证失败:', formError);
                        message.error('请先完成必填项');
                        setPreviewLoading(false);
                        return;
                    }
                }
            }

            console.log("发送预览请求:", requestData);

            // 使用axios直接请求，确保正确处理响应内容
            const response = await axios.post('/report-templates/preview', requestData, {
                responseType: 'text',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/html'
                }
            });

            const responseHtml = response.data;  // 使用不同的变量名避免覆盖
            console.log("收到预览响应, 内容长度:", responseHtml.length);

            // 设置预览HTML内容
            setPreviewUrl(responseHtml);

            if (!templateId) {
                setActiveTab('preview');
            } else {
                // 如果是列表中的预览，在新窗口打开HTML内容
                const newWindow = window.open();
                if (newWindow) {
                    newWindow.document.write(responseHtml);
                    newWindow.document.close();
                } else {
                    message.warning('请允许打开弹出窗口以查看预览');
                }
            }
        } catch (error) {
            console.error('Failed to generate preview:', error);
            if (axios.isAxiosError(error)) {
                const errorDetail = error.response?.data?.detail || error.message;
                console.log('错误详情:', error.response?.data);
                message.error(`生成预览失败: ${errorDetail}`);
            } else {
                message.error('生成预览失败');
            }
        } finally {
            setPreviewLoading(false);
        }
    };

    // 验证YAML
    const validateYaml = () => {
        try {
            yaml.load(yamlContent);
            message.success('YAML格式正确');
        } catch (e) {
            message.error(`YAML格式错误: ${(e as Error).message}`);
        }
    };

    // 格式化YAML
    const formatYaml = () => {
        try {
            const obj = yaml.load(yamlContent);
            const formatted = yaml.dump(obj, { indent: 2 });
            setYamlContent(formatted);
            message.success('YAML已格式化');
        } catch (e) {
            message.error(`格式化失败: ${(e as Error).message}`);
        }
    };

    // 复制模板
    const handleCopy = async (template: ReportTemplate) => {
        try {
            const newTemplate = {
                ...template,
                name: `${template.name} (复制)`,
                id: undefined
            };

            await apiService.create('/report-templates', newTemplate);
            message.success('模板复制成功');
            fetchTemplates();
        } catch (error) {
            console.error('Failed to copy template:', error);
            message.error('复制模板失败');
        }
    };

    // 删除模板
    const handleDelete = async (templateId: number) => {
        try {
            await apiService.delete('/report-templates', templateId);
            message.success('模板删除成功');
            fetchTemplates();
        } catch (error) {
            console.error('Failed to delete template:', error);
            message.error('删除模板失败');
        }
    };

    // 编辑模板
    const handleEdit = async (template: ReportTemplate) => {
        setCurrentTemplate(template);

        // 获取维度
        await fetchDimensions(template.paper_id);

        // 填充表单
        form.setFieldsValue({
            name: template.name,
            paper_id: template.paper_id,
            title: template.title,
            introduction: template.introduction,
            conclusion: template.conclusion,
            dimensions: template.dimensions,
            charts: template.charts
        });

        // 设置YAML内容
        setYamlContent(template.yaml_config || '');

        // 尝试从config中提取html_content
        try {
            if (typeof template.config === 'string') {
                const config = JSON.parse(template.config);
                if (config && config.html_content) {
                    setHtmlContent(config.html_content);
                }
            } else if (template.config && template.config.html_content) {
                setHtmlContent(template.config.html_content);
            }
        } catch (error) {
            console.error('Failed to parse template config:', error);
            setHtmlContent('');
        }

        setActiveTab('basic');
        setModalVisible(true);
    };

    // 新建模板
    const handleCreate = () => {
        setCurrentTemplate(null);
        form.resetFields();
        setYamlContent('');
        setHtmlContent('');
        setActiveTab('basic');
        setModalVisible(true);
    };

    // 处理设计器保存
    const handleDesignerSave = (components: ComponentItem[], html: string) => {
        setTemplateComponents(components);
        setHtmlContent(html);
        message.success('模板设计已保存');
    };

    return (
        <div style={{ padding: '24px' }}>
            <Card
                title="报告模板管理"
                extra={
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                        新建模板
                    </Button>
                }
                loading={loading}
            >
                {templates.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                        <Text type="secondary">暂无模板，请点击"新建模板"按钮创建</Text>
                    </div>
                ) : (
                    <List
                        itemLayout="horizontal"
                        dataSource={templates}
                        renderItem={(template) => (
                            <List.Item
                                actions={[
                                    <Button
                                        key="preview"
                                        icon={<EyeOutlined />}
                                        onClick={() => handlePreview(template.id)}
                                    >
                                        预览
                                    </Button>,
                                    <Button
                                        key="edit"
                                        type="primary"
                                        icon={<EditOutlined />}
                                        onClick={() => handleEdit(template)}
                                    >
                                        编辑
                                    </Button>,
                                    <Button
                                        key="copy"
                                        icon={<CopyOutlined />}
                                        onClick={() => handleCopy(template)}
                                    >
                                        复制
                                    </Button>,
                                    <Popconfirm
                                        key="delete"
                                        title="确定要删除此模板吗？"
                                        onConfirm={() => handleDelete(template.id!)}
                                        okText="确定"
                                        cancelText="取消"
                                    >
                                        <Button
                                            danger
                                            icon={<DeleteOutlined />}
                                        >
                                            删除
                                        </Button>
                                    </Popconfirm>
                                ]}
                            >
                                <List.Item.Meta
                                    title={template.name}
                                    description={
                                        <>
                                            <Tag color="blue">试卷: {template.paper_name}</Tag>
                                            <Tag color="green">创建时间: {new Date(template.created_at!).toLocaleString()}</Tag>
                                            {template.updated_at && (
                                                <Tag color="orange">更新时间: {new Date(template.updated_at).toLocaleString()}</Tag>
                                            )}
                                        </>
                                    }
                                />
                            </List.Item>
                        )}
                    />
                )}
            </Card>

            {/* 模板编辑模态框 */}
            <Modal
                title={currentTemplate ? '编辑报告模板' : '新建报告模板'}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                width={1000}
                footer={null}
                destroyOnClose
            >
                <Form form={form} layout="vertical">
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="name"
                                label="模板名称"
                                rules={[{ required: true, message: '请输入模板名称' }]}
                            >
                                <Input placeholder="请输入模板名称，例如：管理潜质测评报告模板" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="paper_id"
                                label="关联试卷"
                                rules={[{ required: true, message: '请选择关联试卷' }]}
                            >
                                <Select
                                    placeholder="请选择关联试卷"
                                    onChange={handlePaperChange}
                                >
                                    {papers.map(paper => (
                                        <Option key={paper.id} value={paper.id}>{paper.name}</Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>
                </Form>

                <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    items={[
                        {
                            key: 'designer',
                            label: '模板设计器',
                            children: (
                                <div>
                                    <Alert
                                        message="使用模板设计器可视化构建报告模板"
                                        description="拖放组件到设计区域，调整顺序和参数，实时预览报告效果。"
                                        type="info"
                                        showIcon
                                        style={{ marginBottom: '20px' }}
                                    />
                                    <TemplateDesigner
                                        onSave={handleDesignerSave}
                                        paperConfig={{ dimensions }}
                                    />
                                </div>
                            )
                        },
                        {
                            key: 'basic',
                            label: '基础配置',
                            children: <Form
                                form={form}
                                layout="vertical"
                                onValuesChange={(_, values) => {
                                    if (activeTab === 'basic') {
                                        formToYaml(values);
                                    }
                                }}
                                initialValues={{
                                    score_levels: [
                                        { name: "高潜力", min: 8.5, max: 10.0, summary: "", development_focus: "", color: "#4CAF50" },
                                        { name: "中高潜力", min: 7.5, max: 8.4, summary: "", development_focus: "", color: "#FFC107" },
                                        { name: "中等潜力", min: 6.5, max: 7.4, summary: "", development_focus: "", color: "#3498db" },
                                        { name: "基础潜力", min: 1.0, max: 6.4, summary: "", development_focus: "", color: "#F44336" }
                                    ]
                                }}
                            >
                                {/* 基本信息部分 */}
                                <Card title="基本信息" style={{ marginBottom: '20px' }}>
                                    <Form.Item
                                        name="title"
                                        label="报告标题"
                                        rules={[{ required: true, message: '请输入报告标题' }]}
                                    >
                                        <Input placeholder="请输入报告标题，例如：管理潜质测评报告" />
                                    </Form.Item>

                                    <Form.Item
                                        name="introduction"
                                        label="报告介绍"
                                        tooltip="此内容将显示在报告开头，介绍报告的目的和内容"
                                    >
                                        <Input.TextArea
                                            rows={3}
                                            placeholder="请输入报告介绍文字，例如：本报告基于管理潜质测评结果生成，反映受测者在管理序列上的发展潜力和能力特点。"
                                        />
                                    </Form.Item>
                                </Card>

                                {/* 分数区间配置部分 */}
                                <Card title="分数区间配置" style={{ marginBottom: '20px' }}>
                                    <Alert
                                        message="在此设置不同分数段的评价和发展重点，将用于生成报告的总体评价部分"
                                        type="info"
                                        showIcon
                                        style={{ marginBottom: '20px' }}
                                    />
                                    <Form.List name="score_levels">
                                        {(fields, { add, remove }) => (
                                            <>
                                                {fields.map((field, index) => (
                                                    <Card
                                                        key={field.key}
                                                        type="inner"
                                                        title={
                                                            <Space>
                                                                <Form.Item
                                                                    name={[field.name, 'name']}
                                                                    fieldKey={[field.fieldKey, 'name']}
                                                                    noStyle
                                                                >
                                                                    <Input placeholder="等级名称" style={{ width: '100px' }} />
                                                                </Form.Item>
                                                                <Form.Item
                                                                    name={[field.name, 'min']}
                                                                    fieldKey={[field.fieldKey, 'min']}
                                                                    noStyle
                                                                >
                                                                    <Input type="number" placeholder="最小值" style={{ width: '80px' }} />
                                                                </Form.Item>
                                                                <Text>-</Text>
                                                                <Form.Item
                                                                    name={[field.name, 'max']}
                                                                    fieldKey={[field.fieldKey, 'max']}
                                                                    noStyle
                                                                >
                                                                    <Input type="number" placeholder="最大值" style={{ width: '80px' }} />
                                                                </Form.Item>
                                                                <Form.Item
                                                                    name={[field.name, 'color']}
                                                                    fieldKey={[field.fieldKey, 'color']}
                                                                    noStyle
                                                                >
                                                                    <Input type="color" style={{ width: '60px' }} />
                                                                </Form.Item>
                                                            </Space>
                                                        }
                                                        extra={
                                                            fields.length > 1 ?
                                                                <Button
                                                                    type="text"
                                                                    danger
                                                                    icon={<MinusCircleOutlined />}
                                                                    onClick={() => remove(field.name)}
                                                                >
                                                                    删除区间
                                                                </Button> : null
                                                        }
                                                        style={{ marginBottom: '16px' }}
                                                    >
                                                        <Form.Item
                                                            name={[field.name, 'summary']}
                                                            fieldKey={[field.fieldKey, 'summary']}
                                                            label="综合评价"
                                                        >
                                                            <Input.TextArea
                                                                rows={3}
                                                                placeholder="请输入此分数区间的综合评价，例如：说明其具有卓越的领导潜质，在领导力通道上具备快速晋升的强劲潜力。这类人才不仅能在更高层级的领导角色上持续创造卓越绩效，且有潜力在战略层面引领组织变革与发展。"
                                                            />
                                                        </Form.Item>
                                                        <Form.Item
                                                            name={[field.name, 'development_focus']}
                                                            fieldKey={[field.fieldKey, 'development_focus']}
                                                            label="发展重点"
                                                        >
                                                            <Input.TextArea
                                                                rows={2}
                                                                placeholder="请输入此分数区间的发展重点建议，例如：需着重培养其战略领导力与跨体系协同能力，同时防范长期高压环境下的倦怠风险"
                                                            />
                                                        </Form.Item>
                                                    </Card>
                                                ))}
                                                <Form.Item>
                                                    <Button
                                                        type="dashed"
                                                        onClick={() => add({
                                                            name: `区间${fields.length + 1}`,
                                                            min: 0,
                                                            max: 10,
                                                            summary: '',
                                                            development_focus: '',
                                                            color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                                        })}
                                                        block
                                                        icon={<PlusOutlined />}
                                                    >
                                                        添加分数区间
                                                    </Button>
                                                </Form.Item>
                                            </>
                                        )}
                                    </Form.List>
                                </Card>

                                {/* 维度结构配置部分 */}
                                {dimensions.length > 0 && (
                                    <Card title="维度结构配置" style={{ marginBottom: '20px' }}>
                                        <Alert
                                            message="在此配置各维度的描述信息，这些信息将显示在报告中"
                                            type="info"
                                            showIcon
                                            style={{ marginBottom: '20px' }}
                                        />
                                        <Form.List name={['dimensions']}>
                                            {(fields, { add }) => (
                                                <>
                                                    {dimensions.filter(d => !d.parent_id).map((dimension, index) => (
                                                        <Card
                                                            key={dimension.id}
                                                            type="inner"
                                                            title={dimension.name}
                                                            style={{ marginBottom: '16px' }}
                                                        >
                                                            <Form.Item
                                                                name={[dimension.id.toString(), 'description']}
                                                                label="维度描述"
                                                            >
                                                                <Input.TextArea
                                                                    rows={2}
                                                                    placeholder="请输入此维度的描述，例如：展现个人成长内驱力和发展潜力"
                                                                />
                                                            </Form.Item>

                                                            <Form.Item
                                                                name={[dimension.id.toString(), 'color']}
                                                                label="维度颜色"
                                                                initialValue={dimension.defaultColor || "#1890ff"}
                                                            >
                                                                <Input
                                                                    type="color"
                                                                    style={{ width: '120px' }}
                                                                    placeholder="#FF0000"
                                                                />
                                                            </Form.Item>

                                                            <Divider orientation="left">子维度配置</Divider>

                                                            {dimension.children && dimension.children.map((subDim: any) => (
                                                                <Card
                                                                    key={subDim.id}
                                                                    size="small"
                                                                    title={subDim.name}
                                                                    style={{ marginBottom: '10px' }}
                                                                >
                                                                    <Form.Item
                                                                        name={[dimension.id.toString(), 'sub_dimensions', subDim.id.toString(), 'description']}
                                                                        label="子维度描述"
                                                                    >
                                                                        <Input
                                                                            placeholder="请输入此子维度的描述，例如：主动学习新知识和探索未知领域的动机"
                                                                        />
                                                                    </Form.Item>
                                                                </Card>
                                                            ))}
                                                        </Card>
                                                    ))}
                                                </>
                                            )}
                                        </Form.List>
                                    </Card>
                                )}

                                {/* 维度评价内容配置部分 */}
                                {dimensions.length > 0 && (
                                    <Card title="维度评价内容配置" style={{ marginBottom: '20px' }}>
                                        <Alert
                                            message="在此配置不同分数段的维度评价内容，包括总体评价、潜质特点和工作中的倾向"
                                            type="info"
                                            showIcon
                                            style={{ marginBottom: '20px' }}
                                        />

                                        <Collapse>
                                            {dimensions.filter(d => !d.parent_id).map(dimension => (
                                                <Panel header={dimension.name} key={dimension.id}>
                                                    {evaluationLevels.map(level => (
                                                        <Card
                                                            key={level}
                                                            type="inner"
                                                            title={
                                                                <Space>
                                                                    <Tag color={
                                                                        level === 'high' ? 'green' :
                                                                            level === 'medium' ? 'blue' :
                                                                                level === 'low' ? 'orange' : 'red'
                                                                    }>
                                                                        {
                                                                            level === 'high' ? '高分段' :
                                                                                level === 'medium' ? '中分段' :
                                                                                    level === 'low' ? '低分段' : '极低分段'
                                                                        }
                                                                    </Tag>
                                                                    <Tooltip title="高分段通常对应8.5-10分，中分段对应7-8.5分，低分段对应5-7分，极低分段对应5分以下">
                                                                        <InfoCircleOutlined />
                                                                    </Tooltip>
                                                                </Space>
                                                            }
                                                            style={{ marginBottom: '16px' }}
                                                        >
                                                            <Form.Item
                                                                name={['dimension_evaluations', dimension.name, level, 'dimension_eval']}
                                                                label="维度总体评价"
                                                            >
                                                                <Input.TextArea
                                                                    rows={3}
                                                                    placeholder="请输入此维度在该分数段的总体评价，例如：展现出卓越的成长内驱力，系统化构建个人发展路径。能够精准把握学习机会，成熟运用反馈机制实现持续迭代，在压力情境中保持情绪韧性，形成自我成长的良性循环。"
                                                                />
                                                            </Form.Item>

                                                            <Divider orientation="left">子维度评价</Divider>

                                                            {dimension.children && dimension.children.map((subDim: any) => (
                                                                <Card
                                                                    key={subDim.id}
                                                                    size="small"
                                                                    title={subDim.name}
                                                                    style={{ marginBottom: '10px' }}
                                                                >
                                                                    <Form.Item
                                                                        name={['dimension_evaluations', dimension.name, level, 'sub_dimensions', subDim.name, 'potentials']}
                                                                        label="潜质特点"
                                                                    >
                                                                        <Input.TextArea
                                                                            rows={2}
                                                                            placeholder="请输入此子维度在该分数段的潜质特点，例如：具备强烈的好奇心和认知拓展热情，主动挑战能力舒适区。将陌生领域视为成长契机，持续构建跨领域知识体系"
                                                                        />
                                                                    </Form.Item>
                                                                    <Form.Item
                                                                        name={['dimension_evaluations', dimension.name, level, 'sub_dimensions', subDim.name, 'behaviors']}
                                                                        label="工作中的倾向"
                                                                    >
                                                                        <Input.TextArea
                                                                            rows={2}
                                                                            placeholder="请输入此子维度在该分数段的工作表现倾向，例如：在日常工作中创造学习机会，主动承担未知领域的任务；建立行业信息网络，将新知识快速转化为实践能力"
                                                                        />
                                                                    </Form.Item>
                                                                </Card>
                                                            ))}
                                                        </Card>
                                                    ))}
                                                </Panel>
                                            ))}
                                        </Collapse>
                                    </Card>
                                )}

                                {/* 报告结论配置 */}
                                <Card title="报告结论配置" style={{ marginBottom: '20px' }}>
                                    <Form.Item
                                        name="conclusion"
                                        label="结论文字"
                                        tooltip="此内容将显示在报告结尾部分，可以包含总结和建议"
                                    >
                                        <Input.TextArea
                                            rows={4}
                                            placeholder="请输入报告结论文字，此部分会出现在报告的最后，通常包含整体评价和发展建议。"
                                        />
                                    </Form.Item>
                                </Card>
                            </Form>
                        },
                        {
                            key: 'advanced',
                            label: '高级配置(YAML)',
                            children: <>
                                <div style={{ marginBottom: 16 }}>
                                    <Alert
                                        message="提示"
                                        description="在此编辑器中可以直接修改YAML配置，适合高级用户使用。修改后可以点击'同步到表单'将更改应用到基础配置中。"
                                        type="info"
                                        showIcon
                                    />
                                </div>
                                <div style={{ marginBottom: 16 }}>
                                    <Space>
                                        <Button onClick={validateYaml}>验证YAML</Button>
                                        <Button onClick={formatYaml}>格式化</Button>
                                        <Button onClick={yamlToForm}>同步到表单</Button>
                                    </Space>
                                </div>
                                <div style={{ border: '1px solid #d9d9d9', borderRadius: '2px' }}>
                                    <MonacoEditor
                                        height="600px"
                                        language="yaml"
                                        theme="vs-light"
                                        value={yamlContent}
                                        onChange={(value) => {
                                            if (typeof value === 'string') {
                                                setYamlContent(value);
                                            }
                                        }}
                                        options={{
                                            minimap: { enabled: false },
                                            scrollBeyondLastLine: false,
                                            automaticLayout: true
                                        }}
                                    />
                                </div>
                            </>
                        },
                        {
                            key: 'html',
                            label: 'HTML编辑',
                            children: <>
                                <div style={{ marginBottom: 16 }}>
                                    <Alert
                                        message="HTML编辑"
                                        description="在此编辑器中可以直接修改HTML模板，适合有HTML经验的用户使用。"
                                        type="info"
                                        showIcon
                                    />
                                </div>
                                <div style={{ border: '1px solid #d9d9d9', borderRadius: '2px' }}>
                                    <MonacoEditor
                                        height="600px"
                                        language="html"
                                        theme="vs-light"
                                        value={htmlContent}
                                        onChange={(value) => {
                                            if (typeof value === 'string') {
                                                setHtmlContent(DOMPurify.sanitize(value));
                                            }
                                        }}
                                        options={{
                                            minimap: { enabled: false },
                                            scrollBeyondLastLine: false,
                                            automaticLayout: true
                                        }}
                                    />
                                </div>
                            </>
                        },
                        {
                            key: 'preview',
                            label: '预览',
                            children: <div style={{ height: '700px', position: 'relative' }}>
                                {previewLoading ? (
                                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                                        <Spin tip="生成预览中..." />
                                    </div>
                                ) : previewUrl ? (
                                    <div
                                        style={{ width: '100%', height: '100%' }}
                                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(previewUrl) }}
                                    />
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                                        <Text type="secondary">点击"生成预览"按钮查看报告效果</Text>
                                    </div>
                                )}
                            </div>
                        }
                    ]}
                />

                <div style={{ marginTop: 24, textAlign: 'right' }}>
                    <Space>
                        <Button onClick={() => setModalVisible(false)}>取消</Button>
                        <Button onClick={() => handlePreview()}>生成预览</Button>
                        <Button type="primary" onClick={handleSave}>保存模板</Button>
                    </Space>
                </div>
            </Modal>
        </div>
    );
};

export default ReportTemplateManagement; 