import json
import os
import random
import time
from pathlib import Path

import click
from tqdm import tqdm

from .cli_utils import cli, generator, parallel, processor
from .evaluation import EvaluationModel
from .generation import GenerationModel

model_set = None


class ModelSet:
    def __init__(self, rule, temperature, minimum, maximum):
        print(f"Model initialized at pid:{os.getpid()}")
        self.evaluation_model = EvaluationModel(
            minimum,
            maximum
        )
        self.generation_model = GenerationModel(
            rule,
            temperature
        )

    def run(self, data):
        output = self.generation_model.generate(data)
        score = self.evaluation_model.evaluate(output)

        wait_time = random.random() * 0.01
        time.sleep(wait_time)
        return output, score

def num_lines(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return len(fp.readlines())


@cli.command("open")
@click.option(
    "-i", "--input", "files",
    type=click.Path(), multiple=True,
    help="File(s) to open.")
@click.option(
    "-f", "--format", "format_", default="txt",
    type=click.Choice(["jsonl", "txt"], case_sensitive=False),
    help="File format for per-line formatting.")
@generator
def open_cmd(files, format_):
    """Loads one or multiple files for processing. The input parameter
    can be specified multiple times to load more than one file.
    """
    for file in files:
        try:
            click.echo(f"Opening '{file}'")
            line_no = num_lines(file)
            with open(file, "r", encoding="utf-8") as fp:
                for line in tqdm(fp.readlines(), ncols=80, total=line_no):
                    if format_ == "jsonl":
                        yield json.loads(line)
                    else:
                        yield line
        except Exception as e:
            click.echo(f"Could not open file '{file}': {e}", err=True)


@cli.command("save")
@click.option(
    "-o", "--output-path", default="_result.jsonl",
    type=click.Path(), show_default=True,
    help="The name and format for the output file.")
@click.option(
    "-s", "--stat", is_flag=True,
    help="Whether to print statistics")
@processor
def save_cmd(streamed_results, output_path, stat):
    """Saves all processed JSON to a single .jsonl file"""

    # Collect streamed outputs
    outputs = []
    for result in streamed_results:
        outputs.append(result)
        yield True

    if stat:
        total = 0.0
        cnt = 0
        for o in outputs:
            total += o["score"]
            cnt += 1

        average = total / cnt
        click.echo(f"Average : {average:.3f} ({cnt})")

    output_path = Path(output_path)
    if not output_path.parent.exists():
        output_path.parent.mkdir()
    with output_path.open("w", encoding="utf-8") as ofp:
        for result in outputs:
            try:
                print(json.dumps(result, ensure_ascii=False), file=ofp)
            except Exception as e:
                click.echo(f"Could not save data {result}: {e}", err=True)


@cli.command("txt2json")
@processor
def txt2json_cmd(data):
    """Convert arbitrary string into a JSON object in {'input': $data} form.
    """
    for d in data:
        yield {"input": d}


@cli.command("process")
@click.option(
    '--num-process', default=1,
    type=int, show_default=True,
    help='Number of processes')
@click.option(
    "--rule", "rule", required=True,
    type=click.Choice(["reverse", "shuffle", "bypass"], case_sensitive=False),
    help="Generation rule choice")
@click.option(
    "-t", "--temperature", default=0.1,
    type=float, show_default=True,
    help="(opt) wild case probability")
@click.option(
    "-m", "--minimum", default=1.,
    type=float, show_default=True,
    help="(opt) minimum score value")
@click.option(
    "-M", "--maximum", default=5.,
    type=float, show_default=True,
    help="(opt) maximum score value")
@processor
def process_cmd(data, rule, temperature, minimum, maximum, num_process):
    """Given a string, generate some output string and evaluate the result
    as a score within the given min-max range.
    """
    # Initializer will create seperate 'model_set' per sub-processes
    def init_worker(id_):
        global model_set
        model_set = ModelSet(
            rule,
            temperature,
            minimum,
            maximum
        )

    # your processing logic here
    @parallel(num_process, init_worker)
    def process_data(data):
        output, score = model_set.run(data["input"])

        data.update({
            "output": output,
            "score": score})
        return data

    return process_data(data)
