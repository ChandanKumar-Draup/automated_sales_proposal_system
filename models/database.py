"""SQLAlchemy database models for document editing and user tracking."""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import json

# Create base class for models
Base = declarative_base()


class User(Base):
    """User model for tracking document editors."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to documents
    edited_documents = relationship("EditableDocument", back_populates="last_edited_by_user")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class EditableDocument(Base):
    """Editable document model for storing proposal content with edit history."""
    __tablename__ = 'editable_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    original_content = Column(Text, nullable=True)  # Store original for comparison
    client_name = Column(String(200), nullable=True)
    document_type = Column(String(50), default="proposal")  # proposal, rfp_response

    # Edit tracking
    last_edited_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    last_edited_at = Column(DateTime, nullable=True)
    edit_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    last_edited_by_user = relationship("User", back_populates="edited_documents")

    def to_dict(self):
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "title": self.title,
            "content": self.content,
            "original_content": self.original_content,
            "client_name": self.client_name,
            "document_type": self.document_type,
            "last_edited_by": self.last_edited_by,
            "last_edited_by_user": self.last_edited_by_user.to_dict() if self.last_edited_by_user else None,
            "last_edited_at": self.last_edited_at.isoformat() if self.last_edited_at else None,
            "edit_count": self.edit_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Workflow(Base):
    """Workflow model for tracking RFP and proposal processing state."""
    __tablename__ = 'workflows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    state = Column(String(20), nullable=False, default="created", index=True)
    workflow_type = Column(String(20), nullable=True)  # quick_proposal, rfp_response

    # Client information
    client_name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=True)

    # Step 1: RFP Analysis (stored as JSON)
    rfp_analysis = Column(JSON, nullable=True)  # {questions: [...], sections: [...], total_questions: int}

    # Step 2: Generated Responses (stored as JSON array)
    generated_responses = Column(JSON, nullable=True)  # [{question, answer, sources, confidence}, ...]

    # Step 3: Review Result (stored as JSON)
    review_result = Column(JSON, nullable=True)  # {overall_quality, completeness_score, issues_found}

    # Step 4: Output
    output_file_path = Column(String(500), nullable=True)
    proposal_content = Column(Text, nullable=True)  # For quick proposals

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert workflow to dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "state": self.state,
            "workflow_type": self.workflow_type,
            "client_name": self.client_name,
            "industry": self.industry,
            "file_path": self.file_path,
            "rfp_analysis": self.rfp_analysis,
            "generated_responses": self.generated_responses,
            "review_result": self.review_result,
            "output_file_path": self.output_file_path,
            "proposal_content": self.proposal_content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


# Database connection management
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        # Ensure data directory exists
        os.makedirs("./data", exist_ok=True)

        # Use synchronous SQLite (not aiosqlite)
        database_url = "sqlite:///./data/proposals.db"
        _engine = create_engine(database_url, connect_args={"check_same_thread": False})
    return _engine


def get_session():
    """Get a new database session."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()


def init_database():
    """Initialize database and create tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    # Create default user if not exists
    session = get_session()
    try:
        default_user = session.query(User).filter_by(username="default_user").first()
        if not default_user:
            default_user = User(
                username="default_user",
                display_name="Sales Team User",
                email="sales@company.com"
            )
            session.add(default_user)
            session.commit()
            print("Created default user: Sales Team User")
        else:
            print("Default user already exists")
    except Exception as e:
        session.rollback()
        print(f"Error creating default user: {e}")
    finally:
        session.close()


def get_default_user():
    """Get the default user for document editing."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username="default_user").first()
        return user
    finally:
        session.close()


def save_document(workflow_id: str, title: str, content: str, client_name: str = None,
                  document_type: str = "proposal", user_id: int = None):
    """Save or update an editable document."""
    session = get_session()
    try:
        # Check if document exists
        doc = session.query(EditableDocument).filter_by(workflow_id=workflow_id).first()

        if doc:
            # Update existing document
            doc.content = content
            doc.title = title
            doc.client_name = client_name
            doc.last_edited_by = user_id
            doc.last_edited_at = datetime.utcnow()
            doc.edit_count += 1
        else:
            # Create new document
            doc = EditableDocument(
                workflow_id=workflow_id,
                title=title,
                content=content,
                original_content=content,
                client_name=client_name,
                document_type=document_type,
                last_edited_by=user_id,
                last_edited_at=datetime.utcnow() if user_id else None,
                edit_count=0
            )
            session.add(doc)

        session.commit()

        # Refresh to get relationships
        session.refresh(doc)
        return doc.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_document(workflow_id: str):
    """Get a document by workflow ID."""
    session = get_session()
    try:
        doc = session.query(EditableDocument).filter_by(workflow_id=workflow_id).first()
        return doc.to_dict() if doc else None
    finally:
        session.close()


def get_all_documents(limit: int = 50):
    """Get all documents, most recent first."""
    session = get_session()
    try:
        docs = session.query(EditableDocument).order_by(
            EditableDocument.updated_at.desc()
        ).limit(limit).all()
        return [doc.to_dict() for doc in docs]
    finally:
        session.close()


def get_user_by_id(user_id: int):
    """Get a user by ID."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        return user.to_dict() if user else None
    finally:
        session.close()


def get_all_users():
    """Get all active users."""
    session = get_session()
    try:
        users = session.query(User).filter_by(is_active=True).all()
        return [user.to_dict() for user in users]
    finally:
        session.close()


# ==================== Workflow Database Functions ====================

def create_workflow(workflow_id: str, client_name: str, workflow_type: str = "rfp_response",
                   industry: str = None, file_path: str = None):
    """Create a new workflow in the database."""
    session = get_session()
    try:
        workflow = Workflow(
            workflow_id=workflow_id,
            state="created",
            workflow_type=workflow_type,
            client_name=client_name,
            industry=industry,
            file_path=file_path
        )
        session.add(workflow)
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_workflow(workflow_id: str):
    """Get a workflow by workflow_id."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        return workflow.to_dict() if workflow else None
    finally:
        session.close()


def update_workflow_state(workflow_id: str, state: str):
    """Update workflow state."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.state = state
        workflow.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_workflow_analysis(workflow_id: str, rfp_analysis: dict):
    """Update workflow with RFP analysis results."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.rfp_analysis = rfp_analysis
        workflow.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_workflow_responses(workflow_id: str, responses: list):
    """Update workflow with generated responses (progressive)."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.generated_responses = responses
        workflow.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_workflow_review(workflow_id: str, review_result: dict):
    """Update workflow with review results."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.review_result = review_result
        workflow.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_workflow_final(workflow_id: str, output_file_path: str = None,
                         proposal_content: str = None, state: str = "ready"):
    """Update workflow with final output and mark as complete."""
    session = get_session()
    try:
        workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.state = state
        if output_file_path:
            workflow.output_file_path = output_file_path
        if proposal_content:
            workflow.proposal_content = proposal_content
        workflow.completed_at = datetime.utcnow()
        workflow.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(workflow)
        return workflow.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_workflows(limit: int = 50):
    """Get all workflows, most recent first."""
    session = get_session()
    try:
        workflows = session.query(Workflow).order_by(
            Workflow.created_at.desc()
        ).limit(limit).all()
        return [wf.to_dict() for wf in workflows]
    finally:
        session.close()
