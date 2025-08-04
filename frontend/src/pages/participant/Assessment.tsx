import { useState, useEffect, useRef } from 'react'
import { Card, Button, Radio, Checkbox, Progress, message, Modal, List, Tag, Typography, Alert, Space, Divider, Badge } from 'antd'
import { ArrowLeftOutlined, ArrowRightOutlined, ClockCircleOutlined, FullscreenOutlined, FullscreenExitOutlined, CheckCircleFilled } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import React from 'react';

const { Title, Text } = Typography

interface Assignment {
    id: number
    paper_id: number
    paper_name: string
    paper_description: string
    duration: number
    status: string
    assigned_at: string
    started_at: string | null
    completed_at: string | null
}

interface Question {
    id: number
    content: string
    type: string
    options: Array<{ label: string; text: string; score: number }>
    order_num: number
    parent_case_id?: number // 新增：用于关联案例背景题
}

// 新增：将题目分组，支持parent_case_id
function groupQuestionsByParent(questions: Question[]) {
    const caseMap = new Map();
    const groups = [];
    // 先找所有case题
    questions.forEach(q => {
        if (q.type === 'case') {
            caseMap.set(q.id, { background: q, subQuestions: [] });
        }
    });
    // 再分配子题和普通题
    questions.forEach(q => {
        if (q.type !== 'case' && q.parent_case_id) {
            if (caseMap.has(q.parent_case_id)) {
                caseMap.get(q.parent_case_id).subQuestions.push(q);
            }
        } else if (q.type !== 'case') {
            groups.push({ type: 'normal', question: q });
        }
    });
    // 合并所有案例组
    for (const group of caseMap.values()) {
        groups.push({ type: 'case-group', ...group });
    }
    return groups;
}

