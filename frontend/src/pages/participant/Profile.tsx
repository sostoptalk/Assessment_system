import { Card, Descriptions, Button, message, Modal, Form, Input, Spin } from 'antd'
import { EditOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'
import { useState, useEffect } from 'react'

interface UserInfo {
    username: string
    real_name: string
    email: string
    phone: string
    role: string
}

const Profile = () => {
    const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
    const [loading, setLoading] = useState(true)
    const [profileModalVisible, setProfileModalVisible] = useState(false)
    const [passwordModalVisible, setPasswordModalVisible] = useState(false)
    const [profileForm] = Form.useForm()
    const [passwordForm] = Form.useForm()
    const [updating, setUpdating] = useState(false)

    // 获取用户信息
    const fetchUserInfo = async () => {
        try {
            setLoading(true)
            const response = await fetch('http://localhost:8000/me', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setUserInfo(data)
            } else {
                message.error('获取用户信息失败')
            }
        } catch (error) {
            console.error('获取用户信息错误:', error)
            message.error('获取用户信息失败')
        } finally {
            setLoading(false)
        }
    }

    // 更新基本信息
    const handleUpdateProfile = async (values: any) => {
        try {
            setUpdating(true)
            const response = await fetch('http://localhost:8000/me/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    email: values.email,
                    phone: values.phone
                })
            })

            if (response.ok) {
                const data = await response.json()
                setUserInfo(data)
                setProfileModalVisible(false)
                message.success('基本信息更新成功')
                profileForm.resetFields()
            } else {
                const errorData = await response.json()
                message.error(errorData.detail || '更新失败')
            }
        } catch (error) {
            console.error('更新基本信息错误:', error)
            message.error('更新失败')
        } finally {
            setUpdating(false)
        }
    }

    // 更新密码
    const handleUpdatePassword = async (values: any) => {
        try {
            setUpdating(true)
            const response = await fetch('http://localhost:8000/me/password', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    old_password: values.old_password,
                    new_password: values.new_password
                })
            })

            if (response.ok) {
                setPasswordModalVisible(false)
                message.success('密码更新成功')
                passwordForm.resetFields()
            } else {
                const errorData = await response.json()
                message.error(errorData.detail || '密码更新失败')
            }
        } catch (error) {
            console.error('更新密码错误:', error)
            message.error('密码更新失败')
        } finally {
            setUpdating(false)
        }
    }

    // 组件加载时获取用户信息
    useEffect(() => {
        fetchUserInfo()
    }, [])

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>加载中...</div>
            </div>
        )
    }

    if (!userInfo) {
        return (
            <Card title="个人信息">
                <div style={{ textAlign: 'center', padding: '20px' }}>
                    无法获取用户信息
                </div>
            </Card>
        )
    }

    return (
        <div>
            <Card
                title="个人信息"
                extra={
                    <div>
                        <Button
                            type="primary"
                            icon={<EditOutlined />}
                            onClick={() => setProfileModalVisible(true)}
                            style={{ marginRight: 8 }}
                        >
                            编辑信息
                        </Button>
                        <Button
                            icon={<LockOutlined />}
                            onClick={() => setPasswordModalVisible(true)}
                        >
                            修改密码
                        </Button>
                    </div>
                }
            >
                <Descriptions bordered>
                    <Descriptions.Item label="用户名">{userInfo.username}</Descriptions.Item>
                    <Descriptions.Item label="真实姓名">{userInfo.real_name}</Descriptions.Item>
                    <Descriptions.Item label="邮箱">{userInfo.email || '未设置'}</Descriptions.Item>
                    <Descriptions.Item label="手机号">{userInfo.phone || '未设置'}</Descriptions.Item>
                    <Descriptions.Item label="角色">被试者</Descriptions.Item>
                </Descriptions>
            </Card>

            {/* 编辑基本信息模态框 */}
            <Modal
                title="编辑基本信息"
                open={profileModalVisible}
                onCancel={() => {
                    setProfileModalVisible(false)
                    profileForm.resetFields()
                }}
                footer={null}
                destroyOnClose
            >
                <Form
                    form={profileForm}
                    layout="vertical"
                    onFinish={handleUpdateProfile}
                    initialValues={{
                        email: userInfo.email || '',
                        phone: userInfo.phone || ''
                    }}
                >
                    <Form.Item
                        label="邮箱"
                        name="email"
                        rules={[
                            { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                    >
                        <Input
                            prefix={<MailOutlined />}
                            placeholder="请输入邮箱地址"
                        />
                    </Form.Item>

                    <Form.Item
                        label="手机号"
                        name="phone"
                        rules={[
                            { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                        ]}
                    >
                        <Input
                            prefix={<PhoneOutlined />}
                            placeholder="请输入手机号"
                        />
                    </Form.Item>

                    <Form.Item>
                        <div style={{ textAlign: 'right' }}>
                            <Button
                                onClick={() => {
                                    setProfileModalVisible(false)
                                    profileForm.resetFields()
                                }}
                                style={{ marginRight: 8 }}
                            >
                                取消
                            </Button>
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={updating}
                            >
                                保存
                            </Button>
                        </div>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 修改密码模态框 */}
            <Modal
                title="修改密码"
                open={passwordModalVisible}
                onCancel={() => {
                    setPasswordModalVisible(false)
                    passwordForm.resetFields()
                }}
                footer={null}
                destroyOnClose
            >
                <Form
                    form={passwordForm}
                    layout="vertical"
                    onFinish={handleUpdatePassword}
                >
                    <Form.Item
                        label="原密码"
                        name="old_password"
                        rules={[
                            { required: true, message: '请输入原密码' },
                            { min: 6, message: '密码长度不能少于6位' }
                        ]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="请输入原密码"
                        />
                    </Form.Item>

                    <Form.Item
                        label="新密码"
                        name="new_password"
                        rules={[
                            { required: true, message: '请输入新密码' },
                            { min: 6, message: '密码长度不能少于6位' }
                        ]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="请输入新密码"
                        />
                    </Form.Item>

                    <Form.Item
                        label="确认新密码"
                        name="confirm_password"
                        dependencies={['new_password']}
                        rules={[
                            { required: true, message: '请确认新密码' },
                            ({ getFieldValue }) => ({
                                validator(_, value) {
                                    if (!value || getFieldValue('new_password') === value) {
                                        return Promise.resolve()
                                    }
                                    return Promise.reject(new Error('两次输入的密码不一致'))
                                }
                            })
                        ]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="请再次输入新密码"
                        />
                    </Form.Item>

                    <Form.Item>
                        <div style={{ textAlign: 'right' }}>
                            <Button
                                onClick={() => {
                                    setPasswordModalVisible(false)
                                    passwordForm.resetFields()
                                }}
                                style={{ marginRight: 8 }}
                            >
                                取消
                            </Button>
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={updating}
                            >
                                修改密码
                            </Button>
                        </div>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    )
}

export default Profile 