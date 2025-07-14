import React, { useState, useEffect } from 'react';
import {
    Table,
    Button,
    Modal,
    Form,
    Input,
    InputNumber,
    Space,
    Popconfirm,
    message,
    Tag,
    Card,
    Row,
    Col,
    Select,
    Transfer,
    List,
    Empty,
    Divider,
    Checkbox,
    Upload,
    Tree,
    TreeSelect,
    Collapse
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    EyeOutlined,
    SendOutlined,
    UserOutlined,
    FolderOutlined,
    FileOutlined,
    TeamOutlined,
    ReloadOutlined,
    MinusCircleOutlined
} from '@ant-design/icons';
import type { TransferDirection } from 'antd/es/transfer';

const { TextArea } = Input;
const { Option } = Select;

interface Paper {
    id: number;
    name: string;
    description?: string;
    duration: number;
    status: string;
    created_at: string;
    updated_at: string;
}

interface Question {
    id: number;
    content: string;
    type: string;
    options: string[];
    scores: number[];
}

interface User {
    id: number;
    username: string;
    real_name: string;
    role: string;
}

interface Dimension {
    id: number;
    paper_id: number;
    parent_id?: number;
    name: string;
    description?: string;
    weight: number;
    order_num: number;
    created_at: string;
    updated_at: string;
    children?: Dimension[];
}

