"""
默认路径配置 - 用户可以根据需要修改
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(r"C:\Users\zhang\Desktop\01-2China_soil")

# 配置目录 - 存放映射文件等
CONFIG_DIR = Path(__file__).resolve().parent

# 各分析模块基础路径
CARD_DIR = PROJECT_ROOT / "01 CARD"
SARG_DIR = PROJECT_ROOT / "02 SARG"
VICTORS_DIR = PROJECT_ROOT / "03 victors"  # 统一大小写
BACMET_DIR = PROJECT_ROOT / "04 BacMet"
MGE_DIR = PROJECT_ROOT / "05 MGE"

# 公共文件路径
OTHERS_DIR = PROJECT_ROOT / "Others"
READS_FILE = OTHERS_DIR / "reads_number.txt"
READS_16S_FILE = OTHERS_DIR / "16S_reads_number.txt"

# 各模块特定文件
CARD_FILES = {
    "input": CARD_DIR / "CARD.xlsx",
    "output": CARD_DIR / "CARD_processed.xlsx",
    "mapping": CONFIG_DIR / "CARD_mapping.txt",  # 指向配置目录
    "types_class": CONFIG_DIR / "Types_Class.txt",  # 指向配置目录
}

SARG_FILES = {
    "input": SARG_DIR / "SARG.xlsx",
    "output": SARG_DIR / "SARG_processed.xlsx",
    "risk": CONFIG_DIR / "ARGs_RankSearch.xlsx",  # 指向配置目录
}

VICTORS_FILES = {
    "input": VICTORS_DIR / "victors.xlsx",
    "output": VICTORS_DIR / "victors_processed.xlsx"
}

BACMET_FILES = {
    "input": BACMET_DIR / "BacMet.xlsx",
    "output": BACMET_DIR / "BacMet_processed.xlsx",
    "mapping": CONFIG_DIR / "BacMet21_EXP.753.mapping.txt",  # 指向配置目录
}

MGE_FILES = {
    "input": MGE_DIR / "count.xlsx",
    "output": MGE_DIR / "MGE_RPKM.xlsx",
    "search": CONFIG_DIR / "Search.txt",  # 指向配置目录
}