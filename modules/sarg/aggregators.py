"""
SARG 数据聚合模块
包含风险等级添加和各类分类汇总功能
"""

import pandas as pd
import logging

def add_risk_rank(risk_file, target_file):
    """添加风险等级列"""
    try:
        logging.info("添加风险等级信息...")
        # 读取风险映射数据
        risk_df = pd.read_excel(risk_file, sheet_name=0)
        risk_mapping = risk_df.drop_duplicates('ID', keep='first').set_index('ID')['risk_level']
        
        # 处理两个工作表
        sheets_to_process = ['RPKM', '16SRPKM']
        
        with pd.ExcelWriter(target_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for sheet_name in sheets_to_process:
                df = pd.read_excel(target_file, sheet_name=sheet_name)
                
                # 添加Rank列
                df['Rank'] = df['ID'].map(risk_mapping)
                
                # 调整列顺序
                cols = df.columns.tolist()
                id_index = cols.index('ID')
                cols.insert(id_index + 1, cols.pop(cols.index('Rank')))
                
                # 保存更新
                df[cols].to_excel(writer, index=False, sheet_name=sheet_name)
        
        logging.info(f"✅ 风险等级已添加至 {target_file}")
        return True
    except Exception as e:
        logging.error(f"添加风险等级失败: {str(e)}")
        raise

def generate_types_classification(input_path, output_path):
    """按ARGs类型(Types)分类汇总"""
    try:
        logging.info("汇总ARGs类型(Types)...")
        process_config = [
            ('RPKM', 'ARGs_Types'),
            ('16SRPKM', 'ARGs_Types_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 删除非必要列
                df = df.drop(columns=['Length', 'Rank'], errors='ignore')
                
                # 按类型分组汇总
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_cols = [col for col in numeric_cols if col != 'Types']
                
                grouped = df.groupby('Types')[sample_cols].sum().T
                grouped.loc['Total'] = grouped.sum()
                
                # 格式化结果
                result = grouped.T.reset_index()
                result = result.rename(columns={'index': 'Types'})
                result = result.sort_values('Total', ascending=False)
                
                # 保存结果
                result.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"✅ ARGs类型汇总完成! 结果保存至 {output_path}")
        return True
    except Exception as e:
        logging.error(f"类型汇总失败: {str(e)}")
        raise

def generate_gene_classification(input_path, output_path):
    """按ARGs基因分类汇总"""
    try:
        logging.info("汇总ARGs基因(Gene)...")
        process_config = [
            ('RPKM', 'ARGs_Gene'),
            ('16SRPKM', 'ARGs_Gene_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 删除非必要列
                df = df.drop(columns=['Length', 'Rank'], errors='ignore')
                
                # 按基因分组汇总
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_cols = [col for col in numeric_cols if col != 'ARGs']
                
                grouped = df.groupby('ARGs')[sample_cols].sum().T
                grouped.loc['Total'] = grouped.sum()
                
                # 格式化结果
                result = grouped.T.reset_index()
                result = result.rename(columns={'index': 'ARGs'})
                result = result.sort_values('Total', ascending=False)
                
                # 保存结果
                result.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"✅ ARGs基因汇总完成! 结果保存至 {output_path}")
        return True
    except Exception as e:
        logging.error(f"基因汇总失败: {str(e)}")
        raise

def generate_rank_classification(input_path, output_path):
    """按风险等级(Rank)分类汇总"""
    try:
        logging.info("汇总风险等级(Rank)...")
        rpkm_df = pd.read_excel(input_path, sheet_name='RPKM')
        s16_df = pd.read_excel(input_path, sheet_name='16SRPKM')
        
        # 验证Rank列存在
        def validate_columns(df, sheet_name):
            if 'Rank' not in df.columns:
                raise ValueError(f"工作表 '{sheet_name}' 缺少Rank列")
            return df[df['Rank'].isin(['I', 'II'])]
        
        # 处理单个风险等级
        def process_rank_data(rank_df, rank_name):
            rank_df = rank_df.drop(columns=['Length'], errors='ignore')
            numeric_cols = rank_df.select_dtypes(include=['number']).columns.tolist()
            sample_cols = [col for col in numeric_cols if col != 'ARGs']
            
            grouped = rank_df.groupby('ARGs')[sample_cols].sum().T
            grouped.loc['Total'] = grouped.sum()
            result = grouped.T.reset_index()
            result = result.rename(columns={'index': 'ARGs'})
            result['Risk Rank'] = rank_name
            return result.sort_values('Total', ascending=False)
        
        # 处理单个工作表
        def process_sheet(df, sheet_name):
            valid_df = validate_columns(df, sheet_name)
            rank_i = process_rank_data(valid_df[valid_df['Rank'] == 'I'], 'I')
            rank_ii = process_rank_data(valid_df[valid_df['Rank'] == 'II'], 'II')
            return pd.concat([rank_i, rank_ii])
        
        # 处理两个工作表
        rpkm_result = process_sheet(rpkm_df, 'RPKM')
        s16_result = process_sheet(s16_df, '16SRPKM')
        
        # 保存结果
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            rpkm_result.to_excel(writer, index=False, sheet_name='ARGs_Rank_RPKM')
            s16_result.to_excel(writer, index=False, sheet_name='ARGs_Rank_16SRPKM')
        
        logging.info("✅ 风险等级汇总完成!")
        return True
    except Exception as e:
        logging.error(f"风险等级汇总失败: {str(e)}")
        raise