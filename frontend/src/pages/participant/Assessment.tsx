import { useState, useEffect, useRef } from 'react'
import { Card, Button, Radio, Checkbox, Progress, message, Modal, List, Tag, Typography, Alert } from 'antd'
import { ArrowLeftOutlined, ArrowRightOutlined, ClockCircleOutlined, FullscreenOutlined, FullscreenExitOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

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

            // 解析JWT token获取用户ID（这里需要根据实际的token结构调整）
            let userId = null
            try {
                const payload = JSON.parse(atob(token.split('.')[1]))
                userId = payload.sub || payload.user_id
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
                enterFullscreen()
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
        if (fullscreenRef.current) {
            if (fullscreenRef.current.requestFullscreen) {
                fullscreenRef.current.requestFullscreen()
            }
        }
        setIsFullscreen(true)
    }

    // 退出全屏
    const exitFullscreen = () => {
        if (document.exitFullscreen) {
            document.exitFullscreen()
        }
        setIsFullscreen(false)
    }

    // 处理全屏变化
    useEffect(() => {
        const handleFullscreenChange = () => {
            if (!document.fullscreenElement) {
                setIsFullscreen(false)
                if (testStarted) {
                    message.warning(`您已退出全屏，再退出将终止测试`)
                }
            } else {
                setIsFullscreen(true)
            }
        }

        document.addEventListener('fullscreenchange', handleFullscreenChange)
        return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
    }, [testStarted])

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

    const handleQuestionClick = (index: number) => {
        setCurrentQuestion(index)
    }

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
    }

    const handleStartTest = () => {
        if (selectedAssignment) {
            startAssessment(selectedAssignment.id)
        }
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
                                        <Tag color="orange">进行中</Tag>
                                    ),
                                    assignment.status === 'completed' && (
                                        <Tag color="green">已完成</Tag>
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
                            <li>测试开始后会打开全屏，测试结束前禁止退出全屏，三次退出全屏则终止测试</li>
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
        const currentQ = questions[currentQuestion]
        const progress = ((currentQuestion + 1) / questions.length) * 100
        const answeredQuestions = Object.keys(answers).length

        return (
            <div ref={fullscreenRef} style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
                {/* 顶部工具栏 */}
                <div style={{
                    padding: '16px',
                    borderBottom: '1px solid #d9d9d9',
                    backgroundColor: '#fafafa',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div>
                        <Title level={4} style={{ margin: 0 }}>{selectedAssignment.paper_name}</Title>
                        <Text type="secondary">第 {currentQuestion + 1} 题 / 共 {questions.length} 题</Text>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: timeLeft < 300 ? '#ff4d4f' : '#1890ff' }}>
                                <ClockCircleOutlined /> {formatTime(timeLeft)}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>剩余时间</div>
                        </div>

                        <Button
                            icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                            onClick={isFullscreen ? exitFullscreen : enterFullscreen}
                        >
                            {isFullscreen ? '退出全屏' : '全屏'}
                        </Button>
                    </div>
                </div>

                <div style={{ flex: 1, display: 'flex' }}>
                    {/* 左侧题目列表 */}
                    <div style={{
                        width: '300px',
                        borderRight: '1px solid #d9d9d9',
                        padding: '16px',
                        overflowY: 'auto'
                    }}>
                        <Title level={5}>题目导航</Title>
                        <div style={{ marginBottom: 8 }}>
                            <Text type="secondary">已答题: {answeredQuestions}/{questions.length}</Text>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8 }}>
                            {questions.map((question, index) => {
                                const isAnswered = answers[question.id] && answers[question.id].length > 0
                                const isCurrent = index === currentQuestion

                                return (
                                    <Button
                                        key={question.id}
                                        size="small"
                                        type={isCurrent ? 'primary' : 'default'}
                                        style={{
                                            backgroundColor: isAnswered ? '#52c41a' : '#f0f0f0',
                                            color: isAnswered ? 'white' : 'black',
                                            border: isCurrent ? '2px solid #1890ff' : '1px solid #d9d9d9'
                                        }}
                                        onClick={() => handleQuestionClick(index)}
                                    >
                                        {index + 1}
                                    </Button>
                                )
                            })}
                        </div>
                    </div>

                    {/* 右侧题目内容 */}
                    <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
                        <div style={{ marginBottom: 24 }}>
                            <Progress percent={progress} />
                        </div>

                        {currentQ && (
                            <div>
                                <div style={{ marginBottom: 24 }}>
                                    <Title level={4}>题目 {currentQuestion + 1}</Title>
                                    <div style={{ fontSize: '16px', lineHeight: 1.6 }}>
                                        {currentQ.content}
                                    </div>
                                </div>

                                <div style={{ marginBottom: 24 }}>
                                    {renderQuestion()}
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Button
                                        icon={<ArrowLeftOutlined />}
                                        disabled={currentQuestion === 0}
                                        onClick={handlePrev}
                                    >
                                        上一题
                                    </Button>

                                    {currentQuestion === questions.length - 1 ? (
                                        <Button
                                            type="primary"
                                            loading={submitting}
                                            onClick={handleSubmit}
                                        >
                                            提交测评
                                        </Button>
                                    ) : (
                                        <Button
                                            type="primary"
                                            icon={<ArrowRightOutlined />}
                                            onClick={handleNext}
                                        >
                                            下一题
                                        </Button>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )
    }

    // 开始测试按钮界面
    if (agreedToRules && selectedAssignment && !testStarted) {
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
                </div>
            </Card>
        )
    }

    return null
}

export default Assessment 