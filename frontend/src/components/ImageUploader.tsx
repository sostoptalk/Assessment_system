import { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';

interface ImageUploaderProps {
    onUploadSuccess: (imageUrl: string) => void;
}

const ImageUploader = ({ onUploadSuccess }: ImageUploaderProps) => {
    const [loading, setLoading] = useState(false);
    const token = localStorage.getItem('token') || '';

    const beforeUpload = (file: File) => {
        const isImage = file.type.startsWith('image/');
        if (!isImage) {
            message.error('只能上传图片文件!');
            return false;
        }

        // 限制文件大小为5MB
        const isLt5M = file.size / 1024 / 1024 < 5;
        if (!isLt5M) {
            message.error('图片必须小于5MB!');
            return false;
        }

        return true;
    };

    const handleUpload = async (options: any) => {
        const { file, onSuccess, onError } = options;

        try {
            setLoading(true);
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post('/api/upload/image', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.data && response.data.url) {
                onSuccess(response.data, file);
                onUploadSuccess(response.data.url);
                message.success('上传成功');
            } else {
                onError(new Error('上传失败'));
                message.error('上传失败');
            }
        } catch (error) {
            console.error('上传图片错误:', error);
            onError(error);
            message.error('上传失败，请重试');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Upload
            name="file"
            showUploadList={false}
            customRequest={handleUpload}
            beforeUpload={beforeUpload}
        >
            <Button
                icon={<UploadOutlined />}
                loading={loading}
            >
                上传图片
            </Button>
        </Upload>
    );
};

export default ImageUploader; 