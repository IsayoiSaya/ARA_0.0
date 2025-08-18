"""
BacMet 数据预处理模块
"""

import pandas as pd
import logging


def preprocess_bacmet(input_path, bacmet_mapping_file, output_path):
    """处理BacMet原始数据并添加元数据信息"""
    try:
        # 读取原始数据
        df = pd.read_excel(input_path)

        # 处理ID列（保留|之前的内容）
        df['ID'] = df['ID'].str.split('|', n=1).str[0]

        # 读取BacMet映射文件
        bacmet_df = pd.read_csv(bacmet_mapping_file, sep='\t', header=0)
        bacmet_df = bacmet_df.drop_duplicates('BacMet_ID', keep='first')
        bacmet_mapping = bacmet_df.set_index('BacMet_ID').to_dict('index')

        # 删除可能存在的重复列
        columns_to_drop = [
            'Organism', 'Location', 'Compound', 'Gene_name',
            'Accession', 'gene lentgh'
        ]
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

        # 添加映射信息
        mapping_data = df['ID'].map(lambda x: bacmet_mapping.get(x, {})).apply(pd.Series)
        mapping_columns = ['Accession', 'gene lentgh', 'Organism', 'Location', 'Compound', 'Gene_name']
        df = pd.concat([df, mapping_data[list(set(mapping_columns) & set(mapping_data.columns))]], axis=1)
        
        # 保存结果
        df.to_excel(output_path, index=False)
        logging.info(f"BacMet预处理完成! 结果保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"BacMet预处理失败: {str(e)}")
        raise