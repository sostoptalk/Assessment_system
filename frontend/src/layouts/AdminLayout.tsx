import { useState } from 'react'
import { Layout, Menu, Button, message } from 'antd'
import {
    QuestionCircleOutlined,
    UserOutlined,
    FileTextOutlined,
    LogoutOutlined,
    DashboardOutlined,
    BookOutlined,
    FileSearchOutlined
} from '@ant-design/icons'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import Dashboard from '../pages/admin/Dashboard'
import QuestionManagement from '../pages/admin/QuestionManagement'
import PaperManagement from '../pages/admin/PaperManagement'
import ParticipantManagement from '../pages/admin/ParticipantManagement'
import ReportManagement from '../pages/admin/ReportManagement'
import ResultManagement from '../pages/admin/ResultManagement'
import ReportTemplateManagement from '../pages/admin/ReportTemplateManagement'

const { Header, Sider, Content } = Layout

const AdminLayout = () => {
    const [collapsed, setCollapsed] = useState(false)
    const navigate = useNavigate()
    const location = useLocation()

    const menuItems = [
        {
            key: '/admin/dashboard',
            icon: <DashboardOutlined />,
            label: '仪表盘',
        },
        {
            key: '/admin/questions',
            icon: <QuestionCircleOutlined />,
            label: '题库管理',
        },
        {
            key: '/admin/papers',
            icon: <BookOutlined />,
            label: '试卷管理',
        },
        {
            key: '/admin/participants',
            icon: <UserOutlined />,
            label: '被试者管理',
        },
        {
            key: '/admin/reports',
            icon: <FileTextOutlined />,
            label: '报告管理',
        },
        {
            key: '/admin/report-templates',
            icon: <FileTextOutlined />,
            label: '报告模板',
        },
        {
            key: '/admin/result',
            icon: <FileSearchOutlined />,
            label: '测试结果',
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
        <Layout style={{ height: '100vh', width: '100vw', overflow: 'auto' }}>
            <Sider
                collapsible
                collapsed={collapsed}
                onCollapse={setCollapsed}
                theme="light"
            >
                {/* 添加公司logo */}
                <div style={{
                    height: collapsed ? 48 : 100,
                    margin: '16px auto',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    flexDirection: collapsed ? 'column' : 'column',
                    transition: 'all 0.3s'
                }}>
                    <img
                        src="/logo.png"
                        alt="中量工程咨询有限公司"
                        style={{
                            width: collapsed ? 32 : 64,
                            height: collapsed ? 32 : 64,
                            objectFit: 'contain'
                        }}
                    />
                    {!collapsed && (
                        <span style={{
                            fontSize: '14px',
                            fontWeight: 'bold',
                            marginTop: '8px',
                            color: '#333'
                        }}>中量工程咨询</span>
                    )}
                </div>

                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={handleMenuClick}
                />
            </Sider>
            <Layout style={{ height: '100%', overflow: 'auto' }}>
                <Header style={{
                    padding: '0 16px',
                    background: '#fff',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    {/* 保持现有标题不变 */}
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
                    height: '100%',
                    overflow: 'auto'
                }}>
                    <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/questions" element={<QuestionManagement />} />
                        <Route path="/papers" element={<PaperManagement />} />
                        <Route path="/participants" element={<ParticipantManagement />} />
                        <Route path="/reports" element={<ReportManagement />} />
                        <Route path="/report-templates" element={<ReportTemplateManagement />} />
                        <Route path="/result" element={<ResultManagement />} />
                        <Route path="/" element={<Dashboard />} />
                    </Routes>
                </Content>
            </Layout>
        </Layout>
    )
}

export default AdminLayout