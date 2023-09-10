import requests
from sqlalchemy import create_engine, text
from tqdm import tqdm
import argparse
import json

API_SECRET_FN = "secretkey.txt"
    
def get_embeddings(inp_text: str) -> list:
    """Send natural language text to OpenAI Embeddings API

    Args:
        input_text (str): A string that represents the input

    Returns:
        list: list of embeddings
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {APIKEY}"
    }
    
    data = {
        "input": inp_text,
        "model": "text-embedding-ada-002"
    }
    
    result = requests.post(
        url = "https://api.openai.com/v1/embeddings",
        headers = header,
        json = data
    )
    
    return json.loads(result.content)["data"][0]["embedding"]

def get_cmdargs() -> dict:
    """Obtain arguments from command line

    Returns:
        dict: Arguments
    """
    ap = argparse.ArgumentParser(
        description = "Point to a raw text file and do crude splitting and db writing"
    )
    
    ap.add_argument(
        "-t", 
        "--textfile", 
        help = "Raw text file to parse",
        required = True
        )
    
    ap.add_argument(
        "-n",
        "--nlists",
        help = "Number of lists in IVFFlat index",
        default = str(100)
    )
    
    return vars(ap.parse_args())

if __name__ == "__main__":
    
    cmdargs = get_cmdargs()

    with open(API_SECRET_FN, "r") as fh:
        APIKEY = fh.read().strip()
    
    with open(cmdargs["textfile"], "r") as fh:
        texts = fh.read().strip().split("\n\n")
    
    texts = [txt.replace("\n", "") for txt in texts if len(txt) > 5]
    embs = [get_embeddings(txt) for txt in tqdm(texts)]

    engine = create_engine("postgresql+psycopg2://root:password@localhost:5432/postgres")

    with engine.connect() as c:
        for i in range(len(embs)):
            params = {
                "insemb": str(embs[i]).replace(" ", ""),
                "rawtext": texts[i]
                }
            c.execute(text("insert into embed (rawtext, embeddings) values (:rawtext, :insemb)"), parameters = params)
    
        c.execute(text("CREATE INDEX ON embed USING ivfflat (embeddings vector_cosine_ops) WITH (lists = :nlists)"),
                  parameters = {"nlists": cmdargs["nlists"]})
        c.commit()