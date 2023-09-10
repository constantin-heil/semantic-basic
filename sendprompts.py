import requests
from sqlalchemy import create_engine, text, Connection
from tqdm import tqdm
import argparse
import json

API_SECRET_FN = "secretkey.txt"

def get_cmdargs() -> dict:
    """get args from command line

    Returns:
        dict: cmd arguments
    """
    ap = argparse.ArgumentParser(
        description = "Send prompt to OpenAI and print response"
    )
    
    ap.add_argument(
        "-u",
        "--userprompt",
        help = "Users question to the Augustus",
        required = True
    )
    
    ap.add_argument(
        "-v",
        "--verbose",
        default = False,
        action = "store_true"
    )
    
    return vars(ap.parse_args())

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

def send_prompt(userrequest: str, topn: int, con: Connection, verbose: bool) -> str:
    """Query vector store and send prompt to OpenAI completions endpoint

    Args:
        userrequest (str): Question to ask
        topn (int): Number of top results to return from db
        con (Connection): Connection object

    Returns:
        str: Answer to question
    """
    CONTEXTPROMPT = """
    You will respond with the voice of roman emperor Marcus Aurelius.
    """
    
    PROMTTEMPLATE1 = """
    Give response to the following question:
    """ 
    
    PROMTTEMPLATE2 = """
    Use only the content of the following list to give answer:
    """
    
    qemb = get_embeddings(userrequest)
    
    res = con.execute(
        text("select rawtext from embed order by embeddings <=> :qemb limit :topn;"), 
        parameters = {"qemb": str(qemb).replace(" ", ""), "topn": topn}
        )
    
    res_list = ["- " + r[0] for r in res]
    user_str = "\n".join(res_list)
    
    prompt = CONTEXTPROMPT + PROMTTEMPLATE1 + userrequest + PROMTTEMPLATE2 + user_str
    
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {APIKEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    request = requests.post(
        url = "https://api.openai.com/v1/chat/completions",
        headers = header,
        json = data
    )
    
    outp = json.loads(request.content)["choices"][0]["message"]["content"]
    
    if verbose:
        return f"question : {userrequest}\ndblist : {res_list}\n" + outp
    else:
        return outp

if __name__ == "__main__":
    
    cmdargs = get_cmdargs()

    with open(API_SECRET_FN, "r") as fh:
        APIKEY = fh.read().strip()
        
    engine = create_engine("postgresql+psycopg2://root:password@localhost:5432/postgres")
    
    with engine.connect() as c:
        result = send_prompt(cmdargs["userprompt"], 10, c, cmdargs["verbose"])
        
    print(result)

    