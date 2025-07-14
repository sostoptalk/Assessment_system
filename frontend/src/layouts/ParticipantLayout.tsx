import { useState } from 'react'
import { Layout, Menu, Button, message } from 'antd'
import {
    FormOutlined,
    FileTextOutlined,
    LogoutOutlined,
    UserOutlined
} from '@ant-design/icons'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import Profile from '../pages/participant/Profile'
import Assessment from '../pages/participant/Assessment'
import Report from '../pages/participant/Report'

const { Header, Sider, Content } = Layout

const ParticipantLayout = () => {
    const [collapsed, setCollapsed] = useState(false)
    const navigate = useNavigate()
    const location = useLocation()

    const menuItems = [
        {
            key: '/participant/profile',
            icon: <UserOutlined />,
            label: '个人信息',
        },
        {
            key: '/participant/assessment',
            icon: <FormOutlined />,
            label: '开始测评',
        },
        {
            key: '/participant/report',
            icon: <FileTextOutlined />,
            label: '我的报告',
        },
    ]

    const handleMenuClick = ({ key }: { key: string }) => {
        navigate(key)
    }

    const handleLogout = () => {
        localStorage.removeItem('token')
        message.success('已退出登录')
        navigate('/login')
    }

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider
                collapsible
                collapsed={collapsed}
                onCollapse={setCollapsed}
                theme="light"
            >
                <div style={{
                    height: 32,
                    margin: 16,
                    background: 'rgba(255, 255, 255, 0.2)',
                    textAlign: 'center',
                    lineHeight: '32px',
                    fontWeight: 'bold'
                }}>
                    测评平台
                </div>
                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={handleMenuClick}
                />
            </Sider>
            <Layout>
                <Header style={{
                    padding: '0 16px',
                    background: '#fff',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <h2 style={{ margin: 0 }}>中量工程咨询有限公司</h2>
                    <Button
                        type="text"
                        icon={<LogoutOutlined />}
                        onClick={handleLogout}
                    >
                        退出登录
                    </Button>
                </Header>
                <Content style={{
                    margin: '16px',
                    padding: '24px',
                    background: '#fff',
                    borderRadius: '8px',
                    minHeight: 'calc(100vh - 120px)'
                }}>
                    <Routes>
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/assessment" element={<Assessment />} />
                        <Route path="/report" element={<Report />} />
                        <Route path="/" element={<Profile />} />
                    </Routes>
                </Content>
            </Layout>
        </Layout>
    )
}

export default ParticipantLayout 