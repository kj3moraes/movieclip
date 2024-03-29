<img style="float: left; padding:20px" src="media/clip.svg" alt="movieclip" width="75"/>

# movieclip

This repository is an experiment in contrastive learning and how it can be applied to something I like a lot - movies. What if we can train models to recognize cinematographic styles from training on movie scenes? This is what I try to solve in this experiment.

The repo is divided into 3 parts:

- [Dataset](#dataset) contains code for how the Moviescene dataset is generated. The dataset is published to S3.
- [Model](#model) - contains a Jupyter notebook exported from Colab where I trained the model.
- [Search](#search) - contains a full app where I use the CLIP model to perform movie scene searches.

More information about these are present in their respective directories.

## Dataset

The code to generate the Moviescene dataset, The README file in that directory shows how to replicate the download process and how to use the dataset. To download the dataset do

```bash
wget https://moviescene-dataset.s3.us-east-2.amazonaws.com/moviescene_2024_01.zip
unzip moviescene_2024_01.zip -d dataset/
```

Your dataset will look like this  

```bash
$ tree -L 1 dataset 
.
├── DISCLAIMER.md
├── directors.json
├── genres.json
├── ids.json
├── results.json
├── test
└── train

3 directories, 5 files
```

## Model

Using the Moviescene dataset, I fine-tune CLIP in [this notebook](./model/finetuning-clip.ipynb). In this notebook, I fine-tune ONLY on sci-fi movies for accuracy on zero-shot classification on movies.

I train two models:

- One with captions
- One with captions and (director + year) information.

## Search

The Moviesearch app is in the `search/` directory. You can have a custom server of yours running by following the instructions in the directory. You will need to have

- a JS runtime and package manager (bun or node+npm) installed
- Docker
- Python 3.11

# Licensing

This repository is licensed under the Apache2.0 License.

## References

- [FILM-GRAB](https://film-grab.com/)
- [Finetuning CLIP (Contrastive Language-Image Pre-training)](https://abdulkaderhelwan.medium.com/finetuning-clip-contrastive-language-image-pre-training-c15431e81330)
- [Indofashionclip](https://github.com/shashnkvats/Indofashionclip/blob/main/indofashion_clip.py)
