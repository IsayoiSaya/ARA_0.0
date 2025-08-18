"""SARG RPKM计算模块"""
import pandas as pd
import re
import logging
# 添加以下导入
from modules.utils import read_reads_file, read_16s_reads_file, calculate_rpkm, process_columns

def process_sarg_data(file_path, output_path, reads_path, reads_16s_path):
    try:
        logging.info("开始处理SARG数据...")
        df = pd.read_excel(file_path)

        # 新增列处理步骤
        df = process_columns(df)  # <-- 添加这行处理列拆分

        # 列名标准化 (原有代码保持不变)
        column_mapping = {}
        pattern = re.compile(r'^(.+?)_[12]\.fastq\.gz-SARG\.txt$')

        for col in df.columns:
            if col == 'ID':
                continue
            match = pattern.match(col)
            if match and "_1.fastq.gz-SARG.txt" in col:
                base_name = match.group(1).split('_')[0]
                column_mapping[col] = base_name
            else:
                column_mapping[col] = col

        renamed_df = df.rename(columns=column_mapping)
        columns_to_keep = [col for col in renamed_df.columns
                           if not col.endswith('_2.fastq.gz-SARG.txt')]
        base_df = renamed_df[columns_to_keep].copy()

        # 使用统一的calculate_rpkm函数
        reads_data = read_reads_file(reads_path)
        final_df = calculate_rpkm(base_df, reads_data)

        # 计算16S RPKM
        reads_16s_data = read_16s_reads_file(reads_16s_path)
        final_16s_df = base_df.copy()
        numeric_cols = final_16s_df.select_dtypes(include=['number']).columns

        for col in numeric_cols:
            if col in reads_16s_data and col in reads_data:
                numerator = reads_16s_data[col]
                denominator = (1492 / 1000) * (reads_data[col] / 1e6)
                final_16s_df[col] = numerator / denominator

        # 保存结果
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='RPKM')

            # 计算比值
            numeric_cols = final_df.select_dtypes(include=['number']).columns
            ratio_df = final_df[numeric_cols] / final_16s_df[numeric_cols]
            ratio_df = pd.concat([final_df[final_df.columns.difference(numeric_cols)], ratio_df], axis=1)
            ratio_df.to_excel(writer, index=False, sheet_name='16SRPKM')

        logging.info(f"✅ RPKM计算完成! 结果保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"处理SARG数据时出错: {str(e)}")
        raise