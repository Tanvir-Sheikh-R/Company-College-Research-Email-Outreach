from transformers import pipeline

pipe = pipeline("image-text-to-text", model="moonshotai/Kimi-K2.7-Code", trust_remote_code=True)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "What animal is on the candy?"}
        ]
    },
]
pipe(text=messages)