const PaperManagement: React.FC = () => {
    const [papers, setPapers] = useState<Paper[]>([]);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingPaper, setEditingPaper] = useState<Paper | null>(null);
    const [form] = Form.useForm();
    const [questionModalVisible, setQuestionModalVisible] = useState(false);
    const [currentPaperId, setCurrentPaperId] = useState<number | null>(null);
    const [selectedQuestions, setSelectedQuestions] = useState<number[]>([]);
    const [paperQuestions, setPaperQuestions] = useState<any[]>([]);
    const [assignModalVisible, setAssignModalVisible] = useState(false);
    const [assignPaperId, setAssignPaperId] = useState<number | null>(null);
    const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
    const [questionModalMode, setQuestionModalMode] = useState<'view' | 'add' | 'manual' | 'import'>('view');
    const [selectedPaperQuestions, setSelectedPaperQuestions] = useState<number[]>([]);
    const [manualQuestionForm] = Form.useForm();
    const [importLoading, setImportLoading] = useState(false);
    const [manualOptions, setManualOptions] = useState(['', '', '', '']);
    const [manualScores, setManualScores] = useState([10, 7, 4, 1]);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [importedQuestions, setImportedQuestions] = useState<any[]>([]);
    const [importShuffleOptions, setImportShuffleOptions] = useState(false);
    const [editQuestionModalVisible, setEditQuestionModalVisible] = useState(false);
    const [editingQuestion, setEditingQuestion] = useState<any>(null);
    const [editQuestionForm] = Form.useForm();

    // 乱序相关状态
    const [shuffleStatus, setShuffleStatus] = useState<{
        is_shuffled: boolean;
        shuffle_seed?: number;
        question_count: number;
    } | null>(null);
    const [shuffleLoading, setShuffleLoading] = useState(false);

    // 维度相关状态
    const [dimensions, setDimensions] = useState<Dimension[]>([]);
    const [dimensionModalVisible, setDimensionModalVisible] = useState(false);
    const [editingDimension, setEditingDimension] = useState<Dimension | null>(null);
    const [dimensionForm] = Form.useForm();
    const [currentPaperForDimension, setCurrentPaperForDimension] = useState<number | null>(null);
    const [showDimensionForm, setShowDimensionForm] = useState(false);

    // 维度题目匹配相关状态
    const [dimensionQuestionModalVisible, setDimensionQuestionModalVisible] = useState(false);
    const [currentDimensionForQuestion, setCurrentDimensionForQuestion] = useState<Dimension | null>(null);
    const [availableQuestions, setAvailableQuestions] = useState<Question[]>([]);
    const [selectedQuestionsForDimension, setSelectedQuestionsForDimension] = useState<number[]>([]);
    const [matchedQuestions, setMatchedQuestions] = useState<Question[]>([]);

    // 获取试卷列表
    const fetchPapers = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/papers/');
            if (response.ok) {
                const data = await response.json();
                setPapers(data);
            } else {
                message.error('获取试卷列表失败');
            }
        } catch (error) {
            message.error('网络错误');
        } finally {
            setLoading(false);
        }
    };

    // 获取题目列表
    const fetchQuestions = async () => {
        try {
            const response = await fetch('http://localhost:8000/questions');
            if (response.ok) {
                const data = await response.json();
                setQuestions(data);
            }
        } catch (error) {
            console.error('获取题目列表失败:', error);
        }
    };

    // 获取用户列表
    const fetchUsers = async () => {
        try {
            const response = await fetch('http://localhost:8000/users');
            if (response.ok) {
                const data = await response.json();
                setUsers(data.filter((user: User) => user.role === 'participant'));
            }
        } catch (error) {
            console.error('获取用户列表失败:', error);
        }
    };

    // 获取试卷维度
    const fetchPaperDimensions = async (paperId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/paper/${paperId}`);
            if (response.ok) {
                const data = await response.json();
                setDimensions(data);
            } else {
                message.error('获取维度失败');
            }
        } catch (error) {
            console.error('获取维度失败:', error);
            message.error('获取维度失败');
        }
    };

    // 获取乱序状态
    const fetchShuffleStatus = async (paperId: number) => {
        try {
            const token = localStorage.getItem('token') || '';
            const response = await fetch(`http://localhost:8000/papers/${paperId}/shuffle-status`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setShuffleStatus(data);
            } else {
                console.error('获取乱序状态失败');
            }
        } catch (error) {
            console.error('获取乱序状态失败:', error);
        }
    };

    // 切换乱序状态
    const toggleShuffle = async (paperId: number, enableShuffle: boolean) => {
        setShuffleLoading(true);
        try {
            const token = localStorage.getItem('token') || '';
            const response = await fetch(`http://localhost:8000/papers/${paperId}/shuffle-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ enable_shuffle: enableShuffle })
            });

            if (response.ok) {
                const data = await response.json();
                message.success(data.message);
                // 重新获取乱序状态
                await fetchShuffleStatus(paperId);
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '操作失败');
            }
        } catch (error) {
            console.error('切换乱序状态失败:', error);
            message.error('网络错误');
        } finally {
            setShuffleLoading(false);
        }
    };

    // 创建维度
    const createDimension = async (values: any) => {
        try {
            const response = await fetch('http://localhost:8000/dimensions/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(values),
            });
            if (response.ok) {
                message.success('维度创建成功');
                setDimensionModalVisible(false);
                dimensionForm.resetFields();
                setShowDimensionForm(false);
                if (currentPaperForDimension) {
                    fetchPaperDimensions(currentPaperForDimension);
                }
            } else {
                message.error('维度创建失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 更新维度
    const updateDimension = async (values: any) => {
        if (!editingDimension) return;
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${editingDimension.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(values),
            });
            if (response.ok) {
                message.success('维度更新成功');
                setDimensionModalVisible(false);
                setEditingDimension(null);
                dimensionForm.resetFields();
                setShowDimensionForm(false);
                if (currentPaperForDimension) {
                    fetchPaperDimensions(currentPaperForDimension);
                }
            } else {
                message.error('维度更新失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 删除维度
    const deleteDimension = async (dimensionId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                message.success('维度删除成功');
                if (currentPaperForDimension) {
                    fetchPaperDimensions(currentPaperForDimension);
                }
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '维度删除失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 获取维度可匹配的题目
    const fetchAvailableQuestionsForDimension = async (dimensionId: number, paperId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}/available-questions?paper_id=${paperId}`);
            if (response.ok) {
                const data = await response.json();
                setAvailableQuestions(data);
            } else {
                const errorData = await response.json();
                if (response.status === 400 && errorData.detail?.includes('有子维度')) {
                    message.warning('该维度有子维度，请为子维度匹配题目');
                    setDimensionQuestionModalVisible(false);
                } else {
                    message.error('获取可匹配题目失败');
                }
            }
        } catch (error) {
            console.error('获取可匹配题目失败:', error);
            message.error('获取可匹配题目失败');
        }
    };

    // 获取试卷已匹配的题目
    const fetchMatchedQuestionsForDimension = async (dimensionId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}/matched-questions`);
            if (response.ok) {
                const data = await response.json();
                setMatchedQuestions(data);
            } else {
                setMatchedQuestions([]);
            }
        } catch (error) {
            setMatchedQuestions([]);
        }
    };

    // 匹配题目到维度
    const matchQuestionsToDimension = async () => {
        if (!currentDimensionForQuestion || selectedQuestionsForDimension.length === 0) return;

        try {
            const response = await fetch(`http://localhost:8000/dimensions/${currentDimensionForQuestion.id}/match-questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_ids: selectedQuestionsForDimension }),
            });
            if (response.ok) {
                message.success(`成功匹配 ${selectedQuestionsForDimension.length} 道题目到维度`);
                setSelectedQuestionsForDimension([]);
                if (currentDimensionForQuestion && currentPaperForDimension !== null) {
                    fetchAvailableQuestionsForDimension(currentDimensionForQuestion.id, currentPaperForDimension);
                }
                fetchMatchedQuestionsForDimension(currentDimensionForQuestion.id);
                // 刷新维度列表
                if (currentPaperForDimension) {
                    fetchPaperDimensions(currentPaperForDimension);
                }
            } else {
                const errorData = await response.json();
                if (response.status === 400) {
                    if (errorData.detail?.includes('有子维度')) {
                        message.warning('该维度有子维度，请为子维度匹配题目');
                    } else if (errorData.detail?.includes('已被其他维度匹配')) {
                        message.warning('部分题目已被其他维度匹配，请重新选择');
                        // 刷新可匹配题目列表
                        if (currentDimensionForQuestion && currentPaperForDimension !== null) {
                            fetchAvailableQuestionsForDimension(currentDimensionForQuestion.id, currentPaperForDimension);
                        }
                    } else {
                        message.error(errorData.detail || '匹配题目失败');
                    }
                } else {
                    message.error('匹配题目失败');
                }
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 获取试卷题目
    const fetchPaperQuestions = async (paperId: number) => {
        try {
            console.log('开始获取试卷题目，试卷ID:', paperId);
            const response = await fetch(`http://localhost:8000/papers/${paperId}/questions/`);
            if (response.ok) {
                const data = await response.json();
                const questions = data.questions || [];
                console.log('获取到题目数据:', questions);
                setPaperQuestions(questions);
                console.log('题目状态已更新，题目数:', questions.length);
            } else {
                message.error('获取试卷题目失败');
                console.error('获取题目失败，状态码:', response.status);
            }
        } catch (error) {
            message.error('网络错误');
            console.error('获取题目网络错误:', error);
        }
    };

    // 移除题目与维度的归属
    const removeQuestionFromDimension = async (dimensionId: number, questionId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}/remove-question`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(questionId),
            });
            if (response.ok) {
                message.success('移除成功');
                // 刷新
                fetchMatchedQuestionsForDimension(dimensionId);
                if (currentDimensionForQuestion && currentPaperForDimension !== null) {
                    fetchAvailableQuestionsForDimension(currentDimensionForQuestion.id, currentPaperForDimension);
                }
            } else {
                message.error('移除失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    useEffect(() => {
        fetchPapers();
        fetchQuestions();
        fetchUsers();
    }, []);

    // 创建或更新试卷
    const handleSubmit = async (values: any) => {
        try {
            if (editingPaper) {
                // 更新试卷
                const response = await fetch(`http://localhost:8000/papers/${editingPaper.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values),
                });
                if (response.ok) {
                    message.success('试卷更新成功');
                    setModalVisible(false);
                    setEditingPaper(null);
                    form.resetFields();
                    fetchPapers();
                } else {
                    message.error('更新失败');
                }
            } else {
                // 创建试卷
                const response = await fetch('http://localhost:8000/papers/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values),
                });
                if (response.ok) {
                    message.success('试卷创建成功');
                    setModalVisible(false);
                    form.resetFields();
                    fetchPapers();
                } else {
                    message.error('创建失败');
                }
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 删除试卷
    const handleDelete = async (id: number) => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${id}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                message.success('删除成功');
                fetchPapers();
            } else {
                message.error('删除失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 发布试卷
    const handlePublish = async (id: number) => {
        Modal.confirm({
            title: '确认发布试卷',
            content: '发布试卷将自动分配给所有被试者，是否继续？',
            onOk: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/papers/${id}/publish/`, {
                        method: 'POST',
                    });
                    if (response.ok) {
                        message.success('发布成功，已分配给所有被试者');
                        fetchPapers();
                    } else {
                        message.error('发布失败');
                    }
                } catch (error) {
                    message.error('网络错误');
                }
            },
        });
    };

    // 添加题目到试卷
    const handleAddQuestions = async () => {
        if (!currentPaperId || selectedQuestions.length === 0) return;

        try {
            // 转换为后端期望的格式
            const questionsData = selectedQuestions.map(questionId => ({
                question_id: questionId,
                dimension_id: null // 暂时不设置维度，后续可以扩展
            }));

            const response = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(questionsData),
            });
            if (response.ok) {
                message.success('题目添加成功');
                setSelectedQuestions([]);
                setQuestionModalMode('view');
                // 刷新题目列表
                console.log('刷新题目列表，试卷ID:', currentPaperId);
                await fetchPaperQuestions(currentPaperId);
                console.log('题目列表刷新完成，当前题目数:', paperQuestions.length);
            } else {
                message.error('添加失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('添加题目错误:', error);
        }
    };

    // 批量删除试卷题目
    const handleDeletePaperQuestions = async () => {
        if (!currentPaperId || selectedPaperQuestions.length === 0) return;

        try {
            const response = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_ids: selectedPaperQuestions }),
            });
            if (response.ok) {
                message.success(`成功删除 ${selectedPaperQuestions.length} 道题目`);
                setSelectedPaperQuestions([]);
                // 刷新题目列表
                await fetchPaperQuestions(currentPaperId);
            } else {
                message.error('删除失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('删除题目错误:', error);
        }
    };

    // 编辑试卷题目
    const handleEditPaperQuestion = (question: any) => {
        setEditingQuestion(question);

        // 确保options是数组格式
        let options = question.options;

        // 如果是字符串，尝试解析为JSON
        if (typeof options === 'string') {
            try {
                options = JSON.parse(options);
            } catch (e) {
                console.error('解析options失败:', e);
                options = [];
            }
        }

        // 确保是数组
        if (!Array.isArray(options)) {
            options = [];
        }

        // 处理options格式：如果是对象数组（包含label、text、score），转换为简单字符串数组
        let processedOptions: string[] = [];
        let processedScores: number[] = [];

        if (options.length > 0 && typeof options[0] === 'object' && options[0].hasOwnProperty('text')) {
            // 如果是对象数组格式，提取text和score字段
            processedOptions = options.map((opt: any) => opt.text || '');
            processedScores = options.map((opt: any) => opt.score || 0);
        } else if (Array.isArray(options)) {
            // 如果是简单字符串数组
            processedOptions = options;
            processedScores = question.scores || [];
        }

        editQuestionForm.setFieldsValue({
            content: question.content,
            type: question.type,
            shuffle_options: question.shuffle_options || false,
            options: processedOptions,
            scores: processedScores
        });
        setEditQuestionModalVisible(true);
    };

    // 保存编辑的题目
    const handleSaveEditQuestion = async (values: any) => {
        if (!editingQuestion) return;

        try {
            // 确保options和scores是数组格式
            let options = values.options;
            let scores = values.scores;

            // 确保是数组
            if (!Array.isArray(options)) {
                options = [];
            }
            if (!Array.isArray(scores)) {
                scores = [];
            }

            // 过滤掉空的选项
            const validOptions = options.filter((opt: string) => opt && opt.trim() !== '');
            const validScores = scores.slice(0, validOptions.length);

            const response = await fetch(`http://localhost:8000/questions/${editingQuestion.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: values.content,
                    type: values.type,
                    options: validOptions,
                    scores: validScores,
                    shuffle_options: values.shuffle_options || false
                }),
            });

            if (response.ok) {
                message.success('题目更新成功');
                setEditQuestionModalVisible(false);
                setEditingQuestion(null);
                editQuestionForm.resetFields();
                // 刷新题目列表
                if (currentPaperId) {
                    await fetchPaperQuestions(currentPaperId);
                }
            } else {
                message.error('更新题目失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('更新题目错误:', error);
        }
    };

    // 手动添加题目到试卷
    const handleManualAddQuestion = async (values: any) => {
        if (!currentPaperId) return;

        const requestData = {
            content: values.content,
            type: values.type,
            options: manualOptions,
            scores: manualScores,
            shuffle_options: values.shuffle_options || false
        };

        console.log('发送的题目数据:', requestData);

        try {
            // 先创建题目
            const createResponse = await fetch('http://localhost:8000/questions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });

            if (createResponse.ok) {
                const newQuestion = await createResponse.json();

                // 将新题目添加到试卷
                const addResponse = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify([{
                        question_id: newQuestion.id,
                        dimension_id: null
                    }]),
                });

                if (addResponse.ok) {
                    message.success('题目添加成功');
                    manualQuestionForm.resetFields();
                    setQuestionModalMode('view');
                    // 刷新题目列表
                    await fetchPaperQuestions(currentPaperId);
                } else {
                    message.error('添加到试卷失败');
                }
            } else {
                message.error('创建题目失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('手动添加题目错误:', error);
        }
    };

    // 从Word文档导入题目
    const handleImportFromWord = async (file: File) => {
        if (!currentPaperId) return;

        setImportLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://localhost:8000/questions/import_word', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                const questions = data.questions || [];

                if (questions.length === 0) {
                    message.warning('Word文档中没有找到有效题目');
                    return;
                }

                // 显示导入预览模态框
                setImportedQuestions(questions);
                setImportModalVisible(true);
            } else {
                message.error('解析Word文档失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('导入Word文档错误:', error);
        } finally {
            setImportLoading(false);
        }
    };

    // 确认导入题目
    const handleConfirmImport = async () => {
        if (!currentPaperId || importedQuestions.length === 0) return;

        setImportLoading(true);
        try {
            // 批量创建题目
            const createdQuestionIds = [];
            for (const question of importedQuestions) {
                const questionData = {
                    ...question,
                    shuffle_options: importShuffleOptions
                };

                const createResponse = await fetch('http://localhost:8000/questions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(questionData),
                });

                if (createResponse.ok) {
                    const newQuestion = await createResponse.json();
                    createdQuestionIds.push(newQuestion.id);
                }
            }

            if (createdQuestionIds.length > 0) {
                // 将新题目添加到试卷
                const questionsData = createdQuestionIds.map(questionId => ({
                    question_id: questionId,
                    dimension_id: null
                }));
                const addResponse = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(questionsData),
                });

                if (addResponse.ok) {
                    message.success(`成功导入并添加 ${createdQuestionIds.length} 道题目`);
                    setImportModalVisible(false);
                    setImportedQuestions([]);
                    setImportShuffleOptions(false);
                    setQuestionModalMode('view');
                    // 刷新题目列表
                    await fetchPaperQuestions(currentPaperId);
                } else {
                    message.error('添加到试卷失败');
                }
            } else {
                message.error('导入题目失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('导入题目错误:', error);
        } finally {
            setImportLoading(false);
        }
    };

    // 分配试卷给用户
    const handleAssign = async () => {
        if (!assignPaperId || selectedUserIds.length === 0) return;

        try {
            const response = await fetch(`http://localhost:8000/papers/${assignPaperId}/assign/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_ids: selectedUserIds }),
            });
            if (response.ok) {
                message.success('分配成功');
                setAssignModalVisible(false);
                setSelectedUserIds([]);
                setAssignPaperId(null);
            } else {
                message.error('分配失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 获取试卷分配情况
    const [assignments, setAssignments] = useState<any[]>([]);
    const [assignmentModalVisible, setAssignmentModalVisible] = useState(false);
    const [currentPaperForAssignment, setCurrentPaperForAssignment] = useState<number | null>(null);

    const fetchPaperAssignments = async (paperId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${paperId}/list-assignment`);
            if (response.ok) {
                const data = await response.json();
                setAssignments(data);
            } else {
                message.error('获取分配情况失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    const columns = [
        {
            title: '试卷名称',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: '描述',
            dataIndex: 'description',
            key: 'description',
            render: (text: string) => text || '-',
        },
        {
            title: '答题时间',
            dataIndex: 'duration',
            key: 'duration',
            render: (duration: number) => `${duration}分钟`,
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                const statusMap = {
                    draft: { color: 'default', text: '草稿' },
                    published: { color: 'success', text: '已发布' },
                    closed: { color: 'error', text: '已关闭' },
                };
                const config = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
                return <Tag color={config.color}>{config.text}</Tag>;
            },
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
            render: (_: any, record: Paper) => (
                <Space size="middle">
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => {
                            setEditingPaper(record);
                            form.setFieldsValue(record);
                            setModalVisible(true);
                        }}
                    >
                        编辑
                    </Button>
                    <Button
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={async () => {
                            setCurrentPaperId(record.id);
                            setQuestionModalMode('view');
                            await fetchPaperQuestions(record.id);
                            await fetchShuffleStatus(record.id);
                            setQuestionModalVisible(true);
                        }}
                    >
                        题目
                    </Button>
                    {record.status === 'draft' && (
                        <Button
                            type="link"
                            icon={<SendOutlined />}
                            onClick={() => handlePublish(record.id)}
                        >
                            发布
                        </Button>
                    )}
                    <Button
                        type="link"
                        icon={<UserOutlined />}
                        onClick={() => {
                            setAssignPaperId(record.id);
                            setAssignModalVisible(true);
                        }}
                    >
                        分配
                    </Button>
                    <Button
                        type="link"
                        icon={<TeamOutlined />}
                        onClick={() => {
                            setCurrentPaperForAssignment(record.id);
                            fetchPaperAssignments(record.id);
                            setAssignmentModalVisible(true);
                        }}
                    >
                        分配情况
                    </Button>
                    <Button
                        type="link"
                        icon={<FolderOutlined />}
                        onClick={() => {
                            setCurrentPaperForDimension(record.id);
                            fetchPaperDimensions(record.id);
                            setDimensionModalVisible(true);
                        }}
                    >
                        维度
                    </Button>
                    <Popconfirm
                        title="确定要删除这个试卷吗？"
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
            <Card title="试卷管理" extra={
                <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                        setEditingPaper(null);
                        form.resetFields();
                        setModalVisible(true);
                    }}
                >
                    创建试卷
                </Button>
            }>
                <Table
                    columns={columns}
                    dataSource={papers}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                />
            </Card>

            {/* 创建/编辑试卷模态框 */}
            <Modal
                title={editingPaper ? '编辑试卷' : '创建试卷'}
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false);
                    setEditingPaper(null);
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
                        name="name"
                        label="试卷名称"
                        rules={[{ required: true, message: '请输入试卷名称' }]}
                    >
                        <Input placeholder="请输入试卷名称" />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="试卷描述"
                    >
                        <TextArea rows={3} placeholder="请输入试卷描述" />
                    </Form.Item>
                    <Form.Item
                        name="duration"
                        label="答题时间（分钟）"
                        rules={[{ required: true, message: '请输入答题时间' }]}
                    >
                        <InputNumber min={1} max={480} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                {editingPaper ? '更新' : '创建'}
                            </Button>
                            <Button onClick={() => {
                                setModalVisible(false);
                                setEditingPaper(null);
                                form.resetFields();
                            }}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 题目管理模态框 */}
            <Modal
                title="试卷题目管理"
                open={questionModalVisible}
                onCancel={() => {
                    setQuestionModalVisible(false);
                    setSelectedQuestions([]);
                    setSelectedPaperQuestions([]);
                    setCurrentPaperId(null);
                    setPaperQuestions([]);
                    setQuestionModalMode('view');
                    manualQuestionForm.resetFields();
                    setManualOptions(['', '', '', '']);
                    setManualScores([10, 7, 4, 1]);
                }}
                footer={null}
                width={1200}
            >
                {questionModalMode === 'view' ? (
                    <div>
                        {/* 现有题目列表 */}
                        <div style={{ marginBottom: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <h3>试卷题目列表 (共{paperQuestions.length}题)</h3>
                                    {shuffleStatus && (
                                        <Tag color={shuffleStatus.is_shuffled ? 'green' : 'default'}>
                                            {shuffleStatus.is_shuffled ? '已启用乱序' : '未启用乱序'}
                                        </Tag>
                                    )}
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    {paperQuestions.length > 0 && currentPaperId && (
                                        <Button
                                            type={shuffleStatus?.is_shuffled ? 'default' : 'primary'}
                                            icon={<ReloadOutlined />}
                                            loading={shuffleLoading}
                                            onClick={() => toggleShuffle(currentPaperId, !shuffleStatus?.is_shuffled)}
                                        >
                                            {shuffleStatus?.is_shuffled ? '禁用乱序' : '启用乱序'}
                                        </Button>
                                    )}
                                    {selectedPaperQuestions.length > 0 && (
                                        <Button
                                            type="primary"
                                            danger
                                            onClick={handleDeletePaperQuestions}
                                            icon={<DeleteOutlined />}
                                        >
                                            删除选中题目 ({selectedPaperQuestions.length})
                                        </Button>
                                    )}
                                </div>
                            </div>
                            {paperQuestions.length === 0 ? (
                                <Empty description="暂无题目" />
                            ) : (
                                <>
                                    {/* 全选功能 */}
                                    <div style={{ marginBottom: '12px', padding: '8px 12px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
                                        <Checkbox
                                            checked={selectedPaperQuestions.length === paperQuestions.length && paperQuestions.length > 0}
                                            indeterminate={selectedPaperQuestions.length > 0 && selectedPaperQuestions.length < paperQuestions.length}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    // 全选
                                                    setSelectedPaperQuestions(paperQuestions.map(q => q.id));
                                                } else {
                                                    // 取消全选
                                                    setSelectedPaperQuestions([]);
                                                }
                                            }}
                                        >
                                            全选 ({selectedPaperQuestions.length}/{paperQuestions.length})
                                        </Checkbox>
                                    </div>
                                    <List
                                        dataSource={paperQuestions}
                                        renderItem={(item, index) => (
                                            <List.Item>
                                                <div style={{ width: '100%', display: 'flex', alignItems: 'flex-start' }}>
                                                    <Checkbox
                                                        checked={selectedPaperQuestions.includes(item.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedPaperQuestions([...selectedPaperQuestions, item.id]);
                                                            } else {
                                                                setSelectedPaperQuestions(selectedPaperQuestions.filter(id => id !== item.id));
                                                            }
                                                        }}
                                                        style={{ marginRight: '12px', marginTop: '4px' }}
                                                    />
                                                    <div style={{ flex: 1 }}>
                                                        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                                            题目{index + 1}: {item.content}
                                                        </div>
                                                        <div style={{ color: '#666', fontSize: '12px' }}>
                                                            类型: {item.type} | 选项数: {item.options?.length || 0}
                                                            {item.shuffle_options && (
                                                                <Tag color="green" style={{ marginLeft: '8px' }}>
                                                                    选项乱序
                                                                </Tag>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div style={{ marginLeft: '12px' }}>
                                                        <Button
                                                            type="link"
                                                            size="small"
                                                            icon={<EditOutlined />}
                                                            onClick={() => handleEditPaperQuestion(item)}
                                                        >
                                                            编辑
                                                        </Button>
                                                    </div>
                                                </div>
                                            </List.Item>
                                        )}
                                    />
                                </>
                            )}
                        </div>

                        {/* 添加题目选项 */}
                        <Divider />
                        <div>
                            <h3>添加题目</h3>
                            <Space size="large">
                                <Button
                                    type="primary"
                                    onClick={() => setQuestionModalMode('add')}
                                >
                                    从题库选择题目
                                </Button>
                                <Button
                                    onClick={() => setQuestionModalMode('manual')}
                                >
                                    手动添加题目
                                </Button>
                                <Upload
                                    accept=".docx,.doc"
                                    showUploadList={false}
                                    beforeUpload={(file) => {
                                        handleImportFromWord(file);
                                        return false; // 阻止自动上传
                                    }}
                                >
                                    <Button loading={importLoading}>
                                        从Word文档导入
                                    </Button>
                                </Upload>
                            </Space>
                        </div>
                    </div>
                ) : questionModalMode === 'add' ? (
                    <div>
                        <div style={{ marginBottom: '20px' }}>
                            <Button
                                type="link"
                                onClick={() => setQuestionModalMode('view')}
                                style={{ padding: 0 }}
                            >
                                ← 返回题目列表
                            </Button>
                        </div>
                        <Transfer
                            dataSource={questions.map(q => ({
                                key: q.id,
                                title: q.content,
                                description: `类型: ${q.type}`,
                            }))}
                            titles={['可选题目', '已选题目']}
                            targetKeys={selectedQuestions}
                            onChange={(targetKeys) => setSelectedQuestions(targetKeys.map(Number))}
                            render={item => item.title}
                            listStyle={{
                                width: 500,
                                height: 400,
                            }}
                        />
                        <div style={{ marginTop: '20px', textAlign: 'center' }}>
                            <Space>
                                <Button onClick={() => setQuestionModalMode('view')}>
                                    取消
                                </Button>
                                <Button type="primary" onClick={handleAddQuestions}>
                                    添加选中题目
                                </Button>
                            </Space>
                        </div>
                    </div>
                ) : questionModalMode === 'manual' ? (
                    <div>
                        <div style={{ marginBottom: '20px' }}>
                            <Button
                                type="link"
                                onClick={() => setQuestionModalMode('view')}
                                style={{ padding: 0 }}
                            >
                                ← 返回题目列表
                            </Button>
                        </div>
                        <Form
                            form={manualQuestionForm}
                            layout="vertical"
                            onFinish={handleManualAddQuestion}
                            initialValues={{
                                options: ['', '', '', ''],
                                scores: [10, 7, 4, 1],
                                shuffle_options: false
                            }}
                        >
                            <Form.Item
                                name="content"
                                label="题目内容"
                                rules={[{ required: true, message: '请输入题目内容' }]}
                            >
                                <TextArea rows={4} placeholder="请输入题目内容" />
                            </Form.Item>
                            <Form.Item
                                name="type"
                                label="题目类型"
                                rules={[{ required: true, message: '请选择题目类型' }]}
                            >
                                <Select placeholder="请选择题目类型">
                                    <Option value="single">单选题</Option>
                                    <Option value="multiple">多选题</Option>
                                </Select>
                            </Form.Item>

                            <Form.Item
                                name="shuffle_options"
                                label="选项乱序"
                                valuePropName="checked"
                            >
                                <Checkbox>启用选项乱序（被试者答题时选项顺序随机化）</Checkbox>
                            </Form.Item>
                            <Form.Item
                                name="options"
                                label="选项"
                                rules={[{ required: true, message: '请输入选项' }]}
                            >
                                <div>
                                    {[0, 1, 2, 3].map((index) => (
                                        <div key={index} style={{ display: 'flex', marginBottom: '8px', alignItems: 'center' }}>
                                            <span style={{ width: '30px', marginRight: '8px' }}>
                                                {String.fromCharCode(65 + index)}.
                                            </span>
                                            <Input
                                                placeholder={`选项${String.fromCharCode(65 + index)}`}
                                                style={{ flex: 1, marginRight: '8px' }}
                                                value={manualOptions[index]}
                                                onChange={(e) => {
                                                    const newOptions = [...manualOptions];
                                                    newOptions[index] = e.target.value;
                                                    setManualOptions(newOptions);
                                                }}
                                            />
                                            <InputNumber
                                                placeholder="分数"
                                                min={0}
                                                max={10}
                                                style={{ width: '80px' }}
                                                value={manualScores[index]}
                                                onChange={(value) => {
                                                    const newScores = [...manualScores];
                                                    newScores[index] = value || 0;
                                                    setManualScores(newScores);
                                                }}
                                            />
                                        </div>
                                    ))}
                                </div>
                            </Form.Item>
                            <Form.Item>
                                <Space>
                                    <Button type="primary" htmlType="submit">
                                        添加题目
                                    </Button>
                                    <Button onClick={() => setQuestionModalMode('view')}>
                                        取消
                                    </Button>
                                </Space>
                            </Form.Item>
                        </Form>
                    </div>
                ) : null}
            </Modal>

            {/* 分配试卷模态框 */}
            <Modal
                title="分配试卷"
                open={assignModalVisible}
                onCancel={() => {
                    setAssignModalVisible(false);
                    setSelectedUserIds([]);
                    setAssignPaperId(null);
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setAssignModalVisible(false);
                        setSelectedUserIds([]);
                        setAssignPaperId(null);
                    }}>
                        取消
                    </Button>,
                    <Button key="assign" type="primary" onClick={handleAssign}>
                        分配
                    </Button>,
                ]}
                width={600}
            >
                <Transfer
                    dataSource={users.map(u => ({
                        key: u.id,
                        title: u.real_name || u.username,
                        description: u.username,
                    }))}
                    titles={['可选用户', '已选用户']}
                    targetKeys={selectedUserIds}
                    onChange={(targetKeys) => setSelectedUserIds(targetKeys.map(Number))}
                    render={item => item.title}
                    listStyle={{
                        width: 250,
                        height: 300,
                    }}
                />
            </Modal>

            {/* 维度管理模态框 */}
            <Modal
                title="维度管理"
                open={dimensionModalVisible}
                onCancel={() => {
                    setDimensionModalVisible(false);
                    setEditingDimension(null);
                    setCurrentPaperForDimension(null);
                    dimensionForm.resetFields();
                }}
                footer={null}
                width={800}
            >
                <div style={{ marginBottom: '20px' }}>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => {
                            setEditingDimension(null);
                            dimensionForm.resetFields();
                            dimensionForm.setFieldsValue({
                                paper_id: currentPaperForDimension,
                                parent_id: null,
                                weight: 1.0,
                                order_num: 0
                            });
                            setShowDimensionForm(true);
                        }}
                    >
                        添加大维度
                    </Button>
                </div>

                {/* 维度树形展示 */}
                <div style={{ marginBottom: '20px' }}>
                    <h4>当前维度结构</h4>
                    {dimensions.length === 0 ? (
                        <Empty description="暂无维度" />
                    ) : (
                        <Tree
                            treeData={dimensions.map(dim => ({
                                key: dim.id,
                                title: (
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                                        <span>{dim.name}</span>
                                        <Space>
                                            <Button
                                                size="small"
                                                type="link"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingDimension(null); // 关键：不设置为dim，表示新建
                                                    dimensionForm.resetFields();
                                                    dimensionForm.setFieldsValue({
                                                        paper_id: currentPaperForDimension,
                                                        parent_id: dim.id,
                                                        name: '',
                                                        description: '',
                                                        weight: 1.0,
                                                        order_num: 0
                                                    });
                                                    setShowDimensionForm(true);
                                                }}
                                            >
                                                添加子维度
                                            </Button>
                                            <Button
                                                size="small"
                                                type="link"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingDimension(dim);
                                                    dimensionForm.setFieldsValue(dim);
                                                    setShowDimensionForm(true);
                                                }}
                                            >
                                                编辑
                                            </Button>
                                            {(!dim.children || dim.children.length === 0) && (
                                                <Button
                                                    size="small"
                                                    type="link"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setCurrentDimensionForQuestion(dim);
                                                        if (currentPaperForDimension !== null) {
                                                            fetchAvailableQuestionsForDimension(dim.id, currentPaperForDimension);
                                                        }
                                                        fetchMatchedQuestionsForDimension(dim.id);
                                                        setDimensionQuestionModalVisible(true);
                                                    }}
                                                >
                                                    匹配题目
                                                </Button>
                                            )}
                                            {dim.children && dim.children.length > 0 && (
                                                <span style={{ color: '#999', fontSize: '12px' }}>
                                                    有子维度
                                                </span>
                                            )}
                                            <Popconfirm
                                                title="确定要删除这个维度吗？"
                                                onConfirm={() => deleteDimension(dim.id)}
                                                okText="确定"
                                                cancelText="取消"
                                            >
                                                <Button
                                                    size="small"
                                                    type="link"
                                                    danger
                                                    onClick={(e) => e.stopPropagation()}
                                                >
                                                    删除
                                                </Button>
                                            </Popconfirm>
                                        </Space>
                                    </div>
                                ),
                                children: dim.children?.map(child => ({
                                    key: child.id,
                                    title: (
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                                            <span>{child.name}</span>
                                            <Space>
                                                <Button
                                                    size="small"
                                                    type="link"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setEditingDimension(child);
                                                        dimensionForm.setFieldsValue(child);
                                                        setShowDimensionForm(true);
                                                    }}
                                                >
                                                    编辑
                                                </Button>
                                                <Button
                                                    size="small"
                                                    type="link"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setCurrentDimensionForQuestion(child);
                                                        if (currentPaperForDimension !== null) {
                                                            fetchAvailableQuestionsForDimension(child.id, currentPaperForDimension);
                                                        }
                                                        fetchMatchedQuestionsForDimension(child.id);
                                                        setDimensionQuestionModalVisible(true);
                                                    }}
                                                >
                                                    匹配题目
                                                </Button>
                                                <Popconfirm
                                                    title="确定要删除这个维度吗？"
                                                    onConfirm={() => deleteDimension(child.id)}
                                                    okText="确定"
                                                    cancelText="取消"
                                                >
                                                    <Button
                                                        size="small"
                                                        type="link"
                                                        danger
                                                        onClick={(e) => e.stopPropagation()}
                                                    >
                                                        删除
                                                    </Button>
                                                </Popconfirm>
                                            </Space>
                                        </div>
                                    ),
                                }))
                            }))}
                        />
                    )}
                </div>

                {/* 维度表单 */}
                {showDimensionForm && (
                    <div>
                        <Divider />
                        <h4>{editingDimension ? '编辑维度' : '添加维度'}</h4>
                        <Form
                            form={dimensionForm}
                            layout="vertical"
                            onFinish={editingDimension ? updateDimension : createDimension}
                        >
                            <Form.Item
                                name="paper_id"
                                hidden
                            >
                                <Input />
                            </Form.Item>
                            <Form.Item
                                name="parent_id"
                                hidden
                            >
                                <Input />
                            </Form.Item>
                            <Form.Item
                                name="name"
                                label="维度名称"
                                rules={[{ required: true, message: '请输入维度名称' }]}
                            >
                                <Input placeholder="请输入维度名称" />
                            </Form.Item>
                            <Form.Item
                                name="description"
                                label="维度描述"
                            >
                                <TextArea rows={2} placeholder="请输入维度描述" />
                            </Form.Item>
                            <Row gutter={16}>
                                <Col span={12}>
                                    <Form.Item
                                        name="weight"
                                        label="权重"
                                        rules={[{ required: true, message: '请输入权重' }]}
                                    >
                                        <InputNumber
                                            min={0}
                                            max={10}
                                            step={0.1}
                                            style={{ width: '100%' }}
                                            placeholder="权重"
                                        />
                                    </Form.Item>
                                </Col>
                                <Col span={12}>
                                    <Form.Item
                                        name="order_num"
                                        label="排序"
                                        rules={[{ required: true, message: '请输入排序' }]}
                                    >
                                        <InputNumber
                                            min={0}
                                            style={{ width: '100%' }}
                                            placeholder="排序"
                                        />
                                    </Form.Item>
                                </Col>
                            </Row>
                            <Form.Item>
                                <Space>
                                    <Button type="primary" htmlType="submit">
                                        {editingDimension ? '更新' : '创建'}
                                    </Button>
                                    <Button onClick={() => {
                                        setEditingDimension(null);
                                        dimensionForm.resetFields();
                                        setShowDimensionForm(false);
                                    }}>
                                        取消
                                    </Button>
                                </Space>
                            </Form.Item>
                        </Form>
                    </div>
                )}
            </Modal>

            {/* 分配情况模态框 */}
            <Modal
                title="试卷分配情况"
                open={assignmentModalVisible}
                onCancel={() => {
                    setAssignmentModalVisible(false);
                    setCurrentPaperForAssignment(null);
                    setAssignments([]);
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setAssignmentModalVisible(false);
                        setCurrentPaperForAssignment(null);
                        setAssignments([]);
                    }}>
                        关闭
                    </Button>,
                ]}
                width={800}
            >
                <div>
                    <p>该试卷的分配情况：</p>
                    {assignments.length === 0 ? (
                        <Empty description="暂无分配记录" />
                    ) : (
                        <List
                            dataSource={assignments}
                            renderItem={(assignment) => (
                                <List.Item
                                    actions={[
                                        assignment.status === 'completed' && (
                                            <Button
                                                size="small"
                                                type="primary"
                                                onClick={async () => {
                                                    // 重新分配已完成测试的被试者
                                                    if (currentPaperForAssignment) {
                                                        try {
                                                            const response = await fetch(`http://localhost:8000/papers/${currentPaperForAssignment}/assign/`, {
                                                                method: 'POST',
                                                                headers: { 'Content-Type': 'application/json' },
                                                                body: JSON.stringify({ user_ids: [assignment.user_id] }),
                                                            });
                                                            if (response.ok) {
                                                                message.success('重新分配成功');
                                                                // 刷新分配情况
                                                                fetchPaperAssignments(currentPaperForAssignment);
                                                            } else {
                                                                message.error('重新分配失败');
                                                            }
                                                        } catch (error) {
                                                            message.error('网络错误');
                                                        }
                                                    }
                                                }}
                                            >
                                                重新分配
                                            </Button>
                                        )
                                    ]}
                                >
                                    <div style={{ width: '100%' }}>
                                        <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                            {assignment.user_name} ({assignment.username})
                                        </div>
                                        <div style={{ color: '#666', fontSize: '12px' }}>
                                            状态:
                                            <Tag color={
                                                assignment.status === 'assigned' ? 'blue' :
                                                    assignment.status === 'started' ? 'orange' :
                                                        assignment.status === 'completed' ? 'green' : 'default'
                                            }>
                                                {assignment.status === 'assigned' ? '已分配' :
                                                    assignment.status === 'started' ? '进行中' :
                                                        assignment.status === 'completed' ? '已完成' : assignment.status}
                                            </Tag>
                                        </div>
                                        <div style={{ color: '#999', fontSize: '12px', marginTop: '4px' }}>
                                            分配时间: {new Date(assignment.assigned_at).toLocaleString()}
                                            {assignment.started_at && ` | 开始时间: ${new Date(assignment.started_at).toLocaleString()}`}
                                            {assignment.completed_at && ` | 完成时间: ${new Date(assignment.completed_at).toLocaleString()}`}
                                        </div>
                                    </div>
                                </List.Item>
                            )}
                        />
                    )}
                </div>
            </Modal>

            {/* 维度题目匹配模态框 */}
            <Modal
                title={`为维度"${currentDimensionForQuestion?.name}"匹配题目`}
                open={dimensionQuestionModalVisible}
                onCancel={() => {
                    setDimensionQuestionModalVisible(false);
                    setSelectedQuestionsForDimension([]);
                    setCurrentDimensionForQuestion(null);
                    setMatchedQuestions([]);
                    setAvailableQuestions([]);
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setDimensionQuestionModalVisible(false);
                        setSelectedQuestionsForDimension([]);
                        setCurrentDimensionForQuestion(null);
                        setMatchedQuestions([]);
                        setAvailableQuestions([]);
                    }}>
                        取消
                    </Button>,
                    <Button key="match" type="primary" onClick={matchQuestionsToDimension} disabled={selectedQuestionsForDimension.length === 0}>
                        匹配选中题目 ({selectedQuestionsForDimension.length})
                    </Button>,
                ]}
                width={800}
            >
                {/* 已匹配题目列表 */}
                <div style={{ marginBottom: '16px' }}>
                    <p>该维度已匹配的题目：</p>
                    {matchedQuestions.length === 0 ? (
                        <span style={{ color: '#aaa' }}>暂无</span>
                    ) : (
                        <List
                            dataSource={matchedQuestions}
                            renderItem={(item, index) => (
                                <List.Item
                                    actions={[
                                        <Button size="small" danger onClick={() => {
                                            if (currentDimensionForQuestion) {
                                                removeQuestionFromDimension(currentDimensionForQuestion.id, item.id);
                                            }
                                        }}>
                                            移除
                                        </Button>
                                    ]}
                                >
                                    <div style={{ fontWeight: 'bold' }}>题目{index + 1}: {item.content}</div>
                                </List.Item>
                            )}
                        />
                    )}
                </div>
                <Divider />
                <div style={{ marginBottom: '16px' }}>
                    <p>选择要匹配到该维度的题目（已匹配的题目不会显示）：</p>
                </div>
                {availableQuestions.length === 0 ? (
                    <Empty description="暂无可匹配的题目" />
                ) : (
                    <div>
                        {/* 全选功能 */}
                        <div style={{ marginBottom: '12px', padding: '8px 12px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
                            <Checkbox
                                checked={selectedQuestionsForDimension.length === availableQuestions.length && availableQuestions.length > 0}
                                indeterminate={selectedQuestionsForDimension.length > 0 && selectedQuestionsForDimension.length < availableQuestions.length}
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setSelectedQuestionsForDimension(availableQuestions.map(q => q.id));
                                    } else {
                                        setSelectedQuestionsForDimension([]);
                                    }
                                }}
                            >
                                全选 ({selectedQuestionsForDimension.length}/{availableQuestions.length})
                            </Checkbox>
                        </div>
                        <List
                            dataSource={availableQuestions}
                            renderItem={(item, index) => (
                                <List.Item>
                                    <div style={{ width: '100%', display: 'flex', alignItems: 'flex-start' }}>
                                        <Checkbox
                                            checked={selectedQuestionsForDimension.includes(item.id)}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedQuestionsForDimension([...selectedQuestionsForDimension, item.id]);
                                                } else {
                                                    setSelectedQuestionsForDimension(selectedQuestionsForDimension.filter(id => id !== item.id));
                                                }
                                            }}
                                            style={{ marginRight: '12px', marginTop: '4px' }}
                                        />
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                                题目{index + 1}: {item.content}
                                            </div>
                                            <div style={{ color: '#666', fontSize: '12px' }}>
                                                类型: {item.type} | 选项数: {item.options?.length || 0}
                                            </div>
                                        </div>
                                    </div>
                                </List.Item>
                            )}
                        />
                    </div>
                )}
            </Modal>

            {/* 编辑题目模态框 */}
            <Modal
                title="编辑题目"
                open={editQuestionModalVisible}
                onCancel={() => {
                    setEditQuestionModalVisible(false);
                    setEditingQuestion(null);
                    editQuestionForm.resetFields();
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setEditQuestionModalVisible(false);
                        setEditingQuestion(null);
                        editQuestionForm.resetFields();
                    }}>
                        取消
                    </Button>,
                    <Button key="save" type="primary" onClick={() => editQuestionForm.submit()}>
                        保存
                    </Button>,
                ]}
                width={800}
            >
                <Form
                    form={editQuestionForm}
                    layout="vertical"
                    onFinish={handleSaveEditQuestion}
                >
                    <Form.Item
                        name="content"
                        label="题目内容"
                        rules={[{ required: true, message: '请输入题目内容' }]}
                    >
                        <TextArea rows={4} placeholder="请输入题目内容" />
                    </Form.Item>

                    <Form.Item
                        name="type"
                        label="题目类型"
                        rules={[{ required: true, message: '请选择题目类型' }]}
                    >
                        <Select placeholder="请选择题目类型">
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

                    <Form.List name="options">
                        {(fields, { add, remove }) => (
                            <>
                                {fields.map((field, idx) => (
                                    <Space key={field.key} align="baseline" style={{ display: 'flex', marginBottom: 8 }}>
                                        <Form.Item
                                            {...field}
                                            name={[field.name]}
                                            rules={[{ required: true, message: '请输入选项内容' }]}
                                        >
                                            <Input placeholder={`选项${String.fromCharCode(65 + idx)}`} style={{ width: 200 }} />
                                        </Form.Item>
                                        <Form.Item
                                            name={['scores', idx]}
                                            rules={[{ required: true, message: '请输入分数' }]}
                                        >
                                            <InputNumber placeholder="分数" style={{ width: 80 }} />
                                        </Form.Item>
                                        {fields.length > 2 && (
                                            <MinusCircleOutlined onClick={() => remove(field.name)} />
                                        )}
                                    </Space>
                                ))}
                                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                                    添加选项
                                </Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>

            {/* 导入预览模态框 */}
            <Modal
                title="导入题目预览"
                open={importModalVisible}
                onCancel={() => {
                    setImportModalVisible(false);
                    setImportedQuestions([]);
                    setImportShuffleOptions(false);
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setImportModalVisible(false);
                        setImportedQuestions([]);
                        setImportShuffleOptions(false);
                    }}>
                        取消
                    </Button>,
                    <Button key="confirm" type="primary" onClick={handleConfirmImport} loading={importLoading}>
                        确认导入 ({importedQuestions.length} 道题目)
                    </Button>,
                ]}
                width={800}
            >
                <div style={{ marginBottom: '16px' }}>
                    <Checkbox
                        checked={importShuffleOptions}
                        onChange={(e) => setImportShuffleOptions(e.target.checked)}
                    >
                        为所有导入的题目启用选项乱序
                    </Checkbox>
                </div>
                <Divider />
                <div>
                    <p>预览导入的题目：</p>
                    <List
                        dataSource={importedQuestions}
                        renderItem={(item, index) => (
                            <List.Item>
                                <div>
                                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                        题目{index + 1}: {item.content}
                                    </div>
                                    <div style={{ color: '#666', fontSize: '12px' }}>
                                        类型: {item.type} | 选项数: {item.options?.length || 0}
                                    </div>
                                </div>
                            </List.Item>
                        )}
                    />
                </div>
            </Modal>
        </div>
    );
};

export default PaperManagement; 