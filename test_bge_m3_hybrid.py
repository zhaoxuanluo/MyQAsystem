"""测试BGE-M3混合检索功能"""
import sys
sys.path.insert(0, 'backend')

from app.core.vector_store import InMemoryVectorStore
from app.core.embedder import BGEM3Embedder
import numpy as np

# 创建测试数据
test_docs = [
    "智能吸顶灯是一款照明设备，功率12W，价格299元，安装在客厅",
    "智能筒灯是照明设备，功率8W，价格199元，安装在卧室",
    "门窗传感器是安防设备，功率0.5W，价格89元，安装在窗户",
    "智能灯带是照明设备，功率24W，价格399元，安装在电视墙",
    "智能门锁是安防设备，功率5W，价格1299元，安装在入户门",
]

# 初始化
print("初始化BGE-M3模型...")
store = InMemoryVectorStore("backend/data/test_bge_vectors.json")
embedder = BGEM3Embedder()

# 创建集合
store.create_collection("test_kb")

# 嵌入并插入
print("正在嵌入文档...")
data = []
for i, doc in enumerate(test_docs):
    emb = embedder.embed_query(doc)
    data.append({
        "id": f"id_{i}",
        "chunk_id": f"chunk_{i}",
        "doc_id": "test_doc",
        "dense_vector": emb["dense"].tolist(),
        "sparse_vector": emb["sparse"],
        "content": doc,
    })
    print(f"  文档{i+1}: sparse向量有 {len(emb['sparse'])} 个token")

store.insert("test_kb", data)
print(f"已插入 {len(data)} 个文档\n")

# 测试查询
queries = ["智能吸顶灯", "照明设备", "安防设备"]

for query in queries:
    print(f"{'='*60}")
    print(f"查询: {query}")
    print(f"{'='*60}")

    query_emb = embedder.embed_query(query)
    print(f"查询sparse向量有 {len(query_emb['sparse'])} 个token\n")

    # 测试混合检索
    print("=== 混合检索结果 (Dense + Sparse + RRF) ===")
    results = store.hybrid_search("test_kb", query_emb["dense"], query_emb["sparse"], top_k=3)
    for i, r in enumerate(results, 1):
        print(f"{i}. RRF评分: {r['score']:.4f}")
        print(f"   内容: {r['content'][:50]}...")

    # 测试纯dense检索
    print("\n=== 纯Dense检索结果 ===")
    results_dense = store.search("test_kb", query_emb["dense"], top_k=3)
    for i, r in enumerate(results_dense, 1):
        print(f"{i}. Dense评分: {r['score']:.4f}")
        print(f"   内容: {r['content'][:50]}...")

    # 测试纯sparse检索
    print("\n=== 纯Sparse检索结果 ===")
    results_sparse = store.sparse_search("test_kb", query_emb["sparse"], top_k=3)
    for i, r in enumerate(results_sparse, 1):
        print(f"{i}. Sparse评分: {r['score']:.4f}")
        print(f"   内容: {r['content'][:50]}...")

    print()

print("\n测试完成！")
