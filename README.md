# 智能招聘信息聚合与分析系统

一个基于Python的自动化招聘信息聚合与分析系统，支持多种大语言模型，能够从多个招聘网站抓取信息并智能提取结构化数据。

## 功能特性

- **多网站支持**：可配置支持拉勾网、智联招聘、BOSS直聘等主流招聘网站
- **多LLM集成**：支持GPT、豆包、千问、DeepSeek、混元等多种大语言模型
- **灵活爬虫**：集成Requests（快速）和Selenium（动态页面）两种爬虫方式
- **智能提取**：通过提示词工程引导LLM精准提取招聘信息
- **结构化输出**：支持JSON、Markdown、CSV等多种输出格式
- **批量处理**：支持单个URL或批量URL处理
- **可配置性**：通过YAML配置文件轻松定制系统行为

## 技术栈

- **核心语言**：Python 3.8+
- **爬虫工具**：Requests, Selenium, BeautifulSoup4
- **LLM集成**：OpenAI API
- **配置管理**：PyYAML, python-dotenv
- **日志管理**：Loguru
- **数据处理**：Pandas
- **命令行工具**：argparse

## 项目结构

```
recruitment-analyzer/
├── src/                  # 源代码目录
│   ├── config/           # 配置模块
│   │   ├── config.yaml   # 主配置文件
│   │   └── config_loader.py # 配置加载器
│   ├── crawler/          # 爬虫模块
│   │   ├── base_crawler.py      # 爬虫基类
│   │   ├── requests_crawler.py  # Requests实现
│   │   ├── selenium_crawler.py  # Selenium实现
│   │   └── crawler_factory.py   # 爬虫工厂
│   ├── llm/              # LLM客户端模块
│   │   ├── base_llm.py        # LLM基类
│   │   ├── gpt_client.py      # GPT实现
│   │   └── llm_factory.py     # LLM工厂
│   ├── processor/        # 处理器模块
│   │   ├── base_processor.py          # 处理器基类
│   │   └── recruitment_processor.py   # 招聘信息处理器
│   └── utils/            # 工具模块
│       ├── logger.py            # 日志配置
│       └── output_formatter.py  # 输出格式化
├── data/                 # 数据目录
│   └── output/           # 输出结果目录
├── logs/                 # 日志目录
├── .env.example          # 环境变量示例
├── main.py               # 主程序入口
├── requirements.txt      # 依赖列表
└── README.md             # 项目说明文档
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd recruitment-analyzer
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

将`.env.example`复制为`.env`，并填入你的API密钥：

```bash
cp .env.example .env
```

编辑`.env`文件，配置你要使用的LLM提供商的API密钥：

```
# OpenAI (GPT)
OPENAI_API_KEY=your_openai_api_key_here

# 豆包
DOUBAO_API_KEY=your_doubao_api_key_here

# 千问
QWEN_API_KEY=your_qwen_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 混元
HUNYUAN_API_KEY=your_hunyuan_api_key_here
```

### 5. （可选）安装浏览器驱动（如果使用Selenium）

如果需要使用Selenium爬虫（用于动态加载页面），请确保安装了Chrome浏览器，并根据需要安装ChromeDriver。

系统会自动尝试通过WebDriverManager安装ChromeDriver，但你也可以手动下载并配置。

## 配置说明

主要配置文件位于`src/config/config.yaml`，你可以根据需要修改以下配置：

### LLM配置

```yaml
llm:
  provider: "gpt"  # 可选: gpt, doubao, qwen, deepseek, hunyuan
  api_key: "your_api_key_here"  # 如果环境变量已配置，这里可以留空
  model: "gpt-3.5-turbo"  # 模型名称
  temperature: 0.1  # 温度参数（控制生成多样性）
  max_tokens: 2000  # 最大生成令牌数
```

### 爬虫配置

```yaml
crawler:
  driver: "requests"  # 可选: selenium, playwright, requests
  timeout: 30  # 请求超时时间（秒）
  retry_times: 3  # 重试次数
  retry_delay: 5  # 重试间隔（秒）
  browser:
    headless: true  # 是否无头模式
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### 网站规则配置

