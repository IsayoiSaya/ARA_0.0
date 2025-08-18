"""
MGE 数据聚合模块
包含基因分类汇总功能
"""

import pandas as pd
import logging


def generate_gene_classification(input_path, output_path):
    """按基因(Genes)分类汇总"""
    try:
        process_config = [
            ('RPKM', 'Gene_RPKM'),
            ('16SRPKM', 'Gene_16SRPKM')
        ]

        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                df.drop(columns=['Length', 'Number'], inplace=True, errors='ignore')

                # 预处理Genes列
                if 'Genes' not in df.columns:
                    raise ValueError(f"输入表 {input_sheet} 中缺少Genes列")

                # 分割第一个下划线
                df['Genes'] = df['Genes'].str.split('_', n=1).str[0]

                # 按Genes聚合
                numeric_cols = df.select_dtypes(include=['number']).columns.difference(['Genes'])
                grouped = df.groupby('Genes')[numeric_cols].sum().T
                grouped.loc['Total'] = grouped.sum()

                # 格式化结果
                result = grouped.T.reset_index()
                result = result.rename(columns={'index': 'Genes'})
                result = result.sort_values('Total', ascending=False)

                # 保存结果
                result.to_excel(writer, index=False, sheet_name=output_sheet)
                logging.info(f"✅ {output_sheet} 工作表已创建")

        logging.info(f"基因分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"基因分类汇总时出错: {str(e)}")
        raise