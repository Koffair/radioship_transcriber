import click
import os

# --- Notes ---- 
# create main function pseudo code
# Click interface in action
# talk to Zoli about the model usage
# check check if hooks are working
# --------------


default_model = "[addres of default model]"


@click.command()
@click.option("--in_path", "-i",  help="Path to input file or directory")
@click.option("--out_path", "-o",  help="Path to output directory")
@click.option("--model", "-m",  default=default_model, help="Address to transripter model",)
def make_transcript(in_path, out_path, model):

    # create output folder if does not exist (ask maybe...)
    # asking only makes sense for the cli, not the callable... get it outside.
    if not os.path.isdir(out_path):
       print("Output dir [{}] does not exist!".format(out_path))
       create_q = input("Would you like to create it? y/n: ")
       if create_q == "y":
           os.mkdir(out_path)
           print("Output dir [{}] created!\n".format(out_path))
       else:
           return

    # fetch model 
    print("\nModel: {} fetched\n".format(model))

    print("Creating transcript for files in {}. \nOutput dir: {}".format(in_path, out_path))
    # get filesr_list
    input_files = os.listdir(in_path)
    for f in input_files:
        if os.path.isfile(f):
            # create transcript
            print("transcipt created for {}".format(f))



if __name__ == '__main__':

    make_transcript()

