"""
Advanced code complexity analyzer.
Calculates cyclomatic complexity, cognitive complexity, and maintainability index.
"""

import re
import logging
import math
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """Analyzes code complexity using multiple metrics."""
    
    def __init__(self):
        """Initialize complexity analyzer."""
        self.complexity_thresholds = {
            'cyclomatic': {'low': 10, 'medium': 20, 'high': 30},
            'cognitive': {'low': 15, 'medium': 25, 'high': 40},
            'nesting': {'low': 3, 'medium': 5, 'high': 7}
        }
    
    def analyze(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """
        Analyze code complexity.
        
        Args:
            code: Source code
            filename: File name
            
        Returns:
            List of complexity issues
        """
        issues = []
        
        # Extract functions
        functions = self._extract_functions(code, filename)
        
        for func in functions:
            # Calculate various complexity metrics
            cyclomatic = self._calculate_cyclomatic_complexity(func['code'])
            cognitive = self._calculate_cognitive_complexity(func['code'])
            nesting = self._calculate_max_nesting(func['code'])
            maintainability = self._calculate_maintainability_index(func['code'], cyclomatic)
            
            # Create issue if complexity is too high
            if cyclomatic > self.complexity_thresholds['cyclomatic']['low']:
                issues.append(self._create_complexity_issue(
                    func, cyclomatic, cognitive, nesting, maintainability, 'cyclomatic'
                ))
            
            if cognitive > self.complexity_thresholds['cognitive']['low']:
                issues.append(self._create_complexity_issue(
                    func, cyclomatic, cognitive, nesting, maintainability, 'cognitive'
                ))
            
            if nesting > self.complexity_thresholds['nesting']['low']:
                issues.append(self._create_complexity_issue(
                    func, cyclomatic, cognitive, nesting, maintainability, 'nesting'
                ))
        
        logger.info(f"Found {len(issues)} complexity issues in {filename}")
        return issues
    
    def _extract_functions(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Extract functions from code."""
        functions = []
        
        if filename.endswith('.py'):
            functions = self._extract_python_functions(code)
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            functions = self._extract_javascript_functions(code)
        
        return functions
    
    def _extract_python_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract Python functions."""
        functions = []
        lines = code.split('\n')
        current_func = None
        func_lines = []
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            if stripped.startswith('def '):
                # Save previous function
                if current_func:
                    functions.append({
                        'name': current_func,
                        'start_line': func_start,
                        'end_line': i - 1,
                        'code': '\n'.join(func_lines)
                    })
                
                # Start new function
                match = re.match(r'def\s+(\w+)', stripped)
                if match:
                    current_func = match.group(1)
                    func_start = i
                    func_lines = [line]
                    indent_level = len(line) - len(stripped)
            
            elif current_func:
                current_indent = len(line) - len(stripped)
                if current_indent > indent_level or not stripped:
                    func_lines.append(line)
                else:
                    # End of function
                    functions.append({
                        'name': current_func,
                        'start_line': func_start,
                        'end_line': i - 1,
                        'code': '\n'.join(func_lines)
                    })
                    current_func = None
                    func_lines = []
        
        # Add last function
        if current_func:
            functions.append({
                'name': current_func,
                'start_line': func_start,
                'end_line': len(lines),
                'code': '\n'.join(func_lines)
            })
        
        return functions
    
    def _extract_javascript_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract JavaScript functions."""
        functions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Match function declarations
            match = re.search(r'function\s+(\w+)\s*\(', line)
            if match:
                func_name = match.group(1)
                func_code = self._extract_js_function_body(lines, i - 1)
                functions.append({
                    'name': func_name,
                    'start_line': i,
                    'end_line': i + func_code.count('\n'),
                    'code': func_code
                })
        
        return functions
    
    def _extract_js_function_body(self, lines: List[str], start_idx: int) -> str:
        """Extract JavaScript function body."""
        brace_count = 0
        func_lines = []
        started = False
        
        for line in lines[start_idx:]:
            func_lines.append(line)
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
            
            if started and brace_count == 0:
                break
        
        return '\n'.join(func_lines)
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity.
        M = E - N + 2P
        Simplified: Count decision points + 1
        """
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b',
            r'\band\b', r'\bor\b',
            r'\bcase\b', r'\bcatch\b',
            r'\?\s*.*\s*:', # Ternary operator
        ]
        
        for keyword in decision_keywords:
            complexity += len(re.findall(keyword, code))
        
        return complexity
    
    def _calculate_cognitive_complexity(self, code: str) -> int:
        """
        Calculate cognitive complexity (more human-centric than cyclomatic).
        Accounts for nesting and structural complexity.
        """
        complexity = 0
        nesting_level = 0
        lines = code.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # Increase nesting
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try', 'with']):
                complexity += (1 + nesting_level)
                if stripped.endswith(':') or stripped.endswith('{'):
                    nesting_level += 1
            
            # Logical operators add complexity
            complexity += stripped.count(' and ')
            complexity += stripped.count(' or ')
            complexity += stripped.count('&&')
            complexity += stripped.count('||')
            
            # Decrease nesting
            if stripped.startswith(('else', 'elif', 'except', 'finally', '}')):
                nesting_level = max(0, nesting_level - 1)
        
        return complexity
    
    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth."""
        max_nesting = 0
        current_nesting = 0
        
        for line in code.split('\n'):
            stripped = line.strip()
            
            # Increase nesting
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try', 'with', 'def', 'class']):
                if stripped.endswith(':') or stripped.endswith('{'):
                    current_nesting += 1
                    max_nesting = max(max_nesting, current_nesting)
            
            # Decrease nesting
            if stripped.startswith('}') or (stripped and not line.startswith(' ' * (current_nesting * 4))):
                current_nesting = max(0, current_nesting - 1)
        
        return max_nesting
    
    def _calculate_maintainability_index(self, code: str, cyclomatic: int) -> float:
        """
        Calculate maintainability index (0-100).
        MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        Simplified version using available metrics.
        """
        lines = [l for l in code.split('\n') if l.strip()]
        loc = len(lines)
        
        if loc == 0:
            return 100.0
        
        # Simplified MI calculation
        volume = loc * math.log2(max(cyclomatic, 1))
        mi = max(0, 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * cyclomatic - 16.2 * math.log(max(loc, 1)))
        
        # Normalize to 0-100
        return min(100, max(0, mi))
    
    def _create_complexity_issue(
        self,
        func: Dict[str, Any],
        cyclomatic: int,
        cognitive: int,
        nesting: int,
        maintainability: float,
        issue_type: str
    ) -> Dict[str, Any]:
        """Create a complexity issue."""
        func_name = func['name']
        
        # Determine severity
        if issue_type == 'cyclomatic':
            value = cyclomatic
            thresholds = self.complexity_thresholds['cyclomatic']
            metric_name = "Cyclomatic Complexity"
        elif issue_type == 'cognitive':
            value = cognitive
            thresholds = self.complexity_thresholds['cognitive']
            metric_name = "Cognitive Complexity"
        else:  # nesting
            value = nesting
            thresholds = self.complexity_thresholds['nesting']
            metric_name = "Nesting Depth"
        
        if value > thresholds['high']:
            severity = 'high'
        elif value > thresholds['medium']:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Generate refactoring suggestions
        suggestions = self._generate_refactoring_suggestions(
            func_name, cyclomatic, cognitive, nesting
        )
        
        return {
            'type': 'quality',
            'severity': severity,
            'line': func['start_line'],
            'message': f'High {metric_name} in function "{func_name}" ({value})',
            'suggestion': f'Consider refactoring to reduce complexity',
            'metrics': {
                'cyclomatic_complexity': cyclomatic,
                'cognitive_complexity': cognitive,
                'max_nesting_depth': nesting,
                'maintainability_index': round(maintainability, 1),
                'lines_of_code': len(func['code'].split('\n'))
            },
            'refactoring_suggestions': suggestions,
            'auto_fix': {
                'description': 'Refactoring suggestions',
                'hints': suggestions
            }
        }
    
    def _generate_refactoring_suggestions(
        self,
        func_name: str,
        cyclomatic: int,
        cognitive: int,
        nesting: int
    ) -> List[str]:
        """Generate refactoring suggestions based on complexity metrics."""
        suggestions = []
        
        if cyclomatic > 15:
            suggestions.append("Extract complex conditional logic into separate functions")
            suggestions.append("Use early returns to reduce nesting")
        
        if cognitive > 20:
            suggestions.append("Break down into smaller, single-purpose functions")
            suggestions.append("Simplify boolean expressions")
        
        if nesting > 4:
            suggestions.append("Reduce nesting depth by extracting nested blocks")
            suggestions.append("Use guard clauses to exit early")
            suggestions.append("Consider using polymorphism instead of nested conditionals")
        
        if cyclomatic > 10 and nesting > 3:
            suggestions.append("Apply the Single Responsibility Principle")
            suggestions.append("Consider using design patterns (Strategy, State, etc.)")
        
        return suggestions
    
    def generate_complexity_report(self, issues: List[Dict[str, Any]]) -> str:
        """Generate complexity analysis report."""
        if not issues:
            return "✅ Code complexity is within acceptable limits!"
        
        report = "## 🧮 Code Complexity Analysis\n\n"
        
        # Calculate average metrics
        avg_cyclomatic = sum(i['metrics']['cyclomatic_complexity'] for i in issues) / len(issues)
        avg_cognitive = sum(i['metrics']['cognitive_complexity'] for i in issues) / len(issues)
        avg_maintainability = sum(i['metrics']['maintainability_index'] for i in issues) / len(issues)
        
        report += f"**Average Cyclomatic Complexity:** {avg_cyclomatic:.1f}\n"
        report += f"**Average Cognitive Complexity:** {avg_cognitive:.1f}\n"
        report += f"**Average Maintainability Index:** {avg_maintainability:.1f}/100\n\n"
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        if by_severity:
            report += "### 📊 Issues by Severity:\n"
            for severity in ['high', 'medium', 'low']:
                if severity in by_severity:
                    count = len(by_severity[severity])
                    emoji = {'high': '🚨', 'medium': '⚠️', 'low': 'ℹ️'}
                    report += f"- {emoji[severity]} **{severity.upper()}**: {count} function(s)\n"
            report += "\n"
        
        # List complex functions
        report += "### 🎯 Most Complex Functions:\n\n"
        
        # Sort by cyclomatic complexity
        sorted_issues = sorted(issues, key=lambda x: x['metrics']['cyclomatic_complexity'], reverse=True)
        
        for i, issue in enumerate(sorted_issues[:5], 1):
            func_name = issue['message'].split('"')[1]
            metrics = issue['metrics']
            
            report += f"{i}. **{func_name}** (Line {issue['line']})\n"
            report += f"   - Cyclomatic: {metrics['cyclomatic_complexity']}\n"
            report += f"   - Cognitive: {metrics['cognitive_complexity']}\n"
            report += f"   - Nesting: {metrics['max_nesting_depth']}\n"
            report += f"   - Maintainability: {metrics['maintainability_index']}/100\n"
            
            if 'refactoring_suggestions' in issue:
                report += "   **Suggestions:**\n"
                for suggestion in issue['refactoring_suggestions'][:2]:
                    report += f"   - {suggestion}\n"
            report += "\n"
        
        if len(issues) > 5:
            report += f"*...and {len(issues) - 5} more complex functions*\n\n"
        
        report += "💡 **Recommendation:** Refactor functions with complexity > 15 for better maintainability.\n\n"
        
        return report
