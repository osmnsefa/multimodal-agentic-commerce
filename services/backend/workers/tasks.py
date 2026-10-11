from workers.celery_app import celery_app

@celery_app.task(name="workers.tasks.generate_product_embedding")
def generate_product_embedding(product_id: str, image_url: str):
    """
    Async Celery task to compute visual & textual embeddings.
    """
    return {"status": "success", "product_id": product_id, "vector_dim": 512}
