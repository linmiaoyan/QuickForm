# 教程管理说明

## 文件结构

- `tutorials.json` - 教程配置文件，定义所有教程的元信息

## 添加新教程

在 `tutorials.json` 中添加教程信息：

```json
{
    "title": "教程标题",
    "author": "作者姓名",
    "author_link": "https://教程链接.com",
    "description": "教程描述（可选）"
}
```

## 示例

```json
[
    {
        "title": "快速入门教程",
        "author": "张三",
        "author_link": "https://github.com/zhangsan",
        "description": "这是一个快速入门教程"
    },
    {
        "title": "高级功能教程",
        "author": "李四",
        "author_link": "https://example.com",
        "description": "介绍高级功能的使用"
    }
]
```

## 注意事项

- `author_link` 字段为教程的链接地址，用户点击后会在新标签页打开
- `author_link` 可以为空，如果为空则不显示链接
- `description` 字段可选，用于描述教程内容