const Assessment = () => {
    const [assignments, setAssignments] = useState<Assignment[]>([])
    const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null)
    const [questions, setQuestions] = useState<Question[]>([])
    const [currentQuestion, setCurrentQuestion] = useState(0)
    const [answers, setAnswers] = useState<Record<number, string[]>>({})
    const [assignmentLoading, setAssignmentLoading] = useState(true)
    const [showRules, setShowRules] = useState(false)
    const [agreedToRules, setAgreedToRules] = useState(false)
    const [isFullscreen, setIsFullscreen] = useState(false)
    const [timeLeft, setTimeLeft] = useState(0)
    const [testStarted, setTestStarted] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [fullscreenExitCount, setFullscreenExitCount] = useState(0) // 新增：退出全屏计数
    const MAX_FULLSCREEN_EXIT = 3 // 最大允许退出次数

    const navigate = useNavigate()
    const timerRef = useRef<number | null>(null)
    const fullscreenRef = useRef<HTMLDivElement>(null)

    // 获取试卷分配列表
    const fetchAssignments = async () => {
        try {
            setAssignmentLoading(true)
            const response = await fetch('http://localhost:8000/my-assignments', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setAssignments(data)
            } else {
                message.error('获取试卷分配失败')
            }
        } catch (error) {
            console.error('获取试卷分配错误:', error)
            message.error('获取试卷分配失败')
        } finally {
            setAssignmentLoading(false)
        }
    }

    // 获取试卷题目
    const fetchQuestions = async (paperId: number) => {
        try {
            // 从token中获取用户ID
            const token = localStorage.getItem('token')
            if (!token) {
                message.error('未找到登录信息')
                return
            }

            // 解析JWT token获取用户ID（只用user_id字段，必须为数字）
            let userId = null
            try {
                const payload = JSON.parse(atob(token.split('.')[1]))
                userId = payload.user_id // 只用user_id字段
            } catch (e) {
                console.warn('无法从token中获取用户ID')
            }

            const url = userId
                ? `http://localhost:8000/papers/${paperId}/questions-with-options?user_id=${userId}`
                : `http://localhost:8000/papers/${paperId}/questions-with-options`

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setQuestions(data.questions)
            } else {
                message.error('获取题目失败')
            }
        } catch (error) {
            console.error('获取题目错误:', error)
            message.error('获取题目失败')
        }
    }

    // 开始测试
    const startAssessment = async (assignmentId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/start-assessment/${assignmentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (response.ok) {
                setTestStarted(true)
                setTimeLeft(selectedAssignment!.duration * 60) // 转换为秒
                message.success('测试开始成功')

                // 尝试进入全屏模式，如果失败也允许继续
                try {
                    enterFullscreen();
                } catch (err) {
                    console.error('全屏启动错误:', err);
                    message.warning('全屏模式启动失败，请点击右上角全屏按钮手动进入全屏');
                }
            } else {
                const errorData = await response.json()
                message.error(errorData.detail || '开始测试失败')
            }
        } catch (error) {
            console.error('开始测试错误:', error)
            message.error('开始测试失败')
        }
    }

    // 进入全屏
    const enterFullscreen = () => {
        if (!fullscreenRef.current) return;

        try {
            if (fullscreenRef.current.requestFullscreen) {
                fullscreenRef.current.requestFullscreen()
                    .then(() => {
                        setIsFullscreen(true);
                    })
                    .catch((err) => {
                        console.error('全屏请求失败:', err);
                        message.warning('全屏模式启动失败，请点击右上角全屏按钮手动进入全屏');
                    });
            } else if ((fullscreenRef.current as any).webkitRequestFullscreen) {
                (fullscreenRef.current as any).webkitRequestFullscreen();
                setIsFullscreen(true);
            } else if ((fullscreenRef.current as any).msRequestFullscreen) {
                (fullscreenRef.current as any).msRequestFullscreen();
                setIsFullscreen(true);
            } else {
                message.warning('您的浏览器不支持自动全屏，请点击右上角全屏按钮手动进入全屏');
            }
        } catch (error) {
            console.error('全屏请求错误:', error);
            message.warning('全屏模式启动失败，请点击右上角全屏按钮手动进入全屏');
        }
    };

    // 退出全屏
    const exitFullscreen = () => {
        if (document.exitFullscreen) {
            document.exitFullscreen()
        } else if ((document as any).webkitExitFullscreen) {
            (document as any).webkitExitFullscreen()
        } else if ((document as any).msExitFullscreen) {
            (document as any).msExitFullscreen()
        }
        setIsFullscreen(false)
    }

    // 处理全屏变化
    useEffect(() => {
        const handleFullscreenChange = () => {
            if (testStarted) {
                if (!document.fullscreenElement) {
                    setIsFullscreen(false)
                    setFullscreenExitCount(prev => {
                        const newCount = prev + 1
                        if (newCount >= MAX_FULLSCREEN_EXIT) {
                            Modal.error({
                                title: '测试终止',
                                content: '您已多次退出全屏，测试已被终止。',
                                okText: '返回首页',
                                onOk: () => {
                                    setTestStarted(false)
                                    setTimeLeft(0)
                                    setFullscreenExitCount(0)
                                    navigate('/')
                                }
                            })
                        } else {
                            message.warning(`请保持全屏作答！再退出${MAX_FULLSCREEN_EXIT - newCount}次将终止测试。`)
                            // 尝试重新进入全屏
                            setTimeout(() => {
                                enterFullscreen()
                            }, 500)
                        }
                        return newCount
                    })
                } else {
                    setIsFullscreen(true)
                    // 确保全屏元素可见
                    if (fullscreenRef.current) {
                        // 强制重绘并设置背景色
                        fullscreenRef.current.style.backgroundColor = 'white'
                        fullscreenRef.current.style.color = 'black'
                        fullscreenRef.current.style.display = 'flex'

                        // 延迟一点点时间以确保样式已应用
                        setTimeout(() => {
                            if (fullscreenRef.current) {
                                // 触发重绘
                                fullscreenRef.current.style.opacity = '0.99'
                                setTimeout(() => {
                                    if (fullscreenRef.current) {
                                        fullscreenRef.current.style.opacity = '1'
                                    }
                                }, 50)
                            }
                        }, 10)
                    }
                }
            }
        }
        document.addEventListener('fullscreenchange', handleFullscreenChange)
        return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
    }, [testStarted, navigate])

    // 计时器
    useEffect(() => {
        if (testStarted && timeLeft > 0) {
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        // 时间到，自动提交
                        handleSubmit()
                        return 0
                    }
                    return prev - 1
                })
            }, 1000)
        }

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [testStarted, timeLeft])

    // 禁止复制
    useEffect(() => {
        if (testStarted) {
            const handleCopy = (e: ClipboardEvent) => {
                e.preventDefault()
                message.warning('测试期间禁止复制')
            }

            const handleKeyDown = (e: KeyboardEvent) => {
                if (e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
                    e.preventDefault()
                    message.warning('测试期间禁止复制')
                }
            }

            document.addEventListener('copy', handleCopy)
            document.addEventListener('keydown', handleKeyDown)

            return () => {
                document.removeEventListener('copy', handleCopy)
                document.removeEventListener('keydown', handleKeyDown)
            }
        }
    }, [testStarted])

    // 组件加载时获取试卷分配
    useEffect(() => {
        fetchAssignments()
    }, [])

    // 在组件首次加载时添加全屏提示
    useEffect(() => {
        message.info('如果测试无法自动进入全屏，请在测试开始后点击右上角全屏按钮手动进入全屏模式', 5);
    }, []);

    // 格式化时间
    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        const secs = seconds % 60
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const handleAnswerChange = (value: string | string[]) => {
        setAnswers(prev => ({
            ...prev,
            [questions[currentQuestion].id]: Array.isArray(value) ? value : [value]
        }))
    }

    const handleNext = () => {
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(prev => prev + 1)
        }
    }

    const handlePrev = () => {
        if (currentQuestion > 0) {
            setCurrentQuestion(prev => prev - 1)
        }
    }

    // 新增：用于记录每个题目在展平数组中的索引
    const [flatIndexMap, setFlatIndexMap] = useState<Record<number, number>>({});

    // 更新groupQuestionsByParent函数，增加更清晰的类型定义
    interface QuestionGroup {
        type: 'normal' | 'case-group';
        question?: Question;
        background?: Question;
        subQuestions?: Question[];
    }

    function groupQuestionsByParent(questions: Question[]): QuestionGroup[] {
        const caseMap = new Map();
        const groups: QuestionGroup[] = [];
        const indexMap: Record<number, number> = {}; // 记录每个题目ID对应的索引

        // 先找所有case题
        questions.forEach(q => {
            if (q.type === 'case') {
                caseMap.set(q.id, { background: q, subQuestions: [] });
            }
        });

        // 再分配子题和普通题
        questions.forEach(q => {
            if (q.type !== 'case' && q.parent_case_id) {
                if (caseMap.has(q.parent_case_id)) {
                    caseMap.get(q.parent_case_id).subQuestions.push(q);
                }
            } else if (q.type !== 'case') {
                groups.push({ type: 'normal', question: q });
            }
        });

        // 合并所有案例组
        for (const group of caseMap.values()) {
            groups.push({ type: 'case-group', ...group });
        }

        // 建立题目ID到展平后索引的映射
        let flatIndex = 0;
        for (const group of groups) {
            if (group.type === 'normal' && group.question) {
                indexMap[group.question.id] = flatIndex++;
            } else if (group.type === 'case-group' && group.subQuestions) {
                for (const subQ of group.subQuestions) {
                    indexMap[subQ.id] = flatIndex++;
                }
            }
        }

        return groups;
    }

    // 在useEffect中在分组后建立索引映射
    useEffect(() => {
        if (questions.length > 0) {
            const groups = groupQuestionsByParent(questions);
            const indexMap: Record<number, number> = {};

            let flatIndex = 0;
            for (const group of groups) {
                if (group.type === 'normal' && group.question) {
                    indexMap[group.question.id] = flatIndex++;
                } else if (group.type === 'case-group' && group.subQuestions) {
                    for (const subQ of group.subQuestions) {
                        indexMap[subQ.id] = flatIndex++;
                    }
                }
            }

            setFlatIndexMap(indexMap);
        }
    }, [questions]);

    // 修改题目跳转函数，使用索引映射
    const handleQuestionClick = (index: number) => {
        setCurrentQuestion(index);
    };

    const handleSubmit = async () => {
        setSubmitting(true)
        try {
            const response = await fetch(`http://localhost:8000/submit-assessment/${selectedAssignment!.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ answers })
            })

            if (response.ok) {
                message.success('测评完成！')
                setTestStarted(false)
                setTimeLeft(0)
                navigate('/participant/report')
            } else {
                const errorData = await response.json()
                message.error(errorData.detail || '提交失败')
            }
        } catch (error) {
            console.error('提交错误:', error)
            message.error('提交失败，请重试')
        } finally {
            setSubmitting(false)
        }
    }

    const handleSelectAssignment = async (assignment: Assignment) => {
        setSelectedAssignment(assignment)
        await fetchQuestions(assignment.paper_id)
        setShowRules(true)
    }

    const handleAgreeToRules = () => {
        setAgreedToRules(true)
        setShowRules(false)
        message.info('测试开始后请点击右上角全屏按钮进入全屏模式', 5);
    }

    // 开始测试时重置退出全屏计数
    const handleStartTest = () => {
        if (selectedAssignment) {
            setFullscreenExitCount(0)
            startAssessment(selectedAssignment.id)
        }
    }

    // 申请重做
    const handleRedoRequest = async () => {
        if (!selectedAssignment) return;
        try {
            const response = await fetch(`http://localhost:8000/redo-request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ assignment_id: selectedAssignment.id })
            });
            if (response.ok) {
                message.success('重做申请已提交，请等待管理员处理');
            } else {
                const data = await response.json();
                message.error(data.detail || '重做申请提交失败');
            }
        } catch (e) {
            message.error('重做申请提交失败');
        }
    };

    // 申请重做（列表页专用）
    const handleRedoRequestFromList = async (assignment: Assignment) => {
        try {
            const response = await fetch(`http://localhost:8000/redo-request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ assignment_id: assignment.id })
            });
            if (response.ok) {
                message.success('重做申请已提交，请等待管理员处理');
            } else {
                const data = await response.json();
                message.error(data.detail || '重做申请提交失败');
            }
        } catch (e) {
            message.error('重做申请提交失败');
        }
    };

    // 添加回渲染题目选项的函数
    // 渲染题目选项（单题/多题）
    function renderQuestionBlock(q: Question | undefined, value: string[], onChange: (value: string[]) => void) {
        if (!q) return null;
        if (q.type === 'single') {
            return (
                <Radio.Group
                    value={value[0]}
                    onChange={e => onChange([e.target.value])}
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        width: '100%'
                    }}
                >
                    {q.options?.map(option => {
                        const isChecked = value.includes(option.label);
                        return (
                            <Radio
                                key={option.label}
                                value={option.label}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    marginBottom: 16,
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    border: isChecked ? '1px solid #1890ff' : '1px solid #f0f0f0',
                                    background: isChecked ? '#e6f7ff' : 'white',
                                    boxShadow: isChecked ? '0 2px 8px rgba(24, 144, 255, 0.15)' : 'none',
                                    transition: 'all 0.3s'
                                }}
                            >
                                <span style={{ fontWeight: isChecked ? 600 : 500 }}>{option.label}.</span> {option.text}
                            </Radio>
                        );
                    })}
                </Radio.Group>
            );
        } else if (q.type === 'multiple' || q.type === 'indefinite') {
            return (
                <Checkbox.Group
                    value={value}
                    onChange={onChange}
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        width: '100%'
                    }}
                >
                    {q.options?.map(option => {
                        const isChecked = value.includes(option.label);
                        return (
                            <Checkbox
                                key={option.label}
                                value={option.label}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    marginBottom: 16,
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    border: isChecked ? '1px solid #1890ff' : '1px solid #f0f0f0',
                                    background: isChecked ? '#e6f7ff' : 'white',
                                    boxShadow: isChecked ? '0 2px 8px rgba(24, 144, 255, 0.15)' : 'none',
                                    transition: 'all 0.3s'
                                }}
                            >
                                <span style={{ fontWeight: isChecked ? 600 : 500 }}>{option.label}.</span> {option.text}
                            </Checkbox>
                        );
                    })}
                </Checkbox.Group>
            );
        }
        return null;
    }

    const renderQuestion = () => {
        if (!questions.length || currentQuestion >= questions.length) return null

        const currentQ = questions[currentQuestion]
        const currentAnswer = answers[currentQ.id] || []

        if (currentQ.type === 'single') {
            return (
                <Radio.Group
                    value={currentAnswer[0]}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                >
                    {currentQ.options.map(option => (
                        <Radio key={option.label} value={option.label} style={{ display: 'block', marginBottom: 16 }}>
                            {option.label}. {option.text}
                        </Radio>
                    ))}
                </Radio.Group>
            )
        } else {
            return (
                <Checkbox.Group
                    value={currentAnswer}
                    onChange={handleAnswerChange}
                >
                    {currentQ.options.map(option => (
                        <Checkbox key={option.label} value={option.label} style={{ display: 'block', marginBottom: 16 }}>
                            {option.label}. {option.text}
                        </Checkbox>
                    ))}
                </Checkbox.Group>
            )
        }
    }

    // 试卷选择界面
    if (!selectedAssignment && !testStarted) {
        return (
            <Card title="我的测试" loading={assignmentLoading}>
                {assignments.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <Text type="secondary">暂无分配的试卷</Text>
                    </div>
                ) : (
                    <List
                        dataSource={assignments}
                        renderItem={(assignment) => (
                            <List.Item
                                actions={[
                                    assignment.status === 'assigned' && (
                                        <Button
                                            type="primary"
                                            onClick={() => handleSelectAssignment(assignment)}
                                        >
                                            开始测试
                                        </Button>
                                    ),
                                    assignment.status === 'started' && (
                                        <>
                                            <Tag color="orange">进行中</Tag>
                                            <Button
                                                danger
                                                size="small"
                                                onClick={() => handleRedoRequestFromList(assignment)}
                                            >
                                                申请重做
                                            </Button>
                                        </>
                                    ),
                                    assignment.status === 'completed' && (
                                        <>
                                            <Tag color="green">已完成</Tag>
                                            <Button
                                                danger
                                                size="small"
                                                onClick={() => handleRedoRequestFromList(assignment)}
                                            >
                                                申请重做
                                            </Button>
                                        </>
                                    )
                                ]}
                            >
                                <List.Item.Meta
                                    title={assignment.paper_name}
                                    description={
                                        <div>
                                            <div>{assignment.paper_description}</div>
                                            <div>时长: {assignment.duration} 分钟</div>
                                            <div>分配时间: {assignment.assigned_at}</div>
                                        </div>
                                    }
                                />
                            </List.Item>
                        )}
                    />
                )}
            </Card>
        )
    }

    // 测试规则界面
    if (showRules) {
        return (
            <Modal
                title="测试规则"
                open={showRules}
                onCancel={() => setShowRules(false)}
                footer={null}
                width={600}
                closable={false}
                maskClosable={false}
            >
                <div style={{ marginBottom: 20 }}>
                    <Alert
                        message="重要提示"
                        description="请仔细阅读以下测试规则，同意后方可开始测试"
                        type="warning"
                        showIcon
                        style={{ marginBottom: 20 }}
                    />

                    <div style={{ marginBottom: 20 }}>
                        <Title level={4}>测试规则：</Title>
                        <ol>
                            <li>测试开始后会尝试自动打开全屏，如果自动全屏失败，请点击右上角全屏按钮手动进入全屏模式</li>
                            <li>测试结束前禁止退出全屏，三次退出全屏则终止测试</li>
                            <li>禁止复制题目内容</li>
                            <li>测试期间请勿刷新页面或关闭浏览器</li>
                            <li>请在规定时间内完成所有题目</li>
                            <li>提交后无法修改答案</li>
                        </ol>
                    </div>

                    <div style={{ textAlign: 'center' }}>
                        <Button
                            type="primary"
                            size="large"
                            onClick={handleAgreeToRules}
                        >
                            我已阅读并同意以上规则
                        </Button>
                    </div>
                </div>
            </Modal>
        )
    }

    // 测试界面
    if (testStarted && selectedAssignment) {
        // 分组并创建展平的题目列表（只包含可回答的题目）
        const questionGroups = groupQuestionsByParent(questions);
        const flattenedAnswerableQuestions: Question[] = [];

        // 创建展平的题目列表和建立映射关系
        questionGroups.forEach(group => {
            if (group.type === 'normal' && group.question) {
                flattenedAnswerableQuestions.push(group.question);
            } else if (group.type === 'case-group' && group.subQuestions) {
                flattenedAnswerableQuestions.push(...group.subQuestions);
            }
        });

        // 统计总题数（不含case背景）
        const totalQuestions = flattenedAnswerableQuestions.length;

        // 当前问题是展平后的索引
        const currentQ = flattenedAnswerableQuestions[currentQuestion];

        // 判断是否显示提交按钮（到达最后一题）
        const isLastQuestion = currentQuestion === totalQuestions - 1;

        // 统计已答题数
        const answeredQuestions = Object.keys(answers).length;

        // 渲染题目导航（只显示可答题）
        const navButtons = flattenedAnswerableQuestions.map((q, index) => {
            const isAnswered = answers[q.id] && answers[q.id].length > 0;
            return (
                <Badge
                    key={q.id}
                    count={isAnswered ? <CheckCircleFilled style={{ color: '#52c41a' }} /> : 0}
                    offset={[-5, 5]}
                >
                    <Button
                        size="middle"
                        type={index === currentQuestion ? 'primary' : 'default'}
                        style={{
                            width: '40px',
                            height: '40px',
                            margin: '6px',
                            borderRadius: '8px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            fontWeight: index === currentQuestion ? 'bold' : 'normal',
                            boxShadow: index === currentQuestion ? '0 2px 8px rgba(24, 144, 255, 0.3)' : 'none'
                        }}
                        onClick={() => handleQuestionClick(index)}
                    >
                        {index + 1}
                    </Button>
                </Badge>
            );
        });

        // 查找当前题目所在的组和背景
        let currentCaseBackground: Question | null = null;
        for (const group of questionGroups) {
            if (group.type === 'case-group' &&
                group.background &&
                group.subQuestions &&
                group.subQuestions.some(q => q.id === currentQ?.id)) {
                currentCaseBackground = group.background;
                break;
            }
        }

        // 底部操作按钮组件，确保提交按钮正确显示
        const bottomButtons = (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 32 }}>
                <Button
                    icon={<ArrowLeftOutlined />}
                    disabled={currentQuestion === 0}
                    onClick={handlePrev}
                    style={{
                        minWidth: '120px',
                        height: '46px',
                        borderRadius: '8px',
                        fontSize: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px'
                    }}
                >
                    上一题
                </Button>
                {isLastQuestion ? (
                    <Button
                        type="primary"
                        loading={submitting}
                        onClick={handleSubmit}
                        style={{
                            minWidth: '120px',
                            height: '46px',
                            borderRadius: '8px',
                            fontSize: '16px'
                        }}
                    >
                        提交测评
                    </Button>
                ) : (
                    <Button
                        type="primary"
                        icon={<ArrowRightOutlined />}
                        onClick={handleNext}
                        style={{
                            minWidth: '120px',
                            height: '46px',
                            borderRadius: '8px',
                            fontSize: '16px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}
                    >
                        下一题
                    </Button>
                )}
            </div>
        );

        // 渲染当前题目
        const renderCurrentQuestion = () => {
            if (!currentQ) return null;

            return (
                <>
                    {/* 如果是案例子题，先显示案例背景 */}
                    {currentCaseBackground && (
                        <div style={{
                            marginBottom: 32,
                            border: '1px solid #e6f7ff',
                            borderRadius: '12px',
                            background: 'linear-gradient(to right, #f0f7ff, #e6f7ff)',
                            padding: '24px',
                            boxShadow: '0 2px 8px rgba(24, 144, 255, 0.1)'
                        }}>
                            <div>
                                <Title level={4} style={{ color: '#1890ff', marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
                                    <span style={{
                                        display: 'inline-block',
                                        width: '4px',
                                        height: '18px',
                                        background: '#1890ff',
                                        marginRight: '8px',
                                        borderRadius: '2px'
                                    }}></span>
                                    案例背景
                                </Title>
                                <div
                                    style={{ fontSize: '16px', lineHeight: 1.7 }}
                                    dangerouslySetInnerHTML={{ __html: currentCaseBackground.content }}
                                />
                            </div>
                        </div>
                    )}

                    {/* 显示当前题目 */}
                    <div style={{ marginBottom: 32 }}>
                        <Title level={4} style={{
                            marginBottom: '24px',
                            display: 'flex',
                            alignItems: 'center',
                            color: '#262626'
                        }}>
                            <span style={{
                                display: 'inline-flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                background: '#1890ff',
                                color: 'white',
                                marginRight: '12px',
                                fontSize: '16px'
                            }}>{currentQuestion + 1}</span>
                            题目
                        </Title>
                        <div style={{
                            fontSize: '16px',
                            lineHeight: 1.6,
                            marginBottom: 24,
                            background: '#fafafa',
                            padding: '16px',
                            borderRadius: '8px',
                            border: '1px solid #f0f0f0'
                        }}>
                            <div dangerouslySetInnerHTML={{ __html: currentQ.content }} />
                        </div>
                        <div style={{ marginBottom: 24 }}>
                            {renderQuestionBlock(currentQ, answers[currentQ.id] || [], v => setAnswers(prev => ({ ...prev, [currentQ.id]: v })))}
                        </div>
                    </div>

                    {/* 底部按钮区域 */}
                    <div style={{ padding: '16px 0' }}>
                        {bottomButtons}
                    </div>
                </>
            );
        };

        return (
            <div ref={fullscreenRef} style={{
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'white',
                color: 'black',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* 顶部工具栏 */}
                <div style={{
                    padding: '16px 24px',
                    borderBottom: '1px solid #e8e8e8',
                    backgroundColor: '#fff',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
                    zIndex: 10
                }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <img
                            src="/纯logo.png"
                            alt="公司Logo"
                            style={{ height: '40px', marginRight: '16px' }}
                        />
                        <div>
                            <Title level={4} style={{ margin: 0 }}>{selectedAssignment.paper_name}</Title>
                            <Text type="secondary">第 {currentQuestion + 1} 题 / 共 {totalQuestions} 题</Text>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <div style={{
                            textAlign: 'center',
                            background: timeLeft < 300 ? '#fff1f0' : '#e6f7ff',
                            borderRadius: '8px',
                            padding: '8px 16px'
                        }}>
                            <div style={{
                                fontSize: '18px',
                                fontWeight: 'bold',
                                color: timeLeft < 300 ? '#ff4d4f' : '#1890ff'
                            }}>
                                <ClockCircleOutlined /> {formatTime(timeLeft)}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>剩余时间</div>
                        </div>
                        <Button
                            icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                            onClick={isFullscreen ? exitFullscreen : enterFullscreen}
                            type="default"
                            size="large"
                            style={{
                                minWidth: '100px',
                                height: '40px',
                                borderRadius: '8px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '4px'
                            }}
                        >
                            {isFullscreen ? '退出全屏' : '全屏'}
                        </Button>
                    </div>
                </div>
                <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}> {/* 添加overflow: hidden防止双重滚动条 */}
                    {/* 左侧题目列表 */}
                    <div style={{
                        width: '240px',
                        borderRight: '1px solid #e8e8e8',
                        background: 'linear-gradient(to bottom, #f9f9f9, #f0f0f0)',
                        display: 'flex',
                        flexDirection: 'column',
                        zIndex: 5
                    }}>
                        <div style={{ padding: '16px', borderBottom: '1px solid #e8e8e8' }}>
                            <Title level={5} style={{ margin: 0 }}>题目导航</Title>
                            <div style={{ marginTop: 8 }}>
                                <Progress
                                    percent={Math.round((answeredQuestions / totalQuestions) * 100)}
                                    size="small"
                                    format={() => `${answeredQuestions}/${totalQuestions}`}
                                    strokeColor={{
                                        '0%': '#108ee9',
                                        '100%': '#87d068',
                                    }}
                                />
                            </div>
                        </div>
                        <div style={{
                            padding: '16px',
                            overflowY: 'auto',
                            flex: 1,
                            display: 'flex',
                            flexDirection: 'column'
                        }}>
                            <Text type="secondary" style={{ marginBottom: '8px' }}>点击数字跳转到对应题目</Text>
                            <div style={{
                                display: 'flex',
                                flexWrap: 'wrap',
                                justifyContent: 'flex-start'
                            }}>
                                {navButtons}
                            </div>
                        </div>
                        <div style={{
                            padding: '16px',
                            borderTop: '1px solid #e8e8e8',
                            background: '#f9f9f9',
                            textAlign: 'center'
                        }}>
                            <Space direction="vertical">
                                <Text>完成情况</Text>
                                <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <div
                                            style={{
                                                backgroundColor: '#52c41a',
                                                color: 'white',
                                                minWidth: '30px',
                                                height: '30px',
                                                lineHeight: '30px',
                                                borderRadius: '15px',
                                                display: 'inline-block',
                                                padding: '0 10px',
                                                fontWeight: 'bold',
                                                fontSize: '14px',
                                                margin: '0 auto 5px auto'
                                            }}
                                        >
                                            {answeredQuestions}
                                        </div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>已答题</div>
                                    </div>
                                    <div style={{ textAlign: 'center' }}>
                                        <div
                                            style={{
                                                backgroundColor: '#999',
                                                color: 'white',
                                                minWidth: '30px',
                                                height: '30px',
                                                lineHeight: '30px',
                                                borderRadius: '15px',
                                                display: 'inline-block',
                                                padding: '0 10px',
                                                fontWeight: 'bold',
                                                fontSize: '14px',
                                                margin: '0 auto 5px auto'
                                            }}
                                        >
                                            {totalQuestions - answeredQuestions}
                                        </div>
                                        <div style={{ fontSize: '12px', color: '#666' }}>未答题</div>
                                    </div>
                                </div>
                            </Space>
                        </div>
                    </div>
                    {/* 右侧题目内容 */}
                    <div style={{
                        flex: 1,
                        height: '100%', // 确保占满剩余高度
                        display: 'flex',
                        flexDirection: 'column',
                        backgroundColor: 'white',
                        zIndex: 5
                    }}>
                        <div style={{
                            padding: '24px 40px',
                            overflowY: 'auto', // 这个区域添加滚动条
                            flex: 1 // 允许内容区域伸展填充
                        }}>
                            <div style={{ marginBottom: 24 }}>
                                <Progress
                                    percent={((currentQuestion + 1) / totalQuestions) * 100}
                                    strokeColor={{
                                        '0%': '#108ee9',
                                        '100%': '#87d068',
                                    }}
                                    size="small"
                                />
                            </div>
                            <div style={{
                                maxWidth: '900px',
                                margin: '0 auto',
                                background: '#fff',
                                padding: '24px',
                                borderRadius: '12px',
                                boxShadow: '0 2px 12px rgba(0, 0, 0, 0.05)',
                                width: '100%'
                            }}>
                                {renderCurrentQuestion()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    // 开始测试按钮界面
    if (agreedToRules && selectedAssignment && !testStarted) {
        const showRedo = selectedAssignment.status === 'completed' || selectedAssignment.status === 'started';
        return (
            <Card title="准备开始测试">
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <Title level={3}>{selectedAssignment.paper_name}</Title>
                    <div style={{ marginBottom: 20 }}>
                        <Text>试卷时长: {selectedAssignment.duration} 分钟</Text>
                    </div>
                    <div style={{ marginBottom: 20 }}>
                        <Text>题目数量: {questions.length} 题</Text>
                    </div>
                    <Button
                        type="primary"
                        size="large"
                        onClick={handleStartTest}
                    >
                        开始测试
                    </Button>
                    {showRedo && (
                        <Button
                            type="default"
                            danger
                            size="large"
                            style={{ marginLeft: 16 }}
                            onClick={handleRedoRequest}
                        >
                            申请重做
                        </Button>
                    )}
                </div>
            </Card>
        )
    }

    return null
}

export default Assessment 