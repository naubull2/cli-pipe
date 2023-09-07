# 🛝 cli-pipe

Provides a simple template code for building UNIX pipe-like cli commands with parallel processing using multi-processing.

- ex. Chaining generation, evaluation, filter, etc. for preprocessing of data or such.



# ⚙️ Install

Simple usage.
```
pip install .
```

For developing / debugging.
```
pip install --editable .
```
- No hastle through uninstalling → reinstalling each time code changes.



# 📝 How-to

Installing this repo off the shelf would create a cli command named `cmd`.

There are sample subcommands in `cmd`, where they can be chained in order, as you would pipe commands in UNIX-like environments.

> ex. cat $FILE | cut -f 2 -d ":" | head -n 20 | jq


The following sample bash script will,

1. `open` multiple **"text"** files,
2. for each line from the input files,`txt2json` reformat line data into JSON,
4. `process` each JSON from the stream in parallel,
6. then `save` the result at the specified location.

```
#!/bin/bash
NUM_PROCESS=${1:-1}

cmd \
  open \
    -i "./scripts/sample.txt" \
    -i "./scripts/sample2.txt" \
    -f "txt" \
  txt2json \
  process \
    --num-process ${NUM_PROCESS} \
    --rule "shuffle" \
    -t 0.4 \
    -m 1.0 \
    -M 6.0 \
  save \
    -o "./results/eval.jsonl" \
    --stat

```



## Multi-processing

The first argument to the example shell script would designate number of processes to handle the input stream.

- Notice the number of processes used and the total executaion time of the following results.

```shell
❯ ./run_sample.sh 20
Model initialized at pid:86417
Model initialized at pid:86418
Model initialized at pid:86419
Model initialized at pid:86420
Model initialized at pid:86421
Model initialized at pid:86422
Model initialized at pid:86423
Model initialized at pid:86424
Model initialized at pid:86425
Model initialized at pid:86426
Model initialized at pid:86427
Model initialized at pid:86428
Model initialized at pid:86429
Model initialized at pid:86430
Model initialized at pid:86431
Model initialized at pid:86432
Model initialized at pid:86433
Model initialized at pid:86434
Model initialized at pid:86435
Model initialized at pid:86436
Opening './scripts/sample.txt'
100%|█████████████████████████████████████| 4000/4000 [00:01<00:00, 3657.86it/s]
Opening './scripts/sample2.txt'
100%|█████████████████████████████████████| 4978/4978 [00:01<00:00, 3546.33it/s]
Average : 4.491 (8978)
2574.6819972991943 msecs taken!

❯ ./run_sample.sh 5
Model initialized at pid:86520
Model initialized at pid:86521
Model initialized at pid:86522
Model initialized at pid:86523
Model initialized at pid:86524
Opening './scripts/sample.txt'
100%|██████████████████████████████████████| 4000/4000 [00:04<00:00, 915.61it/s]
Opening './scripts/sample2.txt'
100%|██████████████████████████████████████| 4978/4978 [00:05<00:00, 890.94it/s]
Average : 4.516 (8978)
10099.210023880005 msecs taken!
```
- Multiprocessing is restricted in uses of function that is passed through pool.map() and
  would not work well with python generator functions in general.
  - `pathos.multiprocessing.ProcessingPool` is a similar alternative to the built-in `multiprocessing.Pool`
    that would take care of the serialization in many cases.



## Commands in detail

```
❯ cmd --help
Usage: cmd [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

  Pipeline any following sub commands in the given order, lazily processing
  each data.

Options:
  --help  Show this message and exit.

Commands:
  open      Loads one or multiple files for processing.
  process   Given a string, generate some output string and evaluate the...
  save      Saves all processed JSON to a single .jsonl file
  txt2json  Convert arbitrary string into a JSON object in {'input':...


❯ cmd open --help
Usage: cmd open [OPTIONS]

  Loads one or multiple files for processing. The input parameter can be
  specified multiple times to load more than one file.

Options:
  -i, --input PATH          File(s) to open.
  -f, --format [jsonl|txt]  File format for per-line formatting.
  --help                    Show this message and exit.


❯ cmd save --help
Usage: cmd save [OPTIONS]

  Saves all processed JSON to a single .jsonl file

Options:
  -o, --output-path PATH  The name and format for the output file.  [default:
                          _result.jsonl]
  -s, --stat              Whether to print statistics
  --help                  Show this message and exit.


❯ cmd txt2json --help
Usage: cmd txt2json [OPTIONS]

  Convert arbitrary string into a JSON object in {'input': $data} form.

Options:
  --help  Show this message and exit.



❯ cmd process --help
Usage: cmd process [OPTIONS]

  Given a string, generate some output string and evaluate the result as a
  score within the given min-max range.

Options:
  --num-process INTEGER           Number of processes  [default: 1]
  --rule [reverse|shuffle|bypass]
                                  Generation rule choice  [required]
  -t, --temperature FLOAT         (opt) wild case probability  [default: 0.1]
  -m, --minimum FLOAT             (opt) minimum score value  [default: 1.0]
  -M, --maximum FLOAT             (opt) maximum score value  [default: 5.0]
  --help                          Show this message and exit.

```



# Reference

- Code reference: [click-examples](https://github.com/pallets/click/tree/main/examples)
   - CLI pipe skeleton was developed from the imagepipe example from click.
- Sample data: [parlai-personachat](https://github.com/facebookresearch/ParlAI/tree/main/projects/personachat) 
   - sample input data used in the examples are sentences drawn from the ParlAI persona-chat valid set.
