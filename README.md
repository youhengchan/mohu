# MOHU

**Multi-Objective Homophone Understanding**

一个强大的中英文模糊字符串匹配库，支持字符级和拼音级模糊匹配策略。

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-81%20passed-brightgreen)](tests/)

## ✨ 特性

- 🔍 **多种匹配策略**：字符级、拼音级、混合模式
- 🚀 **高性能搜索**：基于 AC 自动机的快速模糊匹配
- 🌏 **中英文支持**：完整支持中文拼音和英文字符匹配
- ⚙️ **灵活配置**：可调整编辑距离、相似度阈值、结果数量
- 🔄 **动态管理**：运行时添加/删除词汇，自动重建索引
- 📊 **精确评分**：基于加权编辑距离的相似度计算

## 📦 安装

### 使用 pip 安装（推荐）

```bash
pip install mohu
```

### 从源码安装

```bash
git clone https://github.com/youhengchan/mohu.git
cd mohu
pip install -e .
```

### 开发环境安装

```bash
git clone https://github.com/youhengchan/mohu.git
cd mohu
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## 🚀 快速开始

```python
from mohu import MohuMatcher

# 创建匹配器实例
matcher = MohuMatcher()

# 构建词典
words = ["北京", "南京", "东京", "apple", "application", "apply"]
matcher.build(words)

# 字符级模糊匹配
results = matcher.match("appl", mode='char')
print(results)  # [('apply', 0.8), ('apple', 0.8)]

# 拼音级模糊匹配
results = matcher.match("背景", mode='pinyin')
print(results)  # [('北京', 1.0), ...]

# 混合模式匹配（默认）
results = matcher.match("北", mode='hybrid')
print(results)  # [('北京', 0.5), ...]
```

## 🎭 快速开始

> *"长大后才发现，北京就是背景，上海就是商海，彩礼就是财力，而理想就是离乡"*

让我们用 MOHU 来验证这句话中蕴含的同音字智慧：

```python
from mohu import MohuMatcher

# 构建人生词典
life_words = [
    # 地名与含义
    "北京", "背景", "上海", "商海",
    # 情感与现实  
    "彩礼", "财力", "理想", "离乡",
    # 更多人生感悟
    "奋斗", "愤怒", "成功", "成空", 
    "青春", "轻纯", "岁月", "碎月"
]

matcher = MohuMatcher()
matcher.build(life_words)

print("🌟 人生哲学匹配演示：")
print("=" * 40)

# 验证哲学对应关系
philosophical_pairs = [
    ("北京", "在这座城市里，每个人都只是..."),
    ("上海", "在商业的海洋中，我们都在..."), 
    ("彩礼", "表面的仪式，实质考验的是..."),
    ("理想", "追求梦想的代价往往是...")
]

for word, description in philosophical_pairs:
    print(f"\n🔍 搜索: '{word}' - {description}")
    
    # 使用拼音模式发现同音字
    results = matcher.match(word, mode='pinyin', max_results=3)
    
    for match_word, score in results:
        if match_word != word and score > 0.8:  # 找到高度相似的同音字
            print(f"   💫 发现同音奥秘: {word} ≈ {match_word} (相似度: {score:.2f})")
            
            # 展示混合模式的智能匹配
            hybrid_results = matcher.match(word, mode='hybrid', max_results=2)
            print(f"   🎯 混合匹配: {[f'{w}({s:.2f})' for w, s in hybrid_results]}")

print("\n" + "=" * 40)

```

**输出示例：**
```
🌟 人生哲学匹配演示：
========================================

🔍 搜索: '北京' - 在这座城市里，每个人都只是...
   💫 发现同音奥秘: 北京 ≈ 背景 (相似度: 1.00)
   🎯 混合匹配: ['北京(1.00)', '背景(0.40)']

🔍 搜索: '上海' - 在商业的海洋中，我们都在...
   💫 发现同音奥秘: 上海 ≈ 商海 (相似度: 1.00)
   🎯 混合匹配: ['上海(1.00)', '商海(0.70)']

🔍 搜索: '彩礼' - 表面的仪式，实质考验的是...
   💫 发现同音奥秘: 彩礼 ≈ 财力 (相似度: 1.00)
   🎯 混合匹配: ['彩礼(1.00)', '财力(0.40)']

🔍 搜索: '理想' - 追求梦想的代价往往是...
   💫 发现同音奥秘: 理想 ≈ 离乡 (相似度: 1.00)
   🎯 混合匹配: ['理想(1.00)', '离乡(0.40)']

========================================
```


## 📚 详细使用教程

### 基本用法

#### 1. 创建匹配器

```python
from mohu import MohuMatcher

# 使用默认配置
matcher = MohuMatcher()

# 自定义配置
matcher = MohuMatcher(
    max_distance=3,           # 最大编辑距离
    ignore_tones=True,        # 忽略拼音声调
    similarity_threshold=0.5   # 默认相似度阈值
)
```

#### 2. 构建词典

```python
# 从词汇列表构建
words = ["苹果", "香蕉", "橘子", "apple", "banana", "orange"]
matcher.build(words)

# 检查词典状态
print(f"词典大小: {matcher.get_word_count()}")
print(f"词汇列表: {matcher.get_words()}")
```

#### 3. 执行匹配

```python
# 字符级匹配
char_results = matcher.match("苹", mode='char', max_results=5)

# 拼音级匹配
pinyin_results = matcher.match("pingguo", mode='pinyin')

# 混合模式（推荐）
hybrid_results = matcher.match("苹果", mode='hybrid')

