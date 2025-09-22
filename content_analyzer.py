#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟化容器化技术文档内容分析器
用于批判性分析文档内容的真实性和准确性
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ContentAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.analysis_results = {}
        self.exaggerated_patterns = [
            r'终极|终极版|终极方案|终极分析|终极论证|终极报告',
            r'全面|全方位|完美|最佳|最优|顶级|领先|革命性',
            r'突破性|颠覆性|创新性|前沿|先进|高端',
            r'100%|完全|绝对|彻底|根本性|本质性',
            r'未来.*年|.*年后|.*年发展|.*年趋势',
            r'智能.*系统|AI.*驱动|量子.*计算|边缘.*计算'
        ]
        self.technical_verification_keywords = {
            'docker': ['容器', '镜像', 'Dockerfile', 'registry', 'compose'],
            'kubernetes': ['Pod', 'Service', 'Deployment', 'kubectl', 'CRD'],
            'vmware': ['vSphere', 'ESXi', 'vCenter', 'VM', '虚拟化'],
            'webassembly': ['WASM', 'WebAssembly', '字节码', '沙箱']
        }
        
    def analyze_all_files(self) -> Dict[str, Any]:
        """递归分析所有文件"""
        logging.info(f"开始分析目录: {self.root_dir}")
        
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    self.analyze_file(file_path)
                    
        return self.analysis_results
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            analysis = {
                'file_path': str(file_path),
                'file_size': len(content),
                'line_count': len(content.splitlines()),
                'exaggerated_content': self.detect_exaggerated_content(content),
                'technical_accuracy': self.verify_technical_accuracy(content),
                'content_quality': self.assess_content_quality(content),
                'recommendations': []
            }
            
            # 生成建议
            if analysis['exaggerated_content']['count'] > 5:
                analysis['recommendations'].append('删除或修改夸大性内容')
            if analysis['technical_accuracy']['score'] < 0.7:
                analysis['recommendations'].append('验证技术内容的准确性')
            if analysis['content_quality']['score'] < 0.6:
                analysis['recommendations'].append('提升内容质量和结构')
                
            self.analysis_results[str(file_path)] = analysis
            logging.info(f"已分析文件: {file_path}")
            
        except Exception as e:
            logging.error(f"分析文件失败 {file_path}: {e}")
            
    def detect_exaggerated_content(self, content: str) -> Dict[str, Any]:
        """检测夸大性内容"""
        exaggerated_matches = []
        
        for pattern in self.exaggerated_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            exaggerated_matches.extend(matches)
            
        return {
            'count': len(exaggerated_matches),
            'matches': exaggerated_matches,
            'severity': 'high' if len(exaggerated_matches) > 10 else 'medium' if len(exaggerated_matches) > 5 else 'low'
        }
        
    def verify_technical_accuracy(self, content: str) -> Dict[str, Any]:
        """验证技术内容准确性"""
        accuracy_score = 1.0
        issues = []
        
        # 检查技术关键词的准确性
        for tech, keywords in self.technical_verification_keywords.items():
            tech_mentions = sum(1 for keyword in keywords if keyword.lower() in content.lower())
            if tech_mentions > 0:
                # 简单的准确性检查
                if tech == 'docker' and 'Dockerfile' in content:
                    accuracy_score -= 0.1  # 需要更详细的验证
                elif tech == 'kubernetes' and 'kubectl' in content:
                    accuracy_score -= 0.1
                    
        return {
            'score': max(0, accuracy_score),
            'issues': issues
        }
        
    def assess_content_quality(self, content: str) -> Dict[str, Any]:
        """评估内容质量"""
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        # 计算质量指标
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0
        structure_score = 1.0 if any(line.startswith('#') for line in lines) else 0.5
        
        quality_score = min(1.0, (avg_line_length / 100) * structure_score)
        
        return {
            'score': quality_score,
            'avg_line_length': avg_line_length,
            'has_structure': structure_score > 0.5
        }
        
    def generate_report(self) -> str:
        """生成分析报告"""
        report = f"""
# 虚拟化容器化技术文档内容分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计
- 分析文件总数: {len(self.analysis_results)}
- 需要修改的文件数: {sum(1 for r in self.analysis_results.values() if r['recommendations'])}
- 夸大内容严重文件数: {sum(1 for r in self.analysis_results.values() if r['exaggerated_content']['severity'] == 'high')}

## 详细分析结果
"""
        
        for file_path, analysis in self.analysis_results.items():
            report += f"""
### {file_path}
- 文件大小: {analysis['file_size']} 字符
- 行数: {analysis['line_count']}
- 夸大内容数量: {analysis['exaggerated_content']['count']}
- 技术准确性评分: {analysis['technical_accuracy']['score']:.2f}
- 内容质量评分: {analysis['content_quality']['score']:.2f}
- 建议: {', '.join(analysis['recommendations']) if analysis['recommendations'] else '无'}
"""
            
        return report
        
    def save_results(self, output_file: str = 'analysis_results.json'):
        """保存分析结果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        logging.info(f"分析结果已保存到: {output_file}")

if __name__ == "__main__":
    analyzer = ContentAnalyzer(".")
    results = analyzer.analyze_all_files()
    
    # 生成报告
    report = analyzer.generate_report()
    with open('content_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存结果
    analyzer.save_results()
    
    print("内容分析完成！")
    print(f"分析报告已保存到: content_analysis_report.md")
    print(f"详细结果已保存到: analysis_results.json")
