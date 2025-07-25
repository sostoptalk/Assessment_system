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
    Collapse,
    Typography
} from 'antd';

const { Text } = Typography;
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
    MinusCircleOutlined,
    UploadOutlined
} from '@ant-design/icons';
import type { TransferDirection } from 'antd/es/transfer';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import QuestionContentDisplay from '../../components/QuestionContentDisplay';
import RichTextEditor from '../../components/RichTextEditor';

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
    parent_case_id?: number;
    children?: Question[];  // 添加子题字段
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

// Quill 编辑器配置，增强表格粘贴体验
const quillModules = {
    toolbar: [
        [{ 'header': [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        ['blockquote', 'code-block'],
        ['link', 'image'],
        ['clean'],
    ]
}

const PaperManagement: React.FC = () => {
    const [papers, setPapers] = useState<Paper[]>([]);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [filteredQuestions, setFilteredQuestions] = useState<Question[]>([]);
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

    // 新增：添加案例背景题
    const [caseModalVisible, setCaseModalVisible] = useState(false);
    const [caseForm] = Form.useForm();
    const [caseQuestions, setCaseQuestions] = useState<any[]>([]);
    const [caseBackground, setCaseBackground] = useState('');

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

                // 组织案例背景题和子题的关系
                const allQuestions = data;
                const caseMap = new Map(); // 存储案例背景题ID到题目对象的映射
                const regularQuestions: Question[] = []; // 存储非子题的普通题目

                // 第一遍遍历，找出所有案例背景题和普通题
                allQuestions.forEach((q: Question) => {
                    if (q.type === 'case') {
                        q.children = []; // 初始化子题数组
                        caseMap.set(q.id, q);
                    } else if (!q.parent_case_id) {
                        regularQuestions.push(q);
                    }
                });

                // 第二遍遍历，将子题添加到对应的案例背景题中
                allQuestions.forEach((q: Question) => {
                    if (q.parent_case_id && caseMap.has(q.parent_case_id)) {
                        const parent = caseMap.get(q.parent_case_id);
                        parent.children.push(q);
                    }
                });

                // 合并案例背景题和普通题
                const result = [...caseMap.values(), ...regularQuestions];
                setQuestions(result);
                setFilteredQuestions(result);  // 同时设置 filteredQuestions
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
    const toggleShuffle = async (paperId: number | null, enableShuffle: boolean) => {
        if (!paperId) return;

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
                message.success(enableShuffle ? '题目乱序已启用' : '题目乱序已禁用');
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

                // 组织案例背景题和子题的关系
                const allQuestions = data || [];
                const caseMap = new Map(); // 存储案例背景题ID到题目对象的映射
                const regularQuestions: Question[] = []; // 存储非子题的普通题目

                // 第一遍遍历，找出所有案例背景题和普通题
                allQuestions.forEach((q: Question) => {
                    if (q.type === 'case') {
                        q.children = []; // 初始化子题数组
                        caseMap.set(q.id, q);
                    } else if (!q.parent_case_id) {
                        regularQuestions.push(q);
                    }
                });

                // 第二遍遍历，将子题添加到对应的案例背景题中
                allQuestions.forEach((q: Question) => {
                    if (q.parent_case_id && caseMap.has(q.parent_case_id)) {
                        const parent = caseMap.get(q.parent_case_id);
                        parent.children.push(q);
                    }
                });

                // 合并案例背景题和普通题
                const result = [...caseMap.values(), ...regularQuestions];
                setAvailableQuestions(result);
            }
        } catch (error) {
            console.error('获取可用题目失败:', error);
        }
    };

    // 获取试卷已匹配的题目
    const fetchMatchedQuestionsForDimension = async (dimensionId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}/matched-questions`);
            if (response.ok) {
                const data = await response.json();

                // 组织案例背景题和子题的关系
                const allQuestions = data || [];
                const caseMap = new Map(); // 存储案例背景题ID到题目对象的映射
                const regularQuestions: Question[] = []; // 存储非子题的普通题目

                // 第一遍遍历，找出所有案例背景题和普通题
                allQuestions.forEach((q: Question) => {
                    if (q.type === 'case') {
                        q.children = []; // 初始化子题数组
                        caseMap.set(q.id, q);
                    } else if (!q.parent_case_id) {
                        regularQuestions.push(q);
                    }
                });

                // 第二遍遍历，将子题添加到对应的案例背景题中
                allQuestions.forEach((q: Question) => {
                    if (q.parent_case_id && caseMap.has(q.parent_case_id)) {
                        const parent = caseMap.get(q.parent_case_id);
                        parent.children.push(q);
                    }
                });

                // 合并案例背景题和普通题
                const result = [...caseMap.values(), ...regularQuestions];
                setMatchedQuestions(result);
            }
        } catch (error) {
            console.error('获取匹配题目失败:', error);
        }
    };

    // 修改匹配题目到维度的函数，支持案例背景题和子题的匹配
    const matchQuestionsToDimension = async () => {
        if (!currentDimensionForQuestion || selectedQuestionsForDimension.length === 0) return;

        const dimensionId = currentDimensionForQuestion.id;

        try {
            // 处理所有选中题目，包括案例背景题的子题
            const allSelectedQuestionIds: number[] = [];

            for (const questionId of selectedQuestionsForDimension) {
                // 先添加主题目
                allSelectedQuestionIds.push(questionId);

                // 如果是案例背景题，添加其所有子题
                const selectedQuestion = availableQuestions.find(q => q.id === questionId);
                if (selectedQuestion && selectedQuestion.type === 'case' && selectedQuestion.children) {
                    selectedQuestion.children.forEach(child => {
                        allSelectedQuestionIds.push(child.id);
                    });
                }
            }

            const response = await fetch(`http://localhost:8000/dimensions/${dimensionId}/match-questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_ids: allSelectedQuestionIds }),
            });

            if (response.ok) {
                message.success('匹配题目成功');
                setSelectedQuestionsForDimension([]);

                // 刷新两个列表
                await fetchMatchedQuestionsForDimension(dimensionId);
                await fetchAvailableQuestionsForDimension(dimensionId, currentPaperId);
            } else {
                message.error('匹配失败');
            }
        } catch (error) {
            console.error('匹配题目失败:', error);
            message.error('匹配失败');
        }
    };

    // 获取试卷题目
    const fetchPaperQuestions = async (paperId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${paperId}/questions/`);
            if (response.ok) {
                const data = await response.json();

                // 组织案例背景题和子题的关系
                const allQuestions = data.questions || [];
                const caseMap = new Map(); // 存储案例背景题ID到题目对象的映射
                const regularQuestions: Question[] = []; // 存储非子题的普通题目

                // 第一遍遍历，找出所有案例背景题和普通题
                allQuestions.forEach((q: Question) => {
                    if (q.type === 'case') {
                        q.children = []; // 初始化子题数组
                        caseMap.set(q.id, q);
                    } else if (!q.parent_case_id) {
                        regularQuestions.push(q);
                    }
                });

                // 第二遍遍历，将子题添加到对应的案例背景题中
                allQuestions.forEach((q: Question) => {
                    if (q.parent_case_id && caseMap.has(q.parent_case_id)) {
                        const parent = caseMap.get(q.parent_case_id);
                        parent.children.push(q);
                    }
                });

                // 合并案例背景题和普通题
                const result = [...caseMap.values(), ...regularQuestions];
                setPaperQuestions(result);
            }
        } catch (error) {
            console.error('获取试卷题目失败:', error);
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
            // 获取所有选中的题目，包括案例背景题的子题
            const allSelectedQuestionIds: number[] = [];

            for (const questionId of selectedQuestions) {
                // 先添加主题目
                allSelectedQuestionIds.push(questionId);

                // 如果是案例背景题，添加其所有子题
                const selectedQuestion = questions.find(q => q.id === questionId);
                if (selectedQuestion && selectedQuestion.type === 'case' && selectedQuestion.children) {
                    selectedQuestion.children.forEach(child => {
                        allSelectedQuestionIds.push(child.id);
                    });
                }
            }

            // 转换为后端期望的格式
            const questionsData = allSelectedQuestionIds.map(questionId => ({
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
        if (editingQuestion && typeof editingQuestion._excelIndex === 'number') {
            // 编辑的是Excel导入预览题目
            const idx = editingQuestion._excelIndex;
            const updated = [...excelImportedQuestions];
            updated[idx] = {
                ...updated[idx],
                content: values.content,
                type: values.type,
                shuffle_options: values.shuffle_options,
                options: values.options,
                scores: values.scores,
            };
            setExcelImportedQuestions(updated);
            setEditQuestionModalVisible(false);
            setEditingQuestion(null);
            editQuestionForm.resetFields();
            return;
        }
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
                            setShuffleLoading(false); // 重置loading状态
                            // 并行请求，提高页面加载速度
                            await Promise.all([
                                fetchPaperQuestions(record.id),
                                fetchShuffleStatus(record.id)
                            ]);
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

    // 新增Excel导入相关状态
    const [excelImportLoading, setExcelImportLoading] = useState(false);
    const [excelImportModalVisible, setExcelImportModalVisible] = useState(false);
    const [excelImportedQuestions, setExcelImportedQuestions] = useState<any[]>([]);
    const [excelImportFile, setExcelImportFile] = useState<File | null>(null);

    // Excel导入预览
    const handleImportFromExcel = async (file: File) => {
        setExcelImportLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            let url = currentPaperId
                ? `http://localhost:8000/papers/${currentPaperId}/import_excel`
                : 'http://localhost:8000/questions/import_excel';
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                const data = await response.json();
                const questions = data.questions || [];
                if (questions.length === 0) {
                    message.warning('Excel中没有找到有效题目');
                    setExcelImportLoading(false);
                    return;
                }
                setExcelImportedQuestions(questions);
                setExcelImportModalVisible(true);
                setExcelImportFile(file);
            } else {
                message.error('解析Excel失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('导入Excel错误:', error);
        } finally {
            setExcelImportLoading(false);
        }
    };

    // Excel导入确认
    const handleConfirmImportExcel = async () => {
        if (excelImportedQuestions.length === 0) return;
        setExcelImportLoading(true);
        try {
            let url = currentPaperId
                ? `http://localhost:8000/papers/${currentPaperId}/import_excel_confirm`
                : 'http://localhost:8000/questions/import_excel_confirm';
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(excelImportedQuestions),
            });
            if (response.ok) {
                message.success('Excel题目导入成功');
                setExcelImportModalVisible(false);
                setExcelImportedQuestions([]);
                setExcelImportFile(null);
                setQuestionModalMode('view');
                // 刷新题目列表
                if (currentPaperId) {
                    await fetchPaperQuestions(currentPaperId);
                } else {
                    await fetchQuestions();
                }
            } else {
                message.error('导入题目失败');
            }
        } catch (error) {
            message.error('网络错误');
            console.error('确认导入Excel错误:', error);
        } finally {
            setExcelImportLoading(false);
        }
    };

    // 新增：添加案例背景题
    const handleAddCase = () => {
        setCaseQuestions([{ content: '', type: 'single', options: ['', '', '', ''], scores: [10, 7, 4, 1], shuffle_options: false }]);
        setCaseBackground('');
        setCaseModalVisible(true);
        caseForm.resetFields();
    };
    // 新增：案例背景题提交
    const handleCaseModalOk = async () => {
        if (!currentPaperId) return;
        try {
            const values = await caseForm.validateFields();
            if (!caseBackground || caseBackground.trim() === '') {
                message.error('请输入案例背景内容');
                return;
            }
            // 组装payload
            const questions = values.questions.map((q: any) => ({
                ...q,
                options: q.options.map((item: any) => item.value || item),
                scores: q.options.map((item: any, idx: number) => Number(item.score ?? q.scores?.[idx] ?? 0)),
            }));
            // 先保存案例背景题（主表）
            const res = await fetch('http://localhost:8000/questions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: caseBackground,
                    type: 'case',
                    options: [],
                    scores: [],
                    shuffle_options: false
                })
            });
            if (!res.ok) throw new Error('案例背景题创建失败');
            const caseData = await res.json();
            const caseId = caseData.id;
            // 再保存子题，带 parent_case_id
            const createdIds: number[] = [];
            for (const q of questions) {
                const resp = await fetch('http://localhost:8000/questions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ...q,
                        content: `[案例子题] ${q.content}`,
                        type: q.type,
                        options: q.options,
                        scores: q.scores,
                        shuffle_options: q.shuffle_options || false,
                        parent_case_id: caseId
                    })
                });
                if (resp.ok) {
                    const data = await resp.json();
                    createdIds.push(data.id);
                }
            }
            // 批量添加到试卷：包括案例背景题和所有子题
            const allIds = [caseId, ...createdIds];
            if (allIds.length > 0) {
                const questionsData = allIds.map(id => ({ question_id: id, dimension_id: null }));
                await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(questionsData)
                });
            }
            message.success('案例背景题添加成功');
            setCaseModalVisible(false);
            await fetchPaperQuestions(currentPaperId);
        } catch (e) {
            message.error('添加失败');
        }
    };

    // 在 PaperManagement 组件内部添加
    const handleRemovePaperQuestion = async (questionId: number) => {
        if (!currentPaperId) return;
        try {
            const response = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_ids: [questionId] }),
            });
            if (response.ok) {
                message.success('题目已移除');
                await fetchPaperQuestions(currentPaperId);
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '移除失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 撤销单个分配
    const handleRevokeAssignment = async (paperId: number, assignmentId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${paperId}/assignment/${assignmentId}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                message.success('撤销分配成功');
                fetchPaperAssignments(paperId);
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '撤销分配失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };
    // 撤销全部分配
    const handleRevokeAllAssignments = async (paperId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${paperId}/assignments`, {
                method: 'DELETE',
            });
            if (response.ok) {
                message.success('已撤销全部分配');
                fetchPaperAssignments(paperId);
            } else {
                const errorData = await response.json();
                message.error(errorData.detail || '撤销全部分配失败');
            }
        } catch (error) {
            message.error('网络错误');
        }
    };

    // 修改renderQuestionItem函数，为案例背景题添加移除按钮
    const renderQuestionItem = (item: Question, index: number, options: {
        showCheckbox?: boolean;
        selectedIds?: number[];
        onCheckChange?: (id: number, checked: boolean) => void;
        showActions?: boolean;
        actions?: React.ReactNode[];
    } = {}) => {
        const {
            showCheckbox = true,
            selectedIds = selectedQuestions,
            onCheckChange,
            showActions = false,
            actions = []
        } = options;

        // 判断是否为案例背景题
        const isCaseQuestion = item.type === 'case';

        // 处理复选框选择
        const handleCheckChange = (checked: boolean) => {
            if (onCheckChange) {
                onCheckChange(item.id, checked);
            } else {
                // 默认行为 - 修改selectedQuestions
                if (checked) {
                    setSelectedQuestions([...selectedQuestions, item.id]);
                } else {
                    setSelectedQuestions(selectedQuestions.filter(id => id !== item.id));
                }
            }
        };

        // 为案例背景题创建移除按钮，点击后同时移除其所有子题
        const handleRemoveCaseQuestion = (caseItem: Question) => {
            Modal.confirm({
                title: '确认移除',
                content: `该题为案例背景题，包含${caseItem.children?.length || 0}个子题，移除后将同时移除所有子题，是否继续？`,
                okText: '确认',
                cancelText: '取消',
                onOk: async () => {
                    if (caseItem.children && caseItem.children.length > 0) {
                        // 先移除所有子题
                        for (const child of caseItem.children) {
                            await handleRemovePaperQuestion(child.id);
                        }
                    }
                    // 再移除案例背景题
                    await handleRemovePaperQuestion(caseItem.id);
                }
            });
        };

        // 为案例背景题创建自定义操作按钮
        const caseActions = isCaseQuestion ? [
            <Button
                type="link"
                size="small"
                icon={<DeleteOutlined />}
                onClick={() => handleRemoveCaseQuestion(item)}
                danger
            >
                移除(含子题)
            </Button>
        ] : actions;

        return (
            <div key={item.id} style={{ marginBottom: '16px', border: '1px solid #f0f0f0', borderRadius: '4px', padding: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    {showCheckbox && (
                        <Checkbox
                            checked={selectedIds.includes(item.id)}
                            onChange={(e) => handleCheckChange(e.target.checked)}
                            style={{ marginRight: '12px', marginTop: '4px' }}
                        />
                    )}
                    <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                            {!isCaseQuestion && `题目${index + 1}: `}<QuestionContentDisplay content={item.content} maxLength={150} />
                        </div>
                        <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>
                            类型: {
                                {
                                    'single': '单选题',
                                    'multiple': '多选题',
                                    'indefinite': '不定项',
                                    'case': '案例背景题'
                                }[item.type] || item.type
                            } |
                            {item.type !== 'case' && `选项数: ${item.options?.length || 0}`}
                            {item.shuffle_options && (
                                <Tag color="green" style={{ marginLeft: '8px' }}>选项乱序</Tag>
                            )}
                        </div>

                        {/* 案例背景题的子题列表 */}
                        {isCaseQuestion && item.children && item.children.length > 0 && (
                            <Collapse ghost>
                                <Collapse.Panel
                                    header={<span style={{ color: '#1890ff' }}>包含 {item.children.length} 个子题 (点击展开)</span>}
                                    key="1"
                                >
                                    <List
                                        size="small"
                                        dataSource={item.children}
                                        renderItem={(child, childIndex) => (
                                            <List.Item
                                                actions={showActions ? [
                                                    <Button
                                                        type="link"
                                                        size="small"
                                                        icon={<EditOutlined />}
                                                        onClick={() => handleEditPaperQuestion(child)}
                                                    >
                                                        编辑
                                                    </Button>,
                                                    <Button
                                                        type="link"
                                                        size="small"
                                                        icon={<DeleteOutlined />}
                                                        onClick={() => handleRemovePaperQuestion(child.id)}
                                                    >
                                                        移除
                                                    </Button>
                                                ] : undefined}
                                            >
                                                <div>
                                                    <div style={{ fontWeight: 'normal' }}>
                                                        子题{childIndex + 1}: <QuestionContentDisplay content={child.content} maxLength={100} />
                                                    </div>
                                                    <div style={{ color: '#666', fontSize: '12px' }}>
                                                        类型: {
                                                            {
                                                                'single': '单选题',
                                                                'multiple': '多选题',
                                                                'indefinite': '不定项'
                                                            }[child.type] || child.type
                                                        } |
                                                        选项数: {child.options?.length || 0}
                                                        {child.shuffle_options && (
                                                            <Tag color="green" style={{ marginLeft: '8px' }}>选项乱序</Tag>
                                                        )}
                                                    </div>
                                                </div>
                                            </List.Item>
                                        )}
                                    />
                                </Collapse.Panel>
                            </Collapse>
                        )}
                    </div>

                    {showActions && (isCaseQuestion ? (
                        <div style={{ marginLeft: '12px' }}>
                            {caseActions}
                        </div>
                    ) : (
                        <div style={{ marginLeft: '12px' }}>
                            {actions}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    // 维度匹配的列表展示也需要修改，使用相同的展开/收起逻辑
    const renderDimensionQuestionItem = (item: Question, index: number) => {
        // 判断是否为案例背景题
        const isCaseQuestion = item.type === 'case';

        return (
            <div key={item.id} style={{ marginBottom: '16px', border: '1px solid #f0f0f0', borderRadius: '4px', padding: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                            {!isCaseQuestion && `题目${index + 1}: `}<QuestionContentDisplay content={item.content} maxLength={150} />
                        </div>
                        <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>
                            类型: {
                                {
                                    'single': '单选题',
                                    'multiple': '多选题',
                                    'indefinite': '不定项',
                                    'case': '案例背景题'
                                }[item.type] || item.type
                            } |
                            {item.type !== 'case' && `选项数: ${item.options?.length || 0}`}
                            {item.shuffle_options && (
                                <Tag color="green" style={{ marginLeft: '8px' }}>选项乱序</Tag>
                            )}
                        </div>

                        {/* 案例背景题的子题列表 */}
                        {isCaseQuestion && item.children && item.children.length > 0 && (
                            <Collapse ghost>
                                <Collapse.Panel
                                    header={<span style={{ color: '#1890ff' }}>包含 {item.children.length} 个子题 (点击展开)</span>}
                                    key="1"
                                >
                                    <List
                                        size="small"
                                        dataSource={item.children}
                                        renderItem={(child, childIndex) => (
                                            <List.Item
                                                actions={[
                                                    <Button
                                                        type="link"
                                                        size="small"
                                                        icon={<DeleteOutlined />}
                                                        onClick={() => removeQuestionFromDimension(currentDimensionForQuestion?.id || 0, child.id)}
                                                    >
                                                        移除
                                                    </Button>
                                                ]}
                                            >
                                                <div>
                                                    <div style={{ fontWeight: 'normal' }}>
                                                        子题{childIndex + 1}: <QuestionContentDisplay content={child.content} maxLength={100} />
                                                    </div>
                                                    <div style={{ color: '#666', fontSize: '12px' }}>
                                                        类型: {
                                                            {
                                                                'single': '单选题',
                                                                'multiple': '多选题',
                                                                'indefinite': '不定项'
                                                            }[child.type] || child.type
                                                        } |
                                                        选项数: {child.options?.length || 0}
                                                    </div>
                                                </div>
                                            </List.Item>
                                        )}
                                    />
                                </Collapse.Panel>
                            </Collapse>
                        )}
                    </div>

                    {!isCaseQuestion && (
                        <Button
                            type="link"
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => removeQuestionFromDimension(currentDimensionForQuestion?.id || 0, item.id)}
                        >
                            移除
                        </Button>
                    )}
                </div>
            </div>
        );
    };

    // 添加批量删除函数
    const handleBatchRemovePaperQuestions = async () => {
        if (!currentPaperId || selectedPaperQuestions.length === 0) {
            return;
        }

        Modal.confirm({
            title: '批量移除题目',
            content: `确定要移除选中的 ${selectedPaperQuestions.length} 道题目吗？`,
            okText: '确认',
            cancelText: '取消',
            onOk: async () => {
                try {
                    // 使用已有的API批量删除题目
                    const response = await fetch(`http://localhost:8000/papers/${currentPaperId}/questions/`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question_ids: selectedPaperQuestions }),
                    });

                    if (response.ok) {
                        message.success(`已成功移除 ${selectedPaperQuestions.length} 道题目`);
                        setSelectedPaperQuestions([]);
                        // 刷新题目列表
                        await fetchPaperQuestions(currentPaperId);
                    } else {
                        message.error('移除失败');
                    }
                } catch (error) {
                    console.error('批量移除题目失败:', error);
                    message.error('移除失败');
                }
            }
        });
    };

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
                    setShuffleStatus(null); // 重置乱序状态
                    setShuffleLoading(false); // 重置加载状态
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
                                <Space>
                                    <Button type="primary" icon={<PlusOutlined />} onClick={() => setQuestionModalMode('add')}>添加题目</Button>
                                    <Button type="dashed" onClick={handleAddCase}>添加案例背景题</Button>
                                </Space>
                            </div>

                            {/* 添加题目乱序控制区域 */}
                            {paperQuestions.length > 0 && (
                                <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f9f9f9', borderRadius: '8px', border: '1px solid #eee' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <div style={{ marginBottom: '4px' }}>
                                                <Text strong style={{ fontSize: '16px' }}>题目乱序控制</Text>
                                                {shuffleStatus?.is_shuffled && shuffleStatus.shuffle_seed && (
                                                    <Tag color="blue" style={{ marginLeft: '8px' }}>
                                                        乱序种子: {shuffleStatus.shuffle_seed}
                                                    </Tag>
                                                )}
                                            </div>
                                            <Text type="secondary">
                                                启用后，被试者答题时题目将不按原顺序，而是随机打乱顺序展示
                                            </Text>
                                        </div>
                                        <div>
                                            <Button
                                                type={shuffleStatus?.is_shuffled ? "default" : "primary"}
                                                danger={shuffleStatus?.is_shuffled}
                                                loading={shuffleLoading}
                                                onClick={() => toggleShuffle(currentPaperId, !shuffleStatus?.is_shuffled)}
                                                icon={shuffleStatus?.is_shuffled ? <ReloadOutlined /> : null}
                                            >
                                                {shuffleStatus?.is_shuffled ? "取消题目乱序" : "启用题目乱序"}
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {paperQuestions.length === 0 ? (
                                <Empty description="暂无题目" />
                            ) : (
                                <>
                                    {/* 全选功能 */}
                                    <div style={{ marginBottom: '12px', padding: '8px 12px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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

                                            <Button
                                                type="primary"
                                                danger
                                                size="small"
                                                disabled={selectedPaperQuestions.length === 0}
                                                onClick={handleBatchRemovePaperQuestions}
                                            >
                                                批量移除({selectedPaperQuestions.length})
                                            </Button>
                                        </div>
                                    </div>
                                    <List
                                        dataSource={paperQuestions}
                                        renderItem={(item, index) => renderQuestionItem(item, index, {
                                            selectedIds: selectedPaperQuestions,
                                            onCheckChange: (id, checked) => {
                                                if (checked) {
                                                    setSelectedPaperQuestions([...selectedPaperQuestions, id]);
                                                } else {
                                                    setSelectedPaperQuestions(selectedPaperQuestions.filter(itemId => itemId !== id));
                                                }
                                            },
                                            showActions: true,
                                            actions: [
                                                <Button
                                                    type="link"
                                                    size="small"
                                                    icon={<EditOutlined />}
                                                    onClick={() => handleEditPaperQuestion(item)}
                                                >
                                                    编辑
                                                </Button>,
                                                <Button
                                                    type="link"
                                                    size="small"
                                                    icon={<DeleteOutlined />}
                                                    onClick={() => handleRemovePaperQuestion(item.id)}
                                                >
                                                    移除
                                                </Button>
                                            ]
                                        })}
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
                                <Upload
                                    accept=".xlsx,.xls"
                                    showUploadList={false}
                                    beforeUpload={(file) => {
                                        handleImportFromExcel(file);
                                        return false;
                                    }}
                                >
                                    <Button icon={<UploadOutlined />} loading={excelImportLoading}>
                                        从Excel导入
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

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div>
                                <Input.Search
                                    placeholder="搜索题目内容"
                                    allowClear
                                    enterButton="搜索"
                                    size="large"
                                    onSearch={(value) => {
                                        // 简单的内容搜索
                                        const filtered = questions.filter(q =>
                                            q.content.toLowerCase().includes(value.toLowerCase())
                                        );
                                        setFilteredQuestions(filtered);
                                    }}
                                    onChange={(e) => {
                                        if (!e.target.value) {
                                            setFilteredQuestions(questions);
                                        }
                                    }}
                                    style={{ marginBottom: '16px' }}
                                />

                                <Card
                                    title={`题库题目 (共${filteredQuestions.length}题)`}
                                    extra={
                                        <div>
                                            <Button
                                                type="primary"
                                                onClick={() => {
                                                    // 全选
                                                    if (selectedQuestions.length === filteredQuestions.length) {
                                                        setSelectedQuestions([]);
                                                    } else {
                                                        setSelectedQuestions(filteredQuestions.map(q => q.id));
                                                    }
                                                }}
                                            >
                                                {selectedQuestions.length === filteredQuestions.length ? '取消全选' : '全选'}
                                            </Button>
                                        </div>
                                    }
                                    style={{ maxHeight: '500px', overflowY: 'auto' }}
                                >
                                    {filteredQuestions.length > 0 ? (
                                        <List
                                            dataSource={filteredQuestions}
                                            renderItem={(item, index) => renderQuestionItem(item, index)}
                                            style={{ maxHeight: '400px', overflowY: 'auto' }}
                                        />
                                    ) : (
                                        <Empty description="没有找到题目" />
                                    )}
                                </Card>
                            </div>

                            <div style={{ marginTop: '20px', textAlign: 'right' }}>
                                <Space>
                                    <Button onClick={() => setQuestionModalMode('view')}>
                                        取消
                                    </Button>
                                    <Button
                                        type="primary"
                                        onClick={handleAddQuestions}
                                        disabled={selectedQuestions.length === 0}
                                    >
                                        添加选中题目({selectedQuestions.length})
                                    </Button>
                                </Space>
                            </div>
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
                    ...(currentPaperForAssignment && assignments.length > 0 ? [
                        <Button key="revokeAll" danger onClick={() => handleRevokeAllAssignments(currentPaperForAssignment)}>
                            撤销全部分配
                        </Button>
                    ] : [])
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
                                        ),
                                        <Button
                                            size="small"
                                            danger
                                            onClick={() => handleRevokeAssignment(currentPaperForAssignment!, assignment.id)}
                                        >
                                            撤销分配
                                        </Button>
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
                            renderItem={(item, index) => renderDimensionQuestionItem(item, index)}
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
                            renderItem={(item, index) => renderQuestionItem(item, index, {
                                selectedIds: selectedQuestionsForDimension,
                                onCheckChange: (id, checked) => {
                                    if (checked) {
                                        setSelectedQuestionsForDimension([...selectedQuestionsForDimension, id]);
                                    } else {
                                        setSelectedQuestionsForDimension(selectedQuestionsForDimension.filter(itemId => itemId !== id));
                                    }
                                }
                            })}
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
                        <Form.Item noStyle shouldUpdate>
                            {({ getFieldValue }) => (
                                <RichTextEditor
                                    value={getFieldValue('content') || ''}
                                    onChange={value => editQuestionForm.setFieldValue('content', value)}
                                    placeholder="请输入题目内容，可以直接上传或粘贴图片"
                                />
                            )}
                        </Form.Item>
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
                                            key={`${field.key}`}
                                            name={[field.name]}
                                            fieldKey={[field.fieldKey]}
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

            {/* 导入Excel题目预览模态框 */}
            <Modal
                title="导入Excel题目预览"
                open={excelImportModalVisible}
                onCancel={() => {
                    setExcelImportModalVisible(false);
                    setExcelImportedQuestions([]);
                    setExcelImportFile(null);
                }}
                footer={[
                    <Button key="cancel" onClick={() => {
                        setExcelImportModalVisible(false);
                        setExcelImportedQuestions([]);
                        setExcelImportFile(null);
                    }}>
                        取消
                    </Button>,
                    <Button key="confirm" type="primary" onClick={handleConfirmImportExcel} loading={excelImportLoading}>
                        确认导入 ({excelImportedQuestions.length} 道题目)
                    </Button>,
                ]}
                width={800}
            >
                <div>
                    <List
                        dataSource={excelImportedQuestions}
                        renderItem={(item, index) => (
                            <List.Item
                                actions={[
                                    <Button
                                        type="link"
                                        icon={<EditOutlined />}
                                        onClick={() => {
                                            setEditingQuestion({ ...item, _excelIndex: index });
                                            editQuestionForm.setFieldsValue({
                                                content: item.content,
                                                type: item.type,
                                                shuffle_options: item.shuffle_options,
                                                options: item.options,
                                                scores: item.scores,
                                            });
                                            setEditQuestionModalVisible(true);
                                        }}
                                    >编辑</Button>
                                ]}
                            >
                                <div>
                                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                        题目{index + 1}: <QuestionContentDisplay content={item.content} maxLength={150} />
                                    </div>
                                    <div style={{ color: '#666', fontSize: '12px' }}>
                                        类型: {item.type} | 选项乱序: {item.shuffle_options ? '是' : '否'} | 选项数: {item.options?.length || 0}
                                    </div>
                                    <div style={{ marginTop: 4 }}>
                                        {item.options && item.options.map((opt: string, idx: number) => (
                                            <div key={idx}>
                                                {String.fromCharCode(65 + idx)}. {opt} <span style={{ color: '#999', marginLeft: 8 }}>分数: {item.scores && item.scores[idx]}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </List.Item>
                        )}
                    />
                </div>
            </Modal>

            {/* 案例背景题弹窗 */}
            <Modal
                title="添加案例背景题"
                open={caseModalVisible}
                onOk={handleCaseModalOk}
                onCancel={() => setCaseModalVisible(false)}
                width={900}
                okText="提交全部"
            >
                <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, marginBottom: 8 }}>案例背景（支持直接粘贴或上传图片）：</div>
                    <RichTextEditor
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
                                            <Form.Item noStyle shouldUpdate>
                                                {() => (
                                                    <RichTextEditor
                                                        value={caseForm.getFieldValue(['questions', field.name, 'content']) || ''}
                                                        onChange={value => caseForm.setFieldValue(['questions', field.name, 'content'], value)}
                                                        placeholder="请输入题目内容，可以直接上传或粘贴图片"
                                                    />
                                                )}
                                            </Form.Item>
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
                                        <Form.List name={[field.name, 'options']} initialValue={[{ value: '', score: 0 }, { value: '', score: 0 }, { value: '', score: 0 }, { value: '', score: 0 }]}>
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
                                                    <Button type="dashed" onClick={() => addOpt({ value: '', score: 0 })} block icon={<PlusOutlined />}>添加选项</Button>
                                                </>
                                            )}
                                        </Form.List>
                                    </Card>
                                ))}
                                <Button type="dashed" onClick={() => add({ content: '', type: 'single', options: [{ value: '', score: 0 }, { value: '', score: 0 }, { value: '', score: 0 }, { value: '', score: 0 }], scores: [10, 7, 4, 1], shuffle_options: false })} block icon={<PlusOutlined />}>添加更多子题</Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>
        </div>
    );
};

export default PaperManagement; 