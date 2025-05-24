from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from ipfs_upload import upload_to_ipfs  # ✅ Uses Pinata
# from contract_call import record_result  # 🔒 Currently disabled
from evaluator import upload_and_check  # 🧠 Your custom Agent AI
import os

app = FastAPI()

# ✅ Allow React (or any other frontend) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Upload & Evaluate Patent
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    result = upload_and_check(file)
    return result

# 📦 Upload evaluation result to IPFS (via Pinata)
@app.post("/upload_ipfs/")
async def upload_ipfs(data: dict):
    try:
        cid = upload_to_ipfs(data)
        return {"cid": cid}  # ✅ frontend expects cid to be string inside {"cid": ...}
    except Exception as e:
        return {"error": str(e)}


# 🛠️ (Optional) Blockchain writing route
# @app.post("/record_tx/")
# async def record_tx(request: Request):
#     try:
#         data = await request.json()
#         cid = data["cid"]
#         score = int(data["score"])
#         decision = data["decision"]
#         tx_hash = record_result(cid, score, decision)
#         return {"status": "success", "tx_hash": tx_hash}
#     except Exception as e:
#         return {"error": str(e)}