```yaml
websites:
  lagou:
    name: "拉勾网"
    base_url: "https://www.lagou.com"
    selectors:  # 网站特定的CSS选择器
      job_list: ".job_list"
      job_item: ".job_item"
      # ... 其他选择器
```

### 输出配置

```yaml
output:
  format: "json"  # 可选: json, markdown, csv
  directory: "data/output"  # 输出目录
  encoding: "utf-8"  # 编码格式
```

## 使用方法

### 命令行参数

```
智能招聘信息聚合与分析系统

Usage:
  python main.py --url <URL> [--config <CONFIG_PATH>] [--format <FORMAT>] [--output <OUTPUT_DIR>]
  python main.py --file <FILE_PATH> [--config <CONFIG_PATH>] [--format <FORMAT>] [--output <OUTPUT_DIR>]
  python main.py --help

Options:
  -u, --url <URL>            单个招聘信息URL
  -f, --file <FILE_PATH>     包含多个URL的文件路径（每行一个URL）
  -c, --config <CONFIG_PATH> 配置文件路径 [default: src/config/config.yaml]
  -o, --format <FORMAT>      输出格式 (json, markdown, csv) [default: json]
  -d, --output <OUTPUT_DIR>  输出目录 [default: data/output]
  -h, --help                 显示帮助信息
```

### 示例用法

#### 1. 处理单个URL

```bash
python main.py --url "https://www.lagou.com/jobs/123456.html" --format json
```

#### 2. 处理多个URL（从文件读取）

创建包含URL的文件`urls.txt`：

```
https://www.lagou.com/jobs/123456.html
https://www.zhaopin.com/jobs/654321.html
https://www.zhipin.com/job_detail/...
```

然后执行：

```bash
python main.py --file urls.txt --format markdown
```

#### 3. 自定义配置和输出

```bash
python main.py --url "https://www.lagou.com/jobs/123456.html" \
               --config my_config.yaml \
               --format csv \
               --output my_results
```

## 输出示例

### JSON格式

```json
[
  {
    "job_title": "Python开发工程师",
    "company": "科技有限公司",
    "industry": "互联网",
    "location": "北京",
    "salary": "20-30K",
    "experience": "3-5年",
    "education": "本科及以上",
    "job_type": "全职",
    "department": "技术部",
    "description": "负责公司Python后端开发工作...",
    "requirements": "熟悉Python，掌握Django或Flask框架...",
    "benefits": ["五险一金", "带薪年假", "弹性工作"],
    "tags": ["Python", "后端", "Django"],
    "post_date": "2024-01-01",
    "website": "lagou",
    "url": "https://www.lagou.com/jobs/123456.html"
  }
]
```

## 扩展与定制

### 添加新的LLM客户端

在`src/llm/`目录下创建新的客户端实现类，继承自`BaseLLMClient`，然后在`llm_factory.py`中添加对应的创建逻辑。

### 添加新的爬虫实现

在`src/crawler/`目录下创建新的爬虫实现类，继承自`BaseCrawler`，然后在`crawler_factory.py`中添加对应的创建逻辑。

### 添加新的网站规则

在`config.yaml`的`websites`部分添加新网站的配置，包括名称、基础URL和CSS选择器。

## 注意事项

1. **API密钥安全**：请勿将包含API密钥的`.env`文件提交到版本控制系统
2. **爬虫规则**：请遵守各招聘网站的 robots.txt 规则和使用条款
3. **请求频率**：批量处理时建议适当控制请求频率，避免给目标网站带来过大压力
4. **动态页面**：对于需要登录或复杂动态加载的页面，建议使用Selenium爬虫
5. **LLM成本**：使用大语言模型会产生API调用成本，请合理设置批量处理数量

## 故障排除

### 常见问题

1. **API密钥错误**：检查`.env`文件中的API密钥是否正确
2. **爬虫失败**：尝试将爬虫驱动从`requests`切换为`selenium`
3. **LLM调用失败**：检查网络连接和API配额
4. **页面解析错误**：检查网站规则配置中的CSS选择器是否正确

### 日志查看

系统日志默认保存在`logs/recruitment_analyzer.log`，可以查看详细的运行信息和错误日志。

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目！

## 更新日志

- **v1.0.0** (2024-01-01)
  - 初始版本发布
  - 支持GPT和Requests爬虫
  - 实现基础的招聘信息提取和结构化输出