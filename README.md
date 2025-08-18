# ARGs reads水平分析 v0.0

## 项目配置
- 依赖安装：`pip install -r requirements.txt`

## 快速开始
 1. 克隆仓库
```bash
git clone https://github.com/IsayoiSaya/ARA_0.0
cd ARGs-reads-analysis

```
 2. 配置路径
修改 config/default_paths.py 中的 PROJECT_ROOT 为您的项目根目录：
```bash
PROJECT_ROOT = Path(r"您的/项目/路径")
```
 3. 准备输入文件 将原始数据文件按以下命名规范放入对应目录：只要带有CARD\SARG\victors\BacMet\.count等字段即可
```text
您的/项目/路径/
 ├──xxx_CARD.xlsx/.csv
 ├──xxx_SARG.xlsx/.csv
 ├──xxx_victors.xlsx/.csv
 ├──xxx_BacMet.xlsx/.csv
 ├──xxx_MGEs.count.xlsx/.csv
 ├──xxxx_reads_number.txt
 ├──xxxx_16S_reads_number.txt
 └── ...
```



## 环境要求
- Python 3.7+，pandas>=1.3.0
- 依赖安装：
`pip install -r requirements.txt`

## 目录结构

```text
ARGs-reads-analysis/
├── config/               # 配置文件夹
│   └── default_paths.py  # 路径配置
├── modules/              # 核心功能
│   ├── card/             # CARD分析
│   ├── sarg/             # SARG分析
│   ├── victors/          # victors病原体分析
│   ├── bacmet/           # BacMet化合物抗性分析
│   └── mge/              # MGEs移动遗传元件
├── pipelines/            # 流程控制
│   ├── card_pipeline.py
│   ├── sarg_pipeline.py
│   └── ...               # 其他流程文件
├── logs/                 # 日志目录（自动生成）
└── main.py               # 主入口文件(在此运行)
```
## 功能特性
#### 1.文件自动归类 

- 自动整理原始数据文件
- 转换CSV/TSV为Excel格式
- 统一reads计数文件存储

#### 2.多数据库分析

- CARD分析：抗性基因家族分类、抗性机制分析
- SARG分析：风险等级评估、基因类型汇总
- Victors分析：病原体分类统计
- BacMet分析：化合物抗性分析
- MGE分析：移动遗传元件分析
- 
#### 3.标准化输出

- 统一生成 *_processed.xlsx 结果文件
- 自动生成 RPKM 和 RPKM/16S RPKM数据
- 日志文件存储于 logs/ 目录

## 常见问题
Q: 出现路径错误怎么办？ 
A: 检查并确认以下配置：
   1.  config/default_paths.py 中的路径配置
   2.  输入文件是否放在正确目录
   3.  系统用户是否有读写权限

Q: 如何添加自定义分析模块？ A:
  1. 在modules目录下创建新模块
  2. 实现预处理、计算、汇总三个核心功能
  3. 在pipelines中添加对应流程控制
  4. 在main.py中集成新流程

Q: 如何处理大型数据集？ A:

  1. 建议分配至少8GB内存
  2. 使用64位Python版本
  3. 分批次处理数据（需修改代码逻辑）

##  技术支持
 如有问题请联系：[shiqiricardian@foxmail.com]

