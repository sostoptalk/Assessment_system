import React, { useState, useEffect } from 'react';
import { Card, Tabs, Collapse, Button, Tooltip, message, Spin, Empty } from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import api, { apiService } from '../utils/api';

const { TabPane } = Tabs;
const { Panel } = Collapse;

interface ComponentItem {
    name: string;
    description: string;
    html: string;
}

interface ComponentLibraryProps {
    onSelectComponent: (componentType: string, componentId: string, componentHtml: string) => void;
}

const TemplateComponentLibrary: React.FC<ComponentLibraryProps> = ({ onSelectComponent }) => {
    const [components, setComponents] = useState<Record<string, Record<string, ComponentItem>>>({});
    const [loading, setLoading] = useState(false);
    const [previewHtml, setPreviewHtml] = useState<string | null>(null);
    const [previewVisible, setPreviewVisible] = useState(false);
    const [activeKey, setActiveKey] = useState('header');

    // 组件类型中文名称映射
    const componentTypeNames: Record<string, string> = {
        header: '页眉',
        text: '文本段落',
        chart: '图表',
        dimension: '维度展示',
        scorecard: '评分卡',
        summary: '总结',
        footer: '页脚',
        table: '表格'
    };

    // 加载组件库
    useEffect(() => {
        fetchComponents();
    }, []);

    const fetchComponents = async () => {
        try {
            setLoading(true);
            const response = await apiService.getList('/report-templates/components');
            setComponents(response);
        } catch (error) {
            console.error('Failed to fetch components:', error);
            message.error('获取组件库失败');
        } finally {
            setLoading(false);
        }
    };

    // 预览组件
    const handlePreview = (html: string) => {
        setPreviewHtml(html);
        setPreviewVisible(true);
    };

    // 添加组件
    const handleAddComponent = (type: string, id: string, html: string) => {
        onSelectComponent(type, id, html);
        message.success(`已添加组件: ${components[type]?.[id]?.name || id}`);
    };

    // 渲染组件列表
    const renderComponentList = (type: string) => {
        const typeComponents = components[type] || {};

        if (Object.keys(typeComponents).length === 0) {
            return <Empty description="暂无组件" />;
        }

        return (
            <Collapse defaultActiveKey={[]}>
                {Object.entries(typeComponents).map(([id, component]) => (
                    <Panel
                        header={
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                                <span>{component.name}</span>
                                <span style={{ fontSize: '12px', color: '#888' }}>{component.description}</span>
                            </div>
                        }
                        key={id}
                    >
                        <div style={{ marginBottom: '10px' }}>
                            <div dangerouslySetInnerHTML={{ __html: component.html }} />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                            <Tooltip title="预览组件">
                                <Button
                                    icon={<EyeOutlined />}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handlePreview(component.html);
                                    }}
                                >
                                    预览
                                </Button>
                            </Tooltip>
                            <Tooltip title="添加到模板">
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleAddComponent(type, id, component.html);
                                    }}
                                >
                                    添加
                                </Button>
                            </Tooltip>
                        </div>
                    </Panel>
                ))}
            </Collapse>
        );
    };

    return (
        <Card title="组件库" style={{ marginBottom: '20px' }}>
            {loading ? (
                <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Spin tip="加载组件库..." />
                </div>
            ) : (
                <Tabs activeKey={activeKey} onChange={setActiveKey}>
                    {Object.keys(componentTypeNames).map(type => (
                        <TabPane tab={componentTypeNames[type]} key={type}>
                            {renderComponentList(type)}
                        </TabPane>
                    ))}
                </Tabs>
            )}

            {previewVisible && previewHtml && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        zIndex: 1000
                    }}
                    onClick={() => setPreviewVisible(false)}
                >
                    <div
                        style={{
                            backgroundColor: 'white',
                            padding: '20px',
                            borderRadius: '4px',
                            maxWidth: '80%',
                            maxHeight: '80%',
                            overflow: 'auto'
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
                        <div style={{ textAlign: 'right', marginTop: '20px' }}>
                            <Button onClick={() => setPreviewVisible(false)}>关闭</Button>
                        </div>
                    </div>
                </div>
            )}
        </Card>
    );
};

export default TemplateComponentLibrary; 