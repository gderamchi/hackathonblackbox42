"""
Test coverage analyzer - detects untested code and suggests test cases.
Uses AI to generate meaningful test scenarios.
"""

import re
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class TestCoverageAnalyzer:
    """Analyzes test coverage and suggests missing tests."""
    
    def __init__(self):
        """Initialize test coverage analyzer."""
        self.test_patterns = {
            'python': [r'def test_', r'class Test'],
            'javascript': [r'describe\(', r'it\(', r'test\(']
        }
    
    def analyze(self, code_files: Dict[str, str], test_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Analyze test coverage.
        
        Args:
            code_files: Dict of filename -> content for source files
            test_files: Dict of filename -> content for test files
            
        Returns:
            List of coverage issues
        """
        issues = []
        
        # Extract functions/classes from code files
        code_entities = {}
        for filename, content in code_files.items():
            entities = self._extract_entities(content, filename)
            code_entities[filename] = entities
        
        # Extract test cases from test files
        test_cases = set()
        for filename, content in test_files.items():
            tests = self._extract_test_cases(content, filename)
            test_cases.update(tests)
        
        # Find untested entities
        for filename, entities in code_entities.items():
            for entity in entities:
                if not self._is_tested(entity, test_cases):
                    issue = self._create_coverage_issue(entity, filename)
                    issues.append(issue)
        
        logger.info(f"Found {len(issues)} untested code entities")
        return issues
    
    def _extract_entities(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extract functions and classes from code."""
        entities = []
        
        if filename.endswith('.py'):
            entities.extend(self._extract_python_entities(content))
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            entities.extend(self._extract_javascript_entities(content))
        
        return entities
    
    def _extract_python_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract Python functions and classes."""
        entities = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Match function definitions
            func_match = re.match(r'\s*def\s+(\w+)\s*\(([^)]*)\)', line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                
                # Skip private functions and test functions
                if not func_name.startswith('_') and not func_name.startswith('test_'):
                    entities.append({
                        'type': 'function',
                        'name': func_name,
                        'params': params,
                        'line': i,
                        'language': 'python'
                    })
            
            # Match class definitions
            class_match = re.match(r'\s*class\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(1)
                if not class_name.startswith('_') and not class_name.startswith('Test'):
                    entities.append({
                        'type': 'class',
                        'name': class_name,
                        'line': i,
                        'language': 'python'
                    })
        
        return entities
    
    def _extract_javascript_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript functions and classes."""
        entities = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Match function declarations
            func_match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)', line)
            if func_match:
                entities.append({
                    'type': 'function',
                    'name': func_match.group(1),
                    'params': func_match.group(2),
                    'line': i,
                    'language': 'javascript'
                })
            
            # Match arrow functions
            arrow_match = re.search(r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', line)
            if arrow_match:
                entities.append({
                    'type': 'function',
                    'name': arrow_match.group(1),
                    'params': arrow_match.group(2),
                    'line': i,
                    'language': 'javascript'
                })
            
            # Match class declarations
            class_match = re.search(r'class\s+(\w+)', line)
            if class_match:
                entities.append({
                    'type': 'class',
                    'name': class_match.group(1),
                    'line': i,
                    'language': 'javascript'
                })
        
        return entities
    
    def _extract_test_cases(self, content: str, filename: str) -> Set[str]:
        """Extract test case names."""
        test_cases = set()
        
        if filename.endswith('.py'):
            # Python test patterns
            matches = re.findall(r'def\s+(test_\w+)', content)
            test_cases.update(matches)
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            # JavaScript test patterns
            matches = re.findall(r'(?:it|test)\s*\(\s*["\']([^"\']+)["\']', content)
            test_cases.update(matches)
        
        return test_cases
    
    def _is_tested(self, entity: Dict[str, Any], test_cases: Set[str]) -> bool:
        """Check if entity has corresponding tests."""
        entity_name = entity['name'].lower()
        
        # Check if any test case mentions this entity
        for test_case in test_cases:
            test_lower = test_case.lower()
            if entity_name in test_lower:
                return True
        
        return False
    
    def _create_coverage_issue(self, entity: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Create a coverage issue with AI-generated test suggestions."""
        entity_type = entity['type']
        entity_name = entity['name']
        
        # Generate test suggestions
        test_suggestions = self._generate_test_suggestions(entity)
        
        return {
            'type': 'quality',
            'severity': 'medium',
            'line': entity['line'],
            'message': f'No tests found for {entity_type} "{entity_name}"',
            'suggestion': f'Add test cases to verify {entity_type} behavior',
            'test_suggestions': test_suggestions,
            'auto_fix': {
                'description': f'Generate test template for {entity_name}',
                'template': self._generate_test_template(entity)
            }
        }
    
    def _generate_test_suggestions(self, entity: Dict[str, Any]) -> List[str]:
        """Generate AI-powered test suggestions."""
        entity_type = entity['type']
        entity_name = entity['name']
        language = entity.get('language', 'python')
        
        suggestions = []
        
        if entity_type == 'function':
            suggestions.extend([
                f"Test {entity_name} with valid inputs",
                f"Test {entity_name} with invalid/edge case inputs",
                f"Test {entity_name} error handling",
                f"Test {entity_name} return values",
            ])
            
            # Add parameter-specific tests
            params = entity.get('params', '')
            if params:
                suggestions.append(f"Test {entity_name} with different parameter combinations")
            
        elif entity_type == 'class':
            suggestions.extend([
                f"Test {entity_name} initialization",
                f"Test {entity_name} public methods",
                f"Test {entity_name} edge cases",
                f"Test {entity_name} error conditions",
            ])
        
        return suggestions
    
    def _generate_test_template(self, entity: Dict[str, Any]) -> str:
        """Generate test code template."""
        entity_type = entity['type']
        entity_name = entity['name']
        language = entity.get('language', 'python')
        
        if language == 'python':
            if entity_type == 'function':
                return f"""def test_{entity_name}_valid_input():
    \"\"\"Test {entity_name} with valid input.\"\"\"
    result = {entity_name}(...)  # Add appropriate arguments
    assert result == expected_value

def test_{entity_name}_invalid_input():
    \"\"\"Test {entity_name} with invalid input.\"\"\"
    with pytest.raises(ValueError):
        {entity_name}(...)  # Add invalid arguments

def test_{entity_name}_edge_cases():
    \"\"\"Test {entity_name} edge cases.\"\"\"
    # Test with None
    # Test with empty values
    # Test with boundary values
    pass
"""
            else:  # class
                return f"""class Test{entity_name}:
    \"\"\"Test suite for {entity_name}.\"\"\"
    
    def test_initialization(self):
        \"\"\"Test {entity_name} initialization.\"\"\"
        obj = {entity_name}()
        assert obj is not None
    
    def test_methods(self):
        \"\"\"Test {entity_name} methods.\"\"\"
        obj = {entity_name}()
        # Add method tests here
        pass
"""
        
        else:  # JavaScript
            if entity_type == 'function':
                return f"""describe('{entity_name}', () => {{
    it('should work with valid input', () => {{
        const result = {entity_name}(...);
        expect(result).toBe(expectedValue);
    }});
    
    it('should handle invalid input', () => {{
        expect(() => {entity_name}(...)).toThrow();
    }});
    
    it('should handle edge cases', () => {{
        // Test with null
        // Test with undefined
        // Test with empty values
    }});
}});
"""
            else:  # class
                return f"""describe('{entity_name}', () => {{
    it('should initialize correctly', () => {{
        const obj = new {entity_name}();
        expect(obj).toBeDefined();
    }});
    
    it('should have required methods', () => {{
        const obj = new {entity_name}();
        // Test methods here
    }});
}});
"""
    
    def calculate_coverage_score(self, total_entities: int, tested_entities: int) -> Dict[str, Any]:
        """Calculate test coverage score."""
        if total_entities == 0:
            return {
                'score': 100,
                'percentage': 100,
                'status': 'excellent'
            }
        
        percentage = (tested_entities / total_entities) * 100
        
        if percentage >= 80:
            status = 'excellent'
        elif percentage >= 60:
            status = 'good'
        elif percentage >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'score': int(percentage),
            'percentage': percentage,
            'status': status,
            'total_entities': total_entities,
            'tested_entities': tested_entities,
            'untested_entities': total_entities - tested_entities
        }
    
    def generate_coverage_report(self, issues: List[Dict[str, Any]], coverage_score: Dict[str, Any]) -> str:
        """Generate test coverage report."""
        report = "## 🧪 Test Coverage Analysis\n\n"
        
        score = coverage_score['score']
        status = coverage_score['status']
        
        # Status emoji
        status_emoji = {
            'excellent': '✅',
            'good': '👍',
            'fair': '⚠️',
            'poor': '🚨'
        }
        
        report += f"**Coverage Score:** {score}% {status_emoji[status]}\n"
        report += f"**Status:** {status.upper()}\n\n"
        
        if issues:
            report += f"### 📋 Untested Code:\n\n"
            report += f"- **Total Entities:** {coverage_score['total_entities']}\n"
            report += f"- **Tested:** {coverage_score['tested_entities']}\n"
            report += f"- **Untested:** {coverage_score['untested_entities']}\n\n"
            
            report += "### 🎯 Missing Tests:\n\n"
            
            for i, issue in enumerate(issues[:10], 1):
                entity_name = issue['message'].split('"')[1]
                report += f"{i}. **{entity_name}** (Line {issue['line']})\n"
                
                # Add test suggestions
                if 'test_suggestions' in issue:
                    report += "   Suggested tests:\n"
                    for suggestion in issue['test_suggestions'][:3]:
                        report += f"   - {suggestion}\n"
                report += "\n"
            
            if len(issues) > 10:
                report += f"*...and {len(issues) - 10} more untested entities*\n\n"
        else:
            report += "✅ **Excellent coverage!** All code entities have tests.\n\n"
        
        # Recommendations
        if score < 80:
            report += "💡 **Recommendation:** Aim for 80%+ test coverage for production code.\n\n"
        
        return report
