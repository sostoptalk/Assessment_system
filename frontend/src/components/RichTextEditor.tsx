import React, { useRef, useEffect, useState } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import axios from 'axios';

interface RichTextEditorProps {
    value: string;
    onChange: (content: string) => void;
    placeholder?: string;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({ value, onChange, placeholder }) => {
    const quillRef = useRef<any>(null);
    const [isLoading, setIsLoading] = useState(false);

    // 监听粘贴图片事件
    useEffect(() => {
        let quillEditor: any = null;
        let pasteListener: ((e: ClipboardEvent) => Promise<void>) | null = null;

        if (quillRef.current) {
            quillEditor = quillRef.current.getEditor();

            // 处理粘贴事件，检测是否粘贴了图片
            pasteListener = async (e: ClipboardEvent) => {
                if (e.clipboardData && e.clipboardData.items) {
                    const items = e.clipboardData.items;

                    for (let i = 0; i < items.length; i++) {
                        if (items[i].type.indexOf('image') !== -1) {
                            e.preventDefault();

                            const file = items[i].getAsFile();
                            if (file) {
                                await handleImageUpload(file, quillEditor);
                            }
                            break;
                        }
                    }
                }
            };

            quillEditor.root.addEventListener('paste', pasteListener);
        }

        // 清理函数，移除事件监听器
        return () => {
            if (quillEditor && pasteListener) {
                quillEditor.root.removeEventListener('paste', pasteListener);
            }
        };
    }, []);

    const handleImageUpload = async (file: File, quill: any) => {
        try {
            setIsLoading(true);

            const token = localStorage.getItem('token') || '';
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post('/api/upload/image', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.data && response.data.url) {
                // 获取当前光标位置
                const range = quill.getSelection(true);
                // 在光标位置插入图片
                quill.insertEmbed(range.index, 'image', response.data.url);
                // 光标向后移动一位
                quill.setSelection(range.index + 1);
            }
        } catch (error) {
            console.error('上传图片错误:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const imageHandler = () => {
        // 创建一个文件输入框
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');
        input.click();

        // 监听文件选择事件
        input.onchange = async () => {
            const file = input.files?.[0];
            if (file) {
                const quill = quillRef.current.getEditor();
                await handleImageUpload(file, quill);
            }
        };
    };

    const modules = {
        toolbar: {
            container: [
                [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                [{ 'indent': '-1' }, { 'indent': '+1' }],
                ['link', 'image'],
                ['clean']
            ],
            handlers: {
                image: imageHandler
            }
        }
    };

    return (
        <div className="rich-text-editor">
            {isLoading && (
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(255,255,255,0.5)',
                    zIndex: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <span>正在上传图片...</span>
                </div>
            )}
            <ReactQuill
                ref={quillRef}
                theme="snow"
                value={value || ''}
                onChange={onChange}
                placeholder={placeholder || "请输入内容..."}
                modules={modules}
                style={{ minHeight: '200px' }}
                preserveWhitespace
            />
        </div>
    );
};

export default RichTextEditor; 