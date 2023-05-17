# radioship_transcripter
This is a CLI interface for the transcripter tool created by the radioship project  

### usage: 
Create transript for mp3 files. [-h] -i  -o  [-m]

options:
  -h, --help          show this help message and exit
  -i , --in_path      Path to input file or directory
  -o , --out_path     Path to output directory
  -m , --model_path   Address to transcripter model

### Example:
to use default model:
python transcript_tool.py -i ../test_input/ -o ../test_output/ 

to use other model:
python transcript_tool.py -i ../test_input/ -o ../test_output/ -m ../models/new_model/  

### Repo structure:
.
├── Pipfile
├── Pipfile.lock
├── README.md
├── src
│   ├── __init__.py
│   └── transcript_tool.py
├── models
│   ├── default_model
│   │   ├── all_results.json
│   │   ├── config.json
│   │   ├── preprocessor_config.json
│   │   ├── pytorch_model.bin
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   ├── trainer_state.json
│   │   ├── train_results.json
│   │   └── vocab.json
├── test_input
│   ├── test_file.mp3
├── test_output
│   ├── test_file.txt


## TODO
- logging
- doctests
- slicing audio (dies on longer sections. how long?)
- writin readme for the interface

- currently works w local model: extend to & test w cloud

