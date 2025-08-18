# modules/utils.py
import re
from collections import defaultdict
import logging
import pandas as pd
import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

def setup_logging(project_root):
    """配置统一日志格式"""
    log_dir = Path(project_root) / "logs"
    log_dir.mkdir(exist_ok=True)

    log_format = "%(asctime)s [%(levelname)-5.5s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 主日志文件（按日期滚动）
    main_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "analysis.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )

    # 错误日志文件
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)

    # 控制台输出（处理中文编码）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # 统一配置
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            main_handler,
            error_handler,
            console_handler
        ]
    )

    # 禁用第三方库的日志
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("openpyxl").setLevel(logging.WARNING)

def read_reads_file(reads_path):
    """通用 reads 文件读取函数"""
    reads_dict = defaultdict(int)
    pattern = re.compile(r'^([A-Za-z0-9-]+)_\d+(?:\.\S+)?:\s+(\d+)\s+reads$')

    try:
        with open(reads_path, 'r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    sample_base = match.group(1)
                    reads = int(match.group(2))
                    reads_dict[sample_base] += reads
        return reads_dict
    except FileNotFoundError:
        logging.error(f"错误: 无法找到文件 {reads_path}")
        raise
    except Exception as e:
        logging.error(f"读取reads文件时出错: {str(e)}")
        raise


def read_16s_reads_file(reads_path):
    """通用 16S reads 文件读取函数"""
    reads_dict = defaultdict(int)
    pattern = re.compile(r'^([A-Za-z0-9-]+)_\d+(?:\.\S+)?\.16s:\s+(\d+)\s+reads$')

    try:
        with open(reads_path, 'r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    sample_base = match.group(1)
                    reads = int(match.group(2))
                    reads_dict[sample_base] += reads
        return reads_dict
    except FileNotFoundError:
        logging.error(f"错误: 无法找到文件 {reads_path}")
        raise
    except Exception as e:
        logging.error(f"读取16s reads文件时出错: {str(e)}")
        raise


def calculate_rpkm(df, reads_dict, length_column=None):
    # 添加更多可能的长度列名匹配
    possible_length_columns = [
        'Length (AA)',
        'gene length',
        'Length',
    ]

    # 自动检测存在的长度列
    if length_column is None:
        for col in possible_length_columns:
            if col in df.columns:
                length_column = col
                break
        else:  # 如果没有找到任何匹配项
            raise KeyError("未找到长度列，请确认数据包含以下任一列名：" + ", ".join(possible_length_columns))
    """通用 RPKM 计算函数"""
    df = df.copy()
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    numeric_cols = [col for col in df.columns if col not in non_numeric_cols]

    # 确保数值列为数值类型
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    for col in numeric_cols:
        if col in reads_dict:
            reads = reads_dict[col]
            df[col] = df[col] / ((df[length_column] / 1000) * (reads / 1e6))
    return df


def process_columns(df):
    """处理列拆分和重命名（新增函数）"""
    # 拆分A2列为Types和ARGs
    if 'A2' in df.columns:
        df[['Types', 'ARGs']] = df['A2'].str.split('_', n=1, expand=True)
        df['ARGs'] = df['ARGs'].str.lstrip('_')

    # 统一长度列名
    if 'Length (AA)' in df.columns:
        df = df.rename(columns={'Length (AA)': 'Length'})

    return df
