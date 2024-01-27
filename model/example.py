from PIL import Image
import requests
from transformers import AutoProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

inputs = processor(
    text=["a photo of a cat", "a photo of a dog"], images=image, return_tensors="pt", padding=True
)

# print(inputs.keys())
# print(inputs["pixel_values"].shape)  # torch.Size([2, 3, 224, 224]
# print(inputs["input_ids"].shape)  # torch.Size([2, 8])
# print(inputs["input_ids"])  # torch.Size([2, 8]
# print(inputs["attention_mask"].shape)  # torch.Size([2, 8])
# print(inputs["attention_mask"])  # torch.Size([2, 8]
outputs = model(**inputs)
logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
ds_with_embeddings = ds_with_embeddings.map(lambda example:
                                          {'image_embeddings': model.get_image_features(
                                              **processor([example["image"]], return_tensors="pt")
                                              .to("cuda"))[0].detach().cpu().numpy()})
print(probs)