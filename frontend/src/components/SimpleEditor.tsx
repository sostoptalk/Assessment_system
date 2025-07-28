import React, { useEffect, useState } from 'react';
import { Input, Button, Space, Upload, message } from 'antd';
import { BoldOutlined, ItalicOutlined, UnderlineOutlined, UploadOutlined } from '@ant-design/icons';
import axios from 'axios';
import type { UploadProps } from 'antd';

const { TextArea } = Input;

interface SimpleEditorProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
}

/**
 * 简单文本编辑器，用于替代ReactQuill
 */
const SimpleEditor: React.FC<SimpleEditorProps> = ({
  value = '',
  onChange,
  placeholder = '请输入内容...'
}) => {
  const [content, setContent] = useState(value || '');

  // 同步外部传入的值
  useEffect(() => {
    if (value !== undefined) {
      setContent(value);
    }
  }, [value]);

  // 处理内容变更
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    if (onChange) {
      onChange(newContent);
    }
  };

  // 处理图片上传
  const uploadProps: UploadProps = {
    name: 'file',
    action: '/upload/image',
    headers: {
      authorization: `Bearer ${localStorage.getItem('token') || ''}`,
    },
    onChange(info) {
      if (info.file.status === 'done') {
        if (info.file.response && info.file.response.url) {
          // 在光标位置或末尾插入图片链接
          const imgTag = `<img src="${info.file.response.url}" alt="上传图片" />`;
          const newContent = content + imgTag;
          setContent(newContent);
          if (onChange) {
            onChange(newContent);
          }
          message.success(`图片上传成功`);
        }
      } else if (info.file.status === 'error') {
        message.error(`图片上传失败`);
      }
    },
  };

  // 添加简单的格式化功能
  const addFormat = (tag: string) => {
    const newContent = content + `<${tag}>${tag === 'br' ? '' : '文字'}</${tag}>`;
    setContent(newContent);
    if (onChange) {
      onChange(newContent);
    }
  };

  return (
    <div className="simple-editor">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <Button
            icon={<BoldOutlined />}
            onClick={() => addFormat('b')}
          />
          <Button
            icon={<ItalicOutlined />}
            onClick={() => addFormat('i')}
          />
          <Button
            icon={<UnderlineOutlined />}
            onClick={() => addFormat('u')}
          />
          <Button onClick={() => addFormat('br')}>
            换行
          </Button>
          <Upload {...uploadProps} showUploadList={false}>
            <Button icon={<UploadOutlined />}>上传图片</Button>
          </Upload>
        </Space>
        <TextArea
          value={content}
          onChange={handleChange}
          placeholder={placeholder}
          autoSize={{ minRows: 6, maxRows: 12 }}
          style={{ width: '100%' }}
        />
        <div>
          <small style={{ color: '#999' }}>
            支持HTML标签，例如: &lt;b&gt;粗体&lt;/b&gt;, &lt;i&gt;斜体&lt;/i&gt;, &lt;u&gt;下划线&lt;/u&gt;
          </small>
        </div>
      </Space>
    </div>
  );
};

export default SimpleEditor; 