from .analysis.summarizer import ChainOfAnalysis
from .scrape import fetch_url
from .ioutil import CaptureFD

VERSION = "0.0.1"
    
def run_summarize(url, **kwargs):
    co = None
    try:
        data = fetch_url(url, **kwargs)

        if not data:
            raise ValueError(f"Data is empty, the url may be invalid")

        with CaptureFD() as co:
            cod = ChainOfAnalysis.factory(**kwargs)

        if len(data) < 100:
            raise ValueError(f"Data is too small: (size {len(data)}), the url may be invalid")
        summary = cod(data=data, **kwargs)

        print(f"""
    Article Summary Chain:

    """)
        for i, s in enumerate(cod.summaries):
            print(s)
        print(f"""Final Summary: {summary}""")
    except ValueError as e:
        print(f"Failed to summarize {url}: {e}")
    except Exception as e:
        print(f"Failed to summarize {url}: {e}")
        if co:
            print(co.stdout)
            print(co.stderr)

if __name__ == '__main__':
    import argparse
    import logging

    parser = argparse.ArgumentParser(description=f"ValAI CLI (v{VERSION})", prog='valai')

    subparsers = parser.add_subparsers(title='subcommands', help='Available commands', dest='command')

    summary_parser = argparse.ArgumentParser(add_help=False)
    summary_parser.add_argument('--model-path', type=str, default='/mnt/biggy/ai/llama/gguf', help='Path to model')
    summary_parser.add_argument('--model-file', type=str, default='zephyr-7b-beta.Q8_0.gguf', help='Model file (gguf)')
    summary_parser.add_argument('-n', '--iterations', type=int, default=3, help='Number of iterations to run')
    summary_parser.add_argument('-p', '--paragraphs', type=int, default=3, help='Number of paragraphs in summary')
    summary_parser.add_argument('-o', '--observations', type=int, default=8, help='Number of initial observations to generate')
    summary_parser.add_argument('-t', '--theories', type=int, default=3, help='Number of missing information theories to generate')
    summary_parser.add_argument('--sl', '--summary_length', type=int, default=150, dest='s_length', help='Max number of tokens in a summary paragraph')
    summary_parser.add_argument('--ol', '--observation_length', type=int, default=50, dest='o_length', help='Max number of tokens in a observation')
    summary_parser.add_argument('--tl', '--theory_length', type=int, default=50, dest='t_length', help='Max number of tokens in a theory')
    summary_parser.add_argument('--st', '--summary_temperature', type=float, default=0.5, dest="s_temp", help='Summary generation temperature')
    summary_parser.add_argument('--ot', '--observation_temperature', type=float, default=0.7, dest="o_temp", help='Observation generation temperature')
    summary_parser.add_argument('--tt', '--theory_temperature', type=float, default=1.0, dest="t_temp", help='Theory generation temperature')
    summary_parser.add_argument('--constrain_data', type=int, default=12000, help='Constrain the url data to this many bytes')
    summary_parser.add_argument('--n_batch', type=int, default=512, help='LLAMA Batch Size')
    summary_parser.add_argument('--n_gpu_layers', type=int, default=14, help='LLAMA GPU Layers')
    summary_parser.add_argument('--n_ctx', type=int, default=2 ** 14, help='LLAMA Context Size')
    summary_parser.add_argument('--log_chunk_length', type=int, default=50, help='Length of generated log chunks')
    summary_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    summary_parser.add_argument('url', type=str, metavar='URL', help='URL to summarize')

    # Add your original parser as a subparser
    summ_cmd = subparsers.add_parser('summarize', parents=[summary_parser], help='Summarize an article')

    args = parser.parse_args()
    kwargs = dict(args._get_kwargs())

    def default():
        parser.print_help()
    
    if kwargs.get('verbose', False):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    {
        'summarize': lambda: run_summarize(**kwargs),
    }.get(kwargs.get('command', None), default)()