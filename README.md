# radioship_transcriber
This is a python package containing the Command Line Interface for the tradioship_transcriber.  

The transcriber creates transcripts for .mp3 files in .txt format using neural networks created for this purpose. It takes an input folder path, an output folder path, and an optional model path that can be a local path or a url on huggingface.co.
If no model path is given, it will use our hungarian model as a default.

### Install:
The transcriber is dependent on the [huggingsoud](https://github.com/jonatasgrosman/huggingsound) package, that uses a specific range of versions of torch. Since older versions of torch are not compatible with the latest versions of python **it is important to use python 3.10.10**.
We recommend using [pyenv](https://github.com/pyenv/pyenv) to install it. Here is a great [tutorial](https://realpython.com/intro-to-pyenv/) for that.

Then create a new virtual environment with [pipenv](https://pipenv.pypa.io/en/latest/):  
`pipenv install --python 3.10.10`  

Activate the new env with:  
`pipenv shell`  

Make sure it really uses python 3.10.10! Then install the radioship_transcriber from this repo:  
`pipenv install git+https://github.com/Koffair/radioship_transcriber.git#egg=radioship_transcriber`  

### Usage:
Now, if your virtual environment is active, you can call the transcriber the following ways (no need to type python):
- to use default model:  
`radioship_transcriber -i path/to/input/ -o path/to/output/`

- to use your own or any other model:  
`radioship_transcriber -i path/to/input/ -o path/to/output/ -m path/to/other/model/`  

The input folder should contain .mp3 files. The output folder will have .txt files, and the logs in a separate folder.
If the specified model is not present, the transcriber will download and cash it for later use.
If you want to remove a cashed model, use:  
`huggingface-cli delete-cache`


### man: 
Create transript for mp3 files. [-h] -i  -o  [-m]
  
options:  
  -h, --help          show this help message and exit  
  -i , --in_path      Path to input file or directory  
  -o , --out_path     Path to output directory  
  -m , --model_path   Address to transcripter model  
  






