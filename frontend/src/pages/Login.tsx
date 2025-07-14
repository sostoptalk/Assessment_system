import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface LoginForm {
    username: string
    password: string
}

const Login = () => {
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const onFinish = async (values: LoginForm) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append('username', values.username)
            formData.append('password', values.password)

            const response = await axios.post('/api/login', formData)
            const { access_token } = response.data

            // 保存token到localStorage
            localStorage.setItem('token', access_token)

            // 用token获取用户信息
            const meRes = await axios.get('/api/me/', {
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            })
            const user = meRes.data
            localStorage.setItem('user', JSON.stringify(user))

            // 根据用户角色跳转
            if (user.role === 'admin') {
                message.success('管理员登录成功！')
                navigate('/admin')
            } else {
                message.success('登录成功！')
                navigate('/participant')
            }
        } catch (error) {
            message.error('登录失败，请检查用户名和密码')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            background: '#f5f5f5',
            overflow: 'hidden',
            position: 'relative'
        }}>
            {/* 背景装饰图片 */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 0,
                opacity: 0.1,
                backgroundImage: 'url(/组合1.png)',
                backgroundSize: 'cover',
                backgroundPosition: 'center'
            }}></div>

            <Card
                title={
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center'
                    }}>
                        {/* 修正logo路径 */}
                        <img 
                            src="/logo.png" 
                            alt="中量工程咨询有限公司"
                            style={{
                                width: '80px',
                                height: '80px',
                                marginBottom: '10px',
                                objectFit: 'contain'
                            }}
                        />
                        <h2 style={{
                            margin: 0,
                            fontSize: '20px',
                            color: '#333'
                        }}>中量工程咨询有限公司</h2>
                        <p style={{
                            margin: '5px 0 0 0',
                            fontSize: '16px',
                            color: '#666'
                        }}>人才测评系统</p>
                    </div>
                }
                style={{ 
                    width: 400,
                    textAlign: 'center',
                    zIndex: 1,
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1)',
                    borderRadius: '12px'
                }}
                headStyle={{ borderBottom: 'none', padding: '20px' }}
            >
                {/* 添加装饰分割线 */}
                <div style={{
                    width: '80%',
                    height: '1px',
                    backgroundColor: '#f0f0f0',
                    margin: '0 auto 20px'
                }}></div>

                <Form
                    name="login"
                    onFinish={onFinish}
                    autoComplete="off"
                    size="large"
                >
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: '请输入用户名!' }]}
                    >
                        <Input
                            prefix={<UserOutlined />}
                            placeholder="用户名"
                        />
                    </Form.Item>

                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: '请输入密码!' }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="密码"
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                            style={{
                                width: '100%',
                                height: '48px',
                                fontSize: '16px',
                                borderRadius: '8px'
                            }}
                        >
                            登录
                        </Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    )
}

export default Login