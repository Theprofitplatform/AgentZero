"""
Code Agent for AgentZero
Specialized in code generation, analysis, refactoring, and optimization
"""

import ast
import asyncio
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import tempfile
import json

import sys
sys.path.append('/home/avi/projects/agentzero')
from src.core.agent import BaseAgent, Task, AgentCapability


class CodeAgent(BaseAgent):
    """
    Agent specialized in code generation and analysis
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "CodeAgent", config)
        
        # Code-specific configuration
        self.supported_languages = config.get("languages", [
            "python", "javascript", "typescript", "java", "cpp", "go", "rust"
        ]) if config else ["python", "javascript"]
        
        self.code_templates = {}
        self.code_patterns = {}
        self.optimization_rules = []
        
        # Initialize code capabilities
        self._register_code_capabilities()
        self._load_code_templates()
    
    def _register_code_capabilities(self):
        """Register code-specific capabilities"""
        self.register_capability(AgentCapability(
            name="generate_code",
            description="Generate code based on requirements",
            handler=self._generate_code
        ))
        
        self.register_capability(AgentCapability(
            name="analyze_code",
            description="Analyze code for issues and improvements",
            handler=self._analyze_code
        ))
        
        self.register_capability(AgentCapability(
            name="refactor_code",
            description="Refactor code for better structure",
            handler=self._refactor_code
        ))
        
        self.register_capability(AgentCapability(
            name="optimize_code",
            description="Optimize code for performance",
            handler=self._optimize_code
        ))
        
        self.register_capability(AgentCapability(
            name="debug_code",
            description="Debug and fix code issues",
            handler=self._debug_code
        ))
        
        self.register_capability(AgentCapability(
            name="test_generation",
            description="Generate unit tests for code",
            handler=self._generate_tests
        ))
    
    def _load_code_templates(self):
        """Load code generation templates"""
        self.code_templates = {
            "python": {
                "class": """class {name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self{params}):
        {init_body}
    
    {methods}""",
                "function": """def {name}({params}){return_type}:
    \"\"\"
    {description}
    
    Args:
        {args_doc}
    
    Returns:
        {returns_doc}
    \"\"\"
    {body}""",
                "async_function": """async def {name}({params}){return_type}:
    \"\"\"
    {description}
    \"\"\"
    {body}"""
            },
            "javascript": {
                "class": """class {name} {{
    /**
     * {description}
     */
    constructor({params}) {{
        {init_body}
    }}
    
    {methods}
}}""",
                "function": """/**
 * {description}
 * @param {params_doc}
 * @returns {returns_doc}
 */
function {name}({params}) {{
    {body}
}}""",
                "async_function": """async function {name}({params}) {{
    {body}
}}"""
            }
        }
    
    async def execute(self, task: Task) -> Any:
        """
        Execute code-related task
        
        Args:
            task: Code task to execute
            
        Returns:
            Task result
        """
        self.logger.info(f"Executing code task: {task.name}")
        
        task_type = task.parameters.get("type", "generate")
        
        if task_type == "generate":
            return await self._generate_code(task.parameters)
        elif task_type == "analyze":
            return await self._analyze_code(task.parameters)
        elif task_type == "refactor":
            return await self._refactor_code(task.parameters)
        elif task_type == "optimize":
            return await self._optimize_code(task.parameters)
        elif task_type == "debug":
            return await self._debug_code(task.parameters)
        elif task_type == "test":
            return await self._generate_tests(task.parameters)
        else:
            return await self._generate_code(task.parameters)
    
    async def _generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications"""
        language = params.get("language", "python")
        code_type = params.get("code_type", "function")
        specifications = params.get("specifications", {})
        
        self.logger.info(f"Generating {language} {code_type}")
        
        # Generate based on specifications
        if code_type == "api":
            code = self._generate_api(language, specifications)
        elif code_type == "cli":
            code = self._generate_cli(language, specifications)
        elif code_type == "class":
            code = self._generate_class(language, specifications)
        elif code_type == "function":
            code = self._generate_function(language, specifications)
        elif code_type == "module":
            code = self._generate_module(language, specifications)
        else:
            code = self._generate_generic(language, specifications)
        
        # Validate generated code
        is_valid, errors = await self._validate_code(code, language)
        
        return {
            "code": code,
            "language": language,
            "type": code_type,
            "valid": is_valid,
            "errors": errors,
            "specifications": specifications
        }
    
    def _generate_api(self, language: str, specs: Dict) -> str:
        """Generate API code"""
        if language == "python":
            return self._generate_python_api(specs)
        elif language == "javascript":
            return self._generate_javascript_api(specs)
        else:
            return f"# API generation not supported for {language}"
    
    def _generate_python_api(self, specs: Dict) -> str:
        """Generate Python FastAPI code"""
        api_name = specs.get("name", "MyAPI")
        endpoints = specs.get("endpoints", [])
        
        code = f"""from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="{api_name}")

# Data Models
"""
        
        # Generate models
        for model in specs.get("models", []):
            code += f"""
class {model['name']}(BaseModel):
"""
            for field in model.get("fields", []):
                field_type = field.get("type", "str")
                required = field.get("required", True)
                if required:
                    code += f"    {field['name']}: {field_type}\n"
                else:
                    code += f"    {field['name']}: Optional[{field_type}] = None\n"
        
        # Generate endpoints
        code += "\n# API Endpoints\n"
        for endpoint in endpoints:
            method = endpoint.get("method", "GET").lower()
            path = endpoint.get("path", "/")
            name = endpoint.get("name", "endpoint")
            
            if method == "get":
                code += f"""
@app.get("{path}")
async def {name}():
    \"\"\"
    {endpoint.get('description', '')}
    \"\"\"
    return {{"message": "Success"}}
"""
            elif method == "post":
                code += f"""
@app.post("{path}")
async def {name}(data: dict):
    \"\"\"
    {endpoint.get('description', '')}
    \"\"\"
    return {{"message": "Created", "data": data}}
"""
        
        code += """
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        return code
    
    def _generate_javascript_api(self, specs: Dict) -> str:
        """Generate Express.js API code"""
        api_name = specs.get("name", "MyAPI")
        
        code = f"""const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// API: {api_name}
