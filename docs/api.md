# API 文档

## 认证接口

### POST /login
用户登录接口

### POST /register  
用户注册接口

### GET /me
获取当前用户信息

## 题库管理

### GET /questions
获取题目列表

### POST /questions
创建新题目

### PUT /questions/{question_id}
更新题目

### DELETE /questions/{question_id}
删除题目

## 试卷管理

### GET /papers
获取试卷列表

### POST /papers
创建新试卷

### PUT /papers/{paper_id}
更新试卷

### DELETE /papers/{paper_id}
删除试卷

## 用户管理

### GET /participants
获取被试者列表

### POST /participants
创建被试者

### PUT /participants/{participant_id}
更新被试者信息

### DELETE /participants/{participant_id}
删除被试者
