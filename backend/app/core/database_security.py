"""
Database security utilities and middleware.
"""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query


class SQLInjectionProtection:
    """SQL injection protection utilities."""
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION)\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bOR\b.*=.*\bOR\b)",
        r"(\bAND\b.*=.*\bAND\b)",
        r"(1=1|1 = 1)",
        r"(\;)\s*(\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(\bxp_\w+)",
        r"(\bsp_\w+)",
    ]
    
    @classmethod
    def sanitize_input(cls, input_string: str) -> str:
        """
        Sanitize input string to prevent SQL injection.
        
        Args:
            input_string: Input string to sanitize
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If potentially dangerous content detected
        """
        if not isinstance(input_string, str):
            return input_string
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                raise ValueError("Input contains potentially dangerous SQL content")
        
        # Remove null bytes
        input_string = input_string.replace('\x00', '')
        
        # Escape quotes
        input_string = input_string.replace("'", "''")
        
        return input_string.strip()
    
    @classmethod
    def validate_table_name(cls, table_name: str) -> bool:
        """
        Validate table name to prevent SQL injection.
        
        Args:
            table_name: Table name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Only allow alphanumeric characters and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(pattern, table_name) is not None
    
    @classmethod
    def validate_column_name(cls, column_name: str) -> bool:
        """
        Validate column name to prevent SQL injection.
        
        Args:
            column_name: Column name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Only allow alphanumeric characters and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(pattern, column_name) is not None
    
    @classmethod
    def validate_order_by(cls, order_by: str, allowed_columns: List[str]) -> bool:
        """
        Validate ORDER BY clause.
        
        Args:
            order_by: Order by string (e.g., "name ASC", "created_at DESC")
            allowed_columns: List of allowed column names
            
        Returns:
            True if valid, False otherwise
        """
        if not order_by:
            return True
        
        parts = order_by.split()
        if len(parts) > 2:
            return False
        
        column = parts[0].strip()
        direction = parts[1].strip().upper() if len(parts) > 1 else "ASC"
        
        if direction not in ["ASC", "DESC"]:
            return False
        
        return column in allowed_columns


class QueryBuilder:
    """Safe query builder with parameterized queries."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.params: Dict[str, Any] = {}
        self.where_clauses: List[str] = []
        self.order_by: Optional[str] = None
        self.limit_val: Optional[int] = None
        self.offset_val: Optional[int] = None
    
    def table(self, table_name: str) -> 'QueryBuilder':
        """Set table name with validation."""
        if not SQLInjectionProtection.validate_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        self.table_name = table_name
        return self
    
    def where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        """Add WHERE clause with parameterized query."""
        if not SQLInjectionProtection.validate_column_name(column):
            raise ValueError(f"Invalid column name: {column}")
        
        if operator not in ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "NOT IN"]:
            raise ValueError(f"Invalid operator: {operator}")
        
        param_name = f"param_{len(self.params)}"
        self.params[param_name] = value
        
        if operator in ["IN", "NOT IN"]:
            self.where_clauses.append(f"{column} {operator} (:{param_name})")
        else:
            self.where_clauses.append(f"{column} {operator} :{param_name}")
        
        return self
    
    def order(self, column: str, direction: str = "ASC") -> 'QueryBuilder':
        """Add ORDER BY clause."""
        if not SQLInjectionProtection.validate_column_name(column):
            raise ValueError(f"Invalid column name: {column}")
        
        if direction.upper() not in ["ASC", "DESC"]:
            raise ValueError(f"Invalid direction: {direction}")
        
        self.order_by = f"{column} {direction.upper()}"
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        if not isinstance(limit, int) or limit < 0 or limit > 1000:
            raise ValueError("Limit must be between 0 and 1000")
        self.limit_val = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("Offset must be a non-negative integer")
        self.offset_val = offset
        return self
    
    def build(self) -> tuple:
        """Build and return query string and parameters."""
        query_parts = [f"SELECT * FROM {self.table_name}"]
        
        if self.where_clauses:
            query_parts.append("WHERE " + " AND ".join(self.where_clauses))
        
        if self.order_by:
            query_parts.append(f"ORDER BY {self.order_by}")
        
        if self.limit_val:
            query_parts.append(f"LIMIT {self.limit_val}")
        
        if self.offset_val:
            query_parts.append(f"OFFSET {self.offset_val}")
        
        query = " ".join(query_parts)
        return query, self.params
    
    async def execute(self):
        """Execute the built query."""
        query, params = self.build()
        result = await self.session.execute(text(query), params)
        return result.fetchall()


class DataEncryption:
    """Data encryption utilities."""
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Encrypted data
        """
        # Simple encryption using XOR (for production, use proper encryption)
        key_bytes = key.encode()
        data_bytes = data.encode()
        encrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
        return encrypted.hex()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data (hex string)
            key: Encryption key
            
        Returns:
            Decrypted data
        """
        key_bytes = key.encode()
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted_bytes)])
        return decrypted.decode()
    
    @staticmethod
    def hash_data(data: str) -> str:
        """
        Hash data using SHA-256.
        
        Args:
            data: Data to hash
            
        Returns:
            Hashed data
        """
        return hashlib.sha256(data.encode()).hexdigest()


class DataValidation:
    """Data validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?[\d\s-]{10,}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_ipv4(ip: str) -> bool:
        """Validate IPv4 address."""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        pattern = r'^[a-zA-Z0-9_-]{3,20}$'
        return re.match(pattern, username) is not None


class DatabaseSecurityManager:
    """Comprehensive database security manager."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sql_protection = SQLInjectionProtection()
        self.query_builder = QueryBuilder(session)
        self.encryption = DataEncryption()
        self.validation = DataValidation()
    
    def create_safe_query(self) -> QueryBuilder:
        """Create a safe query builder."""
        return QueryBuilder(self.session)
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize input string."""
        return self.sql_protection.sanitize_input(input_string)
    
    def validate_input(self, input_type: str, value: Any) -> bool:
        """Validate input based on type."""
        validators = {
            'email': self.validation.validate_email,
            'phone': self.validation.validate_phone,
            'url': self.validation.validate_url,
            'ipv4': self.validation.validate_ipv4,
            'username': self.validation.validate_username,
        }
        
        validator = validators.get(input_type)
        if validator:
            return validator(str(value))
        return True
    
    def encrypt_sensitive_field(self, data: str, encryption_key: str) -> str:
        """Encrypt sensitive field."""
        return self.encryption.encrypt_sensitive_data(data, encryption_key)
    
    def decrypt_sensitive_field(self, encrypted_data: str, encryption_key: str) -> str:
        """Decrypt sensitive field."""
        return self.encryption.decrypt_sensitive_data(encrypted_data, encryption_key)
    
    def hash_sensitive_field(self, data: str) -> str:
        """Hash sensitive field."""
        return self.encryption.hash_data(data)


__all__ = [
    "SQLInjectionProtection",
    "QueryBuilder",
    "DataEncryption",
    "DataValidation",
    "DatabaseSecurityManager",
]