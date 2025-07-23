import torch
import torch.nn as nn
import torch.nn.functional as F

class Matcher(nn.Module):
    def __init__(self, num_cls, conf_dim, embedding_dim=32, hidden_dim=64, num_heads=4, dropout_rate=0.1):
        super().__init__()
        self.class_embeddings = nn.Embedding(num_cls, embedding_dim)

        # --- HATA AYIKLAMA İÇİN PRINT EKLEYELİM ---
        feature_dim = 4 + embedding_dim + conf_dim

        self.input_projection = nn.Linear(feature_dim, hidden_dim)

        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=dropout_rate,
            batch_first=True
        )

        self.classifier_head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 2)
        )

    def forward(self, bboxes, clss, confs):
        cls_embeds = self.class_embeddings(clss)

        combined_features = torch.cat([bboxes, cls_embeds, confs], dim=-1)

        projected_features = self.input_projection(combined_features)

        context, _ = self.attention(projected_features, projected_features, projected_features)
        aggregated_context = context.mean(dim=1)
        logits = self.classifier_head(aggregated_context)
        return logits