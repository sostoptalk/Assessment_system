import React from 'react';
import DOMPurify from 'dompurify';

interface QuestionContentDisplayProps {
    content: string;
    maxLength?: number;
    showImage?: boolean;
}

const QuestionContentDisplay: React.FC<QuestionContentDisplayProps> = ({
    content,
    maxLength = 100,
    showImage = false
}) => {
    // 安全处理HTML内容
    const sanitizedContent = DOMPurify.sanitize(content);

    // 创建一个临时的div来解析HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = sanitizedContent;

    // 检查是否包含图片
    const hasImage = tempDiv.querySelector('img') !== null;

    // 提取纯文本内容
    const textContent = tempDiv.textContent || '';

    // 如果需要简化内容（列表显示时）
    if (!showImage && hasImage) {
        // 如果包含图片但不显示图片
        const truncatedText = textContent.length > maxLength
            ? `${textContent.slice(0, maxLength)}...`
            : textContent;

        return (
            <div>
                {truncatedText}
                {hasImage && <span style={{ color: '#1890ff' }}> [包含图片]</span>}
            </div>
        );
    }

    // 完整显示带格式的内容
    if (showImage) {
        return (
            <div
                dangerouslySetInnerHTML={{ __html: sanitizedContent }}
                style={{
                    overflow: 'auto',
                    maxHeight: hasImage ? '400px' : 'auto'
                }}
            />
        );
    }

    // 默认显示截断的纯文本
    return (
        <div>
            {textContent.length > maxLength
                ? `${textContent.slice(0, maxLength)}...`
                : textContent
            }
        </div>
    );
};

export default QuestionContentDisplay; 