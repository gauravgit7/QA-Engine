import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    history = relationship("TestCaseHistory", back_populates="user", cascade="all, delete-orphan")
    configuration = relationship("Configuration", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class TestCaseHistory(Base):
    __tablename__ = "test_cases_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_type = Column(String(20), nullable=False, index=True)  # UAT, STORY, JIRA
    input_data = Column(Text, nullable=True)
    generated_output = Column(Text, nullable=False)  # JSON stored as text
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Generation metadata
    method_used = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    reviewed = Column(Boolean, default=False)
    token_usage = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    fallback_triggered = Column(Boolean, default=False)

    # Document link
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # Coverage metadata
    domain_detected = Column(String(50), nullable=True)
    total_requirements = Column(Integer, default=0)
    coverage_percentage = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="history")
    document = relationship("Document", back_populates="history_entries")

    def get_output_as_list(self):
        """Parse the stored JSON string into a Python list."""
        try:
            return json.loads(self.generated_output)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f"<TestCaseHistory(id={self.id}, module='{self.module_type}')>"


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    jira_base_url = Column(String(500), nullable=True, default="")
    jira_email = Column(String(255), nullable=True, default="")
    jira_api_token = Column(String(500), nullable=True, default="")
    llm_api_key = Column(String(500), nullable=True, default="")
    ollama_model = Column(String(100), nullable=True, default="dolphin-llama3:latest")

    # User Preferences
    theme = Column(String(50), default="light")
    default_generation_method = Column(String(50), default="llm")

    # Relationships
    user = relationship("User", back_populates="configuration")

    def __repr__(self):
        return f"<Configuration(id={self.id}, user_id={self.user_id})>"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=True)
    domain = Column(String(50), nullable=True)
    word_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    requirement_count = Column(Integer, default=0)
    role_count = Column(Integer, default=0)
    module_count = Column(Integer, default=0)
    parsed_structure = Column(Text, nullable=True)  # JSON
    processing_status = Column(String(50), default="uploaded")  # uploaded, parsed, analyzed, generated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="documents")
    history_entries = relationship("TestCaseHistory", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}')>"