# 带过滤的匹配
filtered_results = matcher.match(
    "apple", 
    mode='char',
    similarity_threshold=0.7,  # 只返回相似度 >= 0.7 的结果
    max_results=3              # 最多返回 3 个结果
)
```

### 高级用法

#### 动态词典管理

```python
# 添加新词汇
success = matcher.add_word("新词汇")
print(f"添加成功: {success}")

# 删除词汇
success = matcher.remove_word("旧词汇")
print(f"删除成功: {success}")

# 批量管理
new_words = ["深圳", "广州", "杭州"]
for word in new_words:
    matcher.add_word(word)
```

#### 匹配模式详解

**字符级匹配 (`mode='char'`)**
- 基于字符编辑距离
- 适合拼写错误、缺字漏字的场景
- 支持中英文混合文本

```python
# 拼写错误匹配
results = matcher.match("aplpe", mode='char')  # 找到 "apple"

# 中文字符匹配
results = matcher.match("北", mode='char')     # 找到 "北京"
```

**拼音级匹配 (`mode='pinyin'`)**
- 基于拼音相似度
- 适合同音字、音近字的场景
- 支持罗马化拼音输入

```python
# 罗马化拼音匹配
results = matcher.match("beijing", mode='pinyin')  # 找到 "北京"

# 音近字匹配
results = matcher.match("背景", mode='pinyin')     # 可能找到 "北京"
```

**混合模式 (`mode='hybrid'`)**
- 结合字符和拼音策略
- 加权组合两种方法的结果
- 提供最全面的匹配效果

```python
# 混合匹配提供最佳结果
results = matcher.match("北京", mode='hybrid')
```

#### 自定义配置示例

```python
# 高精度匹配器（严格模式）
strict_matcher = MohuMatcher(
    max_distance=1,
    similarity_threshold=0.8,
    ignore_tones=False
)

# 宽松匹配器（模糊模式）
fuzzy_matcher = MohuMatcher(
    max_distance=3,
    similarity_threshold=0.3,
    ignore_tones=True
)
```

## 🛠️ API 参考

### MohuMatcher 类

#### 构造函数

```python
MohuMatcher(max_distance=2, ignore_tones=True, similarity_threshold=0.0, 
           char_confusion_path=None, pinyin_confusion_path=None)
```

**参数:**
- `max_distance` (int): 最大编辑距离，默认为 2
- `ignore_tones` (bool): 是否忽略拼音声调，默认为 True
- `similarity_threshold` (float): 默认相似度阈值，默认为 0.0
- `char_confusion_path` (str): 字符混淆矩阵文件路径，可选
- `pinyin_confusion_path` (str): 拼音混淆矩阵文件路径，可选

#### 主要方法

##### `build(word_list: List[str]) -> None`
构建匹配索引。

```python
matcher.build(["词汇1", "词汇2", "词汇3"])
```

##### `match(text: str, mode: str = 'hybrid', **kwargs) -> List[Tuple[str, float]]`
执行模糊匹配。

**参数:**
- `text` (str): 查询文本
- `mode` (str): 匹配模式，'char'/'pinyin'/'hybrid'
- `similarity_threshold` (float): 相似度阈值
- `max_results` (int): 最大结果数量

**返回:** 匹配结果列表，每个元素为 (词汇, 相似度分数) 元组

##### `add_word(word: str) -> bool`
添加新词汇。

**返回:** 是否成功添加（False 表示词汇已存在）

##### `remove_word(word: str) -> bool`
删除词汇。

**返回:** 是否成功删除（False 表示词汇不存在）

##### `get_word_count() -> int`
获取当前词典大小。

##### `get_words() -> List[str]`
获取当前词汇列表（副本）。

## 📁 项目结构

```
mohu/
├── mohu/                   # 主包目录
│   ├── __init__.py        # 包初始化
│   ├── matcher.py         # 主匹配器类
│   ├── ac.py             # AC 自动机实现
│   ├── distance.py       # 编辑距离计算
│   ├── pinyin.py         # 拼音转换器
│   └── config.py         # 配置和常量
├── tests/                 # 测试目录
│   ├── test_matcher.py   # 匹配器测试
│   ├── test_ac.py        # AC 自动机测试
│   ├── test_distance.py  # 距离计算测试
│   ├── test_pinyin.py    # 拼音转换测试
│   └── test_config.py    # 配置测试
├── examples/              # 示例目录
│   └── basic_usage.py    # 基本使用示例
├── data/                  # 数据文件
│   ├── char_confusion.json    # 字符混淆矩阵
│   └── pinyin_confusion.json  # 拼音混淆矩阵
├── pyproject.toml        # 项目配置
├── README.md             # 项目说明
└── .gitignore           # Git 忽略文件
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_matcher.py

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=mohu
```

## 📊 性能说明

- **建议词典大小**: < 100,000 词汇
- **查询响应时间**: < 100ms（10,000 词汇规模）
- **内存使用**: 约 50MB（10,000 词汇规模）
- **支持的编辑距离**: 推荐 1-3，最大支持 5

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 此仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发环境设置

```bash
git clone https://github.com/youhengchan/mohu.git
cd mohu
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## 📋 TODO

- [ ] 增加更多语言支持
- [ ] 实现语义相似度匹配
- [ ] 添加持久化存储支持
- [ ] 优化大规模词典性能
- [ ] 增加 Web API 接口

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [pypinyin](https://github.com/mozillazg/python-pinyin) - 中文拼音转换
- AC 自动机算法的相关研究和实现
- 所有贡献者和用户的反馈

## 📞 联系方式

- 项目主页: https://github.com/youhengchan/mohu
- 问题反馈: https://github.com/youhengchan/mohu/issues
- 邮箱: youhengchan@qq.com

---

**MOHU** - 让模糊字符串匹配变得简单！ 🚀 