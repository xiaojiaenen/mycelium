---
type: source
title: "Attention Is All You Need 论文解读"
source_type: article
source_url: "https://arxiv.org/abs/1706.03762"
created: 2026-06-20
tags:
  - transformer
  - attention
  - nlp
  - deep-learning
status: reviewed
---

# Attention Is All You Need 论文解读

## 元信息
- 来源：arXiv:1706.03762
- 作者：Vaswani et al.
- 日期：2017-06-12
- 类型：论文

---

## 一句话总结
提出Transformer架构，完全基于注意力机制，摒弃RNN和CNN，在机器翻译上取得SOTA。

## 核心观点（5个）
1. 注意力机制可以完全替代RNN/CNN处理序列数据
2. 自注意力(Self-Attention)能捕捉序列内部的长距离依赖
3. 多头注意力(Multi-Head)能关注不同表示子空间
4. 位置编码(Positional Encoding)解决序列顺序问题
5. 并行计算大幅提升训练效率

## 详细内容

### 为什么需要Transformer
传统RNN的问题：
- 无法并行（必须按顺序处理）
- 长距离依赖困难（梯度消失）
- 训练慢

> "Recurrent models typically factor computation along the symbol positions of the input and output sequences... This inherently sequential nature precludes parallelization..." — Section 1

### 注意力机制核心思想
注意力让模型能够"关注"输入中最相关的部分。

**类比**：当你读一个句子时，理解每个词会关注句子中其他相关的词。

> "An attention function can be described as mapping a query and a set of key-value pairs to an output..." — Section 3.1

### 自注意力 (Self-Attention)
序列内部的注意力：每个位置关注整个序列。

**计算过程**：
1. 每个位置生成Query, Key, Value三个向量
2. Query和所有Key计算相似度
3. 用相似度对Value加权求和

> "Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence..." — Section 3.1

### 多头注意力 (Multi-Head)
不是一组Q/K/V，而是多组并行：

```
head_i = Attention(Q·W_i^Q, K·W_i^K, V·W_i^V)
MultiHead = Concat(head_1, ..., head_h)·W^O
```

**好处**：不同头可以关注不同类型的关系（语法、语义等）

> "Multi-head attention allows the model to jointly attend to information from different representation subspaces..." — Section 3.2

### 位置编码 (Positional Encoding)
Attention本身是位置无关的，需要额外注入位置信息。

**方法**：使用正弦/余弦函数生成位置编码

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

> "Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position..." — Section 3.5

---

## 关键概念
- [[transformer]] - 基于注意力的架构
- [[attention-mechanism]] - 注意力函数
- [[self-attention]] - 序列内部注意力
- [[multi-head-attention]] - 多组并行注意力
- [[positional-encoding]] - 位置信息注入

## 引用原文

> "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks..." — Abstract

> "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms..." — Abstract

> "Attention is all you need." — Title

---

## 我的思考
这篇论文的核心洞察是：注意力机制本身就足够了，不需要RNN的顺序处理。这开启了大语言模型时代。

## 相关链接
- [[transformer]]
- [[attention-mechanism]]
- [[self-attention]]

## 待验证
- [ ] 位置编码的其他方案对比
- [ ] Transformer在不同任务上的表现差异
