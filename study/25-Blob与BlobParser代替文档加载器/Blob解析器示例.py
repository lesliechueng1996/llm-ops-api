from langchain_core.document_loaders import Blob
from langchain_core.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document


class CustomParser(BaseBlobParser):
    def lazy_parse(self, blob):
        with blob.as_bytes_io() as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": blob.source},
                )
                line_number += 1


blob = Blob.from_path("./study/24-自定义加载器/喵喵.txt")
parser = CustomParser()

docs = list(parser.lazy_parse(blob))
print(docs)
