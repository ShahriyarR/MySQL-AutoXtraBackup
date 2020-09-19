from fastapi import FastAPI

app = FastAPI()


@app.post("/backup")
async def backup():
    print("Ready to take backup")
