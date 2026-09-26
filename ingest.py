"""
FINORA AI Business Advisor — Knowledge Ingestion CLI

Reads all documents from the knowledge/ directory, splits them into chunks,
creates embeddings via Google Gemini, and persists to ChromaDB.

Run with:
    python ingest.py

Run this script before starting the API server and whenever knowledge changes.
"""
import sys
import logging
import time
from pathlib import Path

# Ensure the project root is in sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logging

setup_logging(level=logging.INFO)
logger = logging.getLogger("ingest")


def main() -> None:
    """Main ingestion pipeline."""
    print("=" * 60)
    print("  FINORA AI — Knowledge Ingestion")
    print("=" * 60)

    # ---- Validate configuration -----------------------------------------
    from config.settings import settings

    try:
        settings.validate_api_key()
    except EnvironmentError as exc:
        print(f"\n❌ Lỗi cấu hình:\n{exc}")
        sys.exit(1)

    knowledge_dir = settings.get_knowledge_dir()
    vector_db_dir = settings.get_vector_db_dir()

    print(f"\n📂 Thư mục kiến thức : {knowledge_dir}")
    print(f"🗄️  Vector database   : {vector_db_dir}")
    print(f"🤖 Embedding model    : {settings.active_embedding_model()}")
    print(f"📏 Chunk size         : {settings.CHUNK_SIZE} | Overlap: {settings.CHUNK_OVERLAP}")

    if not knowledge_dir.is_dir():
        print(f"\n❌ Thư mục knowledge không tồn tại: {knowledge_dir}")
        sys.exit(1)

    # ---- Load documents -------------------------------------------------
    print("\n[1/4] Đang tải tài liệu...")
    from rag.document_loader import load_all_documents

    documents = load_all_documents(knowledge_dir)
    if not documents:
        print("⚠️  Không tìm thấy tài liệu nào. Kiểm tra thư mục knowledge/.")
        sys.exit(1)

    print(f"✅ Đã tải {len(documents)} tài liệu.")

    # ---- Split documents ------------------------------------------------
    print("\n[2/4] Đang chia tài liệu thành chunks...")
    from rag.text_splitter import split_documents

    chunks = split_documents(documents)
    print(f"✅ Đã tạo {len(chunks)} chunks.")

    # Show breakdown by source
    sources: dict[str, int] = {}
    for chunk in chunks:
        fname = chunk.metadata.get("filename", "unknown")
        sources[fname] = sources.get(fname, 0) + 1

    print("\n  Phân bổ chunks theo tài liệu:")
    for fname, count in sorted(sources.items()):
        print(f"    • {fname}: {count} chunks")

    # ---- Create / overwrite vector store --------------------------------
    print("\n[3/4] Đang tạo embeddings và lưu vào ChromaDB...")
    print("  (Bước này có thể mất vài phút tuỳ số lượng chunks...)")

    from rag.vector_store import create_vector_store

    start_time = time.time()
    try:
        store = create_vector_store(chunks, vector_db_dir)
        elapsed = time.time() - start_time
        print(f"✅ Vector store đã được tạo thành công! ({elapsed:.1f}s)")
    except Exception as exc:
        print(f"\n❌ Lỗi khi tạo vector store: {exc}")
        logger.exception("Vector store creation failed.")
        sys.exit(1)

    # ---- Verification ---------------------------------------------------
    print("\n[4/4] Xác minh vector store...")
    try:
        test_results = store.similarity_search("doanh thu lợi nhuận", k=1)
        if test_results:
            print("✅ Kiểm tra truy xuất thành công.")
        else:
            print("⚠️  Truy xuất trả về 0 kết quả — kiểm tra lại nội dung tài liệu.")
    except Exception as exc:
        print(f"⚠️  Không thể kiểm tra: {exc}")

    # ---- Summary --------------------------------------------------------
    print("\n" + "=" * 60)
    print("  ✅ INGESTION HOÀN THÀNH")
    print("=" * 60)
    print(f"  • Số tài liệu đã đọc : {len(documents)}")
    print(f"  • Số chunks đã tạo   : {len(chunks)}")
    print(f"  • Vector DB đường dẫn: {vector_db_dir}")
    print("\n  Bạn có thể chạy ứng dụng bằng:")
    print("    uvicorn server:app --host 0.0.0.0 --port 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
