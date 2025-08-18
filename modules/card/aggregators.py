"""
CARD 数据聚合模块
包含：
- 基因家族分类
- 抗性类别分类
- 类型分类
- 抗性机制分类
- ARGs分类
"""

import pandas as pd
import math
import logging

def generate_gene_family_classification(input_path, output_path):
    """AMR基因家族分类汇总"""
    try:
        process_config = [
            ('RPKM', 'AMR_GeneFamily'),
            ('16SRPKM', 'AMR_GeneFamily_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 检查必要列存在
                if 'AMR gene family' not in df.columns:
                    raise ValueError(f"输入文件缺少'AMR gene family'列")
                
                # 删除非必要列
                df.drop(columns=['Length', 'ARO'], inplace=True, errors='ignore')
                
                # 获取样本列
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'AMR gene family']
                
                # 按基因家族分组
                classification_df = df.groupby('AMR gene family')[sample_columns].sum().T.reset_index()
                
                # 添加总计行
                classification_df.loc['Total'] = classification_df.sum(axis=0)
                classification_df.rename(columns={'index':'Sample'}, inplace=True)
                
                # 调整结果格式
                result_df = classification_df.set_index('Sample').T.reset_index()
                result_df.columns = [*result_df.columns[:-1], 'total']
                result_df.rename(columns={'index':'GeneFamily'}, inplace=True)
                result_df = result_df.sort_values(by='total', ascending=False)
                
                result_df.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"AMR基因家族分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"基因家族分类失败: {str(e)}")
        raise

def generate_class_classification(input_path, output_path):
    """抗性类别分类汇总"""
    try:
        process_config = [
            ('RPKM', 'ARGs_Class'),
            ('16SRPKM', 'ARGs_Class_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 检查必要列存在
                if 'Class' not in df.columns:
                    raise ValueError(f"输入文件缺少'Class'列")
                
                df.drop(columns=['Length', 'ARO'], inplace=True, errors='ignore')
                
                # 分组汇总
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'Class']
                
                classification_df = df.groupby('Class')[sample_columns].sum().T.reset_index()
                classification_df.loc['Total'] = classification_df.sum(axis=0)
                classification_df.rename(columns={'index':'Sample'}, inplace=True)
                
                # 生成结果表
                result_df = classification_df.set_index('Sample').T.reset_index()
                result_df.columns = [*result_df.columns[:-1], 'total']
                result_df.rename(columns={'index':'Class'}, inplace=True)
                result_df = result_df.sort_values(by='total', ascending=False)
                
                result_df.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"抗性类别分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"抗性类别分类失败: {str(e)}")
        raise

def generate_class_types_classification(input_path, output_path, mapping_file):
    """Class-Types分类汇总"""
    try:
        # 读取类型映射文件
        type_mapping = pd.read_csv(mapping_file, sep='\t')
        # 创建Class到Types的映射字典
        class_to_types = type_mapping.groupby('Class')['Types'].apply(
            lambda x: [item for sublist in x.str.split(';') for item in sublist]
        ).to_dict()
        
        process_config = [
            ('RPKM', 'ARGs_Class_Types'),
            ('16SRPKM', 'ARGs_Class_Types_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                if 'Class' not in df.columns:
                    raise ValueError(f"输入文件缺少'Class'列")
                
                # 添加Types列并展开多值
                df['Types'] = df['Class'].map(class_to_types)
                df = df.explode('Types')
                
                # 删除不需要的列
                df.drop(columns=['Length', 'ARO', 'Class'], inplace=True, errors='ignore')
                
                # 分组汇总
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'Types']
                
                classification_df = df.groupby('Types')[sample_columns].sum().T.reset_index()
                classification_df.loc['Total'] = classification_df.sum(axis=0)
                classification_df.rename(columns={'index':'Sample'}, inplace=True)
                
                # 生成结果表
                result_df = classification_df.set_index('Sample').T.reset_index()
                result_df.columns = [*result_df.columns[:-1], 'total']
                result_df.rename(columns={'index':'Types'}, inplace=True)
                result_df = result_df.sort_values(by='total', ascending=False)
                
                result_df.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"Class-Types分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Class-Types分类失败: {str(e)}")
        raise

def generate_mechanism_classification(input_path, output_path):
    """抗性机制分类汇总"""
    try:
        process_config = [
            ('RPKM', 'ARGs_Mechanisms'),
            ('16SRPKM', 'ARGs_Mechanisms_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 校验必要列存在
                if 'resistance mechanisms' not in df.columns:
                    raise ValueError(f"输入文件缺少'resistance mechanisms'列")
                
                # 删除非必要列
                df.drop(columns=['Length', 'ARO'], inplace=True, errors='ignore')
                
                # 获取样本列
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'resistance mechanisms']
                
                # 按抗性机制分组
                classification_df = df.groupby('resistance mechanisms')[sample_columns].sum().T.reset_index()
                
                # 添加总计行
                classification_df.loc['Total'] = classification_df.sum(axis=0)
                classification_df.rename(columns={'index':'Sample'}, inplace=True)
                
                # 调整结果格式
                result_df = classification_df.set_index('Sample').T.reset_index()
                result_df.columns = [*result_df.columns[:-1], 'total']
                result_df.rename(columns={'index':'Mechanisms'}, inplace=True)
                result_df = result_df.sort_values(by='total', ascending=False)
                
                result_df.to_excel(writer, index=False, sheet_name=output_sheet)
        
        logging.info(f"抗性机制分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"抗性机制分类失败: {str(e)}")
        raise

def generate_arg_classification(input_path, output_path):
    """ARGs分类汇总"""
    try:
        process_config = [
            ('RPKM', 'ARGs_Classification'),
            ('16SRPKM', 'ARGs_Classification_16S')
        ]
        
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for input_sheet, output_sheet in process_config:
                df = pd.read_excel(input_path, sheet_name=input_sheet)
                
                # 校验必要列存在
                if 'ARGs' not in df.columns:
                    raise ValueError(f"输入文件缺少'ARGs'列")
                
                # 删除非必要列
                df.drop(columns=['Length', 'ARO'], inplace=True, errors='ignore')
                
                # 分组汇总
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                sample_columns = [col for col in numeric_cols if col != 'ARGs']
                
                classification_df = df.groupby('ARGs')[sample_columns].sum().T.reset_index()
                classification_df.loc['Total'] = classification_df.sum(axis=0)
                classification_df.rename(columns={'index':'Sample'}, inplace=True)
                
                # 调整结果格式
                result_df = classification_df.set_index('Sample').T.reset_index()
                result_df.columns = [*result_df.columns[:-1], 'total']
                result_df.rename(columns={'index':'ARGs'}, inplace=True)
                result_df = result_df.sort_values(by='total', ascending=False)
                
                result_df.to_excel(writer, index=False, sheet_name=output_sheet)
                
                # ===== 高频ARGs筛选 =====
                sample_cols = [col for col in result_df.columns if col not in ['ARGs', 'total']]
                
                if sample_cols:  # 确保存在样本列
                    # 80%样本阈值且向上取整
                    threshold = math.ceil(len(sample_cols) * 0.8)
                    
                    # 统计每个ARG在多少样本中存在（值>0）
                    presence_count = result_df[sample_cols].apply(
                        lambda x: (x > 0).sum(),
                        axis=1
                    )
                    
                    # 筛选高频ARGs并添加统计信息
                    top_args_df = result_df[presence_count >= threshold].copy()
                    top_args_df['Sample_Presence'] = presence_count[presence_count >= threshold]
                    top_args_df['Presence_Percentage'] = top_args_df['Sample_Presence'] / len(sample_cols)
                    
                    # 保存到新sheet（Top_前缀）
                    top_sheet = f"Top_{output_sheet}"
                    top_args_df.to_excel(writer, index=False, sheet_name=top_sheet)
        
        logging.info(f"ARGs分类汇总完成! 结果已保存至: {output_path}")
        return True
    except Exception as e:
        logging.error(f"ARGs分类失败: {str(e)}")
        raise