import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        host: '0.0.0.0', // 允许外部访问
        open: true, // 自动打开浏览器
        proxy: {
            // 处理/api路径的请求
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
                // 删除rewrite，因为后端API路径本来就包含/api
            },
            // 处理根路径的API请求
            '^/(login|me|register)': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 处理各种资源的API请求
            '^/(users|papers|questions|dimensions|reports|results)': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 处理管理路径的API请求
            '^/(participants|report-templates|dashboard)': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 处理上传文件的请求
            '/upload': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 处理静态文件的请求
            '/uploads': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    }
}) 