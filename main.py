from fastapi import FastAPI
from router.router_func import router

app = FastAPI()

app.include_router(router)




