"""Main entry point for the Automated Sales Proposal System."""
import uvicorn
from config import settings


def main():
    """Run the FastAPI server."""
    print("=" * 80)
    print("🚀 Automated Sales Proposal System")
    print("=" * 80)
    print(f"Starting server on {settings.api_host}:{settings.api_port}")
    print(f"LLM Provider: {settings.default_llm_provider}")
    print(f"Model: {settings.default_model}")
    print(f"Vector Store: {settings.vector_store_path}")
    print(f"Output Directory: {settings.output_dir}")
    print("=" * 80)
    print("\nEndpoints:")
    print(f"  - API Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"  - Health Check: http://{settings.api_host}:{settings.api_port}/health")
    print(f"  - Quick Proposal: POST http://{settings.api_host}:{settings.api_port}/api/v1/proposals/quick")
    print(f"  - Upload RFP: POST http://{settings.api_host}:{settings.api_port}/api/v1/rfp/upload")
    print("=" * 80)
    print()

    uvicorn.run(
        "api.routes:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Enable auto-reload for development
    )


if __name__ == "__main__":
    main()
