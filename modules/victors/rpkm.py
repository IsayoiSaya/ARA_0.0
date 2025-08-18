"""
Victors RPKM计算模块
"""

import pandas as pd
import re
from collections import defaultdict
from modules.utils import setup_logging, calculate_rpkm
import logging
from modules.utils import read_reads_file, read_16s_reads_file

def process_victors_data(input_path, output_path, reads_path, reads_16s_path):
    """处理Victors数据并计算RPKM/16S RPKM"""
    try:
        # 读取原始数据
        df = pd.read_excel(input_path)
        df = df.rename(columns={'Length (AA)': 'Length'})
        
        # 识别并重命名病原体列
        pathogen_col = next(
            (col for col in df.columns if pd.isna(col) or str(col).startswith('Unnamed:')), 
            None
        )
        if pathogen_col:
            df = df.rename(columns={pathogen_col: 'Pathogen'})
        
        # 添加病原体属列
        df['Genus'] = df['Pathogen'].str.split().str[0].fillna('Unknown')
        
        # 标准化列名
        column_mapping = {}
        pattern = re.compile(r'^(.+?)_[12]\.fastq\.gz-victors\.txt$')
        for col in df.columns:
            if col == 'ID':
                continue
            match = pattern.match(col)
            if match and "_1.fastq.gz-victors.txt" in col:
                base_name = match.group(1).split('_')[0]
                column_mapping[col] = base_name
            else:
                column_mapping[col] = col
        
        # 重命名列并移除冗余列
        renamed_df = df.rename(columns=column_mapping)
        columns_to_keep = [
            col for col in renamed_df.columns 
            if not col.endswith('_2.fastq.gz-victors.txt')
        ]
        base_df = renamed_df[columns_to_keep].copy()
        
        # 计算常规RPKM
        reads_data = read_reads_file(reads_path)
        final_df = calculate_rpkm(base_df, reads_data)
        
        # 计算16S RPKM
        reads_16s_data = read_16s_reads_file(reads_16s_path)
        final_16s_df = base_df.copy()
        numeric_cols = final_16s_df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            if col in reads_16s_data and col in reads_data:
                # 计算公式：原始数据 * 16s_reads / 分母
                sample_counts = base_df[col]
                denominator = (1492 / 1000) * (reads_data[col] / 1e6)
                final_16s_df[col] = (sample_counts * reads_16s_data[col]) / denominator
        
        # 保存结果
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='RPKM')
            
            # 计算比值
            numeric_cols = final_df.select_dtypes(include=['number']).columns
            ratio_df = final_df[numeric_cols].div(final_16s_df[numeric_cols]).fillna(0)
            ratio_df = pd.concat(
                [final_df[final_df.columns.difference(numeric_cols)], 
                ratio_df
            ], axis=1)
            
            ratio_df.to_excel(writer, index=False, sheet_name='16SRPKM')
        
        logging.info(f"✅ RPKM计算完成! 结果保存至: {output_path}")
        return True
    
    except Exception as e:
        logging.error(f"处理Victors数据时出错: {str(e)}")
        raise

