import React, { useState, useEffect } from 'react';
import {
    Card,
    Button,
    Space,
    Divider,
    Collapse,
    Modal,
    Form,
    Input,
    Tooltip,
    Spin,
    message,
    Typography,
    Select,
    Tag
} from 'antd';
import {
    DeleteOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    EditOutlined,
    EyeOutlined,
    CopyOutlined,
    SaveOutlined,
    PlusOutlined,
    CloudDownloadOutlined,
    CloudUploadOutlined,
    FileOutlined
} from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import TemplateComponentLibrary from './TemplateComponentLibrary';
import api, { apiService } from '../utils/api';
import axios from 'axios';

const { Panel } = Collapse;
const { TextArea } = Input;
const { Text } = Typography;
const { Option } = Select;

// 组件项目接口
interface ComponentItem {
    id: string;
    type: string;
    name: string;
    html: string;
    content: string; // 实际渲染的HTML内容
    params: Record<string, any>; // 组件参数
}

interface SavedTemplate {
    id: number;
    name: string;
}

interface TemplateDesignerProps {
    initialComponents?: ComponentItem[];
    onSave: (components: ComponentItem[], htmlContent: string) => void;
    paperConfig?: any; // 试卷配置信息，如维度等
}

const TemplateDesigner: React.FC<TemplateDesignerProps> = ({
    initialComponents = [],
    onSave,
    paperConfig
}) => {
    const [components, setComponents] = useState<ComponentItem[]>(initialComponents);
    const [editingComponent, setEditingComponent] = useState<ComponentItem | null>(null);
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [previewVisible, setPreviewVisible] = useState(false);
    const [previewHtml, setPreviewHtml] = useState('');
    const [previewLoading, setPreviewLoading] = useState(false);
    const [form] = Form.useForm();
    const [componentLibraryVisible, setComponentLibraryVisible] = useState(false);

    // 新增状态用于保存/加载模板
    const [savedTemplates, setSavedTemplates] = useState<SavedTemplate[]>([]);
    const [saveTemplateVisible, setSaveTemplateVisible] = useState(false);
    const [loadTemplateVisible, setLoadTemplateVisible] = useState(false);
    const [saveTemplateName, setSaveTemplateName] = useState('');
    const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
    const [savingTemplate, setSavingTemplate] = useState(false);
    const [loadingTemplates, setLoadingTemplates] = useState(false);
    const [loadingTemplateContent, setLoadingTemplateContent] = useState(false);

    // 当外部传入的初始组件变化时，更新状态
    useEffect(() => {
        if (initialComponents.length > 0) {
            setComponents(initialComponents);
        }
    }, [initialComponents]);

    // 加载可用的保存模板列表
    useEffect(() => {
        fetchSavedTemplates();
    }, []);

    // 获取保存的模板列表
    const fetchSavedTemplates = async () => {
        try {
            setLoadingTemplates(true);
            const response = await apiService.getList('/report-templates/designer-templates');
            setSavedTemplates(response || []);
        } catch (error) {
            console.error('获取模板列表失败:', error);
            message.error('获取保存的模板列表失败');
        } finally {
            setLoadingTemplates(false);
        }
    };

    // 处理组件拖拽结束事件
    const handleDragEnd = (result: any) => {
        if (!result.destination) return;

        const items = [...components];
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);

        setComponents(items);
    };

    // 添加组件
    const handleAddComponent = (type: string, id: string, html: string) => {
        const newComponent: ComponentItem = {
            id: `${type}_${id}_${Date.now()}`,
            type,
            name: id,
            html,
            content: html,
            params: {}
        };

        setComponents([...components, newComponent]);
    };

    // 删除组件
    const handleDeleteComponent = (index: number) => {
        const newComponents = [...components];
        newComponents.splice(index, 1);
        setComponents(newComponents);
    };

    // 复制组件
    const handleDuplicateComponent = (index: number) => {
        const componentToDuplicate = components[index];
        const duplicatedComponent = {
            ...componentToDuplicate,
            id: `${componentToDuplicate.type}_${componentToDuplicate.name}_${Date.now()}`
        };

        const newComponents = [...components];
        newComponents.splice(index + 1, 0, duplicatedComponent);
        setComponents(newComponents);
    };

    // 移动组件
    const handleMoveComponent = (index: number, direction: 'up' | 'down') => {
        if (
            (direction === 'up' && index === 0) ||
            (direction === 'down' && index === components.length - 1)
        ) {
            return;
        }

        const newComponents = [...components];
        const newIndex = direction === 'up' ? index - 1 : index + 1;

        [newComponents[index], newComponents[newIndex]] =
            [newComponents[newIndex], newComponents[index]];

        setComponents(newComponents);
    };

    // 编辑组件
    const handleEditComponent = (component: ComponentItem) => {
        setEditingComponent(component);

        // 解析组件参数
        const paramRegex = /\{\{\s*([^{}|]+)(?:\|default\(['"](.*?)['"]\))?\s*\}\}/g;
        const params: Record<string, any> = {};
        let match;

        // 重置正则索引
        paramRegex.lastIndex = 0;

        // 从组件HTML中提取所有参数
        while ((match = paramRegex.exec(component.html)) !== null) {
            const paramName = match[1].trim();
            const defaultValue = match[2] || '';
            params[paramName] = defaultValue;
        }

        // 设置表单值
        form.setFieldsValue({
            content: component.content,
            ...params
        });

        setEditModalVisible(true);
    };

    // 保存编辑的组件
    const handleSaveEditedComponent = () => {
        form.validateFields().then(values => {
            if (!editingComponent) return;

            // 获取组件内容和参数
            const { content, ...params } = values;

            // 创建更新后的组件
            const updatedComponents = components.map(comp => {
                if (comp.id === editingComponent.id) {
                    // 替换参数
                    let updatedContent = content;

                    // 使用正则表达式替换所有参数
                    Object.entries(params).forEach(([key, value]) => {
                        const paramRegex = new RegExp(`\\{\\{\\s*${key}(?:\\|default\\(['"].*?['"]\\))?\\s*\\}\\}`, 'g');
                        updatedContent = updatedContent.replace(paramRegex, String(value));
                    });

                    return {
                        ...comp,
                        content: updatedContent,
                        params
                    };
                }
                return comp;
            });

            setComponents(updatedComponents);
            setEditModalVisible(false);
            setEditingComponent(null);
        });
    };

    // 生成预览
    const handlePreview = async () => {
        try {
            setPreviewLoading(true);

            // 将所有组件内容合并为一个完整的HTML
            let combinedHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告预览</title>
  <style>
    * {
      box-sizing: border-box;
      font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
      margin: 0;
      padding: 0;
    }
    body {
      margin: 0 auto;
      padding: 20px;
      max-width: 800px;
      line-height: 1.5;
      color: #333;
      background-color: #fff;
    }
  </style>
</head>
<body>
${components.map(comp => comp.content).join('\n')}
</body>
</html>`;

            setPreviewHtml(combinedHtml);
            setPreviewVisible(true);
        } catch (error) {
            console.error('Failed to generate preview:', error);
            message.error('生成预览失败');
        } finally {
            setPreviewLoading(false);
        }
    };

    // 保存模板
    const handleSaveTemplate = () => {
        // 将所有组件内容合并为一个完整的HTML
        let combinedHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告模板</title>
  <style>
    * {
      box-sizing: border-box;
      font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
      margin: 0;
      padding: 0;
    }
    body {
      margin: 0 auto;
      padding: 20px;
      max-width: 800px;
      line-height: 1.5;
      color: #333;
      background-color: #fff;
    }
  </style>
</head>
<body>
${components.map(comp => comp.content).join('\n')}
</body>
</html>`;

        onSave(components, combinedHtml);
    };

    // 保存模板到库中
    const handleSaveTemplateToLibrary = async () => {
        if (!saveTemplateName.trim()) {
            message.error('请输入模板名称');
            return;
        }

        try {
            setSavingTemplate(true);

            const templateData = {
                name: saveTemplateName.trim(),
                components: components,
                html_content: components.map(comp => comp.content).join('\n')
            };

            await apiService.create('/report-templates/designer-templates', templateData);
            message.success('模板已成功保存到库中');
            setSaveTemplateVisible(false);
            setSaveTemplateName('');

            // 刷新模板列表
            fetchSavedTemplates();
        } catch (error) {
            console.error('保存模板失败:', error);
            message.error('保存模板失败');
        } finally {
            setSavingTemplate(false);
        }
    };

    // 从库中加载模板
    const handleLoadTemplateFromLibrary = async () => {
        if (!selectedTemplateId) {
            message.error('请选择要加载的模板');
            return;
        }

        try {
            setLoadingTemplateContent(true);

            const templateData = await apiService.getDetail('/report-templates/designer-templates', selectedTemplateId);

            if (templateData && templateData.components) {
                setComponents(templateData.components);
                message.success('模板已成功加载');
                setLoadTemplateVisible(false);
                setSelectedTemplateId(null);
            } else {
                throw new Error('模板数据格式错误');
            }
        } catch (error) {
            console.error('加载模板失败:', error);
            message.error('加载模板失败');
        } finally {
            setLoadingTemplateContent(false);
        }
    };

    // 加载默认模板
    const loadDefaultTemplate = async () => {
        try {
            setPreviewLoading(true);
            message.loading('正在加载默认模板...');

            // 使用正确的API路径
            const response = await axios.get('/report-templates/default-template', {
                responseType: 'text',  // 确保以文本方式接收响应
                headers: {
                    'Accept': 'text/html,text/plain',
                    'Content-Type': 'text/plain'  // 明确指定内容类型
                }
            });

            if (response && response.data) {
                const templateHtml = response.data;
                console.log("获取到的模板内容:", templateHtml.substring(0, 100) + "...");  // 记录模板内容前100字符用于调试

                // 解析默认模板并转换为组件
                const parser = new DOMParser();
                const doc = parser.parseFromString(templateHtml, 'text/html');
                const body = doc.querySelector('body');

                if (body) {
                    const componentElements = Array.from(body.children);
                    // @ts-ignore
                    const newComponents: ComponentItem[] = componentElements.map((element, index) => {
                        // 查找组件标记注释节点
                        let componentType = 'text';
                        let componentId = `default_${index}`;

                        // 查找组件注释标记
                        let prevNode = element.previousSibling;
                        while (prevNode) {
                            if (prevNode.nodeType === 8) { // 注释节点
                                const commentContent = prevNode.textContent || '';
                                const componentMatch = commentContent.match(/component:(\w+) id:([a-zA-Z0-9_-]+)/);
                                if (componentMatch) {
                                    componentType = componentMatch[1];
                                    componentId = componentMatch[2];
                                    break;
                                }
                            }
                            prevNode = prevNode.previousSibling;
                        }

                        return {
                            id: `${componentType}_${componentId}_${Date.now() + index}`,
                            type: componentType,
                            name: componentId,
                            html: element.outerHTML,
                            content: element.outerHTML,
                            params: {}
                        };
                    });

                    setComponents(newComponents);
                    message.success('已加载默认模板');
                } else {
                    message.error('加载默认模板失败: 无法解析HTML');
                }
            }
        } catch (error) {
            console.error('Failed to load default template:', error);
            if (axios.isAxiosError(error)) {
                const statusCode = error.response?.status;
                const errorMessage = error.response?.data?.detail || error.message;
                console.log("错误详情:", error.response?.data);  // 打印完整错误信息
                message.error(`加载默认模板失败(${statusCode}): ${errorMessage}`);
            } else if (error instanceof Error) {
                message.error(`加载默认模板失败: ${error.message}`);
            } else {
                message.error('加载默认模板失败: 未知错误');
            }
        } finally {
            setPreviewLoading(false);
        }
    };

    return (
        <div>
            <Card
                title="模板设计器"
                extra={
                    <Space>
                        <Button
                            onClick={() => setComponentLibraryVisible(true)}
                            icon={<PlusOutlined />}
                        >
                            添加组件
                        </Button>
                        <Button
                            onClick={loadDefaultTemplate}
                            icon={<CloudDownloadOutlined />}
                        >
                            加载默认模板
                        </Button>
                        <Tooltip title="保存模板到库中以便后续使用">
                            <Button
                                onClick={() => setSaveTemplateVisible(true)}
                                icon={<CloudUploadOutlined />}
                            >
                                保存到库
                            </Button>
                        </Tooltip>
                        <Tooltip title="从已保存的模板库中加载">
                            <Button
                                onClick={() => setLoadTemplateVisible(true)}
                                icon={<FileOutlined />}
                            >
                                从库加载
                            </Button>
                        </Tooltip>
                        <Button
                            onClick={handlePreview}
                            loading={previewLoading}
                            icon={<EyeOutlined />}
                        >
                            预览
                        </Button>
                        <Button
                            type="primary"
                            onClick={handleSaveTemplate}
                            icon={<SaveOutlined />}
                        >
                            保存模板
                        </Button>
                    </Space>
                }
            >
                {components.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                        <Text type="secondary">暂无组件，请点击"添加组件"按钮从组件库中选择组件</Text>
                        <div style={{ marginTop: '20px' }}>
                            <Button
                                type="primary"
                                onClick={() => setComponentLibraryVisible(true)}
                                icon={<PlusOutlined />}
                            >
                                添加组件
                            </Button>
                            <Button
                                style={{ marginLeft: '10px' }}
                                onClick={loadDefaultTemplate}
                            >
                                加载默认模板
                            </Button>
                            <Button
                                style={{ marginLeft: '10px' }}
                                onClick={() => setLoadTemplateVisible(true)}
                            >
                                从库加载
                            </Button>
                        </div>
                    </div>
                ) : (
                    <DragDropContext onDragEnd={handleDragEnd}>
                        <Droppable droppableId="template-components">
                            {(provided) => (
                                <div
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                    style={{ minHeight: '200px' }}
                                >
                                    {components.map((component, index) => (
                                        <Draggable
                                            key={component.id}
                                            draggableId={component.id}
                                            index={index}
                                        >
                                            {(provided) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                    {...provided.dragHandleProps}
                                                    style={{
                                                        marginBottom: '10px',
                                                        border: '1px solid #f0f0f0',
                                                        borderRadius: '4px',
                                                        backgroundColor: 'white',
                                                        ...provided.draggableProps.style
                                                    }}
                                                >
                                                    <Collapse>
                                                        <Panel
                                                            header={
                                                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                                                    <span>{`${index + 1}. ${component.type} - ${component.name}`}</span>
                                                                    <Tag color="blue" style={{ marginLeft: '8px' }}>{component.type}</Tag>
                                                                </div>
                                                            }
                                                            key={component.id}
                                                            extra={
                                                                <Space>
                                                                    <Tooltip title="上移">
                                                                        <Button
                                                                            size="small"
                                                                            icon={<ArrowUpOutlined />}
                                                                            disabled={index === 0}
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleMoveComponent(index, 'up');
                                                                            }}
                                                                        />
                                                                    </Tooltip>
                                                                    <Tooltip title="下移">
                                                                        <Button
                                                                            size="small"
                                                                            icon={<ArrowDownOutlined />}
                                                                            disabled={index === components.length - 1}
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleMoveComponent(index, 'down');
                                                                            }}
                                                                        />
                                                                    </Tooltip>
                                                                    <Tooltip title="编辑">
                                                                        <Button
                                                                            size="small"
                                                                            icon={<EditOutlined />}
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleEditComponent(component);
                                                                            }}
                                                                        />
                                                                    </Tooltip>
                                                                    <Tooltip title="复制">
                                                                        <Button
                                                                            size="small"
                                                                            icon={<CopyOutlined />}
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleDuplicateComponent(index);
                                                                            }}
                                                                        />
                                                                    </Tooltip>
                                                                    <Tooltip title="删除">
                                                                        <Button
                                                                            size="small"
                                                                            danger
                                                                            icon={<DeleteOutlined />}
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleDeleteComponent(index);
                                                                            }}
                                                                        />
                                                                    </Tooltip>
                                                                </Space>
                                                            }
                                                        >
                                                            <div dangerouslySetInnerHTML={{ __html: component.content }} />
                                                        </Panel>
                                                    </Collapse>
                                                </div>
                                            )}
                                        </Draggable>
                                    ))}
                                    {provided.placeholder}
                                </div>
                            )}
                        </Droppable>
                    </DragDropContext>
                )}
            </Card>

            {/* 组件库模态框 */}
            <Modal
                title="组件库"
                open={componentLibraryVisible}
                onCancel={() => setComponentLibraryVisible(false)}
                width={800}
                footer={null}
            >
                <TemplateComponentLibrary onSelectComponent={handleAddComponent} />
            </Modal>

            {/* 组件编辑模态框 */}
            <Modal
                title="编辑组件"
                open={editModalVisible}
                onCancel={() => setEditModalVisible(false)}
                onOk={handleSaveEditedComponent}
            >
                <Form form={form} layout="vertical">
                    <Form.Item
                        name="content"
                        label="组件内容"
                    >
                        <TextArea rows={10} />
                    </Form.Item>

                    {/* 动态生成参数表单项 */}
                    {editingComponent && (
                        <>
                            <Divider>组件参数</Divider>
                            {/* 解析组件HTML并提取参数 */}
                            {(() => {
                                const paramRegex = /\{\{\s*([^{}|]+)(?:\|default\(['"](.*?)['"]\))?\s*\}\}/g;
                                const params: string[] = [];
                                let match;

                                // 重置正则索引
                                paramRegex.lastIndex = 0;

                                // 提取所有参数名
                                while ((match = paramRegex.exec(editingComponent.html)) !== null) {
                                    const paramName = match[1].trim();
                                    if (!params.includes(paramName)) {
                                        params.push(paramName);
                                    }
                                }

                                // 为每个参数创建表单项
                                return params.map(param => (
                                    <Form.Item
                                        key={param}
                                        name={param}
                                        label={`参数: ${param}`}
                                    >
                                        <Input placeholder={`输入${param}的值`} />
                                    </Form.Item>
                                ));
                            })()}
                        </>
                    )}
                </Form>
            </Modal>

            {/* 预览模态框 */}
            {previewVisible && (
                <Modal
                    title="模板预览"
                    open={previewVisible}
                    onCancel={() => setPreviewVisible(false)}
                    width={800}
                    footer={[
                        <Button key="close" onClick={() => setPreviewVisible(false)}>
                            关闭
                        </Button>
                    ]}
                >
                    <div style={{ height: '600px', border: '1px solid #f0f0f0' }}>
                        <iframe
                            srcDoc={previewHtml}
                            style={{ width: '100%', height: '100%', border: 'none' }}
                            title="模板预览"
                        />
                    </div>
                </Modal>
            )}

            {/* 保存模板到库模态框 */}
            <Modal
                title="保存模板到库"
                open={saveTemplateVisible}
                onCancel={() => setSaveTemplateVisible(false)}
                onOk={handleSaveTemplateToLibrary}
                confirmLoading={savingTemplate}
            >
                <Form layout="vertical">
                    <Form.Item
                        label="模板名称"
                        required
                        rules={[{ required: true, message: '请输入模板名称' }]}
                    >
                        <Input
                            placeholder="输入一个描述性的模板名称"
                            value={saveTemplateName}
                            onChange={(e) => setSaveTemplateName(e.target.value)}
                        />
                    </Form.Item>
                    <Text type="secondary">保存后可以在以后的编辑中重复使用此模板</Text>
                </Form>
            </Modal>

            {/* 从库加载模板模态框 */}
            <Modal
                title="从库加载模板"
                open={loadTemplateVisible}
                onCancel={() => setLoadTemplateVisible(false)}
                onOk={handleLoadTemplateFromLibrary}
                confirmLoading={loadingTemplateContent}
            >
                {loadingTemplates ? (
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Spin tip="加载模板列表..." />
                    </div>
                ) : (
                    <Form layout="vertical">
                        <Form.Item
                            label="选择模板"
                            required
                        >
                            <Select
                                placeholder="选择要加载的模板"
                                style={{ width: '100%' }}
                                value={selectedTemplateId}
                                onChange={(value) => setSelectedTemplateId(value)}
                            >
                                {savedTemplates.map(template => (
                                    <Option key={template.id} value={template.id}>{template.name}</Option>
                                ))}
                            </Select>
                        </Form.Item>
                        {savedTemplates.length === 0 && (
                            <div style={{ textAlign: 'center' }}>
                                <Text type="secondary">暂无保存的模板</Text>
                            </div>
                        )}
                        <Text type="secondary">选择一个已保存的模板进行加载，将替换当前设计器中的所有组件</Text>
                    </Form>
                )}
            </Modal>
        </div>
    );
};

export default TemplateDesigner; 