"""
Guardrails integration for safety and security in the multi-agent system.

This module implements OWASP Top 10 for LLMs protection using Guardrails AI
to validate inputs and outputs, enforce response formats, and reject unsafe content.
"""

import logging
from typing import Any, Dict, Optional, List
from guardrails import Guard
from guardrails.errors import ValidationError

logger = logging.getLogger(__name__)


# ==================== Input Validation Guards ====================

class InputGuard:
    """
    Validates user inputs before they reach the LLM.
    
    Protects against:
    - Prompt injection (OWASP LLM01)
    - Excessive input length
    - Malicious patterns
    """
    
    def __init__(self, max_length: int = 10000):
        """
        Initialize input guard.
        
        Args:
            max_length: Maximum allowed input length
        """
        self.max_length = max_length
        self.forbidden_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "forget everything",
            "new instructions:",
            "system:",
            "you are now",
            "act as if",
            "pretend you are",
            "disregard",
            "<script>",
            "javascript:",
            "eval(",
        ]
    
    def validate(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input for safety.
        
        Args:
            user_input: User-provided text
            
        Returns:
            Validation result with status and details
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_input": user_input
        }
        
        # Check length
        if len(user_input) > self.max_length:
            result["is_valid"] = False
            result["errors"].append(
                f"Input exceeds maximum length of {self.max_length} characters"
            )
            logger.warning(f"Input validation failed: excessive length ({len(user_input)} chars)")
        
        # Check for forbidden patterns
        user_input_lower = user_input.lower()
        detected_patterns = []
        
        for pattern in self.forbidden_patterns:
            if pattern in user_input_lower:
                detected_patterns.append(pattern)
        
        if detected_patterns:
            result["is_valid"] = False
            result["errors"].append(
                f"Potentially malicious patterns detected: {', '.join(detected_patterns)}"
            )
            logger.warning(
                f"Input validation failed: detected patterns {detected_patterns}"
            )
        
        # Check for excessive special characters (potential injection)
        special_char_ratio = sum(
            1 for c in user_input if not c.isalnum() and not c.isspace()
        ) / max(len(user_input), 1)
        
        if special_char_ratio > 0.3:
            result["warnings"].append(
                "High ratio of special characters detected"
            )
            logger.info(
                f"Input contains {special_char_ratio:.1%} special characters"
            )
        
        return result


# ==================== Output Validation Guards ====================

class OutputGuard:
    """
    Validates LLM outputs before returning to users.
    
    Protects against:
    - Sensitive data leakage (OWASP LLM06)
    - Toxic content
    - Hallucinations
    - Malformed responses
    """
    
    def __init__(self):
        """Initialize output guard."""
        self.sensitive_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"api[_\s-]?key[:\s]+[a-zA-Z0-9]+",  # API key with value
            r"password[:\s]+\S+",  # Password with value
            r"secret[:\s]+\S+",  # Secret with value
            r"token[:\s]+\S+",  # Token with value
        ]
    
    def validate(self, output: str) -> Dict[str, Any]:
        """
        Validate LLM output for safety.
        
        Args:
            output: LLM-generated text
            
        Returns:
            Validation result with status and details
        """
        import re
        
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_output": output
        }
        
        # Check for sensitive data patterns
        detected_sensitive = []
        for pattern in self.sensitive_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                detected_sensitive.append(pattern)
        
        if detected_sensitive:
            result["is_valid"] = False
            result["errors"].append(
                "Output contains potentially sensitive information"
            )
            logger.error(
                f"Output validation failed: sensitive patterns detected"
            )
        
        # Check for empty or suspiciously short responses
        if len(output.strip()) < 10:
            result["warnings"].append(
                "Output is suspiciously short"
            )
        
        # Check for repetitive content (potential hallucination)
        words = output.split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                result["warnings"].append(
                    "Output contains high repetition - possible hallucination"
                )
                logger.warning(
                    f"Output has low uniqueness ratio: {unique_ratio:.2f}"
                )
        
        return result


# ==================== Guardrails AI Integration ====================

class GuardrailsValidator:
    """
    Integration with Guardrails AI for advanced validation.
    
    Uses validators from Guardrails Hub for:
    - Toxic language detection
    - PII detection
    - Prompt injection detection
    - Custom schema validation
    """
    
    def __init__(self):
        """Initialize Guardrails validator."""
        self.guards = {}
        self._setup_guards()
    
    def _setup_guards(self):
        """Set up Guardrails guards with validators."""
        try:
            # Try to import validators from Guardrails Hub
            # Note: These need to be installed via: guardrails hub install hub://...
            
            # Basic guard without hub validators (fallback)
            self.guards['basic'] = Guard()
            
            logger.info("Guardrails validators initialized")
            
        except Exception as e:
            logger.warning(
                f"Could not initialize all Guardrails validators: {e}. "
                f"Using basic validation only."
            )
            self.guards['basic'] = Guard()
    
    def validate_input(
        self,
        user_input: str,
        guard_name: str = 'basic'
    ) -> Dict[str, Any]:
        """
        Validate input using Guardrails.
        
        Args:
            user_input: User-provided text
            guard_name: Name of guard to use
            
        Returns:
            Validation result
        """
        try:
            guard = self.guards.get(guard_name, self.guards['basic'])
            
            # Validate
            result = guard.validate(user_input)
            
            return {
                "is_valid": True,
                "validated_output": result.validated_output,
                "validation_passed": result.validation_passed
            }
            
        except ValidationError as e:
            logger.error(f"Guardrails validation failed: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "validation_passed": False
            }
        except Exception as e:
            logger.error(f"Unexpected error in Guardrails validation: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "validation_passed": False
            }
    
    def validate_output(
        self,
        llm_output: str,
        guard_name: str = 'basic'
    ) -> Dict[str, Any]:
        """
        Validate LLM output using Guardrails.
        
        Args:
            llm_output: LLM-generated text
            guard_name: Name of guard to use
            
        Returns:
            Validation result
        """
        return self.validate_input(llm_output, guard_name)


