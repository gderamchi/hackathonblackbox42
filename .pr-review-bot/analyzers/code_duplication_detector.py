"""
Code duplication detector using advanced similarity algorithms.
Finds duplicate code across files and suggests refactoring.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
import hashlib

logger = logging.getLogger(__name__)


class CodeDuplicationDetector:
    """Detects code duplication and suggests refactoring."""
    
    def __init__(self):
        """Initialize duplication detector."""
        self.min_duplicate_lines = 5  # Minimum lines to consider duplication
        self.similarity_threshold = 0.85  # 85% similarity
        self.code_blocks = {}  # Cache of code blocks from all files
    
    def analyze_file(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        Analyze a file for code duplication.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            List of duplication issues
        """
        issues = []
        
        # Extract code blocks
        blocks = self._extract_code_blocks(content, filename)
        
        # Check for duplicates within the same file
        issues.extend(self._find_internal_duplicates(blocks, filename))
        
        # Check for duplicates across files (if we have cached blocks)
        issues.extend(self._find_cross_file_duplicates(blocks, filename))
        
        # Cache blocks for future comparisons
        self.code_blocks[filename] = blocks
        
        logger.info(f"Found {len(issues)} duplication issues in {filename}")
        return issues
    
    def _extract_code_blocks(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extract meaningful code blocks from content."""
        blocks = []
        lines = content.split('\n')
        
        # Extract function/method blocks
        if filename.endswith('.py'):
            blocks.extend(self._extract_python_blocks(lines))
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            blocks.extend(self._extract_javascript_blocks(lines))
        
        # Extract general code blocks (any language)
        blocks.extend(self._extract_general_blocks(lines))
        
        return blocks
    
    def _extract_python_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract Python function/class blocks."""
        blocks = []
        current_block = []
        start_line = 0
        in_block = False
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            # Start of function or class
            if stripped.startswith(('def ', 'class ')):
                if current_block:
                    blocks.append({
                        'type': 'function',
                        'lines': current_block,
                        'start_line': start_line,
                        'end_line': i - 1,
                        'code': '\n'.join(current_block)
                    })
                current_block = [line]
                start_line = i
                in_block = True
                indent_level = len(line) - len(stripped)
            elif in_block:
                current_indent = len(line) - len(stripped)
                # Continue block if indented or empty line
                if current_indent > indent_level or not stripped:
                    current_block.append(line)
                else:
                    # End of block
                    if len(current_block) >= self.min_duplicate_lines:
                        blocks.append({
                            'type': 'function',
                            'lines': current_block,
                            'start_line': start_line,
                            'end_line': i - 1,
                            'code': '\n'.join(current_block)
                        })
                    current_block = []
                    in_block = False
        
        # Add last block
        if current_block and len(current_block) >= self.min_duplicate_lines:
            blocks.append({
                'type': 'function',
                'lines': current_block,
                'start_line': start_line,
                'end_line': len(lines),
                'code': '\n'.join(current_block)
            })
        
        return blocks
    
    def _extract_javascript_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract JavaScript function blocks."""
        blocks = []
        current_block = []
        start_line = 0
        brace_count = 0
        in_function = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Start of function
            if re.search(r'function\s+\w+|const\s+\w+\s*=\s*\(|=>\s*{', stripped):
                current_block = [line]
                start_line = i
                in_function = True
                brace_count = stripped.count('{') - stripped.count('}')
            elif in_function:
                current_block.append(line)
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count == 0:
                    # End of function
                    if len(current_block) >= self.min_duplicate_lines:
                        blocks.append({
                            'type': 'function',
                            'lines': current_block,
                            'start_line': start_line,
                            'end_line': i,
                            'code': '\n'.join(current_block)
                        })
                    current_block = []
                    in_function = False
        
        return blocks
    
    def _extract_general_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract general code blocks (sliding window)."""
        blocks = []
        
        for i in range(len(lines) - self.min_duplicate_lines + 1):
            block_lines = lines[i:i + self.min_duplicate_lines]
            
            # Skip if mostly empty or comments
            non_empty = [l for l in block_lines if l.strip() and not l.strip().startswith(('#', '//'))]
            if len(non_empty) < self.min_duplicate_lines // 2:
                continue
            
            blocks.append({
                'type': 'block',
                'lines': block_lines,
                'start_line': i + 1,
                'end_line': i + self.min_duplicate_lines,
                'code': '\n'.join(block_lines)
            })
        
        return blocks
    
    def _find_internal_duplicates(self, blocks: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
        """Find duplicates within the same file."""
        issues = []
        
        for i, block1 in enumerate(blocks):
            for block2 in blocks[i + 1:]:
                similarity = self._calculate_similarity(block1['code'], block2['code'])
                
                if similarity >= self.similarity_threshold:
                    issues.append({
                        'type': 'quality',
                        'severity': 'medium',
                        'message': f'Duplicate code detected ({int(similarity * 100)}% similar)',
                        'suggestion': 'Extract common code into a reusable function',
                        'line': block1['start_line'],
                        'duplicate_location': f"Lines {block2['start_line']}-{block2['end_line']}",
                        'similarity': similarity,
                        'code_snippet': block1['code'][:100],
                        'auto_fix': {
                            'description': 'Extract to function',
                            'hint': f"Create a function to replace duplicated code at lines {block1['start_line']} and {block2['start_line']}"
                        }
                    })
        
        return issues
    
    def _find_cross_file_duplicates(self, blocks: List[Dict[str, Any]], current_file: str) -> List[Dict[str, Any]]:
        """Find duplicates across different files."""
        issues = []
        
        for filename, cached_blocks in self.code_blocks.items():
            if filename == current_file:
                continue
            
            for block1 in blocks:
                for block2 in cached_blocks:
                    similarity = self._calculate_similarity(block1['code'], block2['code'])
                    
                    if similarity >= self.similarity_threshold:
                        issues.append({
                            'type': 'quality',
                            'severity': 'high',
                            'message': f'Duplicate code found in {filename} ({int(similarity * 100)}% similar)',
                            'suggestion': 'Extract common code into a shared module/utility',
                            'line': block1['start_line'],
                            'duplicate_file': filename,
                            'duplicate_location': f"{filename}:Lines {block2['start_line']}-{block2['end_line']}",
                            'similarity': similarity,
                            'code_snippet': block1['code'][:100],
                            'auto_fix': {
                                'description': 'Extract to shared module',
                                'hint': f"Create a shared utility function to replace code in {current_file} and {filename}"
                            }
                        })
        
        return issues
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code blocks."""
        # Normalize code (remove whitespace, comments)
        norm1 = self._normalize_code(code1)
        norm2 = self._normalize_code(code2)
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison."""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Remove variable names (replace with placeholder)
        code = re.sub(r'\b[a-z_][a-z0-9_]*\b', 'VAR', code, flags=re.IGNORECASE)
        
        return code.strip()
    
    def generate_duplication_report(self, all_issues: List[Dict[str, Any]]) -> str:
        """Generate duplication report."""
        if not all_issues:
            return "✅ No code duplication detected - DRY principle followed!"
        
        # Group by severity
        internal = [i for i in all_issues if 'duplicate_file' not in i]
        cross_file = [i for i in all_issues if 'duplicate_file' in i]
        
        report = "## 🔍 Code Duplication Analysis\n\n"
        
        if internal:
            report += f"### 📄 Internal Duplicates: {len(internal)}\n"
            report += "*Duplicate code within the same file*\n\n"
            
            for issue in internal[:5]:
                similarity = int(issue['similarity'] * 100)
                report += f"- **Lines {issue['line']}** - {similarity}% similar to {issue['duplicate_location']}\n"
            
            if len(internal) > 5:
                report += f"\n*...and {len(internal) - 5} more internal duplicates*\n"
            report += "\n"
        
        if cross_file:
            report += f"### 🔗 Cross-File Duplicates: {len(cross_file)}\n"
            report += "*Duplicate code across different files*\n\n"
            
            for issue in cross_file[:5]:
                similarity = int(issue['similarity'] * 100)
                report += f"- **Line {issue['line']}** - {similarity}% similar to `{issue['duplicate_file']}`\n"
            
            if len(cross_file) > 5:
                report += f"\n*...and {len(cross_file) - 5} more cross-file duplicates*\n"
            report += "\n"
        
        # Calculate duplication percentage
        total_duplicates = len(all_issues)
        if total_duplicates > 10:
            report += "⚠️ **High duplication detected** - Consider refactoring\n\n"
        elif total_duplicates > 5:
            report += "⚡ **Moderate duplication** - Some refactoring recommended\n\n"
        else:
            report += "ℹ️ **Low duplication** - Minor cleanup suggested\n\n"
        
        report += "💡 **Recommendation:** Extract common code into reusable functions or modules.\n\n"
        
        return report
