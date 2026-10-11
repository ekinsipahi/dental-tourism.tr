def compute_related_posts():
    """TF-IDF benzerliği ile 'ilgili yazılar' (iç linkleme)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    from .models import BlogPost, RelatedPost

    posts = list(BlogPost.published.all())
    if len(posts) < 2:
        return {"computed": 0}
    texts = [f"{p.title} {p.title} {p.focus_keyword} {p.excerpt} {p.content[:3000]}" for p in posts]
    sim = cosine_similarity(TfidfVectorizer(max_features=3000, sublinear_tf=True).fit_transform(texts))
    count = 0
    for i, post in enumerate(posts):
        RelatedPost.objects.filter(post=post, is_manual=False).delete()
        ranked = sorted(((j, s) for j, s in enumerate(sim[i]) if j != i), key=lambda x: x[1], reverse=True)[:6]
        for j, score in ranked:
            if score <= 0.02:
                continue
            RelatedPost.objects.update_or_create(post=post, related_post=posts[j],
                                                 defaults={"score": float(score), "is_manual": False})
            count += 1
    return {"computed": count}
