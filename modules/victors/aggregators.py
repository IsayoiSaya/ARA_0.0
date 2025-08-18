"""
Victors 数据聚合模块
包含病原体和病原体属分类汇总功能
"""

import pandas as pd
import logging

def generate_pathogen_classification(input_path, output_path):
    """按病原体(Pathogen)分类汇总"""
    try:
        process_config = [
            ('RPKM', 'ARGs_Pathogens'),
            ('16SRPKM', 'ARGs_Pathogens_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                # 读取数据
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 校验必要列
                if 'Pathogen' not in df.columns:
                    raise ValueError(f"工作表 {input_sheet} 缺少Pathogen列")
                
                # 删除非必要列
                df = df.drop(columns=['Length', 'ID'], errors='ignore')
                
                # 获取样本列
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'Pathogen']
                
                # 按病原体分组
                grouped = df.groupby('Pathogen')[sample_columns].sum()
                totals = grouped.sum(axis=1).rename('Total')
                result = pd.concat([grouped, totals], axis=1)
                result = result.sort_values('Total', ascending=False).reset_index()
                
                # 保存结果
                result.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"✅ 病原体分类汇总完成! 结果保存至 {output_path}")
        return True
    
    except Exception as e:
        logging.error(f"病原体分类汇总失败: {str(e)}")
        raise

def generate_genus_classification(input_path, output_path):
    """按病原体属(Genus)分类汇总"""
    try:
        process_config = [
            ('RPKM', 'ARGs_Genus'),
            ('16SRPKM', 'ARGs_Genus_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                # 读取数据
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 校验必要列
                if 'Genus' not in df.columns:
                    raise ValueError(f"工作表 {input_sheet} 缺少Genus列")
                
                # 删除非必要列
                df = df.drop(columns=['Length', 'ID'], errors='ignore')
                
                # 获取样本列
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'Genus']
                
                # 按病原体属分组
                grouped = df.groupby('Genus')[sample_columns].sum()
                totals = grouped.sum(axis=1).rename('Total')
                result = pd.concat([grouped, totals], axis=1)
                result = result.sort_values('Total', ascending=False).reset_index()
                
                # 保存结果
                result.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"✅ 病原体属分类汇总完成! 结果保存至 {output_path}")
        return True
    
    except Exception as e:
        logging.error(f"病原体属分类汇总失败: {str(e)}")
        raise