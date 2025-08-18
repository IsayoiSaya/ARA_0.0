"""
BacMet RPKM计算模块
"""

import pandas as pd
import re
import logging
from modules.utils import read_reads_file, read_16s_reads_file, calculate_rpkm

def process_sarg_data(file_path, output_path, reads_path, reads_16s_path):
    """处理BacMet数据并计算RPKM/16S RPKM"""
    try:
        # 读取数据
        df = pd.read_excel(file_path)

        # 列名处理逻辑
        column_mapping = {}
        pattern_legacy = re.compile(r'^[^-]*-(.+?)_\d\.fastq\.gz-BacMet2\.txt$')
        pattern_new = re.compile(r'^([A-Za-z0-9]+)_\d\.fastq\.gz-BacMet2\.txt$')

        for col in df.columns:
            if col == 'ID':
                column_mapping[col] = col
                continue

            # 处理遗留格式
            match_legacy = pattern_legacy.match(col)
            if match_legacy and "_1.fastq.gz-BacMet2.txt" in col:
                column_mapping[col] = match_legacy.group(1)
                continue

            # 处理新格式
            match_new = pattern_new.match(col)
            if match_new and "_1.fastq.gz-BacMet2.txt" in col:
                column_mapping[col] = match_new.group(1)
            else:
                column_mapping[col] = col

        # 重命名列并过滤
        renamed_df = df.rename(columns=column_mapping)
        columns_to_keep = [col for col in renamed_df.columns
                           if not col.endswith('_2.fastq.gz-BacMet2.txt')]
        base_df = renamed_df[columns_to_keep].copy()

        # 读取reads数据
        reads_data = read_reads_file(reads_path)
        reads_16s_data = read_16s_reads_file(reads_16s_path)

        # 使用统一函数计算常规RPKM
        final_df = calculate_rpkm(
            base_df,
            reads_data,
            length_column='gene lentgh'  # 注意BacMet的特殊长度列名
        )

        # 计算16S RPKM
        final_16s_df = base_df.copy()
        numeric_cols = final_16s_df.select_dtypes(include=['number']).columns

        for col in numeric_cols:
            if col in reads_16s_data and col in reads_data:
                # 计算公式：16s_reads_number / ((1492/1000) * (DWTP_reads/1e6))
                numerator = reads_16s_data[col]
                denominator = (1492 / 1000) * (reads_data[col] / 1e6)
                final_16s_df[col] = numerator / denominator

        # 保存结果
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='RPKM')

            # 计算比值
            ratio_df = final_df.copy()
            for col in numeric_cols:
                if col in ratio_df.columns:
                    ratio_df[col] = final_df[col] / final_16s_df[col]

            ratio_df.to_excel(writer, index=False, sheet_name='16SRPKM')

        logging.info(f"RPKM & RPKM/16SRPKM计算完成! 保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"RPKM计算失败: {str(e)}")
        raise