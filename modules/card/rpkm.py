"""
CARD RPKM计算模块
包含：
- RPKM和16S RPKM计算
"""

import pandas as pd
import re
from collections import defaultdict
import logging
from modules.utils import read_reads_file, read_16s_reads_file, calculate_rpkm

def process_sarg_data(file_path, output_path, reads_path, reads_16s_path):
    """处理CARD数据并计算RPKM/16S RPKM"""
    try:
        # 直接读取数据
        df = pd.read_excel(file_path, sheet_name='Merged')

        # 标准化列名
        pattern = re.compile(r'^(.+?)_[12]\.fastq\.gz-SARG\.txt$')
        column_mapping = {}

        for col in df.columns:
            if col == 'ID': continue
            match = pattern.match(col)
            if match and "_1.fastq.gz-SARG.txt" in col:
                column_mapping[col] = match.group(1)
            else:
                column_mapping[col] = col

        renamed_df = df.rename(columns=column_mapping)
        columns_to_keep = [col for col in renamed_df.columns
                           if not col.endswith('_2.fastq.gz-SARG.txt')]

        # 计算常规RPKM
        base_df = renamed_df[columns_to_keep].copy()
        reads_data = read_reads_file(reads_path)
        final_df = calculate_rpkm(base_df, reads_data)

        # 计算16S RPKM
        reads_16s_data = read_16s_reads_file(reads_16s_path)
        final_16s_df = base_df.copy()
        numeric_cols = final_16s_df.select_dtypes(include=['number']).columns

        # 使用16s_reads_number.txt中的数值作为分子
        for col in numeric_cols:
            if col in reads_16s_data and col in reads_data:
                # 计算公式：16s_reads_number / ((1492/1000) * (reads_data/1e6))
                numerator = reads_16s_data[col]
                denominator = (1492 / 1000) * (reads_data[col] / 1e6)
                final_16s_df[col] = numerator / denominator

        # 保存到两个sheet
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='RPKM')

            # 计算比值
            numeric_cols = final_df.select_dtypes(include=['number']).columns
            ratio_df = final_df[numeric_cols] / final_16s_df[numeric_cols]
            # 保留非数值列
            ratio_df = pd.concat([final_df[final_df.columns.difference(numeric_cols)], ratio_df], axis=1)

            ratio_df.to_excel(writer, index=False, sheet_name='16SRPKM')

        logging.info(f"RPKM & 16S RPKM计算完成! 保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"RPKM计算失败: {str(e)}")
        raise