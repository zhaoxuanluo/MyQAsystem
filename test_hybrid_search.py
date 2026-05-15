"""测试混合检索功能"""
import sys
sys.path.insert(0, 'backend')

from app.core.vector_store import InMemoryVectorStore
from app.core.embedder import get_embedder
import numpy as np

# 创建测试数据
test_docs = [
    "智能吸顶灯是一款照明设备，功率12W，价格299元",
    "智能筒灯是照明设备，功率8W，价格199元",
    "门窗传感器是安防设备，功率0.5W，价格89元",
    "智能灯带是照明设备，功率24W，价格399元",
]

# 初始化
store = InMemoryVectorStore("backend/data/test_vectors.json")
embedder = get_embedder()

# 创建集合
store.create_collection("test_kb")

# 嵌入并插入
print("正在嵌入文档...")
embeddings_list = [embedder.embed_query(doc) for doc in test_docs]

data = []
for i, doc in enumerate(test_docs):
    emb = embeddings_list[i]
    data.append({
        "id": f"id_{i}",
        "chunk_id": f"chunk_{i}",
        "doc_id": "test_doc",
        "dense_vector": emb["dense"],
        "sparse_vector": emb.get("sparse", {}),  # 如果没有sparse则使用空字典
        "content": doc,
    })

store.insert("test_kb", data)
print(f"已插入 {len(data)} 个文档")

# 测试查询
query = "智能吸顶灯"
print(f"\n查询: {query}")

query_emb = embedder.embed_query(query)

# 测试混合检索
print("\n=== 混合检索结果 (dense + sparse + RRF) ===")
results = store.hybrid_search("test_kb", query_emb["dense"], query_emb.get("sparse"), top_k=3)
for i, r in enumerate(results, 1):
    print(f"{i}. 评分: {r['score']:.4f}")
    print(f"   内容: {r['content']}")

# 测试纯dense检索
print("\n=== 纯Dense检索结果 ===")
results_dense = store.search("test_kb", query_emb["dense"], top_k=3)
for i, r in enumerate(results_dense, 1):
    print(f"{i}. 评分: {r['score']:.4f}")
    print(f"   内容: {r['content']}")

# 测试纯sparse检索（如果有sparse向量）
if query_emb.get("sparse"):
    print("\n=== 纯Sparse检索结果 ===")
    results_sparse = store.sparse_search("test_kb", query_emb["sparse"], top_k=3)
    for i, r in enumerate(results_sparse, 1):
        print(f"{i}. 评分: {r['score']:.4f}")
        print(f"   内容: {r['content']}")
else:
    print("\n当前embedder不支持sparse向量")

print("\n测试完成！")
