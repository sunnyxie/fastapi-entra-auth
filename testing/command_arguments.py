import sys

class BasePipeline:
    def __init__(self, name1, *args, batch_size=100, **kwargs):
        self.name = name1
        self.batch_size = batch_size
        print(f"Pipeline '{self.name}' initialized with batch size {self.batch_size}")
        print(f"extras:  {kwargs}  -- {args}")

class DatabricksPipeline(BasePipeline):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

if __name__ == "__main__":
    _, args = sys.argv[0], sys.argv[1:]
    print(args)
    pipe = DatabricksPipeline("my-data-bucket", "argument 2", batch_size=3500, extra_size=200)