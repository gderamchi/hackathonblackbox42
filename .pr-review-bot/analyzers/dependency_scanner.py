"""
Dependency vulnerability scanner.
Scans package dependencies for known security vulnerabilities.
"""

import re
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DependencyScanner:
    """Scans dependencies for known vulnerabilities."""
    
    def __init__(self):
        """Initialize dependency scanner."""
        self.osv_api_url = "https://api.osv.dev/v1/query"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def scan_file(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        Scan a dependency file for vulnerabilities.
        
        Args:
            filename: Name of the dependency file
            content: File content
            
        Returns:
            List of vulnerabilities found
        """
        vulnerabilities = []
        
        # Detect file type and parse dependencies
        if filename == "requirements.txt" or filename.endswith("requirements.txt"):
            deps = self._parse_requirements_txt(content)
            vulnerabilities.extend(self._scan_python_dependencies(deps))
        
        elif filename == "package.json":
            deps = self._parse_package_json(content)
            vulnerabilities.extend(self._scan_npm_dependencies(deps))
        
        elif filename == "Pipfile" or filename == "Pipfile.lock":
            deps = self._parse_pipfile(content)
            vulnerabilities.extend(self._scan_python_dependencies(deps))
        
        elif filename == "pom.xml":
            deps = self._parse_pom_xml(content)
            vulnerabilities.extend(self._scan_maven_dependencies(deps))
        
        elif filename == "go.mod":
            deps = self._parse_go_mod(content)
            vulnerabilities.extend(self._scan_go_dependencies(deps))
        
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities in {filename}")
        return vulnerabilities
    
    def _parse_requirements_txt(self, content: str) -> List[Dict[str, str]]:
        """Parse Python requirements.txt file."""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse package==version or package>=version
            match = re.match(r'^([a-zA-Z0-9_-]+)\s*([=<>!]+)\s*([0-9.]+)', line)
            if match:
                package = match.group(1)
                version = match.group(3)
                dependencies.append({
                    'name': package,
                    'version': version,
                    'ecosystem': 'PyPI'
                })
        
        return dependencies
    
    def _parse_package_json(self, content: str) -> List[Dict[str, str]]:
        """Parse Node.js package.json file."""
        dependencies = []
        
        try:
            data = json.loads(content)
            
            # Parse dependencies
            for dep_type in ['dependencies', 'devDependencies']:
                deps = data.get(dep_type, {})
                for name, version in deps.items():
                    # Remove ^ or ~ prefix
                    clean_version = version.lstrip('^~')
                    dependencies.append({
                        'name': name,
                        'version': clean_version,
                        'ecosystem': 'npm'
                    })
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing package.json: {e}")
        
        return dependencies
    
    def _parse_pipfile(self, content: str) -> List[Dict[str, str]]:
        """Parse Python Pipfile."""
        dependencies = []
        
        # Basic TOML parsing for Pipfile
        in_packages = False
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[packages]' or line == '[dev-packages]':
                in_packages = True
                continue
            
            if line.startswith('[') and in_packages:
                in_packages = False
            
            if in_packages and '=' in line:
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    package = match.group(1)
                    version = match.group(2).lstrip('=~')
                    dependencies.append({
                        'name': package,
                        'version': version,
                        'ecosystem': 'PyPI'
                    })
        
        return dependencies
    
    def _parse_pom_xml(self, content: str) -> List[Dict[str, str]]:
        """Parse Maven pom.xml file."""
        dependencies = []
        
        # Simple regex-based XML parsing
        dep_pattern = r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>.*?</dependency>'
        matches = re.finditer(dep_pattern, content, re.DOTALL)
        
        for match in matches:
            group_id = match.group(1)
            artifact_id = match.group(2)
            version = match.group(3)
            
            dependencies.append({
                'name': f"{group_id}:{artifact_id}",
                'version': version,
                'ecosystem': 'Maven'
            })
        
        return dependencies
    
    def _parse_go_mod(self, content: str) -> List[Dict[str, str]]:
        """Parse Go go.mod file."""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Match: github.com/package/name v1.2.3
            match = re.match(r'^([a-zA-Z0-9./\-_]+)\s+v([0-9.]+)', line)
            if match:
                package = match.group(1)
                version = match.group(2)
                dependencies.append({
                    'name': package,
                    'version': version,
                    'ecosystem': 'Go'
                })
        
        return dependencies
    
    def _scan_python_dependencies(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan Python dependencies using OSV API."""
        return self._scan_dependencies_osv(dependencies, 'PyPI')
    
    def _scan_npm_dependencies(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan npm dependencies using OSV API."""
        return self._scan_dependencies_osv(dependencies, 'npm')
    
    def _scan_maven_dependencies(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan Maven dependencies using OSV API."""
        return self._scan_dependencies_osv(dependencies, 'Maven')
    
    def _scan_go_dependencies(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan Go dependencies using OSV API."""
        return self._scan_dependencies_osv(dependencies, 'Go')
    
    def _scan_dependencies_osv(self, dependencies: List[Dict[str, str]], ecosystem: str) -> List[Dict[str, Any]]:
        """
        Scan dependencies using OSV (Open Source Vulnerabilities) API.
        
        Args:
            dependencies: List of dependencies to scan
            ecosystem: Package ecosystem (PyPI, npm, Maven, Go)
            
        Returns:
            List of vulnerabilities
        """
        vulnerabilities = []
        
        for dep in dependencies[:20]:  # Limit to 20 to avoid rate limiting
            try:
                # Query OSV API
                payload = {
                    "package": {
                        "name": dep['name'],
                        "ecosystem": ecosystem
                    },
                    "version": dep['version']
                }
                
                response = self.session.post(
                    self.osv_api_url,
                    json=payload,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get('vulns', [])
                    
                    for vuln in vulns:
                        vuln_id = vuln.get('id', 'UNKNOWN')
                        summary = vuln.get('summary', 'No description available')
                        severity = self._extract_severity(vuln)
                        
                        vulnerabilities.append({
                            'type': 'security',
                            'severity': severity,
                            'message': f"Vulnerable dependency: {dep['name']}@{dep['version']}",
                            'suggestion': f"Update to a patched version. Vulnerability: {vuln_id}",
                            'dependency': dep['name'],
                            'current_version': dep['version'],
                            'vulnerability_id': vuln_id,
                            'description': summary,
                            'cwe': self._extract_cwe(vuln),
                            'auto_fix': self._generate_dependency_fix(dep, vuln, ecosystem)
                        })
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout scanning {dep['name']}")
                continue
            except Exception as e:
                logger.error(f"Error scanning {dep['name']}: {e}")
                continue
        
        return vulnerabilities
    
    def _extract_severity(self, vuln: Dict[str, Any]) -> str:
        """Extract severity from vulnerability data."""
        # Check for CVSS score
        severity_data = vuln.get('severity', [])
        if severity_data:
            for sev in severity_data:
                score = sev.get('score')
                if score:
                    # CVSS score to severity mapping
                    if isinstance(score, str) and score.startswith('CVSS:'):
                        # Extract numeric score
                        match = re.search(r'/(\d+\.\d+)', score)
                        if match:
                            score = float(match.group(1))
                    
                    if isinstance(score, (int, float)):
                        if score >= 9.0:
                            return 'critical'
                        elif score >= 7.0:
                            return 'high'
                        elif score >= 4.0:
                            return 'medium'
                        else:
                            return 'low'
        
        # Default to high for vulnerabilities without score
        return 'high'
    
    def _extract_cwe(self, vuln: Dict[str, Any]) -> str:
        """Extract CWE from vulnerability data."""
        # Look for CWE in references or database_specific
        refs = vuln.get('references', [])
        for ref in refs:
            url = ref.get('url', '')
            if 'cwe.mitre.org' in url:
                match = re.search(r'CWE-(\d+)', url)
                if match:
                    return f"CWE-{match.group(1)}"
        
        return "N/A"
    
    def _generate_dependency_fix(self, dep: Dict[str, str], vuln: Dict[str, Any], ecosystem: str) -> Optional[Dict[str, str]]:
        """Generate auto-fix for vulnerable dependency."""
        # Extract fixed versions from vulnerability data
        affected = vuln.get('affected', [])
        if not affected:
            return None
        
        for pkg in affected:
            ranges = pkg.get('ranges', [])
            for range_data in ranges:
                events = range_data.get('events', [])
                
                # Find the fixed version
                for event in events:
                    if 'fixed' in event:
                        fixed_version = event['fixed']
                        
                        # Generate fix based on ecosystem
                        if ecosystem == 'PyPI':
                            original = f"{dep['name']}=={dep['version']}"
                            fixed = f"{dep['name']}=={fixed_version}"
                        elif ecosystem == 'npm':
                            original = f'"{dep["name"]}": "{dep["version"]}"'
                            fixed = f'"{dep["name"]}": "{fixed_version}"'
                        else:
                            original = f"{dep['name']}@{dep['version']}"
                            fixed = f"{dep['name']}@{fixed_version}"
                        
                        return {
                            'original': original,
                            'fixed': fixed,
                            'description': f"Update {dep['name']} to {fixed_version} (fixes {vuln.get('id', 'vulnerability')})"
                        }
        
        return None
    
    def generate_dependency_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """
        Generate a dependency vulnerability report.
        
        Args:
            vulnerabilities: List of vulnerabilities
            
        Returns:
            Formatted report
        """
        if not vulnerabilities:
            return "✅ No vulnerable dependencies detected."
        
        report = "## 📦 Dependency Vulnerability Scan\n\n"
        
        # Group by severity
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        severity
_order = ['critical', 'high', 'medium', 'low']
        for severity in severity_order:
            if severity in by_severity:
                count = len(by_severity[severity])
                emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}
                report += f"{emoji[severity]} **{severity.upper()}**: {count} vulnerable package(s)\n"
        
        report += "\n### 📋 Vulnerable Packages:\n\n"
        
        for vuln in vulnerabilities[:10]:  # Show top 10
            dep = vuln['dependency']
            version = vuln['current_version']
            vuln_id = vuln['vulnerability_id']
            severity = vuln['severity']
            emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}
            
            report += f"- {emoji[severity]} **{dep}@{version}** - {vuln_id}\n"
            report += f"  - {vuln['description'][:100]}...\n"
            
            if vuln.get('auto_fix'):
                fix = vuln['auto_fix']
                report += f"  - 🔧 Fix: Update to `{fix['fixed']}`\n"
            
            report += "\n"
        
        if len(vulnerabilities) > 10:
            report += f"*...and {len(vulnerabilities) - 10} more vulnerabilities*\n\n"
        
        report += "💡 **Recommendation:** Update vulnerable dependencies to patched versions.\n\n"
        
        return report
