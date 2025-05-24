from fastapi import FastAPI, UploadFile, File, Request
from ipfs_upload import upload_to_ipfs
#from contract_call import record_result  # For blockchain write
from evaluator import evaluate_document  # Your custom AI pipeline
import os

app = FastAPI()

# --- Document Evaluation (SBERT + FAISS + LLM) ---
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = evaluate_document(file_path)
    os.remove(file_path)
    return result

# --- Upload result JSON to IPFS ---
@app.post("/upload_ipfs/")
async def upload_ipfs(data: dict):
    try:
        cid = upload_to_ipfs(data)
        return {"status": "success", "cid": cid}
    except Exception as e:
        return {"error": str(e)}

# --- Record IPFS CID + result on Blockchain ---
#@app.post("/record_tx/")
#async def record_tx(request: Request):
#    try:
#        data = await request.json()
#        cid = data["cid"]
#        score = int(data["score"])
#        decision = data["decision"]
#        tx_hash = record_result(cid, score, decision)
#        return {"status": "success", "tx_hash": tx_hash}
#   except Exception as e:
#        return {"error": str(e)}