"""
BacMet 数据聚合模块
"""

import pandas as pd
import logging


def generate_compound_classification(df):
    """化合物分类汇总"""
    try:
        # 标记多组分化合物
        df['Compound'] = df['Compound'].apply(
            lambda x: 'mult-drug' if isinstance(x, str) and ',' in x else x
        )

        # 聚合逻辑
        return _aggregate_by_column(df, 'Compound', 'Compound')
    except Exception as e:
        logging.error(f"化合物分类汇总失败: {str(e)}")
        raise


def generate_gene_classification(df):
    """基因分类汇总"""
    try:
        # 确保Gene_name列存在
        if 'Gene_name' not in df.columns:
            raise ValueError("输入数据中缺少Gene_name列")

        return _aggregate_by_column(df, 'Gene_name', 'Gene_name')
    except Exception as e:
        logging.error(f"基因分类汇总失败: {str(e)}")
        raise


def generate_location_classification(df):
    """位置分类汇总"""
    try:
        # 确保Location列存在
        if 'Location' not in df.columns:
            raise ValueError("输入数据中缺少Location列")

        return _aggregate_by_column(df, 'Location', 'Location')
    except Exception as e:
        logging.error(f"位置分类汇总失败: {str(e)}")
        raise


def generate_organism_classification(df):
    """生物体分类汇总"""
    try:
        # 确保Organism列存在
        if 'Organism' not in df.columns:
            raise ValueError("输入数据中缺少Organism列")

        return _aggregate_by_column(df, 'Organism', 'Organism')
    except Exception as e:
        logging.error(f"生物体分类汇总失败: {str(e)}")
        raise


def _aggregate_by_column(df, group_column, output_name):
    """通用聚合函数"""
    # 删除非必要列
    df = df.drop(columns=['gene lentgh'], errors='ignore')

    # 获取样本列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    sample_columns = [col for col in numeric_cols if col != group_column]

    # 按指定列分组
    grouped = df.groupby(group_column)[sample_columns].sum()

    # 添加总计行
    grouped.loc['Total'] = grouped.sum()

    # 转置结果
    result_df = grouped.T.reset_index()
    result_df.columns = [output_name] + list(result_df.columns[1:])

    # 添加总计列
    result_df['Total'] = result_df.iloc[:, 1:].sum(axis=1)

    return result_df