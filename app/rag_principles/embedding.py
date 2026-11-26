import hashlib


# 向量维度固定：文档与查询映射到同一空间，余弦相似度才能逐维比较
EMBEDDING_DIM = 64


class SimpleKeywordEmbedding:#教学版关键词向量：词元词频 + 确定性哈希，纯规则、不依赖模型
    """把文本切成词元，按词频映射到固定维度的词袋向量。

    与真实 embedding 模型（如 text-embedding）的区别：
    不经过神经网络，只有字面匹配——「退货」和「退款」是两个不同词元，
    哈希到不同维度，语义相近但字面不同的词无法关联。
    用它演示 RAG「向量化 → 相似度检索」的原理足够了。
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 建索引阶段：批量向量化 chunk 文本
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        # 检索阶段：用户问题单独向量化
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        # 词袋：每个词元按哈希落到固定维度，重复出现则累加词频
        vector = [0.0] * EMBEDDING_DIM

        for token in self._tokenize(text):
            index = self._token_index(token)
            vector[index] += 1.0

        return vector

    def _tokenize(self, text: str) -> list[str]:
        # 先清洗：小写化，只保留字母、数字、汉字
        cleaned = "".join(
            char
            for char in text.lower()
            if (char.isascii() and char.isalnum())
            or ("\u4e00" <= char <= "\u9fff")
        )

        tokens: list[str] = []
        word = ""

        # 英文/数字按整词切分；汉字按单字切分
        for char in cleaned:
            if char.isascii() and char.isalnum():
                word += char
                continue

            if word:
                tokens.append(word)
                word = ""

            tokens.append(char)

        if word:
            tokens.append(word)

        # 中文补相邻二字组合（bigram）：
        # 「退款」「发票」这类关键词以二字词为主，bigram 能让它们精确命中
        chinese_chars = [
            char for char in cleaned
            if "\u4e00" <= char <= "\u9fff"
        ]
        tokens.extend(
            first + second
            for first, second in zip(chinese_chars, chinese_chars[1:])
        )

        return tokens

    def _token_index(self, token: str) -> int:
        # 确定性哈希：同一个词无论何时计算都落到同一维度，
        # 这是「无需预先统计词表也能对齐文档与查询向量」的关键
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16) % EMBEDDING_DIM