"""
        
        # Generate endpoints
        for endpoint in specs.get("endpoints", []):
            method = endpoint.get("method", "GET").lower()
            path = endpoint.get("path", "/")
            
            code += f"""
app.{method}('{path}', (req, res) => {{
    // {endpoint.get('description', '')}
    res.json({{ message: 'Success' }});
}});
"""
        
        code += """
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
"""
        
        return code
    
    def _generate_cli(self, language: str, specs: Dict) -> str:
        """Generate CLI application"""
        if language == "python":
            return self._generate_python_cli(specs)
        else:
            return f"# CLI generation not supported for {language}"
    
    def _generate_python_cli(self, specs: Dict) -> str:
        """Generate Python CLI using argparse"""
        cli_name = specs.get("name", "mycli")
        commands = specs.get("commands", [])
        
        code = f"""#!/usr/bin/env python3
\"\"\"
{specs.get('description', 'CLI Application')}
\"\"\"

import argparse
import sys
import json
from typing import Any, Dict, List

def main():
    parser = argparse.ArgumentParser(
        prog='{cli_name}',
        description='{specs.get('description', '')}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
"""
        
        # Generate commands
        for cmd in commands:
            cmd_name = cmd.get("name", "command")
            code += f"""
    # {cmd_name} command
    {cmd_name}_parser = subparsers.add_parser(
        '{cmd_name}',
        help='{cmd.get('description', '')}'
    )
"""
            
            # Add arguments
            for arg in cmd.get("arguments", []):
                arg_name = arg.get("name", "arg")
                arg_type = arg.get("type", "str")
                required = arg.get("required", False)
                
                if required:
                    code += f"    {cmd_name}_parser.add_argument('{arg_name}', type={arg_type}, help='{arg.get('help', '')}')\n"
                else:
                    code += f"    {cmd_name}_parser.add_argument('--{arg_name}', type={arg_type}, help='{arg.get('help', '')}')\n"
        
        code += """
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
"""
        
        # Generate command handlers
        for cmd in commands:
            cmd_name = cmd.get("name", "command")
            code += f"""
    if args.command == '{cmd_name}':
        handle_{cmd_name}(args)
"""
        
        # Generate handler functions
        for cmd in commands:
            cmd_name = cmd.get("name", "command")
            code += f"""

def handle_{cmd_name}(args):
    \"\"\"Handle {cmd_name} command\"\"\"
    print(f"Executing {cmd_name}")
    # Implementation here
"""
        
        code += """

if __name__ == "__main__":
    main()
"""
        
        return code
    
    def _generate_class(self, language: str, specs: Dict) -> str:
        """Generate class code"""
        template = self.code_templates.get(language, {}).get("class", "")
        
        if not template:
            return f"# Class template not available for {language}"
        
        # Fill template
        name = specs.get("name", "MyClass")
        description = specs.get("description", "Class description")
        methods = specs.get("methods", [])
        properties = specs.get("properties", [])
        
        # Generate parameter list
        params = ", ".join([f", {p['name']}" for p in properties])
        
        # Generate init body
        init_body = "\n        ".join([
            f"self.{p['name']} = {p['name']}" for p in properties
        ]) or "pass"
        
        # Generate methods
        method_code = ""
        for method in methods:
            if language == "python":
                method_code += f"""
    def {method['name']}(self{', '.join([''] + method.get('params', []))}):
        \"\"\"
        {method.get('description', '')}
        \"\"\"
        pass
"""
        
        return template.format(
            name=name,
            description=description,
            params=params,
            init_body=init_body,
            methods=method_code
        )
    
    def _generate_function(self, language: str, specs: Dict) -> str:
        """Generate function code"""
        template = self.code_templates.get(language, {}).get("function", "")
        
        if not template:
            return f"# Function template not available for {language}"
        
        name = specs.get("name", "my_function")
        params = ", ".join(specs.get("parameters", []))
        description = specs.get("description", "Function description")
        body = specs.get("body", "pass" if language == "python" else "// Implementation")
        
        # Type hints for Python
        return_type = ""
        if language == "python" and specs.get("return_type"):
            return_type = f" -> {specs['return_type']}"
        
        return template.format(
            name=name,
            params=params,
            return_type=return_type,
            description=description,
            args_doc="",
            returns_doc=specs.get("return_description", ""),
            body=body
        )
    
    def _generate_module(self, language: str, specs: Dict) -> str:
        """Generate complete module"""
        module_name = specs.get("name", "my_module")
        imports = specs.get("imports", [])
        classes = specs.get("classes", [])
        functions = specs.get("functions", [])
        
        code = f"# Module: {module_name}\n"
        code += f"# {specs.get('description', '')}\n\n"
        
        # Add imports
        for imp in imports:
            code += f"import {imp}\n"
        
        code += "\n"
        
        # Add classes
        for cls in classes:
            code += self._generate_class(language, cls) + "\n\n"
        
        # Add functions
        for func in functions:
            code += self._generate_function(language, func) + "\n\n"
        
        return code
    
    def _generate_generic(self, language: str, specs: Dict) -> str:
        """Generate generic code based on description"""
        description = specs.get("description", "")
        
        if language == "python":
            return f"""# Generated code for: {description}
# TODO: Implement based on specifications

def main():
    \"\"\"Main function\"\"\"
    pass

if __name__ == "__main__":
    main()
"""
        else:
            return f"// Generated code for: {description}\n// TODO: Implement"
    
    async def _analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for various metrics and issues"""
        code = params.get("code", "")
        language = params.get("language", "python")
        
        analysis = {
            "language": language,
            "metrics": {},
            "issues": [],
            "suggestions": []
        }
        
        if language == "python":
            analysis = await self._analyze_python_code(code)
        elif language == "javascript":
            analysis = await self._analyze_javascript_code(code)
        
        # Common analysis
        analysis["metrics"]["lines_of_code"] = len(code.split('\n'))
        analysis["metrics"]["complexity"] = self._calculate_complexity(code)
        
        return analysis
    
    async def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code"""
        analysis = {
            "language": "python",
            "metrics": {},
            "issues": [],
            "suggestions": []
        }
        
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Count elements
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            
            analysis["metrics"]["classes"] = len(classes)
            analysis["metrics"]["functions"] = len(functions)
            
            # Check for issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check function length
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:
                        analysis["issues"].append({
                            "type": "long_function",
                            "message": f"Function '{node.name}' is too long ({func_lines} lines)",
                            "line": node.lineno
                        })
                    
                    # Check for docstring
                    if not ast.get_docstring(node):
                        analysis["suggestions"].append({
                            "type": "missing_docstring",
                            "message": f"Function '{node.name}' lacks docstring",
                            "line": node.lineno
                        })
            
        except SyntaxError as e:
            analysis["issues"].append({
                "type": "syntax_error",
                "message": str(e),
                "line": e.lineno if hasattr(e, 'lineno') else 0
            })
        
        return analysis
    
    async def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code"""
        analysis = {
            "language": "javascript",
            "metrics": {},
            "issues": [],
            "suggestions": []
        }
        
        # Basic analysis
        analysis["metrics"]["functions"] = len(re.findall(r'function\s+\w+', code))
        analysis["metrics"]["arrow_functions"] = len(re.findall(r'=>', code))
        
        # Check for common issues
        if 'var ' in code:
            analysis["suggestions"].append({
                "type": "legacy_var",
                "message": "Consider using 'let' or 'const' instead of 'var'"
            })
        
        if '==' in code and '===' not in code:
            analysis["suggestions"].append({
                "type": "loose_equality",
                "message": "Consider using strict equality (===) instead of loose equality (==)"
            })
        
        return analysis
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simple approximation
        complexity = 1
        
        # Count decision points
        complexity += code.count('if ')
        complexity += code.count('elif ')
        complexity += code.count('else:')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('except ')
        complexity += code.count('case ')
        
        return complexity
    
    async def _refactor_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code for better structure"""
        code = params.get("code", "")
        language = params.get("language", "python")
        refactor_type = params.get("refactor_type", "general")
        
        if refactor_type == "extract_function":
            refactored = self._extract_function(code, params)
        elif refactor_type == "rename":
            refactored = self._rename_variables(code, params)
        elif refactor_type == "simplify":
            refactored = self._simplify_code(code, language)
        else:
            refactored = self._general_refactor(code, language)
        
        return {
            "original": code,
            "refactored": refactored,
            "changes": self._describe_changes(code, refactored)
        }
    
    def _extract_function(self, code: str, params: Dict) -> str:
        """Extract code into function"""
        start_line = params.get("start_line", 0)
        end_line = params.get("end_line", 0)
        function_name = params.get("function_name", "extracted_function")
        
        lines = code.split('\n')
        
        # Extract the specified lines
        extracted = lines[start_line:end_line]
        
        # Create function
        new_function = f"def {function_name}():\n"
        for line in extracted:
            new_function += f"    {line}\n"
        
        # Replace in original code
        refactored = lines[:start_line] + [f"    {function_name}()"] + lines[end_line:]
        refactored.append("")
        refactored.append(new_function)
        
        return '\n'.join(refactored)
    
    def _rename_variables(self, code: str, params: Dict) -> str:
        """Rename variables in code"""
        renames = params.get("renames", {})
        
        refactored = code
        for old_name, new_name in renames.items():
            # Simple rename (should use AST for proper renaming)
            refactored = re.sub(r'\b' + old_name + r'\b', new_name, refactored)
        
        return refactored
    
    def _simplify_code(self, code: str, language: str) -> str:
        """Simplify code structure"""
        if language == "python":
            # Simple simplifications
            code = re.sub(r'if\s+(.+)\s*==\s*True:', r'if \1:', code)
            code = re.sub(r'if\s+(.+)\s*==\s*False:', r'if not \1:', code)
            
        return code
    
    def _general_refactor(self, code: str, language: str) -> str:
        """General refactoring"""
        # Apply common refactoring patterns
        return self._simplify_code(code, language)
    
    def _describe_changes(self, original: str, refactored: str) -> List[str]:
        """Describe changes made during refactoring"""
        changes = []
        
        if len(refactored) < len(original):
            changes.append("Code simplified and reduced in size")
        
        if refactored.count('def ') > original.count('def '):
            changes.append("Extracted new functions")
        
        return changes
    
    async def _optimize_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code for performance"""
        code = params.get("code", "")
        language = params.get("language", "python")
        optimization_level = params.get("level", "standard")
        
        optimized = code
        optimizations_applied = []
        
        if language == "python":
            # Apply Python optimizations
            if "for i in range(len(" in code:
                optimized = re.sub(
                    r'for i in range\(len\((.+?)\)\):',
                    r'for i, _ in enumerate(\1):',
                    optimized
                )
                optimizations_applied.append("Replaced range(len()) with enumerate")
            
            # List comprehension optimization
            if "append(" in code:
                # Detect simple append patterns
                optimizations_applied.append("Consider using list comprehension")
        
        performance_gain = self._estimate_performance_gain(code, optimized)
        
        return {
            "original": code,
            "optimized": optimized,
            "optimizations": optimizations_applied,
            "estimated_gain": performance_gain
        }
    
    def _estimate_performance_gain(self, original: str, optimized: str) -> str:
        """Estimate performance improvement"""
        # Simple heuristic
        if len(optimized) < len(original) * 0.8:
            return "20-30% improvement"
        elif len(optimized) < len(original):
            return "5-10% improvement"
        else:
            return "Marginal improvement"
    
    async def _debug_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Debug and fix code issues"""
        code = params.get("code", "")
        language = params.get("language", "python")
        error = params.get("error", "")
        
        issues_found = []
        fixes_applied = []
        fixed_code = code
        
        # Analyze error
        if error:
            if "NameError" in error:
                # Find undefined variable
                match = re.search(r"name '(\w+)' is not defined", error)
                if match:
                    var_name = match.group(1)
                    issues_found.append(f"Undefined variable: {var_name}")
                    
                    # Simple fix: initialize variable
                    fixed_code = f"{var_name} = None  # Fixed: Initialize variable\n" + fixed_code
                    fixes_applied.append(f"Initialized undefined variable {var_name}")
            
            elif "SyntaxError" in error:
                issues_found.append("Syntax error detected")
                # Try to fix common syntax errors
                fixed_code = self._fix_syntax_errors(fixed_code, language)
                fixes_applied.append("Attempted to fix syntax errors")
        
        # Validate fix
        is_valid, remaining_errors = await self._validate_code(fixed_code, language)
        
        return {
            "original": code,
            "fixed": fixed_code,
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "is_valid": is_valid,
            "remaining_errors": remaining_errors
        }
    
    def _fix_syntax_errors(self, code: str, language: str) -> str:
        """Attempt to fix common syntax errors"""
        if language == "python":
            # Fix missing colons
            code = re.sub(r'(if .+)\n', r'\1:\n', code)
            code = re.sub(r'(for .+)\n', r'\1:\n', code)
            code = re.sub(r'(while .+)\n', r'\1:\n', code)
            code = re.sub(r'(def .+\))\n', r'\1:\n', code)
            
            # Fix indentation (simple approach)
            lines = code.split('\n')
            fixed_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.lstrip()
                if stripped.endswith(':'):
                    fixed_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped in ['pass', 'return', 'break', 'continue']:
                    fixed_lines.append('    ' * max(0, indent_level) + stripped)
                    if indent_level > 0:
                        indent_level -= 1
                else:
                    fixed_lines.append('    ' * indent_level + stripped)
            
            code = '\n'.join(fixed_lines)
        
        return code
    
    async def _generate_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unit tests for code"""
        code = params.get("code", "")
        language = params.get("language", "python")
        framework = params.get("framework", "pytest" if language == "python" else "jest")
        
        # Parse code to find testable units
        testable_units = self._find_testable_units(code, language)
        
        # Generate tests
        tests = self._generate_test_code(testable_units, language, framework)
        
        return {
            "tests": tests,
            "framework": framework,
            "testable_units": len(testable_units),
            "coverage_estimate": self._estimate_coverage(testable_units)
        }
    
    def _find_testable_units(self, code: str, language: str) -> List[Dict]:
        """Find functions/methods that can be tested"""
        units = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        units.append({
                            "name": node.name,
                            "type": "function",
                            "params": [arg.arg for arg in node.args.args],
                            "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node))
                        })
            except:
                pass
        
        return units
    
    def _generate_test_code(self, units: List[Dict], language: str, framework: str) -> str:
        """Generate test code for units"""
        if language == "python" and framework == "pytest":
            tests = "import pytest\n\n"
            
            for unit in units:
                tests += f"""
def test_{unit['name']}():
    \"\"\"Test {unit['name']} function\"\"\"
    # Arrange
    # TODO: Set up test data
    
    # Act
    result = {unit['name']}({', '.join(['None'] * len(unit['params']))})
    
    # Assert
    assert result is not None  # TODO: Add proper assertions

"""
        else:
            tests = "// Generated tests\n"
        
        return tests
    
    def _estimate_coverage(self, units: List[Dict]) -> str:
        """Estimate test coverage"""
        if len(units) == 0:
            return "0%"
        
        # Simple estimate based on number of units
        return f"{min(len(units) * 10, 100)}% (estimated)"
    
    async def _validate_code(self, code: str, language: str) -> Tuple[bool, List[str]]:
        """Validate code syntax"""
        errors = []
        
        if language == "python":
            try:
                ast.parse(code)
                return True, []
            except SyntaxError as e:
                errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
                return False, errors
        
        # For other languages, basic validation
        return True, []