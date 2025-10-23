"""
Performance impact analyzer.
Detects performance issues and predicts impact of code changes.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes code for performance issues and impact."""
    
    def __init__(self):
        """Initialize performance analyzer."""
        self.patterns = self._load_performance_patterns()
    
    def _load_performance_patterns(self) -> List[Dict[str, Any]]:
        """Load performance issue patterns."""
        return [
            # Nested loops - O(n²) or worse
            {
                'pattern': r'for\s+\w+\s+in\s+.*:\s*\n\s+for\s+\w+\s+in',
                'language': 'python',
                'message': 'Nested loops detected - O(n²) complexity',
                'severity': 'medium',
                'suggestion': 'Consider using hash maps, sets, or optimizing the algorithm',
                'type': 'performance',
                'impact': 'high',
                'complexity': 'O(n²)',
                'auto_fix_hint': 'Use dictionary lookup or set operations for O(n) complexity'
            },
            {
                'pattern': r'for\s*\([^)]+\)\s*{[^}]*for\s*\(',
                'language': 'javascript',
                'message': 'Nested loops detected - O(n²) complexity',
                'severity': 'medium',
                'suggestion': 'Consider using Map, Set, or optimizing the algorithm',
                'type': 'performance',
                'impact': 'high',
                'complexity': 'O(n²)'
            },
            
            # Triple nested loops - O(n³)
            {
                'pattern': r'for.*:\s*\n\s+for.*:\s*\n\s+for',
                'language': 'python',
                'message': 'Triple nested loops - O(n³) complexity - CRITICAL',
                'severity': 'high',
                'suggestion': 'Refactor algorithm - this will be extremely slow for large inputs',
                'type': 'performance',
                'impact': 'critical',
                'complexity': 'O(n³)'
            },
            
            # List operations in loops
            {
                'pattern': r'for\s+\w+\s+in\s+.*:\s*\n\s+.*\.append\(',
                'language': 'python',
                'message': 'List append in loop - consider list comprehension',
                'severity': 'low',
                'suggestion': 'Use list comprehension for better performance',
                'type': 'performance',
                'impact': 'low',
                'auto_fix': lambda code: self._convert_to_list_comprehension(code),
                'fix_description': 'Convert to list comprehension'
            },
            
            # String concatenation in loops
            {
                'pattern': r'for\s+.*:\s*\n\s+\w+\s*\+=\s*["\']',
                'language': 'python',
                'message': 'String concatenation in loop - use join() instead',
                'severity': 'medium',
                'suggestion': 'Use "".join(list) for O(n) instead of O(n²)',
                'type': 'performance',
                'impact': 'medium',
                'complexity': 'O(n²) vs O(n)'
            },
            {
                'pattern': r'for\s*\([^)]+\)\s*{[^}]*\w+\s*\+=\s*["\']',
                'language': 'javascript',
                'message': 'String concatenation in loop - use array.join()',
                'severity': 'medium',
                'suggestion': 'Push to array and use join() for better performance',
                'type': 'performance',
                'impact': 'medium'
            },
            
            # Inefficient list/array operations
            {
                'pattern': r'\.pop\(0\)|\.insert\(0,',
                'language': 'python',
                'message': 'O(n) operation on list - consider using deque',
                'severity': 'medium',
                'suggestion': 'Use collections.deque for O(1) operations at both ends',
                'type': 'performance',
                'impact': 'medium',
                'complexity': 'O(n) vs O(1)'
            },
            {
                'pattern': r'\.shift\(\)|\.unshift\(',
                'language': 'javascript',
                'message': 'O(n) operation on array - expensive for large arrays',
                'severity': 'low',
                'suggestion': 'Consider using a different data structure if frequent',
                'type': 'performance',
                'impact': 'low'
            },
            
            # Repeated function calls
            {
                'pattern': r'for\s+\w+\s+in\s+range\(len\((\w+)\)\):\s*\n\s+.*\1\[',
                'language': 'python',
                'message': 'Repeated len() call in loop',
                'severity': 'low',
                'suggestion': 'Cache len() result or iterate directly over the list',
                'type': 'performance',
                'impact': 'low'
            },
            
            # Database queries in loops
            {
                'pattern': r'for\s+.*:\s*\n\s+.*\.(?:execute|query|get|filter)\(',
                'language': 'python',
                'message': 'Database query in loop - N+1 query problem',
                'severity': 'high',
                'suggestion': 'Use bulk operations or prefetch data before loop',
                'type': 'performance',
                'impact': 'critical',
                'complexity': 'N queries vs 1 query'
            },
            
            # Inefficient searching
            {
                'pattern': r'if\s+\w+\s+in\s+\[',
                'language': 'python',
                'message': 'Linear search in list - O(n) lookup',
                'severity': 'low',
                'suggestion': 'Use set for O(1) lookup if checking membership frequently',
                'type': 'performance',
                'impact': 'low',
                'complexity': 'O(n) vs O(1)'
            },
            
            # Unnecessary copying
            {
                'pattern': r'\.copy\(\)|list\(|dict\(',
                'language': 'python',
                'message': 'Copying data structure - may be expensive for large data',
                'severity': 'info',
                'suggestion': 'Ensure copying is necessary - consider using views or references',
                'type': 'performance',
                'impact': 'low'
            },
            
            # Regex compilation in loops
            {
                'pattern': r'for\s+.*:\s*\n\s+.*re\.(?:match|search|findall)\(',
                'language': 'python',
                'message': 'Regex operation in loop - compile pattern outside loop',
                'severity': 'medium',
                'suggestion': 'Use re.compile() before the loop for better performance',
                'type': 'performance',
                'impact': 'medium'
            },
            
            # Inefficient sorting
            {
                'pattern': r'sorted\(.*,\s*key=lambda',
                'language': 'python',
                'message': 'Lambda in sort key - consider using operator.itemgetter',
                'severity': 'info',
                'suggestion': 'operator.itemgetter is faster than lambda for simple cases',
                'type': 'performance',
                'impact': 'low'
            },
            
            # Global variable access in loops
            {
                'pattern': r'for\s+.*:\s*\n\s+.*global\s+',
                'language': 'python',
                'message': 'Global variable access in loop - slower than local',
                'severity': 'low',
                'suggestion': 'Cache global variables in local scope before loop',
                'type': 'performance',
                'impact': 'low'
            },
            
            # Inefficient file operations
            {
                'pattern': r'for\s+.*:\s*\n\s+.*open\(',
                'language': 'python',
                'message': 'File open in loop - expensive I/O operation',
                'severity': 'high',
                'suggestion': 'Open file once before loop or batch operations',
                'type': 'performance',
                'impact': 'high'
            },
            
            # Memory-intensive operations
            {
                'pattern': r'\.read\(\)|\.readlines\(\)',
                'language': 'python',
                'message': 'Reading entire file into memory',
                'severity': 'medium',
                'suggestion': 'For large files, iterate line by line or use chunking',
                'type': 'performance',
                'impact': 'medium'
            },
            
            # Synchronous operations that should be async
            {
                'pattern': r'requests\.(?:get|post)\(',
                'language': 'python',
                'message': 'Synchronous HTTP request - blocks execution',
                'severity': 'medium',
                'suggestion': 'Consider using async/await with aiohttp for concurrent requests',
                'type': 'performance',
                'impact': 'medium'
            },
            
            # Inefficient data structures
            {
                'pattern': r'if\s+.*\s+not\s+in\s+\w+:\s*\n\s+\w+\.append\(',
                'language': 'python',
                'message': 'Checking membership before append - use set instead',
                'severity': 'low',
                'suggestion': 'Use set for automatic uniqueness with O(1) operations',
                'type': 'performance',
                'impact': 'low'
            },
        ]
    
    def analyze(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """
        Analyze code for performance issues.
        
        Args:
            code: Source code to analyze
            filename: Name of the file
            
        Returns:
            List of performance issues
        """
        issues = []
        language = self._detect_language(filename)
        lines = code.split('\n')
        
        for pattern_rule in self.patterns:
            # Check if pattern applies to this language
            if pattern_rule['language'] not in ['all', language]:
                continue
            
            pattern = pattern_rule['pattern']
            
            try:
                # Search in full code for multi-line patterns
                matches = re.finditer(pattern, code, re.MULTILINE)
                
                for match in matches:
                    # Find line number
                    line_num = code[:match.start()].count('\n') + 1
                    
                    issue = {
                        'type': pattern_rule['type'],
                        'severity': pattern_rule['severity'],
                        'line': line_num,
                        'message': pattern_rule['message'],
                        'suggestion': pattern_rule['suggestion'],
                        'impact': pattern_rule.get('impact', 'low'),
                        'complexity': pattern_rule.get('complexity', 'N/A'),
                        'code_snippet': match.group()[:100]
                    }
                    
                    # Add auto-fix if available
                    if 'auto_fix' in pattern_rule:
                        try:
                            fixed = pattern_rule['auto_fix'](match.group())
                            issue['auto_fix'] = {
                                'original': match.group(),
                                'fixed': fixed,
                                'description': pattern_rule.get('fix_description', 'Apply performance optimization')
                            }
                        except Exception as e:
                            logger.warning(f"Failed to generate auto-fix: {e}")
                    elif 'auto_fix_hint' in pattern_rule:
                        issue['optimization_hint'] = pattern_rule['auto_fix_hint']
                    
                    issues.append(issue)
                    
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern}: {e}")
                continue
        
        logger.info(f"Performance analyzer found {len(issues)} issues in {filename}")
        return issues
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        
        return 'unknown'
    
    def _convert_to_list_comprehension(self, code: str) -> str:
        """Convert loop with append to list comprehension."""
        # This is a simplified conversion - real implementation would be more complex
        return f"# TODO: Convert to list comprehension\n{code}"
    
    def estimate_performance_impact(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate overall performance impact.
        
        Args:
            issues: List of performance issues
            
        Returns:
            Performance impact summary
        """
        if not issues:
            return {
                'overall_impact': 'none',
                'score': 100,
                'summary': 'No performance issues detected'
            }
        
        # Calculate impact score
        impact_weights = {
            'critical': 40,
            'high': 20,
            'medium': 10,
            'low': 5
        }
        
        total_impact = 0
        for issue in issues:
            impact = issue.get('impact', 'low')
            total_impact += impact_weights.get(impact, 5)
        
        # Score out of 100 (lower is worse)
        score = max(0, 100 - total_impact)
        
        # Determine overall impact
        if score >= 80:
            overall = 'low'
        elif score >= 60:
            overall = 'medium'
        elif score >= 40:
            overall = 'high'
        else:
            overall = 'critical'
        
        return {
            'overall_impact': overall,
            'score': score,
            'total_issues': len(issues),
            'by_impact': self._group_by_impact(issues),
            'summary': self._generate_impact_summary(issues, score)
        }
    
    def _group_by_impact(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by impact level."""
        grouped = {}
        for issue in issues:
            impact = issue.get('impact', 'low')
            grouped[impact] = grouped.get(impact, 0) + 1
        return grouped
    
    def _generate_impact_summary(self, issues: List[Dict[str, Any]], score: int) -> str:
        """Generate human-readable impact summary."""
        if score >= 80:
            return "Minor performance concerns - optimizations recommended but not critical"
        elif score >= 60:
            return "Moderate performance impact - consider optimizing before production"
        elif score >= 40:
            return "Significant performance impact - optimization strongly recommended"
        else:
            return "Critical performance issues - will cause slowdowns, must optimize"
    
    def generate_performance_report(self, issues: List[Dict[str, Any]]) -> str:
        """
        Generate performance analysis report.
        
        Args:
            issues: List of performance issues
            
        Returns:
            Formatted report
        """
        if not issues:
            return "✅ No performance issues detected - code looks efficient!"
        
        impact_summary = self.estimate_performance_impact(issues)
        
        report = "## ⚡ Performance Analysis\n\n"
        report += f"**Performance Score:** {impact_summary['score']}/100\n"
        report += f"**Overall Impact:** {impact_summary['overall_impact'].upper()}\n\n"
        report += f"*{impact_summary['summary']}*\n\n"
        
        # Group by impact
        by_impact = impact_summary['by_impact']
        if by_impact:
            report += "### 📊 Issues by Impact:\n"
            impact_emojis = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}
            for impact in ['critical', 'high', 'medium', 'low']:
                if impact in by_impact:
                    count = by_impact[impact]
                    emoji = impact_emojis.get(impact, 'ℹ️')
                    report += f"- {emoji} **{impact.upper()}**: {count} issue(s)\n"
            report += "\n"
        
        # List top issues
        report += "### 🔍 Key Performance Issues:\n\n"
        for i, issue in enumerate(issues[:5], 1):
            impact = issue.get('impact', 'low')
            emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}[impact]
            message = issue['message']
            complexity = issue.get('complexity', 'N/A')
            
            report += f"{i}. {emoji} **{message}**\n"
            if complexity != 'N/A':
                report += f"   - Complexity: `{complexity}`\n"
            report += f"   - {issue['suggestion']}\n\n"
        
        if len(issues) > 5:
            report += f"*...and {len(issues) - 5} more performance issues*\n\n"
        
        report += "💡 **Recommendation:** Address high-impact issues first for maximum performance gain.\n\n"
        
        return report
