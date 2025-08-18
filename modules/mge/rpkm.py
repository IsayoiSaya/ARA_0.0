"""
MGE RPKM计算模块
包含原始数据处理和RPKM计算功能
"""

import pandas as pd
import re
import logging
from modules.utils import read_reads_file, read_16s_reads_file, calculate_rpkm, setup_logging
from config.default_paths import PROJECT_ROOT

def process_mge_data(input_file, output_file, search_file, reads_path, reads_16s_path):
    """处理MGE原始数据并计算RPKM/16S RPKM"""
    setup_logging(PROJECT_ROOT)  # 添加项目根目录参数
    try:
        search_df = pd.read_csv(search_file, sep='\t', names=['Accession', 'Length'])
        length_mapping = search_df.set_index('Accession')['Length'].to_dict()

        # 读取原始MGE计数数据
        df = pd.read_excel(input_file)

        # 调整执行顺序：先处理数据再计算
        # 删除重复列
        df = df.T.drop_duplicates(keep='first').T

        # 列名处理（简化正则）
        df.columns = df.columns.str.replace(r'\s+Read Count$', '', regex=True)
        df.columns = df.columns.str.replace(r'^.*?-', '', regex=True)  # 仅删除前缀

        # 拆分基因信息
        split_cols = df.iloc[:, 0].str.extract(r'^([^_]*)_(.*)_([^_]*)$')
        split_cols.columns = ['Number', 'Genes', 'Accession']
        df = pd.concat([split_cols.astype(str), df.iloc[:, 1:]], axis=1)

        # 处理Length列
        if 'Length' in df.columns:
            df = df.drop(columns=['Length'])
        df['Length'] = pd.to_numeric(df['Accession'].map(length_mapping), errors='coerce').fillna(1492)

        # 修复样本验证逻辑（排除元数据列）
        metadata_columns = ['Number', 'Genes', 'Accession', 'Length']
        sample_columns = [col for col in df.columns if col not in metadata_columns]  # 先定义

        # 计算常规RPKM（修复参数传递和列处理）
        reads_data = read_reads_file(reads_path)
        rpkm_values = calculate_rpkm(
            df[sample_columns],  # 仅数值列
            reads_data,
            df['Length']
        )
        # 合并元数据与计算结果
        rpkm_df = pd.concat([df[['Number', 'Genes', 'Accession']], rpkm_values], axis=1)

        # 计算16S RPKM（修复分母计算）
        reads_16s_data = read_16s_reads_file(reads_16s_path)
        rpkm_16s_df = df.copy()

        for col in sample_columns:  # 使用已定义的样本列
            base_col = re.sub(r'[-_]\d+$', '', col)
            actual_col = base_col if base_col in reads_16s_data else col
            if actual_col in reads_16s_data:
                denominator = (1492 / 1000) * (reads_16s_data[actual_col] / 1e6)
                rpkm_16s_df[col] = reads_16s_data[actual_col] / denominator

        # 保存结果时保持元数据列
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            rpkm_df.to_excel(writer, index=False, sheet_name='RPKM')

            # 计算比值时保留元数据
            ratio_values = rpkm_df[sample_columns] / rpkm_16s_df[sample_columns]
            ratio_df = pd.concat([rpkm_df[['Number', 'Genes', 'Accession']], ratio_values], axis=1)
            ratio_df.to_excel(writer, index=False, sheet_name='16SRPKM')

        logging.info(f"✅ RPKM计算完成! 结果保存至: {output_file}")
        return True
    except Exception as e:
        logging.error(f"处理MGE数据时出错: {str(e)}")
        raise

