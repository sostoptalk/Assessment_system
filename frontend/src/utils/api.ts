import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const api = axios.create({
    // 不设置baseURL，使用相对路径直接请求
    // 这样可以更灵活地处理不同的API路径
    baseURL: '',
    timeout: 10000, // 请求超时时间
});

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 添加token到请求头
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        console.error('请求错误:', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
    response => {
        // 直接返回响应数据
        return response.data;
    },
    error => {
        // 处理错误响应
        if (error.response) {
            const { status, data } = error.response;

            switch (status) {
                case 401:
                    message.error('登录已过期，请重新登录');
                    // 可以在这里处理登出逻辑
                    break;
                case 403:
                    message.error('没有操作权限');
                    break;
                case 404:
                    message.error('请求的资源不存在');
                    break;
                case 500:
                    message.error('服务器错误');
                    break;
                default:
                    message.error(data.detail || '请求失败');
            }
        } else if (error.request) {
            message.error('无法连接到服务器，请检查网络');
        } else {
            message.error('请求配置错误');
        }

        return Promise.reject(error);
    }
);

// 常用的API请求封装
export const apiService = {
    // 获取列表
    async getList(url: string, params?: any) {
        // 移除URL中的/api前缀
        if (url.startsWith('/api/')) {
            url = url.substring(4); // 去掉/api前缀
        }
        // 确保URL以/开头
        if (!url.startsWith('/')) {
            url = '/' + url;
        }
        return api.get(url, { params });
    },

    // 获取详情
    async getDetail(url: string, id: number | string) {
        if (url.startsWith('/api/')) {
            url = url.substring(4);
        }
        if (!url.startsWith('/')) {
            url = '/' + url;
        }
        return api.get(`${url}/${id}`);
    },

    // 创建
    async create(url: string, data: any) {
        if (url.startsWith('/api/')) {
            url = url.substring(4);
        }
        if (!url.startsWith('/')) {
            url = '/' + url;
        }
        return api.post(url, data);
    },

    // 更新
    async update(url: string, id: number | string, data: any) {
        if (url.startsWith('/api/')) {
            url = url.substring(4);
        }
        if (!url.startsWith('/')) {
            url = '/' + url;
        }
        return api.put(`${url}/${id}`, data);
    },

    // 删除
    async delete(url: string, id: number | string) {
        if (url.startsWith('/api/')) {
            url = url.substring(4);
        }
        if (!url.startsWith('/')) {
            url = '/' + url;
        }
        return api.delete(`${url}/${id}`);
    },

    // 自定义请求
    async request(config: any) {
        // 处理URL中的/api前缀
        if (config.url && config.url.startsWith('/api/')) {
            config.url = config.url.substring(4);
            if (!config.url.startsWith('/')) {
                config.url = '/' + config.url;
            }
        }
        return api(config);
    }
};

export default api; 