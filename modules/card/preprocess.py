"""
CARD 数据预处理模块
包含：
- 原始数据转置处理
- AMR元数据合并
"""

import pandas as pd
import re
from collections import defaultdict
import logging


def process_and_transpose_card_mapping(file_path, output_path, sheet_name='CARD_mapping'):
    """处理并转置CARD原始映射数据"""
    try:
        xls = pd.ExcelFile(file_path)
        available_sheets = xls.sheet_names

        # 如果没有指定sheet_name或sheet_name不存在，则使用第一个工作表
        if sheet_name is None or sheet_name not in available_sheets:
            sheet_name = available_sheets[0]
            logging.warning(f"使用第一个工作表: {sheet_name}")

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        all_columns = df.columns.tolist()
        pairs = defaultdict(dict)
        pattern = re.compile(r'(.+)_([12])\.fastq\.gz-CARD\.txt$')
        non_pair_columns = [col for col in all_columns if not pattern.search(col)]

        for col in all_columns:
            match = pattern.search(col)
            if match:
                base_name = match.group(1).replace('-', '').replace('_', '')
                pair_type = match.group(2)
                pairs[base_name][pair_type] = col

        sample_columns = {}

        for base_name, pair_dict in pairs.items():
            col1 = pair_dict.get('1')
            col2 = pair_dict.get('2')

            if col1 and col2:
                df[col1] = pd.to_numeric(df[col1], errors='coerce').fillna(0)
                df[col2] = pd.to_numeric(df[col2], errors='coerce').fillna(0)

                sample_columns[base_name] = df[col1] + df[col2]

        new_df = pd.DataFrame({
            'ID': df['ID'],
            **sample_columns
        })

        def process_id(id_str):
            parts = id_str.split('|')
            filtered = [p.replace('ARO:', '') for p in parts if p not in ['gb']]
            return filtered[0:1] + filtered[1:2] + filtered[2:3]

        new_df[['Accession', 'ARO', 'ARGs']] = new_df['ID'].apply(
            lambda x: pd.Series(process_id(x))
        )
        new_df.drop('ID', axis=1, inplace=True)

        # 清理列名
        new_df.columns = [col.replace('-', '').replace('_', '') for col in new_df.columns]

        # 调整列顺序
        new_df = new_df[['Accession', 'ARO', 'ARGs'] + list(sample_columns.keys())]

        # 添加汇总行
        sum_row = new_df.iloc[:, 3:].sum()
        total_series = pd.Series(['Total', '', ''] + sum_row.tolist(), index=new_df.columns)
        new_df = pd.concat([new_df, total_series.to_frame().T], ignore_index=True)

        new_df.to_excel(output_path, index=False)
        logging.info(f"处理完成! 结果已保存至: {output_path}")
        logging.info(f"样本数量: {len(new_df.columns) - 3}, 基因数量: {len(new_df)}")
        return True
    except Exception as e:
        logging.error(f"原始数据转置失败: {str(e)}")
        raise


def merge_amr_info(card_path, amr_meta_path, sheet_name='Merged'):
    """合并AMR元数据信息"""
    try:
        # 读取已处理的主表（跳过汇总行）
        main_df = pd.read_excel(card_path).iloc[:-1]

        # 转换ARO列为字符串类型
        main_df['ARO'] = main_df['ARO'].astype(str).str.strip()

        # 读取AMR元数据表（文本文件）
        amr_df = pd.read_csv(amr_meta_path, sep='\t')
        amr_df['ARO'] = amr_df['ARO'].str.replace('ARO:', '', regex=False).str.strip().astype(str)

        # 修正ARO格式
        main_df['ARO'] = main_df['ARO'].str.replace(r'\.0$', '', regex=True)

        # 数据清洗
        amr_df['ARO'] = (amr_df['ARO'].str.extract(r'(\d+)')[0]
                         .fillna('')
                         .astype(str))

        # 合并数据
        merged_df = pd.merge(
            main_df.drop('ARGs', axis=1),
            amr_df,
            on='ARO',
            how='left',
            suffixes=('', '_amr')
        )

        # 填充空值
        merged_df = merged_df.fillna({
            'ARGs': 'Unknown',
            'AMR gene family': 'Not classified',
            'Class': 'N/A',
            'resistance mechanisms': 'Unknown',
            'Length': 0
        })

        # 删除重复列
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

        # 调整列顺序
        sample_cols = [col for col in merged_df if col.startswith('Sample')]
        new_columns = [col for col in merged_df if not col.startswith('Sample')] + sample_cols
        merged_df = merged_df[new_columns]

        # 添加汇总行
        sum_row = merged_df[sample_cols].sum()
        non_sample_count = len(merged_df.columns) - len(sample_cols)
        total_series = pd.Series(['Total'] + [''] * (non_sample_count - 1) + sum_row.tolist(),
                                 index=merged_df.columns)
        merged_df = pd.concat([merged_df, total_series.to_frame().T], ignore_index=True)

        # 保存到新工作表
        with pd.ExcelWriter(card_path, engine='openpyxl', mode='a') as writer:
            merged_df.to_excel(writer, sheet_name=sheet_name, index=False)

        logging.info(f"合并完成! 结果已保存至 {card_path} 的 [{sheet_name}] 工作表")
        return True
    except Exception as e:
        logging.error(f"AMR元数据合并失败: {str(e)}")
        raise