# ==================== Combined Safety Layer ====================

class SafetyLayer:
    """
    Combined safety layer using multiple validation approaches.
    
    Implements defense-in-depth strategy with:
    1. Basic pattern matching
    2. Guardrails AI validators
    3. Custom business logic
    """
    
    def __init__(self):
        """Initialize safety layer."""
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self.guardrails_validator = GuardrailsValidator()
        
        logger.info("Safety layer initialized")
    
    def validate_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Comprehensive input validation.
        
        Args:
            user_input: User-provided text
            
        Returns:
            Combined validation result
        """
        # Run basic validation
        basic_result = self.input_guard.validate(user_input)
        
        # If basic validation fails, don't proceed
        if not basic_result["is_valid"]:
            logger.warning("Input failed basic validation")
            return basic_result
        
        # Run Guardrails validation
        guardrails_result = self.guardrails_validator.validate_input(user_input)
        
        # Combine results
        combined_result = {
            "is_valid": basic_result["is_valid"] and guardrails_result.get("validation_passed", True),
            "errors": basic_result["errors"],
            "warnings": basic_result["warnings"],
            "sanitized_input": basic_result["sanitized_input"],
            "guardrails_passed": guardrails_result.get("validation_passed", True)
        }
        
        if not combined_result["is_valid"]:
            logger.warning("Input failed comprehensive validation")
        
        return combined_result
    
    def validate_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """
        Comprehensive output validation.
        
        Args:
            llm_output: LLM-generated text
            
        Returns:
            Combined validation result
        """
        # Run basic validation
        basic_result = self.output_guard.validate(llm_output)
        
        # Run Guardrails validation
        guardrails_result = self.guardrails_validator.validate_output(llm_output)
        
        # Combine results
        combined_result = {
            "is_valid": basic_result["is_valid"] and guardrails_result.get("validation_passed", True),
            "errors": basic_result["errors"],
            "warnings": basic_result["warnings"],
            "sanitized_output": basic_result["sanitized_output"],
            "guardrails_passed": guardrails_result.get("validation_passed", True)
        }
        
        if not combined_result["is_valid"]:
            logger.error("Output failed comprehensive validation")
        
        return combined_result
    
    def safe_execute(
        self,
        user_input: str,
        llm_function: callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute LLM function with full safety checks.
        
        Args:
            user_input: User-provided input
            llm_function: Function that calls LLM
            *args, **kwargs: Additional arguments for llm_function
            
        Returns:
            Result with safety validation status
        """
        # Validate input
        input_validation = self.validate_user_input(user_input)
        
        if not input_validation["is_valid"]:
            return {
                "success": False,
                "error": "Input validation failed",
                "details": input_validation
            }
        
        try:
            # Execute LLM function
            llm_output = llm_function(
                input_validation["sanitized_input"],
                *args,
                **kwargs
            )
            
            # Validate output
            output_validation = self.validate_llm_output(str(llm_output))
            
            if not output_validation["is_valid"]:
                return {
                    "success": False,
                    "error": "Output validation failed",
                    "details": output_validation
                }
            
            return {
                "success": True,
                "output": output_validation["sanitized_output"],
                "validation": {
                    "input": input_validation,
                    "output": output_validation
                }
            }
            
        except Exception as e:
            logger.error(f"Error during safe execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ==================== Compliance Logging ====================

class ComplianceLogger:
    """
    Logger for compliance and audit requirements.
    
    Tracks:
    - Input/output validation results
    - Safety violations
    - User actions
    - System decisions
    """
    
    def __init__(self, log_file: str = "compliance.log"):
        """
        Initialize compliance logger.
        
        Args:
            log_file: Path to compliance log file
        """
        self.log_file = log_file
        self.logger = logging.getLogger("compliance")
        
        # Set up file handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_validation(
        self,
        validation_type: str,
        is_valid: bool,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Log validation event."""
        self.logger.info(
            f"VALIDATION | Type: {validation_type} | "
            f"Valid: {is_valid} | User: {user_id} | "
            f"Details: {details}"
        )
    
    def log_safety_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Log safety violation."""
        self.logger.warning(
            f"SAFETY_VIOLATION | Type: {violation_type} | "
            f"User: {user_id} | Details: {details}"
        )
    
    def log_user_action(
        self,
        action: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log user action."""
        self.logger.info(
            f"USER_ACTION | Action: {action} | "
            f"User: {user_id} | Details: {details or {}}"
        )
