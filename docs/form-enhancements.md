# QuickForm 表单增强功能使用说明

## 功能概述

QuickForm 现在自动为所有上传的 HTML 表单文件添加了两个增强功能：

1. **选项限制悬浮显示** - 实时显示每个选项的选择次数和限制状态
2. **表格缩放功能** - 允许用户自由缩放表格，适合大表格（如180*5）的查看

## 功能详情

### 1. 选项限制悬浮显示

当用户在填写问卷时，如果表单中设置了选项限制，系统会自动在页面右上角显示一个悬浮提示框，实时显示：

- 每个选项的选择次数（如：选项A: 5 / 10）
- 进度条显示使用比例
- 状态提示（正常/接近/已满）
- 颜色编码：
  - 绿色：正常（< 80%）
  - 橙色：接近限制（80-99%）
  - 红色：已满（≥ 100%）

#### 如何设置选项限制

在您的 HTML 表单中，可以通过以下三种方式之一设置选项限制：

**方法1：使用全局变量（推荐）**
```html
<script>
    window.optionLimits = {
        'A': 10,  // 选项A最多选择10次
        'B': 5,   // 选项B最多选择5次
        'C': 8    // 选项C最多选择8次
    };
</script>
```

**方法2：使用 data 属性**
```html
<div data-option-limits='{"A": 10, "B": 5, "C": 8}'></div>
```

**方法3：使用 meta 标签**
```html
<meta name="option-limits" content='{"A": 10, "B": 5, "C": 8}'>
```

#### 选项值匹配规则

- 系统会自动匹配单选按钮（radio）和复选框（checkbox）的 `value` 属性
- 匹配时不区分大小写（A 和 a 会被视为同一选项）
- 只统计已选中的选项

### 2. 表格缩放功能

所有 `<table>` 标签会自动获得缩放控制功能：

- **缩放按钮**：+ 和 - 按钮可以调整表格大小
- **缩放范围**：50% - 200%
- **缩放步进**：每次调整 10%
- **重置按钮**：一键恢复到 100%
- **实时显示**：显示当前缩放比例

#### 使用方式

1. 表格会自动被包装在一个可缩放的容器中
2. 表格顶部会出现一个控制栏
3. 点击 + 放大，点击 - 缩小
4. 点击"重置"恢复到原始大小

#### 特性

- 缩放是平滑过渡的，有动画效果
- 缩放控制栏会固定在表格顶部（sticky）
- 支持多个表格，每个表格独立缩放
- 动态添加的表格也会自动获得缩放功能

## 技术实现

### 自动注入

系统会在返回 HTML 文件时自动注入增强脚本，无需手动修改 HTML 文件。

### 兼容性

- 支持所有现代浏览器（Chrome, Firefox, Safari, Edge）
- 不影响原有表单功能
- 如果增强脚本加载失败，不会影响表单的正常使用

### 性能

- 脚本使用事件委托，性能优化
- 缩放使用 CSS transform，硬件加速
- 选项限制统计使用高效的事件监听

## 示例

### 完整示例：带选项限制的表单

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>问卷示例</title>
</head>
<body>
    <h1>请填写问卷</h1>
    
    <!-- 设置选项限制 -->
    <script>
        window.optionLimits = {
            'A': 10,
            'B': 5,
            'C': 8
        };
    </script>
    
    <form>
        <div>
            <label>问题1：</label>
            <input type="radio" name="q1" value="A"> 选项A
            <input type="radio" name="q1" value="B"> 选项B
            <input type="radio" name="q1" value="C"> 选项C
        </div>
        
        <div>
            <label>问题2：</label>
            <input type="checkbox" name="q2" value="A"> 选项A
            <input type="checkbox" name="q2" value="B"> 选项B
            <input type="checkbox" name="q2" value="C"> 选项C
        </div>
        
        <button type="submit">提交</button>
    </form>
    
    <!-- 增强脚本会自动注入，无需手动添加 -->
</body>
</html>
```

### 表格示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>表格示例</title>
</head>
<body>
    <h1>数据表格</h1>
    
    <!-- 表格会自动获得缩放功能 -->
    <table border="1">
        <thead>
            <tr>
                <th>列1</th>
                <th>列2</th>
                <th>列3</th>
                <!-- ... 更多列 ... -->
            </tr>
        </thead>
        <tbody>
            <!-- 表格数据 -->
        </tbody>
    </table>
    
    <!-- 增强脚本会自动注入，无需手动添加 -->
</body>
</html>
```

## 注意事项

1. **选项限制**：
   - 选项值必须与限制配置中的键匹配（不区分大小写）
   - 只统计已选中的选项
   - 如果没有设置限制，悬浮提示不会显示

2. **表格缩放**：
   - 缩放只影响表格的显示大小，不影响实际数据
   - 缩放后的表格仍然可以正常交互
   - 建议在移动设备上使用较小的缩放比例

3. **脚本注入**：
   - 脚本会在 HTML 文件的 `</head>` 或 `</body>` 标签前自动注入
   - 如果 HTML 文件结构异常，脚本会在文件末尾添加

## 故障排除

### 选项限制不显示

1. 检查是否正确设置了 `window.optionLimits` 或 data 属性
2. 检查选项的 `value` 属性是否与限制配置匹配
3. 打开浏览器控制台查看是否有错误信息

### 表格缩放不工作

1. 确认 HTML 中包含 `<table>` 标签
2. 检查浏览器控制台是否有 JavaScript 错误
3. 尝试刷新页面

### 脚本未加载

1. 检查网络连接
2. 确认 `/static/js/form-enhancements.js` 文件存在
3. 查看浏览器控制台的网络请求

## 更新日志

- **v1.0.0** (2024-01-19)
  - 初始版本
  - 添加选项限制悬浮显示功能
  - 添加表格缩放功能
  - 自动注入脚本
