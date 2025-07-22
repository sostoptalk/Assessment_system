import { Card, Descriptions, Button, message, Modal, Form, Input, Spin, AutoComplete, Select } from 'antd'
import { EditOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'
import { useState, useEffect } from 'react'

interface UserInfo {
    username: string
    real_name: string
    email: string
    phone: string
    role: string
    gender?: string
    age?: number
    position?: string
}

// 岗位列表（可根据实际岗位补充）
const positionOptions = [
    '生产力促进部副总监',
    '经营管理主管',
    '副总裁兼广州分公司总经理',
    '董事长兼总裁',
    '咨询师',
    '招采项目经理',
    '见习咨询师',
    '数字化总监',
    '项目主管',
    '项目经理',
    '项目专员',
    '法务经理',
    '管培生',
    '审计专员',
    '财务主管',
    '运作支持主管',
    '新咨询发展研究院执行院长',
    '研发赋能专员',
    '法务专员',
    '双碳项目区域负责人',
    '组织发展主管',
    '法务主管',
    '数字化主管',
    '研发赋能主管',
    '总经理助理',
    '合约专员',
    '会计主管',
    '合约主管',
    '询价副经理',
    '品牌专员',
    'IT主管',
    '制度流程主管',
    '品牌经理',
    '招聘专员',
    '档案管理员',
    '会计',
    '办公室主任',
    'IT专员',
    '品牌主管',
    '薪酬绩效主管',
    '综合事务专员',
    '询价专员',
    '合同专员',
    '综合事务主管',
    '人力资源主管',
    '招聘主管',
    '培训主管',
    '文员',
    '司机',
    '资料员',
    '项目资料员',
    '行政专员',
    '行政主管',
    '人力资源部总监',
    '人力行政部经理',
    '人力资源专员',
    '人力行政主管',
    '人力资源部经理',
    '出纳',
    '财务经理',
    '财务专员',
    '保洁',
    '人力行政专员',
    '人力资源副经理',
    '市场部经理',
    '投标专员',
    '投标主管',
    '助理客户经理',
    '高级客户经理',
    '客户经理',
    '商务主管',
    '商务经理',
    '商务专员',
    '市场合约部经理',
    '质控专员',
    '质控副主任兼造价纠纷与法律服务部经理',
    '总工程师兼质控主任',
    '质控主任',
    '质控副主任',
    '质控主管',
    '部门主管',
    'BIM项目经理',
    'BIM工程师',
    '招采专员',
    '招采主管',
    '招采业务部经理',
    '高级造价主管',
    '造价纠纷调解经理',
    '鉴定经理',
    '副经理',
    '经理',
    '部门经理',
    '造价业务部经理',
    '实习生',
    '鉴定主管',
    '鉴定专员',
    '专业经理',
    '造价员',
    '造价主管',
    '数字化与AI创新总监',
    '承包商事业部总监',
    '副总裁兼政企决策与前期咨询事业中心总经理',
    '副总裁兼市场与营销中心总经理',
    '营销中心副总经理兼海南分公司营销负责人',
    '新咨询发展研究院副院长',
    '数字化事业部总监',
    '生产力促进中心副总监',
    '政企决策与前期咨询事业中心副总监',
    '技术总监',
    '（储备）副总经理',
    '成本顾问中心总经理',
    '副总裁',
    '全过程工程咨询事业部副总监',
    '数字化专业技术委员会主任',
    '东莞分公司总经理兼广州分公司常务副总经理',
    '人力资源部副总监',
    '造价纠纷与法律服务中心副总监',
    '副总经理兼东莞分公司常务副总经理（兼质控主任）',
    '常务副总经理',
    '商务总经理',
    '市场部总监',
    '法律咨询业务部总监',
    '造价纠纷与法律服务中心总经理',
    '运营管理中心总经理',
    '造价纠纷业务部总监',
    '政府决策与前期咨询事业中心总经理',
    '运营管理中心副总经理',
    '总监',
    '副总经理',
    '总经理',
    '总裁',
    '董事长',
    '常务副总裁',
    '副董事长',
    '城市公司发展和管理部副总监',
    '总工程师',
    '财务部总监',
]


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
                // 设置表单初始值
                profileForm.setFieldsValue({
                    email: data.email || '',
                    phone: data.phone || '',
                    gender: data.gender || '',
                    age: data.age || '',
                    position: data.position || ''
                })
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
                    phone: values.phone,
                    gender: values.gender,
                    age: values.age,
                    position: values.position
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
                    <Descriptions.Item label="性别">{userInfo.gender || '未设置'}</Descriptions.Item>
                    <Descriptions.Item label="年龄">{userInfo.age || '未设置'}</Descriptions.Item>
                    <Descriptions.Item label="岗位">{userInfo.position || '未设置'}</Descriptions.Item>
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
                        phone: userInfo.phone || '',
                        gender: userInfo.gender || '',
                        age: userInfo.age || '',
                        position: userInfo.position || ''
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

                    <Form.Item
                        label="性别"
                        name="gender"
                        rules={[{ required: false }]}
                    >
                        <Select placeholder="请选择性别" allowClear>
                            <Select.Option value="男">男</Select.Option>
                            <Select.Option value="女">女</Select.Option>
                            <Select.Option value="其他">其他</Select.Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        label="年龄"
                        name="age"
                        rules={[
                            { pattern: /^\d{1,3}$/, message: '请输入有效的年龄' }
                        ]}
                    >
                        <Input type="number" min={0} max={120} placeholder="请输入年龄" />
                    </Form.Item>

                    <Form.Item
                        label="岗位"
                        name="position"
                        rules={[{ required: false }]}
                    >
                        <AutoComplete
                            options={positionOptions.map(pos => ({ value: pos }))}
                            placeholder="请输入或选择岗位"
                            filterOption={(inputValue, option) =>
                                option!.value.toLowerCase().indexOf(inputValue.toLowerCase()) !== -1
                            }
                            allowClear
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